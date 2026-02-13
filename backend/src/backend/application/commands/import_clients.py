import asyncio
import logging
from dataclasses import dataclass

from backend.application.errors import InvalidPhoneNumberError
from backend.application.policies.access import ensure_can_manage
from backend.application.services.client import (
    create_address,
    create_client,
    create_phone,
)
from backend.application.services.district import create_district
from backend.application.validators import normalize_ukraine_phone
from backend.application.vars import DistrictId, ShopId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyDistrictGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    ClientAddress,
)
from backend.infrastructure.transaction_manager import TransactionManager
from backend.infrastructure.xlsx import ClientXlsxParser
from backend.infrastructure.xlsx.client_xlsx_parser import (
    ParsedAddress,
    ParsedClientRow,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportClientsCommand:
    file_bytes: bytes


@dataclass(frozen=True)
class ImportClientsResult:
    imported: int


class ImportClientsCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        district_gateway: SQLAlchemyDistrictGateway,
        tr_manager: TransactionManager,
        parser: ClientXlsxParser,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._district_gateway = district_gateway
        self._tr_manager = tr_manager
        self._parser = parser

    async def handle(
        self,
        command: ImportClientsCommand,
    ) -> ImportClientsResult:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        shop_id = current_user.shop_id

        loop = asyncio.get_running_loop()
        parsed_rows = await loop.run_in_executor(
            None, self._parser.parse, command.file_bytes
        )

        if not parsed_rows:
            return ImportClientsResult(imported=0)

        district_map = await self._resolve_districts(shop_id, parsed_rows)

        clients = []
        for row in parsed_rows:
            phone1 = self._normalize_phone(row.phone1)
            if phone1 is None:
                continue

            phone2 = self._normalize_phone(row.phone2) if row.phone2 else None

            client_id = self._client_gateway.next_id()
            client = create_client(
                client_id=client_id,
                shop_id=shop_id,
                full_name=row.full_name,
            )

            phones = [
                create_phone(
                    number=phone1,
                    is_primary=True,
                    shop_id=shop_id,
                ),
            ]
            if phone2:
                phones.append(
                    create_phone(
                        number=phone2,
                        is_primary=False,
                        shop_id=shop_id,
                    )
                )
            client.phones = phones

            addresses = [
                self._build_address(
                    row.address1,
                    is_primary=True,
                    district_map=district_map,
                ),
            ]
            if row.address2:
                addresses.append(
                    self._build_address(
                        row.address2,
                        is_primary=False,
                        district_map=district_map,
                    ),
                )
            client.addresses = addresses

            clients.append(client)

        if clients:
            self._client_gateway.save_all(clients)
            await self._tr_manager.commit()

        logger.info(
            "Imported %d clients for shop %s (parsed %d rows)",
            len(clients),
            shop_id,
            len(parsed_rows),
        )
        return ImportClientsResult(imported=len(clients))

    async def _resolve_districts(
        self,
        shop_id: ShopId,
        rows: list[ParsedClientRow],
    ) -> dict[str, DistrictId]:
        names: set[str] = set()
        for row in rows:
            if row.address1.district_name:
                names.add(row.address1.district_name)
            if row.address2 and row.address2.district_name:
                names.add(row.address2.district_name)

        if not names:
            return {}

        existing = await self._district_gateway.find_by_names(shop_id, names)
        district_map = {d.name.lower(): DistrictId(d.id) for d in existing}

        for name in names:
            if name.lower() not in district_map:
                district_id = self._district_gateway.next_id()
                district = create_district(
                    district_id=district_id,
                    shop_id=shop_id,
                    name=name,
                )
                self._district_gateway.save(district)
                district_map[name.lower()] = district_id

        return district_map

    @staticmethod
    def _normalize_phone(phone: str) -> str | None:
        try:
            return normalize_ukraine_phone(phone)
        except InvalidPhoneNumberError:
            return None

    @staticmethod
    def _build_address(
        addr: ParsedAddress,
        *,
        is_primary: bool,
        district_map: dict[str, DistrictId],
    ) -> ClientAddress:
        district_id = None
        if addr.district_name:
            district_id = district_map.get(addr.district_name.lower())

        return create_address(
            street=addr.street,
            house=addr.house,
            apartment=addr.apartment,
            entrance=addr.entrance,
            floor=addr.floor,
            intercom=addr.intercom,
            comment=addr.comment,
            is_primary=is_primary,
            district_id=district_id,
        )
