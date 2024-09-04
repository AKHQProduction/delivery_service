from application.common.specification import Specification
from entities.user.model import RoleName


class HasRoleSpec(Specification):
    def __init__(self, role: RoleName):
        self._role = role

    def is_satisfied_by(self, candidate: RoleName) -> bool:
        return self._role == candidate
