from typing import Protocol


class TSPSolver(Protocol):
    def solve(self, matrix: list[list[float]]) -> list[int]: ...


def route_cost(route: list[int], matrix: list[list[float]]) -> float:
    return sum(matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))


def two_opt(route: list[int], matrix: list[list[float]]) -> list[int]:
    n = len(route)
    if n < 4:
        return route

    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                d1 = (
                    matrix[route[i - 1]][route[i]]
                    + matrix[route[j]][route[(j + 1) % n]]
                )
                d2 = (
                    matrix[route[i - 1]][route[j]]
                    + matrix[route[i]][route[(j + 1) % n]]
                )
                if d2 < d1 - 1e-10:
                    route[i : j + 1] = route[i : j + 1][::-1]
                    improved = True

    return route
