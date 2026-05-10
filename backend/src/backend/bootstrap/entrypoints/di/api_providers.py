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
    CreateShopCommandHandler,
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
from backend.application.commands.create_payment_method import (
    CreatePaymentMethodCommandHandler,
)
from backend.application.commands.create_product import (
    CreateProductCommandHandler,
)
from backend.application.commands.create_recurring_order import (
    CreateRecurringOrderCommandHandler,
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
from backend.application.commands.delete_payment_method import (
    DeletePaymentMethodCommandHandler,
)
from backend.application.commands.delete_product import (
    DeleteProductCommandHandler,
)
from backend.application.commands.delete_recurring_order import (
    DeleteRecurringOrderCommandHandler,
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
from backend.application.commands.edit_order import EditOrderCommandHandler
from backend.application.commands.edit_payment_method import (
    EditPaymentMethodCommandHandler,
)
from backend.application.commands.edit_product import EditProductCommandHandler
from backend.application.commands.edit_shop import EditShopCommandHandler
from backend.application.commands.edit_time_slot import (
    EditTimeSlotCommandHandler,
)
from backend.application.commands.generate_order_export_pdf import (
    GenerateOrderExportPDFCommandHandler,
)
from backend.application.commands.import_clients import (
    ImportClientsCommandHandler,
)
from backend.application.commands.login_telegram import (
    LoginTelegramCommandHandler,
)
from backend.application.commands.logout import LogoutCommandHandler
from backend.application.commands.pause_recurring_order import (
    PauseRecurringOrderCommandHandler,
)
from backend.application.commands.pay_order_from_balance import (
    PayOrderFromBalanceCommandHandler,
)
from backend.application.commands.reorder_route import (
    ReorderRouteCommandHandler,
)
from backend.application.commands.resume_recurring_order import (
    ResumeRecurringOrderCommandHandler,
)
from backend.application.commands.reverse_route import (
    ReverseRouteCommandHandler,
)
from backend.application.commands.run_recurring_order import (
    RunRecurringOrderCommandHandler,
)
from backend.application.commands.set_client_balance import (
    SetClientBalanceCommandHandler,
)
from backend.application.commands.update_order_coordinates import (
    UpdateOrderCoordinatesCommandHandler,
)
from backend.application.commands.update_recurring_order import (
    UpdateRecurringOrderCommandHandler,
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
from backend.application.queries.get_payment_methods import (
    GetPaymentMethodsQueryHandler,
)
from backend.application.queries.get_product import GetProductQueryHandler
from backend.application.queries.get_products import GetProductsQueryHandler
from backend.application.queries.get_recurring_order import (
    GetRecurringOrderQueryHandler,
)
from backend.application.queries.get_recurring_orders import (
    GetRecurringOrdersQueryHandler,
)
from backend.application.queries.get_route import GetRouteQueryHandler
from backend.application.queries.get_routes import GetRoutesQueryHandler
from backend.application.queries.get_shared_route import (
    GetSharedRouteQueryHandler,
)
from backend.application.queries.get_time_slots import GetTimeSlotsQueryHandler
from backend.application.queries.preview_import_xlsx import (
    PreviewImportXlsxQueryHandler,
)
from backend.application.services.generated_order_lifecycle import (
    GeneratedOrderLifecycle,
)
from backend.application.services.geocoder import Geocoder
from backend.application.services.order_deletion import OrderDeletion
from backend.application.services.order_intake import OrderIntake
from backend.application.services.recurring_order_execution import (
    RecurringOrderExecution,
)
from backend.application.services.recurring_order_management_context import (
    RecurringOrderManagementContext,
)
from backend.application.services.recurring_order_occurrence_ledger import (
    RecurringOrderOccurrenceLedger,
)
from backend.application.services.recurring_order_planning_read import (
    RecurringOrderPlanningRead,
)
from backend.application.services.recurring_order_resource_impact import (
    RecurringOrderResourceImpact,
)
from backend.application.services.recurring_order_scheduling_clock import (
    RecurringOrderSchedulingClock,
)
from backend.application.services.recurring_order_template_integrity import (
    RecurringOrderTemplateIntegrity,
)
from backend.application.services.tsp_solvers import RouteOptimizer
from backend.application.usecases.invite_employee.generate_invite_link import (
    GenerateInviteLinkCommandHandler,
)
from backend.infrastructure.auth import (
    AuthChain,
    SessionAuthHandler,
    WebAppAuthHandler,
)
from backend.infrastructure.geocoding import (
    DBGeocodingProvider,
    GoogleGeocoderClient,
    HereGeocoderClient,
    NominatimClient,
)
from backend.infrastructure.idp import ApiIdentityProvider, IdentityProvider
from backend.infrastructure.pdf import ReportLabOrdersPDFGenerator
from backend.infrastructure.persistence.gateways import (
    RedisGeocodeCache,
    RedisSessionGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.telegram.auth import WebAppAuth
from backend.infrastructure.telegram.invite_link_generator import (
    TelegramInviteLinkGenerator,
)
from backend.infrastructure.telegram.widget_auth import WidgetAuth
from backend.infrastructure.transaction_manager import TransactionManager
from backend.infrastructure.tsp_solvers import (
    HeldKarpSolver,
    OSRMClient,
    PyVRPSolver,
)
from backend.infrastructure.xlsx import (
    ClientErrorXlsxGenerator,
    ClientXlsxParser,
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
    google_geocoder = provide(GoogleGeocoderClient)
    here_geocoder = provide(HereGeocoderClient)
    xlsx_parser = provide(ClientXlsxParser)
    xlsx_error_generator = provide(ClientErrorXlsxGenerator)


class GeocoderProvider(Provider):
    scope = Scope.REQUEST

    db_geocoding = provide(DBGeocodingProvider)

    @provide
    def geocoder(
        self,
        cache: RedisGeocodeCache,
        db_provider: DBGeocodingProvider,
        here_client: HereGeocoderClient,
        google_client: GoogleGeocoderClient,
        nominatim_client: NominatimClient,
    ) -> Geocoder:
        return Geocoder(
            cache=cache,
            providers=[
                db_provider,
                nominatim_client,
                here_client,
                google_client,
            ],
        )


class ServicesProvider(Provider):
    scope = Scope.APP

    @provide
    def route_optimizer(self, osrm_client: OSRMClient) -> RouteOptimizer:
        return RouteOptimizer(
            osrm_client=osrm_client,
            held_karp=HeldKarpSolver(),
            pyvrp=PyVRPSolver(),
        )


class APIInteractorsProvider(Provider):
    scope = Scope.REQUEST

    handlers = provide_all(
        CreateProductCommandHandler,
        EditProductCommandHandler,
        DeleteProductCommandHandler,
        GetProductQueryHandler,
        GetProductsQueryHandler,
        CreateRecurringOrderCommandHandler,
        DeleteRecurringOrderCommandHandler,
        PauseRecurringOrderCommandHandler,
        ResumeRecurringOrderCommandHandler,
        RunRecurringOrderCommandHandler,
        UpdateRecurringOrderCommandHandler,
        GetRecurringOrderQueryHandler,
        GetRecurringOrdersQueryHandler,
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
        SetClientBalanceCommandHandler,
        CreateOrderCommandHandler,
        EditOrderCommandHandler,
        PayOrderFromBalanceCommandHandler,
        DeleteOrderCommandHandler,
        GetOrderQueryHandler,
        GetOrdersQueryHandler,
        GetOrderStatsQueryHandler,
        GenerateOrderExportPDFCommandHandler,
        GetRouteQueryHandler,
        GetRoutesQueryHandler,
        GetSharedRouteQueryHandler,
        ReorderRouteCommandHandler,
        ReverseRouteCommandHandler,
        UpdateOrderCoordinatesCommandHandler,
        CreateTimeSlotCommandHandler,
        EditTimeSlotCommandHandler,
        DeleteTimeSlotCommandHandler,
        GetTimeSlotsQueryHandler,
        CreatePaymentMethodCommandHandler,
        EditPaymentMethodCommandHandler,
        DeletePaymentMethodCommandHandler,
        GetPaymentMethodsQueryHandler,
        EditShopCommandHandler,
        CreateShopCommandHandler,
        ImportClientsCommandHandler,
        PreviewImportXlsxQueryHandler,
        LoginTelegramCommandHandler,
        LogoutCommandHandler,
    )

    services = provide_all(
        OrderIntake,
        OrderDeletion,
        GeneratedOrderLifecycle,
        RecurringOrderExecution,
        RecurringOrderManagementContext,
        RecurringOrderOccurrenceLedger,
        RecurringOrderPlanningRead,
        RecurringOrderResourceImpact,
        RecurringOrderSchedulingClock,
        RecurringOrderTemplateIntegrity,
    )

    add_employee = provide_all(GenerateInviteLinkCommandHandler)


class AuthProvider(Provider):
    scope = Scope.REQUEST
    request = from_context(provides=Request)

    auth = provide_all(WidgetAuth, WebAppAuth)

    @provide
    def auth_chain(
        self,
        session_gateway: RedisSessionGateway,
        webapp_auth: WebAppAuth,
        user_gateway: SQLAlchemyUserGateway,
        tr_manager: TransactionManager,
    ) -> AuthChain:
        return AuthChain([
            SessionAuthHandler(session_gateway),
            WebAppAuthHandler(webapp_auth, user_gateway, tr_manager),
        ])

    @provide
    def idp(
        self,
        auth_chain: AuthChain,
        request: Request,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> IdentityProvider:
        return ApiIdentityProvider(
            auth_chain=auth_chain,
            request=request,
            shop_gateway=shop_gateway,
        )
