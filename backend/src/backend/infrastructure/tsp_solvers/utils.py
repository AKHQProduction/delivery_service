def route_cost(route: list[int], matrix: list[list[float]]) -> float:
    return sum(matrix[route[i]][route[i + 1]] for i in range(len(route) - 1))


def local_search(route: list[int], matrix: list[list[float]]) -> list[int]:
    n = len(route)
    if n < 4:
        return route

    route = _converge_two_opt(route, matrix)
    route = _converge_or_opt(route, matrix)
    return _converge_two_opt(route, matrix)


def two_opt(route: list[int], matrix: list[list[float]]) -> list[int]:
    if len(route) < 4:
        return route
    return _converge_two_opt(route, matrix)


def _converge_two_opt(
    route: list[int],
    matrix: list[list[float]],
) -> list[int]:
    improved = True
    while improved:
        route, improved = _two_opt_pass(route, matrix)
    return route


def _converge_or_opt(
    route: list[int],
    matrix: list[list[float]],
) -> list[int]:
    improved = True
    while improved:
        route, improved = _or_opt_pass(route, matrix)
    return route


def _or_opt_pass(
    route: list[int],
    matrix: list[list[float]],
) -> tuple[list[int], bool]:
    n = len(route)

    for seg_len in (1, 2, 3):
        for i in range(1, n - seg_len - 1):
            a = route[i - 1]
            seg = route[i : i + seg_len]
            b = route[i + seg_len]

            remove_cost = matrix[a][seg[0]] + matrix[seg[-1]][b] - matrix[a][b]

            for j in range(1, n - 1):
                if i - 1 <= j < i + seg_len:
                    continue
                c, d = route[j], route[j + 1]
                insert_cost = (
                    matrix[c][seg[0]] + matrix[seg[-1]][d] - matrix[c][d]
                )
                if insert_cost - remove_cost < -1e-10:
                    without = route[:i] + route[i + seg_len :]
                    new_j = j if j < i else j - seg_len
                    new_route = (
                        without[: new_j + 1] + seg + without[new_j + 1 :]
                    )
                    return new_route, True

    return route, False


def _two_opt_pass(
    route: list[int],
    matrix: list[list[float]],
) -> tuple[list[int], bool]:
    n = len(route)
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

    return route, improved
