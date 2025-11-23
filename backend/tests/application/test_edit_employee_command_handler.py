import uuid

import pytest

from backend.application.commands.edit_employee import (
    EditEmployeeCommand,
    EditEmployeeCommandHandler,
)
from backend.application.errors import (
    AccessDeniedError,
    EntityNotFoundError,
    ValidationError,
)
from backend.application.interfaces.gateways.shop_gateway import ShopEmployee
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.in_memory import (
    FakeTransactionManager,
    InMemoryIdentityProvider,
    InMemoryShopGateway,
)


@pytest.fixture()
def make_handler():
    def _make_handler(
        user_id: UserId | None = None,
        shop_id: ShopId | None = None,
        role: ShopRole = ShopRole.OWNER,
        employees: dict[UserId, ShopEmployee] | None = None,
    ):
        if not user_id:
            user_id = UserId(uuid.uuid4())
        if not shop_id:
            shop_id = ShopId(uuid.uuid4())

        idp = InMemoryIdentityProvider(
            user_id=user_id, role=role, shop_id=shop_id
        )
        shop_gateway = InMemoryShopGateway()
        if employees:
            shop_gateway.employees = employees
        tr_manager = FakeTransactionManager()

        handler = EditEmployeeCommandHandler(
            idp=idp, shop_gateway=shop_gateway, tr_manager=tr_manager
        )

        return handler, idp, shop_gateway, tr_manager

    return _make_handler


@pytest.mark.asyncio()
async def test_edit_employee_role_successfully(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.COURIER,
    )

    handler, _, shop_gateway, tr_manager = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER
    )

    await handler.handle(command)

    assert shop_gateway.employee_updated is True
    assert tr_manager.committed is True
    assert employee.role == ShopRole.MANAGER


@pytest.mark.asyncio()
async def test_edit_employee_name_successfully(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.MANAGER,
    )

    handler, _, shop_gateway, tr_manager = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(user_id=employee_id, new_name="Jane Smith")

    await handler.handle(command)

    assert shop_gateway.employee_updated is True
    assert tr_manager.committed is True
    assert employee.full_name == "Jane Smith"


@pytest.mark.asyncio()
async def test_edit_employee_both_role_and_name(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.COURIER,
    )

    handler, _, shop_gateway, tr_manager = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER, new_name="Jane Smith"
    )

    await handler.handle(command)

    assert shop_gateway.employee_updated is True
    assert tr_manager.committed is True
    assert employee.role == ShopRole.MANAGER
    assert employee.full_name == "Jane Smith"


@pytest.mark.asyncio()
async def test_raise_access_denied_when_not_owner(make_handler) -> None:
    manager_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.COURIER,
    )

    handler, *_ = make_handler(
        user_id=manager_id,
        shop_id=shop_id,
        role=ShopRole.MANAGER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_entity_not_found_when_employee_not_exists(
    make_handler,
) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, *_ = make_handler(
        user_id=owner_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER
    )

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert "Employee" in exc_info.value.message


@pytest.mark.asyncio()
async def test_raise_access_denied_when_employee_from_different_shop(
    make_handler,
) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    owner_shop_id = ShopId(uuid.uuid4())
    employee_shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=employee_shop_id,
        full_name="John Doe",
        role=ShopRole.COURIER,
    )

    handler, *_ = make_handler(
        user_id=owner_id,
        shop_id=owner_shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER
    )

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_raise_validation_error_when_new_role_is_owner() -> None:
    employee_id = UserId(uuid.uuid4())

    with pytest.raises(ValidationError) as exc_info:
        EditEmployeeCommand(user_id=employee_id, new_role=ShopRole.OWNER)

    assert exc_info.value._field == "new_role"
    assert exc_info.value._value == ShopRole.OWNER
    assert ShopRole.MANAGER in exc_info.value._acceptable_values
    assert ShopRole.COURIER in exc_info.value._acceptable_values


@pytest.mark.asyncio()
async def test_edit_employee_with_only_new_role(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    initial_name = "John Doe"

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name=initial_name,
        role=ShopRole.COURIER,
    )

    handler, _, shop_gateway, _ = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=ShopRole.MANAGER, new_name=None
    )

    await handler.handle(command)

    assert employee.role == ShopRole.MANAGER
    assert employee.full_name == initial_name
    assert shop_gateway.employee_updated is True


@pytest.mark.asyncio()
async def test_edit_employee_with_only_new_name(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())
    initial_role = ShopRole.COURIER

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=initial_role,
    )

    handler, _, shop_gateway, _ = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    command = EditEmployeeCommand(
        user_id=employee_id, new_role=None, new_name="Jane Smith"
    )

    await handler.handle(command)

    assert employee.role == initial_role
    assert employee.full_name == "Jane Smith"
    assert shop_gateway.employee_updated is True
