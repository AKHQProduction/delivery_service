from sqlalchemy import asc, desc
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import Select

from backend.application.dto.gateways import Pagination, SortOrder


def apply_sorting(
    query: Select,
    sort_column: InstrumentedAttribute,
    id_column: InstrumentedAttribute,
    pagination: Pagination,
) -> Select:
    order = asc if pagination.order == SortOrder.ASC else desc
    return (
        query
        .order_by(order(sort_column), asc(id_column))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )
