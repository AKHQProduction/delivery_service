from uuid import UUID

from delivery_service.shared.domain.entity import Entity
from delivery_service.shared.domain.tracker import Tracker


async def test_not_equals_different_entity(tracker: Tracker) -> None:
    first_entity = Entity(
        entity_id=UUID("0195381b-8549-708d-b29b-a923d7870d78"), tracker=tracker
    )
    second_entity = Entity(
        entity_id=UUID("1195381b-8549-708d-b29b-a923d7870d78"), tracker=tracker
    )

    assert first_entity != second_entity
    assert first_entity.entity_id != second_entity.entity_id
