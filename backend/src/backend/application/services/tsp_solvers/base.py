from typing import Protocol


class TSPSolver(Protocol):
    def solve(self, matrix: list[list[float]]) -> list[int]: ...
