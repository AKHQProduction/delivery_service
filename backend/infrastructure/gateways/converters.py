from domain.entities.user import User
from infrastructure.persistence.models import UserORM


def convert_user_entity_to_db_model(user: User) -> UserORM:
    return UserORM(
            user_id=user.user_id.to_raw(),
            full_name=user.full_name,
            username=user.username,
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active
    )
