# Client Preferred Delivery Time Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional preferred delivery time slot to clients and use it to preselect "Час доставки" when creating a new order.

**Architecture:** Persist a nullable `preferred_time_slot_id` on `clients`, validate it through the existing `SQLAlchemyTimeSlotGateway`, expose it through existing client read models, and keep order APIs unchanged. The frontend stores the preference in add/edit client forms and reads it in `useOrderForm` when a client is selected for a new order.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy async ORM, Alembic, pytest, React 19, TypeScript, Vite.

---

## File Structure

- Modify `backend/tests/presentation/http/test_client.py`: backend API tests for create, edit, list, and foreign-shop validation.
- Modify `backend/tests/presentation/http/test_time_slot.py`: backend API test proving time slot deletion clears client preference.
- Modify `backend/tests/conftest.py`: optional `preferred_time_slot_id` fixture support for direct client inserts.
- Create `backend/src/backend/infrastructure/persistence/migrations/versions/00018_add_client_preferred_time_slot.py`: database migration.
- Modify `backend/src/backend/infrastructure/persistence/tables/clients.py`: ORM column and relationship.
- Modify `backend/src/backend/application/dto/gateways/client_gateway.py`: read model field.
- Modify `backend/src/backend/infrastructure/persistence/gateways/client_gateway.py`: save/read preferred slot.
- Modify `backend/src/backend/application/services/client.py`: create/update client preferred slot.
- Modify `backend/src/backend/application/commands/create_client.py`: command field and same-shop validation.
- Modify `backend/src/backend/application/commands/edit_client.py`: command field, omitted-vs-null handling, and same-shop validation.
- Modify `backend/src/backend/presentation/http/v1/schemas/client.py`: edit schema field.
- Modify `backend/src/backend/presentation/http/v1/routes/clients.py`: route mapping for create/edit.
- Modify `frontend/src/types/entities/Client.ts`: client type field.
- Modify `frontend/src/services/api/clientApi.ts`: payload types.
- Modify `frontend/src/hooks/clients/useClientForm.tsx`: form state for preference.
- Modify `frontend/src/components/forms/client/AddClientForm.tsx`: preference select and payload normalization.
- Modify `frontend/src/components/forms/client/EditClientForm.tsx`: preference select and payload normalization.
- Modify `frontend/src/hooks/orders/useOrdersForm.tsx`: preselect preference on client selection for new orders.

---

### Task 1: Backend Tests

**Files:**
- Modify: `backend/tests/conftest.py`
- Modify: `backend/tests/presentation/http/test_client.py`
- Modify: `backend/tests/presentation/http/test_time_slot.py`

- [ ] **Step 1: Extend the client fixture for direct preferred-slot setup**

In `backend/tests/conftest.py`, update `setup_test_client` so tests can create clients with a preference directly:

```python
@pytest.fixture()
def setup_test_client(session: AsyncSession):
    async def _setup_test_client(
        shop_id: ShopId,
        full_name: str = "Test Client",
        phones: list[str] | None = None,
        addresses: list[dict[str, Any]] | None = None,
        balance: Decimal = Decimal(0),
        preferred_time_slot_id: TimeSlotId | None = None,
    ) -> ClientId:
        client_id = ClientId(uuid.uuid4())

        await session.execute(
            insert(Client).values(
                id=client_id,
                full_name=full_name,
                balance=balance,
                shop_id=shop_id,
                preferred_time_slot_id=preferred_time_slot_id,
            )
        )
```

Keep the existing phone/address insert logic below this snippet unchanged.

- [ ] **Step 2: Add client API tests**

In `backend/tests/presentation/http/test_client.py`, add these tests near the existing create/edit/list tests:

```python
@pytest.mark.asyncio()
async def test_create_client_with_preferred_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_time_slot,
) -> None:
    telegram_id = 1100
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.post(
        url=BASE_URL,
        headers=headers,
        json={
            "full_name": "Клієнт з часом",
            "phones": [{"number": "+380501234567"}],
            "addresses": [],
            "preferred_time_slot_id": str(time_slot_id),
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    client_id = response.json()

    await session.flush()

    stored_client = await session.get(Client, uuid.UUID(client_id))
    assert stored_client is not None
    assert stored_client.preferred_time_slot_id == time_slot_id

    client_response = await http_client.get(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
    )
    assert client_response.status_code == status.HTTP_200_OK
    assert client_response.json()["preferred_time_slot_id"] == str(time_slot_id)


@pytest.mark.asyncio()
async def test_edit_client_preferred_time_slot_set_change_and_clear(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_time_slot,
) -> None:
    telegram_id = 3011
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    first_slot_id = await setup_test_time_slot(shop_id=shop_id)
    second_slot_id = await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(10, 0),
        end_time=time(13, 0),
        label="Другий слот",
    )
    client_id = await setup_test_client(shop_id=shop_id)
    await session.commit()

    headers = customer_headers(telegram_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
        json={"preferred_time_slot_id": str(first_slot_id)},
    )
    assert response.status_code == status.HTTP_200_OK

    client_response = await http_client.get(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
    )
    assert client_response.status_code == status.HTTP_200_OK
    assert client_response.json()["preferred_time_slot_id"] == str(first_slot_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
        json={"preferred_time_slot_id": str(second_slot_id)},
    )
    assert response.status_code == status.HTTP_200_OK

    client_response = await http_client.get(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
    )
    assert client_response.status_code == status.HTTP_200_OK
    assert client_response.json()["preferred_time_slot_id"] == str(second_slot_id)

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
        json={"preferred_time_slot_id": None},
    )
    assert response.status_code == status.HTTP_200_OK

    client_response = await http_client.get(
        url=f"{BASE_URL}/{client_id}",
        headers=headers,
    )
    assert client_response.status_code == status.HTTP_200_OK
    assert client_response.json()["preferred_time_slot_id"] is None
```

Add `time` to the existing import from `datetime` in this file:

```python
from datetime import UTC, datetime, time, timedelta
```

- [ ] **Step 3: Add list and foreign-shop validation tests**

In `backend/tests/presentation/http/test_client.py`, add:

```python
@pytest.mark.asyncio()
async def test_get_all_clients_returns_preferred_time_slot(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_time_slot,
) -> None:
    telegram_id = 2103
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    time_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await setup_test_client(
        shop_id=shop_id,
        full_name="Анна з часом",
        phones=["+380501111111"],
        preferred_time_slot_id=time_slot_id,
    )
    await session.commit()

    response = await http_client.get(
        url=f"{BASE_URL}/all",
        headers=customer_headers(telegram_id),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["preferred_time_slot_id"] == str(time_slot_id)


@pytest.mark.asyncio()
async def test_edit_client_rejects_preferred_time_slot_from_another_shop(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_time_slot,
) -> None:
    first_telegram_id = 3012
    second_telegram_id = 3013
    _, first_shop_id = await setup_full_test_user_with_shop(
        telegram_id=first_telegram_id
    )
    _, second_shop_id = await setup_full_test_user_with_shop(
        telegram_id=second_telegram_id
    )
    foreign_slot_id = await setup_test_time_slot(shop_id=second_shop_id)
    client_id = await setup_test_client(shop_id=first_shop_id)
    await session.commit()

    response = await http_client.patch(
        url=f"{BASE_URL}/{client_id}",
        headers=customer_headers(first_telegram_id),
        json={"preferred_time_slot_id": str(foreign_slot_id)},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

    stored_client = await session.get(Client, client_id)
    assert stored_client is not None
    assert stored_client.preferred_time_slot_id is None
```

- [ ] **Step 4: Add time-slot deletion test**

In `backend/tests/presentation/http/test_time_slot.py`, add `Client` to imports from `backend.infrastructure.persistence.tables.clients`, then add:

```python
@pytest.mark.asyncio()
async def test_delete_time_slot_clears_client_preference(
    http_client: AsyncClient,
    session: AsyncSession,
    customer_headers: Callable[[int], dict[str, Any]],
    setup_full_test_user_with_shop,
    setup_test_client,
    setup_test_time_slot,
) -> None:
    telegram_id = 4400
    _, shop_id = await setup_full_test_user_with_shop(telegram_id=telegram_id)
    preferred_slot_id = await setup_test_time_slot(shop_id=shop_id)
    await setup_test_time_slot(
        shop_id=shop_id,
        start_time=time(10, 0),
        end_time=time(13, 0),
        label="Другий слот",
    )
    client_id = await setup_test_client(
        shop_id=shop_id,
        preferred_time_slot_id=preferred_slot_id,
    )
    await session.commit()

    response = await http_client.delete(
        url=f"{BASE_URL}/{preferred_slot_id}",
        headers=customer_headers(telegram_id),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await session.flush()

    stored_client = await session.get(Client, client_id)
    assert stored_client is not None
    assert stored_client.preferred_time_slot_id is None
```

- [ ] **Step 5: Run backend tests and confirm they fail for the new missing field**

Run:

```bash
uv run --project backend pytest backend/tests/presentation/http/test_client.py::test_create_client_with_preferred_time_slot backend/tests/presentation/http/test_client.py::test_edit_client_preferred_time_slot_set_change_and_clear backend/tests/presentation/http/test_client.py::test_get_all_clients_returns_preferred_time_slot backend/tests/presentation/http/test_client.py::test_edit_client_rejects_preferred_time_slot_from_another_shop backend/tests/presentation/http/test_time_slot.py::test_delete_time_slot_clears_client_preference -q
```

Expected: FAIL because `clients.preferred_time_slot_id` and API schema support do not exist yet.

---

### Task 2: Backend Implementation

**Files:**
- Create: `backend/src/backend/infrastructure/persistence/migrations/versions/00018_add_client_preferred_time_slot.py`
- Modify: `backend/src/backend/infrastructure/persistence/tables/clients.py`
- Modify: `backend/src/backend/application/dto/gateways/client_gateway.py`
- Modify: `backend/src/backend/infrastructure/persistence/gateways/client_gateway.py`
- Modify: `backend/src/backend/application/services/client.py`
- Modify: `backend/src/backend/application/commands/create_client.py`
- Modify: `backend/src/backend/application/commands/edit_client.py`
- Modify: `backend/src/backend/presentation/http/v1/schemas/client.py`
- Modify: `backend/src/backend/presentation/http/v1/routes/clients.py`

- [ ] **Step 1: Create the Alembic migration**

Create `backend/src/backend/infrastructure/persistence/migrations/versions/00018_add_client_preferred_time_slot.py`:

```python
"""Add client preferred delivery time slot.

Revision ID: 00018
Revises: 00017
Create Date: 2026-04-27
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "00018"
down_revision: str | Sequence[str] | None = "00017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "clients",
        sa.Column("preferred_time_slot_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_clients_preferred_time_slot_id",
        "clients",
        "shop_delivery_time_slots",
        ["preferred_time_slot_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_clients_preferred_time_slot_id",
        "clients",
        type_="foreignkey",
    )
    op.drop_column("clients", "preferred_time_slot_id")
```

- [ ] **Step 2: Add ORM support**

In `backend/src/backend/infrastructure/persistence/tables/clients.py`, import `TimeSlotId` and the time slot class for type checking:

```python
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    PhoneId,
    ShopId,
    TimeSlotId,
    UserId,
)
```

Add in the `TYPE_CHECKING` block:

```python
    from backend.infrastructure.persistence.tables.shops import (
        Shop,
        ShopDeliveryTimeSlot,
    )
```

Replace the existing single-line `Shop` import in that block with the snippet above.

Add this column after `user_id` in `Client`:

```python
    preferred_time_slot_id: Mapped[TimeSlotId | None] = mapped_column(
        sa.ForeignKey("shop_delivery_time_slots.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
```

Add this relationship after `user`:

```python
    preferred_time_slot: Mapped["ShopDeliveryTimeSlot | None"] = relationship(
        lazy="raise"
    )
```

- [ ] **Step 3: Add read model and gateway persistence**

In `backend/src/backend/application/dto/gateways/client_gateway.py`, import `TimeSlotId` and add the field:

```python
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    PhoneId,
    ShopId,
    TimeSlotId,
)
```

```python
@dataclass(frozen=True)
class ClientReadModel:
    client_id: ClientId
    full_name: str
    phones: list[PhoneDTO]
    addresses: list[AddressDTO]
    balance: Annotated[
        Decimal,
        PlainSerializer(serialize_decimal_as_float, return_type=float),
    ]
    preferred_time_slot_id: TimeSlotId | None = None
```

In `backend/src/backend/infrastructure/persistence/gateways/client_gateway.py`, add `preferred_time_slot_id` to bulk insert rows:

```python
            client_rows.append({
                "id": client.id,
                "shop_id": client.shop_id,
                "full_name": client.full_name,
                "user_id": client.user_id or None,
                "balance": (
                    client.balance
                    if client.balance is not None
                    else Decimal(0)
                ),
                "preferred_time_slot_id": client.preferred_time_slot_id,
            })
```

In `_to_read_model`, include:

```python
            preferred_time_slot_id=client.preferred_time_slot_id,
```

- [ ] **Step 4: Add service-layer create/update support**

In `backend/src/backend/application/services/client.py`, import `Empty` and `TimeSlotId`:

```python
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    Empty,
    PhoneId,
    ShopId,
    TimeSlotId,
)
```

Change `create_client`:

```python
def create_client(
    *,
    client_id: ClientId,
    shop_id: ShopId,
    full_name: str,
    preferred_time_slot_id: TimeSlotId | None = None,
) -> Client:
    return Client(
        id=client_id,
        shop_id=shop_id,
        full_name=full_name,
        balance=Decimal(0),
        preferred_time_slot_id=preferred_time_slot_id,
    )
```

Change `update_client`:

```python
def update_client(
    client: Client,
    *,
    full_name: str | None = None,
    balance: Decimal | None = None,
    preferred_time_slot_id: TimeSlotId | Empty | None = Empty.EMPTY,
) -> None:
    if full_name is not None:
        client.full_name = full_name
    if balance is not None:
        client.balance = balance
    if preferred_time_slot_id is not Empty.EMPTY:
        client.preferred_time_slot_id = preferred_time_slot_id
```

- [ ] **Step 5: Validate preference in create client command**

In `backend/src/backend/application/commands/create_client.py`, import `ensure_exists`, `CurrentUserDTO`, `ensure_related_to_shop`, `SQLAlchemyTimeSlotGateway`, and `TimeSlotId`:

```python
from backend.application.common import ensure_exists
from backend.application.dto.idp import CurrentUserDTO
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import ClientId, DistrictId, ShopId, TimeSlotId
```

Add the command field:

```python
@dataclass(frozen=True)
class CreateClientCommand:
    full_name: str
    phones: list[Phone] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)
    confirm_duplicate_phones: bool = False
    preferred_time_slot_id: TimeSlotId | None = None
```

Add `time_slot_gateway` to the handler constructor:

```python
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
```

Assign it:

```python
        self._time_slot_gateway = time_slot_gateway
```

Before `create_client(...)`, resolve the preference:

```python
        preferred_time_slot_id = await self._resolve_preferred_time_slot_id(
            command.preferred_time_slot_id,
            current_user,
        )
```

Pass it:

```python
        client = create_client(
            client_id=client_id,
            shop_id=current_user.shop_id,
            full_name=command.full_name,
            preferred_time_slot_id=preferred_time_slot_id,
        )
```

Add this method to `CreateClientCommandHandler`:

```python
    async def _resolve_preferred_time_slot_id(
        self,
        time_slot_id: TimeSlotId | None,
        current_user: CurrentUserDTO,
    ) -> TimeSlotId | None:
        if time_slot_id is None:
            return None

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)
        return time_slot.id
```

- [ ] **Step 6: Validate preference in edit client command**

In `backend/src/backend/application/commands/edit_client.py`, import `SQLAlchemyTimeSlotGateway`, `Empty`, and `TimeSlotId`:

```python
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    Empty,
    PhoneId,
    TimeSlotId,
)
```

Add the command field:

```python
@dataclass(frozen=True)
class EditClientCommand:
    client_id: ClientId
    full_name: str | None = None
    balance: Decimal | None = None
    phones: list[Phone] | None = None
    addresses: list[Address] | None = None
    confirm_duplicate_phones: bool = False
    preferred_time_slot_id: TimeSlotId | Empty | None = Empty.EMPTY
```

Add `time_slot_gateway` to the handler constructor and assign it:

```python
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
```

```python
        self._time_slot_gateway = time_slot_gateway
```

Change the first update block:

```python
        preferred_time_slot_id = await self._resolve_preferred_time_slot_id(
            command.preferred_time_slot_id,
            current_user,
        )

        if (
            command.full_name is not None
            or command.balance is not None
            or preferred_time_slot_id is not Empty.EMPTY
        ):
            update_client(
                client,
                full_name=command.full_name,
                balance=command.balance,
                preferred_time_slot_id=preferred_time_slot_id,
            )
            if command.full_name is not None:
                updates.append(f"full_name={command.full_name}")
            if command.balance is not None:
                updates.append(f"balance={command.balance}")
            if preferred_time_slot_id is not Empty.EMPTY:
                updates.append(
                    f"preferred_time_slot_id={preferred_time_slot_id}"
                )
```

Add this method to `EditClientCommandHandler`:

```python
    async def _resolve_preferred_time_slot_id(
        self,
        time_slot_id: TimeSlotId | Empty | None,
        current_user: CurrentUserDTO,
    ) -> TimeSlotId | Empty | None:
        if time_slot_id is Empty.EMPTY or time_slot_id is None:
            return time_slot_id

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)
        return time_slot.id
```

- [ ] **Step 7: Expose preference through schemas and routes**

In `backend/src/backend/presentation/http/v1/schemas/client.py`, import `TimeSlotId` and add the field:

```python
from backend.application.vars import TimeSlotId
```

```python
class EditClientSchema(BaseModel):
    full_name: str | None = None
    balance: Decimal | None = Field(
        default=None, max_digits=10, decimal_places=2
    )
    phones: list[PhoneSchema] | None = None
    addresses: list[AddressSchema] | None = None
    confirm_duplicate_phones: bool = False
    preferred_time_slot_id: TimeSlotId | None = None
```

In `backend/src/backend/presentation/http/v1/routes/clients.py`, import `Empty` and `TimeSlotId`:

```python
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    Empty,
    PhoneId,
    TimeSlotId,
)
```

In `update_client`, pass:

```python
            preferred_time_slot_id=(
                TimeSlotId(body.preferred_time_slot_id)
                if body.preferred_time_slot_id is not None
                else None
            )
            if "preferred_time_slot_id" in body.model_fields_set
            else Empty.EMPTY,
```

In the create endpoint, no manual mapping is needed because FastAPI parses `CreateClientCommand` directly after Task 2 Step 5 adds the dataclass field.

- [ ] **Step 8: Run backend tests**

Run:

```bash
uv run --project backend pytest backend/tests/presentation/http/test_client.py::test_create_client_with_preferred_time_slot backend/tests/presentation/http/test_client.py::test_edit_client_preferred_time_slot_set_change_and_clear backend/tests/presentation/http/test_client.py::test_get_all_clients_returns_preferred_time_slot backend/tests/presentation/http/test_client.py::test_edit_client_rejects_preferred_time_slot_from_another_shop backend/tests/presentation/http/test_time_slot.py::test_delete_time_slot_clears_client_preference -q
```

Expected: PASS.

- [ ] **Step 9: Run focused backend regression tests**

Run:

```bash
uv run --project backend pytest backend/tests/presentation/http/test_client.py backend/tests/presentation/http/test_time_slot.py -q
```

Expected: PASS.

- [ ] **Step 10: Commit backend implementation**

Run:

```bash
git add backend/tests/conftest.py backend/tests/presentation/http/test_client.py backend/tests/presentation/http/test_time_slot.py backend/src/backend/infrastructure/persistence/migrations/versions/00018_add_client_preferred_time_slot.py backend/src/backend/infrastructure/persistence/tables/clients.py backend/src/backend/application/dto/gateways/client_gateway.py backend/src/backend/infrastructure/persistence/gateways/client_gateway.py backend/src/backend/application/services/client.py backend/src/backend/application/commands/create_client.py backend/src/backend/application/commands/edit_client.py backend/src/backend/presentation/http/v1/schemas/client.py backend/src/backend/presentation/http/v1/routes/clients.py
git commit -m "feat: store client preferred delivery time"
```

---

### Task 3: Frontend Client Forms

**Files:**
- Modify: `frontend/src/types/entities/Client.ts`
- Modify: `frontend/src/services/api/clientApi.ts`
- Modify: `frontend/src/hooks/clients/useClientForm.tsx`
- Modify: `frontend/src/components/forms/client/AddClientForm.tsx`
- Modify: `frontend/src/components/forms/client/EditClientForm.tsx`

- [ ] **Step 1: Add client and payload types**

In `frontend/src/types/entities/Client.ts`, add:

```ts
export interface Client {
  client_id: string;
  full_name?: string;
  phones?: Phone[];
  addresses?: Address[];
  balance?: number;
  preferred_time_slot_id?: string | null;
}
```

In `frontend/src/services/api/clientApi.ts`, update payloads:

```ts
interface UpdateClientPayload {
  full_name?: string;
  balance?: number;
  phones?: Phone[];
  addresses?: Address[];
  preferred_time_slot_id?: string | null;
}

interface CreateClientPayload {
  full_name: string;
  phones: Phone[];
  addresses: Address[];
  preferred_time_slot_id?: string | null;
}
```

- [ ] **Step 2: Store preference in client form state**

In `frontend/src/hooks/clients/useClientForm.tsx`, add `preferred_time_slot_id` in all three form initializers.

Initial state:

```ts
  const [formData, setFormData] = useState(() => ({
    full_name: initialData?.full_name || "",
    preferred_time_slot_id: initialData?.preferred_time_slot_id || "",
    phones: initialData?.phones || ([{ number: "", is_primary: true, id: 0 }] as Phone[]),
    addresses:
      initialData?.addresses ||
```

`initializeForm`:

```ts
    setFormData({
      full_name: client.full_name || "",
      preferred_time_slot_id: client.preferred_time_slot_id || "",
      phones:
```

`resetForm`:

```ts
    setFormData({
      full_name: "",
      preferred_time_slot_id: "",
      phones: [{ number: "", is_primary: true }],
```

- [ ] **Step 3: Add the select to add client form**

In `frontend/src/components/forms/client/AddClientForm.tsx`, import `FormSelect` and `useTimeSlotsSettings`:

```ts
import { FormSelect } from "../../shared/FormSelect";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";
```

Inside the component, load slots and format options:

```ts
  const { timeSlots } = useTimeSlotsSettings();
  const timeSlotOptions = timeSlots.map((slot) => ({
    value: slot.time_slot_id,
    label: slot.label
      ? `${slot.label} (${slot.start_time} - ${slot.end_time})`
      : `${slot.start_time} - ${slot.end_time}`,
  }));
```

Add a helper:

```ts
  const buildClientPayload = (data: typeof formData) => ({
    ...data,
    preferred_time_slot_id: data.preferred_time_slot_id || null,
  });
```

Use it in both create calls:

```ts
      const response = await createClient(buildClientPayload(formData), false);
```

```ts
      const response = await createClient(buildClientPayload(pendingClientData), true);
```

Add `preferred_time_slot_id` to both `fullClient` objects:

```ts
        preferred_time_slot_id: formData.preferred_time_slot_id || null,
```

```ts
        preferred_time_slot_id: pendingClientData.preferred_time_slot_id || null,
```

Render the select after the client name input:

```tsx
        <FormSelect
          label="Бажаний час доставки"
          name="preferred_time_slot_id"
          value={formData.preferred_time_slot_id}
          onChange={(e) =>
            setFormData({
              ...formData,
              preferred_time_slot_id: e.target.value,
            })
          }
          options={timeSlotOptions}
        />
```

- [ ] **Step 4: Add the select to edit client form**

In `frontend/src/components/forms/client/EditClientForm.tsx`, import `FormSelect` and `useTimeSlotsSettings`:

```ts
import { FormSelect } from "../../shared/FormSelect";
import { useTimeSlotsSettings } from "../../../hooks/settings/useTimeSlotsSettings";
```

Inside the component:

```ts
  const { timeSlots } = useTimeSlotsSettings();
  const timeSlotOptions = timeSlots.map((slot) => ({
    value: slot.time_slot_id,
    label: slot.label
      ? `${slot.label} (${slot.start_time} - ${slot.end_time})`
      : `${slot.start_time} - ${slot.end_time}`,
  }));
```

Add:

```ts
  const buildClientPayload = (data: typeof formData, nextBalance: number) => ({
    ...data,
    balance: nextBalance,
    preferred_time_slot_id: data.preferred_time_slot_id || null,
  });
```

Use it in both update calls:

```ts
      await updateClient(client.client_id, buildClientPayload(formData, nextBalance));
```

```ts
      await updateClient(
        client.client_id,
        buildClientPayload(pendingClientData, nextBalance),
        true,
      );
```

Render the select after the balance field:

```tsx
        <FormSelect
          label="Бажаний час доставки"
          name="preferred_time_slot_id"
          value={formData.preferred_time_slot_id}
          onChange={(e) =>
            setFormData({
              ...formData,
              preferred_time_slot_id: e.target.value,
            })
          }
          options={timeSlotOptions}
        />
```

- [ ] **Step 5: Run frontend build**

Run:

```bash
npm run build --prefix frontend
```

Expected: PASS.

- [ ] **Step 6: Commit frontend client forms**

Run:

```bash
git add frontend/src/types/entities/Client.ts frontend/src/services/api/clientApi.ts frontend/src/hooks/clients/useClientForm.tsx frontend/src/components/forms/client/AddClientForm.tsx frontend/src/components/forms/client/EditClientForm.tsx
git commit -m "feat: edit client preferred delivery time"
```

---

### Task 4: New Order Autopreselection

**Files:**
- Modify: `frontend/src/hooks/orders/useOrdersForm.tsx`

- [ ] **Step 1: Preselect the client's preferred slot when choosing a client**

In `frontend/src/hooks/orders/useOrdersForm.tsx`, replace `handleClientSelect` with:

```ts
  const handleClientSelect = useCallback(
    (client: Client) => {
      setFormData((prev) => ({
        ...prev,
        client,
        deliveryPhone: client.phones?.[0] || null,
        deliveryAddress: client.addresses?.[0] || null,
        timeSlotId: initialOrder
          ? prev.timeSlotId
          : client.preferred_time_slot_id || "",
      }));
    },
    [initialOrder],
  );
```

- [ ] **Step 2: Keep manually selected slots stable**

Read the two call sites in `frontend/src/components/forms/orders/AddOrderForm.tsx` and `frontend/src/components/forms/orders/AddOrderFormWeb.tsx`.

Expected behavior after Step 1:

- Selecting a client once preselects `client.preferred_time_slot_id`.
- Calling `handleTimeSlotChange` after that stores the operator's explicit slot.
- The slot changes again only if the operator selects a different client.
- Existing order initialization still uses `initialOrder.time_slot_id`.

No code change is needed in the order form components for this step.

- [ ] **Step 3: Run frontend build and lint**

Run:

```bash
npm run build --prefix frontend
npm run lint --prefix frontend
```

Expected: both commands PASS. If lint reports pre-existing unrelated files, capture the exact filenames and messages before continuing.

- [ ] **Step 4: Commit order form autopreselection**

Run:

```bash
git add frontend/src/hooks/orders/useOrdersForm.tsx
git commit -m "feat: preselect client delivery time in orders"
```

---

### Task 5: Final Verification

**Files:**
- Read-only verification across backend and frontend.

- [ ] **Step 1: Run focused backend tests**

Run:

```bash
uv run --project backend pytest backend/tests/presentation/http/test_client.py backend/tests/presentation/http/test_time_slot.py backend/tests/presentation/http/test_order.py -q
```

Expected: PASS.

- [ ] **Step 2: Run frontend checks**

Run:

```bash
npm run build --prefix frontend
npm run lint --prefix frontend
```

Expected: PASS.

- [ ] **Step 3: Inspect final diff**

Run:

```bash
git status --short
git log --oneline -4
```

Expected:

- `git status --short` shows no tracked changes left unstaged.
- The untracked `.DS_Store` may still appear and must remain untouched.
- The recent commits include the backend implementation and frontend implementation commits from this plan.

---

## Self-Review

Spec coverage:

- Storing a nullable client preferred slot is covered by Task 2.
- Add/edit client UI is covered by Task 3.
- Client read/list response is covered by Task 2 and tested by Task 1.
- New order form preselection is covered by Task 4.
- Existing orders and order APIs remain unchanged by design; Task 4 preserves edit-order initialization.
- Time slot deletion clearing preference is covered by Task 1 and Task 2.

Placeholder scan:

- The plan contains no placeholder markers.
- Each code-changing task includes concrete file paths, code snippets, commands, and expected outcomes.

Type consistency:

- The persisted and API field name is `preferred_time_slot_id` in backend and frontend.
- Backend uses `TimeSlotId | None` for create/read and `TimeSlotId | Empty | None` for edit so omitted fields do not clear existing preferences.
- Frontend form state stores an empty string for the select and normalizes it to `null` before API submission.
