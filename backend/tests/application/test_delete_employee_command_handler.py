import uuid

import pytest

from backend.application.commands.delete_employee import (
    DeleteEmployeeCommand,
    DeleteEmployeeCommandHandler,
)
from backend.application.errors import AccessDeniedError, EntityNotFoundError
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

        handler = DeleteEmployeeCommandHandler(
            idp=idp, shop_gateway=shop_gateway, tr_manager=tr_manager
        )

        return handler, idp, shop_gateway, tr_manager

    return _make_handler


@pytest.mark.asyncio()
async def test_delete_employee_successfully(make_handler) -> None:
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

    command = DeleteEmployeeCommand(user_id=employee_id)

    await handler.handle(command)

    assert employee_id not in shop_gateway.employees
    assert tr_manager.committed is True


@pytest.mark.asyncio()
async def test_delete_employee_denied_for_manager(make_handler) -> None:
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

    command = DeleteEmployeeCommand(user_id=employee_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_delete_employee_denied_for_courier(make_handler) -> None:
    courier_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.MANAGER,
    )

    handler, *_ = make_handler(
        user_id=courier_id,
        shop_id=shop_id,
        role=ShopRole.COURIER,
        employees={employee_id: employee},
    )

    command = DeleteEmployeeCommand(user_id=employee_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_delete_employee_not_found(make_handler) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    handler, *_ = make_handler(
        user_id=owner_id, shop_id=shop_id, role=ShopRole.OWNER
    )

    command = DeleteEmployeeCommand(user_id=employee_id)

    with pytest.raises(EntityNotFoundError) as exc_info:
        await handler.handle(command)

    assert "Employee" in exc_info.value.message


@pytest.mark.asyncio()
async def test_delete_employee_from_different_shop_denied(
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

    command = DeleteEmployeeCommand(user_id=employee_id)

    with pytest.raises(AccessDeniedError):
        await handler.handle(command)


@pytest.mark.asyncio()
async def test_delete_employee_removes_from_linked_users(
    make_handler,
) -> None:
    owner_id = UserId(uuid.uuid4())
    employee_id = UserId(uuid.uuid4())
    shop_id = ShopId(uuid.uuid4())

    employee = ShopEmployee(
        user_id=employee_id,
        shop_id=shop_id,
        full_name="John Doe",
        role=ShopRole.MANAGER,
    )

    handler, _, shop_gateway, _ = make_handler(
        user_id=owner_id,
        shop_id=shop_id,
        role=ShopRole.OWNER,
        employees={employee_id: employee},
    )

    # Add employee to linked_users
    shop_gateway.linked_users.add(employee_id)

    command = DeleteEmployeeCommand(user_id=employee_id)

    await handler.handle(command)

    assert employee_id not in shop_gateway.employees
    assert employee_id not in shop_gateway.linked_users
