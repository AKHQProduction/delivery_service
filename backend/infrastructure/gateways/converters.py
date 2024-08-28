from domain.user.entity.user import User
from domain.user.value_objects.user_id import UserId
from infrastructure.persistence.models import UserORM


def convert_user_entity_to_db_user(user: User) -> UserORM:
    return UserORM(
            user_id=user.user_id.to_raw(),
            full_name=user.full_name,
            username=user.username,
            phone_number=user.phone_number,
            role=user.role,
            is_active=user.is_active
    )


def convert_db_user_to_user_entity(db_user: UserORM) -> User:
    return User(
            user_id=UserId(db_user.user_id),
            full_name=db_user.full_name,
            role=db_user.role,
            username=db_user.username,
            phone_number=db_user.phone_number,
            is_active=db_user.is_active
    )
