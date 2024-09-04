from entities.common.errors import DomainError


class AccessDeniedError(DomainError):
    @property
    def message(self):
        return "Access denied"
