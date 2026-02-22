import logging

logger = logging.getLogger(__name__)


class HeldKarpSolver:
    def solve(self, matrix: list[list[float]]) -> list[int]:
        n = len(matrix)
        logger.info("Held-Karp solver started: n=%d", n)

        if n <= 2:
            return [*list(range(n)), 0]

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

        path: list[int] = []
        mask = full_mask
        cur = best_last
        while cur != 0:
            path.append(cur)
            prev = parent[mask, cur]
            mask ^= 1 << cur
            cur = prev
        path.reverse()
        route = [0, *path, 0]

        logger.info("Held-Karp solver finished: n=%d, cost=%.1f", n, best_cost)
        return route
