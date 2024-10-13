from typing import Any

from presentation.common.consts import ACTUAL_GOODS_TYPES


async def get_goods_types(**_kwargs) -> dict[str, Any]:
    return {"types": list(ACTUAL_GOODS_TYPES.items())}
