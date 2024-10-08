from application.common.specification import Specification


class Greate(Specification):
    def __init__(self, value: int):
        self.value = value

    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate > self.value


class Less(Specification):
    def __init__(self, value: int):
        self.value = value

    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate < self.value
