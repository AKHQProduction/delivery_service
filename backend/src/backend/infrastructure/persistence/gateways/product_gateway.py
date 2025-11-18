from typing import cast
from uuid import UUID

from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.product_gateway import (
    CreateProductDTO,
    GetProductsFilters,
    Product,
    ProductGateway,
    ProductReadModel,
)
from backend.application.vars import ProductCategory, ProductId, ShopId
from backend.infrastructure.persistence.tables import Product as ProductDB


class SQLAlchemyProductGateway(ProductGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def next_id(self) -> ProductId:
        return ProductId(UUID(str(uuid7())))

    async def create_product(self, dto: CreateProductDTO) -> None:
        self._session.add(
            ProductDB(
                id=dto.product_id,
                shop_id=dto.shop_id,
                name=dto.name,
                price=dto.price,
                category=str(dto.category),
            )
        )

    async def load(self, product_id: ProductId) -> Product | None:
        row = await self._session.get(ProductDB, product_id)
        if row:
            return Product(
                product_id=ProductId(cast("UUID", cast("object", row.id))),
                shop_id=ShopId(cast("UUID", cast("object", row.shop_id))),
                name=cast("str", cast("object", row.name)),
                category=ProductCategory(
                    cast("str", cast("object", row.category))
                ),
                price=int(cast("int", cast("object", row.price))),
            )
        return None

    async def update(self, updated_product: Product) -> None:
        product_db = await self._session.get(
            ProductDB, updated_product.product_id
        )
        if product_db:
            product_db.name = updated_product.name
            product_db.price = updated_product.price
            product_db.category = str(updated_product.category)

    async def delete(self, product_id: ProductId) -> None:
        product_db = await self._session.get(ProductDB, product_id)
        if product_db:
            await self._session.delete(product_db)

    async def read(
        self, product_id: ProductId, shop_id: ShopId
    ) -> ProductReadModel | None:
        row = await self._session.get(ProductDB, product_id)
        if row:
            return ProductReadModel(
                product_id=ProductId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
                category=ProductCategory(
                    cast("str", cast("object", row.category))
                ),
                price=int(cast("int", cast("object", row.price))),
            )
        return None

    async def read_all(
        self, filters: GetProductsFilters, pagination: Pagination
    ) -> list[ProductReadModel]:
        query = select(ProductDB)

        if filters.shop_id:
            query = query.where(ProductDB.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(ProductDB.name.ilike(f"%{filters.name}%"))

        if pagination.order == SortOrder.ASC:
            query = query.order_by(asc(ProductDB.name))
        else:
            query = query.order_by(desc(ProductDB.name))

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.scalars().all()

        return [
            ProductReadModel(
                product_id=ProductId(cast("UUID", cast("object", row.id))),
                name=cast("str", cast("object", row.name)),
                category=ProductCategory(
                    cast("str", cast("object", row.category))
                ),
                price=int(cast("int", cast("object", row.price))),
            )
            for row in rows
        ]
