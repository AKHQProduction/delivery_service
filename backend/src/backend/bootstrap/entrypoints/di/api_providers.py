from collections.abc import AsyncIterator

import httpx
from dishka import (
    Provider,
    Scope,
    WithParents,
    from_context,
    provide,
    provide_all,
)
from fastapi import Request

from backend.application.commands import (
    DeleteEmployeeCommandHandler,
    EditEmployeeCommandHandler,
)
from backend.application.commands.create_category import (
    CreateCategoryCommandHandler,
)
from backend.application.commands.create_client import (
    CreateClientCommandHandler,
)
from backend.application.commands.create_district import (
    CreateDistrictCommandHandler,
)
from backend.application.commands.create_order import CreateOrderCommandHandler
from backend.application.commands.create_product import (
    CreateProductCommandHandler,
)
from backend.application.commands.create_time_slot import (
    CreateTimeSlotCommandHandler,
)
from backend.application.commands.delete_category import (
    DeleteCategoryCommandHandler,
)
from backend.application.commands.delete_client import (
    DeleteClientCommandHandler,
)
from backend.application.commands.delete_district import (
    DeleteDistrictCommandHandler,
)
from backend.application.commands.delete_order import DeleteOrderCommandHandler
from backend.application.commands.delete_product import (
    DeleteProductCommandHandler,
)
from backend.application.commands.delete_time_slot import (
    DeleteTimeSlotCommandHandler,
)
from backend.application.commands.edit_category import (
    EditCategoryCommandHandler,
)
from backend.application.commands.edit_client import EditClientCommandHandler
from backend.application.commands.edit_district import (
    EditDistrictCommandHandler,
)
from backend.application.commands.edit_order import UpdateOrderCommandHandler
from backend.application.commands.edit_product import EditProductCommandHandler
from backend.application.commands.edit_shop import EditShopCommandHandler
from backend.application.commands.edit_time_slot import (
    EditTimeSlotCommandHandler,
)
from backend.application.commands.generate_order_export_pdf import (
    GenerateOrderExportPDFCommandHandler,
)
from backend.application.queries.get_categories import (
    GetCategoriesQueryHandler,
)
from backend.application.queries.get_client import GetClientQueryHandler
from backend.application.queries.get_clients import GetClientsQueryHandler
from backend.application.queries.get_districts import (
    GetDistrictsQueryHandler,
)
from backend.application.queries.get_employee import GetEmployeeQueryHandler
from backend.application.queries.get_employees import GetEmployeesQueryHandler
from backend.application.queries.get_me import GetMeQueryHandler
from backend.application.queries.get_order import GetOrderQueryHandler
from backend.application.queries.get_order_stats import (
    GetOrderStatsQueryHandler,
)
from backend.application.queries.get_orders import GetOrdersQueryHandler
from backend.application.queries.get_product import GetProductQueryHandler
from backend.application.queries.get_products import GetProductsQueryHandler
from backend.application.queries.get_time_slots import GetTimeSlotsQueryHandler
from backend.application.services.geocoder import Geocoder
from backend.application.services.route_optimizer import RouteOptimizer
from backend.application.usecases.invite_employee.generate_invite_link import (
    GenerateInviteLinkCommandHandler,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.nominatim import NominatimClient
from backend.infrastructure.osrm import OSRMClient
from backend.infrastructure.pdf import ReportLabOrdersPDFGenerator
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.telegram.auth import Headers, InitData, WebAppAuth
from backend.infrastructure.telegram.invite_link_generator import (
    TelegramInviteLinkGenerator,
)


class AdaptersProvider(Provider):
    scope = Scope.APP

    link_generator = provide(WithParents[TelegramInviteLinkGenerator])

    @provide
    def pdf_generator(self) -> ReportLabOrdersPDFGenerator:
        return ReportLabOrdersPDFGenerator()

    @provide
    async def http_client(self) -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient() as client:
            yield client

    osrm_client = provide(OSRMClient)
    nominatim_client = provide(NominatimClient)


class ServicesProvider(Provider):
    scope = Scope.APP

    route_optimizer = provide(RouteOptimizer)
    geocoder = provide(Geocoder)


class APIInteractorsProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        CreateProductCommandHandler,
        EditProductCommandHandler,
        DeleteProductCommandHandler,
        GetProductQueryHandler,
        GetProductsQueryHandler,
        CreateCategoryCommandHandler,
        EditCategoryCommandHandler,
        DeleteCategoryCommandHandler,
        GetCategoriesQueryHandler,
        CreateDistrictCommandHandler,
        EditDistrictCommandHandler,
        DeleteDistrictCommandHandler,
        GetDistrictsQueryHandler,
        DeleteEmployeeCommandHandler,
        EditEmployeeCommandHandler,
        GetEmployeeQueryHandler,
        GetEmployeesQueryHandler,
        GetMeQueryHandler,
        CreateClientCommandHandler,
        GetClientQueryHandler,
        GetClientsQueryHandler,
        DeleteClientCommandHandler,
        EditClientCommandHandler,
        CreateOrderCommandHandler,
        UpdateOrderCommandHandler,
        DeleteOrderCommandHandler,
        GetOrderQueryHandler,
        GetOrdersQueryHandler,
        GetOrderStatsQueryHandler,
        GenerateOrderExportPDFCommandHandler,
        CreateTimeSlotCommandHandler,
        EditTimeSlotCommandHandler,
        DeleteTimeSlotCommandHandler,
        GetTimeSlotsQueryHandler,
        EditShopCommandHandler,
    )

    add_employee = provide_all(GenerateInviteLinkCommandHandler)


class WebAppProvider(Provider):
    scope = Scope.REQUEST
    request = from_context(provides=Request)

    auth = provide(WebAppAuth)

    @provide
    async def get_headers(self, request: Request) -> Headers:
        return Headers(request.headers)

    @provide
    async def init_data(self, auth: WebAppAuth) -> InitData:
        return auth.with_init_data()

    @provide
    def current_user_id(self, init_data: InitData) -> int:
        return init_data.user.id

    @provide
    def idp(
        self,
        current_user_id: int,
        user_gateway: SQLAlchemyUserGateway,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> TelegramIdentityProvider:
        return TelegramIdentityProvider(
            telegram_id=current_user_id,
            user_gateway=user_gateway,
            shop_gateway=shop_gateway,
        )
