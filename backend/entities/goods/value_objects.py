from dataclasses import dataclass

from entities.goods.errors import (
    GoodsTitleTooLongError,
    GoodsTitleTooShortError,
)


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class GoodsTitle:
    title: str

    MIN_TITLE_LEN = 3
    MAX_TITLE_LEN = 20

    def __post_init__(self) -> None:
        len_value = len(self.title)

        if len_value < self.MIN_TITLE_LEN:
            raise GoodsTitleTooShortError(self.title)

        if len_value > self.MAX_TITLE_LEN:
            raise GoodsTitleTooLongError(self.title)

    def __str__(self) -> str:
        return self.title
