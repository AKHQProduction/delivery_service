from entities.common.errors.base import DomainError


class AccessDeniedError(DomainError):
    @property
    def message(self):
        return "Access denied"
