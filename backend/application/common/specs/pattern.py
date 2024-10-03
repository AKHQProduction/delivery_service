import re

from application.common.specification import Specification


class MatchPattern(Specification):
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)

    def is_satisfied_by(self, candidate: str) -> bool:
        return bool(self.pattern.match(candidate))
