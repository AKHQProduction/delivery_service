import json
import uuid
from typing import Any

import pytest
from redis.asyncio import Redis

from backend.application.usecases.invite_employee.interfaces import Link
from backend.application.vars import ShopId, ShopRole
from backend.infrastructure.persistence.gateways import RedisLinkGateway


@pytest.mark.asyncio()
async def test_add(
    link_gateway: RedisLinkGateway, redis_client: Redis
) -> None:
    payload = "abc"
    role = ShopRole.MANAGER
    shop_id = ShopId(uuid.uuid4())
    full_name = "Test User"
    link = Link(
        payload=payload, role=role, shop_id=shop_id, full_name=full_name
    )

    await link_gateway.add(link)

    stored_value = await redis_client.get(payload)
    assert stored_value is not None

    serialize_value: dict[str, Any] = json.loads(stored_value)
    assert serialize_value["payload"] == payload
    assert serialize_value["role"] == role
    assert serialize_value["shop_id"] == str(shop_id)
    assert serialize_value["full_name"] == full_name

    ttl = await redis_client.ttl(payload)
    assert ttl > 0


@pytest.mark.asyncio()
async def test_load_by_payload(
    link_gateway: RedisLinkGateway, redis_client: Redis
) -> None:
    payload = "abc"
    role = ShopRole.MANAGER
    shop_id = ShopId(uuid.uuid4())
    full_name = "Test User"

    await redis_client.set(
        name=payload,
        value=json.dumps({
            "payload": payload,
            "role": role,
            "shop_id": str(shop_id),
            "full_name": full_name,
        }),
    )

    stored_value = await link_gateway.load_by_payload(payload)

    assert stored_value
    assert stored_value.payload == payload
    assert stored_value.shop_id == shop_id
    assert stored_value.full_name == full_name
    assert stored_value.role == role


@pytest.mark.asyncio()
async def test_load_none_by_payload(link_gateway: RedisLinkGateway) -> None:
    stored_value = await link_gateway.load_by_payload("payload")

    assert stored_value is None


@pytest.mark.asyncio()
async def test_delete_existing_link(
    link_gateway: RedisLinkGateway, redis_client: Redis
) -> None:
    payload = "abc"
    role = ShopRole.MANAGER
    shop_id = ShopId(uuid.uuid4())
    full_name = "Test User"

    await redis_client.set(
        name=payload,
        value=json.dumps({
            "payload": payload,
            "role": role,
            "shop_id": str(shop_id),
            "full_name": full_name,
        }),
    )

    await link_gateway.delete(payload)
    data = await redis_client.get(payload)

    assert data is None
