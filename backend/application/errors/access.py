from application.common.errors.base import ApplicationError


class AccessDeniedError(ApplicationError):
    @property
    def message(self):
        return "Access denied"
