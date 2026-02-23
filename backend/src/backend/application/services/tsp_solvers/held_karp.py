import logging

logger = logging.getLogger(__name__)

MAX_N = 22


class HeldKarpSolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info("Held-Karp solver started: n=%d", n)

        if n <= 2:
            return [*range(n), 0]

        if n > MAX_N:
            msg = "Held-Karp: n=%d exceeds max %d"
            raise ValueError(msg % (n, MAX_N))

        dp, parent = _fill_dp(matrix, n)
        route = _backtrack(dp, parent, matrix, n)

        cost = sum(
            matrix[route[i]][route[i + 1]] for i in range(len(route) - 1)
        )
        logger.info(
            "Held-Karp solver finished: n=%d, cost=%.1f",
            n,
            cost,
        )
        return route


def _fill_dp(
    matrix: list[list[float]],
    n: int,
) -> tuple[dict, dict]:
    dp: dict[tuple[int, int], float] = {}
    parent: dict[tuple[int, int], int] = {}

    for i in range(1, n):
        dp[1 << i, i] = matrix[0][i]
        parent[1 << i, i] = 0

    for size in range(2, n):
        for mask in range(1, 1 << n):
            if mask & 1:
                continue
            if mask.bit_count() != size:
                continue
            for last in range(1, n):
                if not (mask & (1 << last)):
                    continue
                prev_mask = mask ^ (1 << last)
                best_cost = float("inf")
                best_prev = -1
                for prev in range(1, n):
                    if not (prev_mask & (1 << prev)):
                        continue
                    key = (prev_mask, prev)
                    if key not in dp:
                        continue
                    cost = dp[key] + matrix[prev][last]
                    if cost < best_cost:
                        best_cost = cost
                        best_prev = prev
                if best_prev != -1:
                    dp[mask, last] = best_cost
                    parent[mask, last] = best_prev

    return dp, parent


def _backtrack(
    dp: dict,
    parent: dict,
    matrix: list[list[float]],
    n: int,
) -> list[int]:
    full_mask = ((1 << n) - 1) ^ 1
    best_cost = float("inf")
    best_last = -1

    for last in range(1, n):
        key = (full_mask, last)
        if key not in dp:
            continue
        cost = dp[key] + matrix[last][0]
        if cost < best_cost:
            best_cost = cost
            best_last = last

    if best_last == -1:
        msg = "Held-Karp: no valid tour, matrix may be disconnected (n=%d)"
        raise RuntimeError(msg % n)

    path: list[int] = []
    mask = full_mask
    cur = best_last
    while cur != 0:
        path.append(cur)
        prev = parent[mask, cur]
        mask ^= 1 << cur
        cur = prev
    path.reverse()
    return [0, *path, 0]
