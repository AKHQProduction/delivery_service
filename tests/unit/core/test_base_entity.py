from uuid import UUID

from delivery_service.shared.domain.entity import Entity


async def test_not_equals_different_entity() -> None:
    first_entity = Entity(
        entity_id=UUID("0195381b-8549-708d-b29b-a923d7870d78"),
    )
    second_entity = Entity(
        entity_id=UUID("1195381b-8549-708d-b29b-a923d7870d78"),
    )

    assert first_entity != second_entity
    assert first_entity.entity_id != second_entity.entity_id
