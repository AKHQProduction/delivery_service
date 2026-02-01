from backend.application.errors import EntityNotFoundError


def ensure_exists[T](entity: T | None, name: str) -> T:
    if entity is None:
        raise EntityNotFoundError(entity=name)
    return entity
