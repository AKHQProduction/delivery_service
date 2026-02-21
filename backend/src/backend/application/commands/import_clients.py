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
from backend.application.validators import (
    normalize_house,
    normalize_street,
    normalize_ukraine_phone,
)
from backend.application.vars import DistrictId, ShopId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    RedisFileStorage,
    SQLAlchemyClientGateway,
    SQLAlchemyDistrictGateway,
)
from backend.infrastructure.persistence.tables.clients import (
    Client,
    ClientAddress,
)
from backend.infrastructure.transaction_manager import TransactionManager
from backend.infrastructure.xlsx import (
    ClientErrorXlsxGenerator,
    ClientXlsxParser,
)
from backend.infrastructure.xlsx.client_xlsx_parser import (
    ImportErrorKind,
    ParsedAddress,
    ParsedClientRow,
    RejectedClientRow,
)

logger = logging.getLogger(__name__)

DedupKey = tuple[str, tuple[str, ...], tuple[tuple[str, str], ...]]


@dataclass(frozen=True)
class ImportClientsCommand:
    file_bytes: bytes


@dataclass(frozen=True)
class ImportClientsResult:
    imported: int
    skipped: int
    error_file_id: str | None = None
    error_filename: str | None = None


class ImportClientsCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        district_gateway: SQLAlchemyDistrictGateway,
        tr_manager: TransactionManager,
        parser: ClientXlsxParser,
        error_report_generator: ClientErrorXlsxGenerator,
        file_storage: RedisFileStorage,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._district_gateway = district_gateway
        self._tr_manager = tr_manager
        self._parser = parser
        self._error_report_generator = error_report_generator
        self._file_storage = file_storage

    async def handle(
        self,
        command: ImportClientsCommand,
    ) -> ImportClientsResult:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        shop_id = current_user.shop_id

        loop = asyncio.get_running_loop()
        parse_result = await loop.run_in_executor(
            None, self._parser.parse, command.file_bytes
        )

        if not parse_result.valid and not parse_result.rejected:
            return ImportClientsResult(imported=0, skipped=0)

        rejected = list(parse_result.rejected)
        clients: list[Client] = []

        if parse_result.valid:
            district_map = await self._resolve_districts(
                shop_id, parse_result.valid
            )
            await self._tr_manager.flush()
            existing_keys = await self._build_existing_keys(
                shop_id, parse_result.valid
            )

            seen_in_file: dict[DedupKey, int] = {}
            raw = parse_result.raw_by_row

            for row in parse_result.valid:
                dup_error = self._check_duplicate(
                    row, existing_keys, seen_in_file
                )
                if dup_error is not None:
                    rejected.append(
                        RejectedClientRow(
                            row_number=row.row_number,
                            raw_values=raw[row.row_number],
                            error_kind=dup_error[0],
                            error_detail=dup_error[1],
                        )
                    )
                    continue

                client = self._build_client(row, shop_id, district_map)
                if client is None:
                    rejected.append(
                        RejectedClientRow(
                            row_number=row.row_number,
                            raw_values=raw[row.row_number],
                            error_kind=ImportErrorKind.INVALID_PHONE,
                        )
                    )
                    continue

                clients.append(client)

            if clients:
                await self._client_gateway.save_all(clients)
                await self._tr_manager.commit()

        error_file_id = None
        error_filename = None
        if rejected:
            rejected.sort(key=lambda r: r.row_number)
            xlsx_bytes = await loop.run_in_executor(
                None, self._error_report_generator.generate, rejected
            )
            error_filename = "import_errors.xlsx"
            error_file_id = await self._file_storage.save(
                xlsx_bytes, error_filename
            )

        logger.info(
            "Imported %d clients (skipped %d) for shop %s",
            len(clients),
            len(rejected),
            shop_id,
        )
        return ImportClientsResult(
            imported=len(clients),
            skipped=len(rejected),
            error_file_id=error_file_id,
            error_filename=error_filename,
        )

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

    def _check_duplicate(
        self,
        row: ParsedClientRow,
        existing_keys: set[DedupKey],
        seen_in_file: dict[DedupKey, int],
    ) -> tuple[ImportErrorKind, str | None] | None:
        phones = [self._normalize_phone(row.phone1) or ""]
        if row.phone2:
            p2 = self._normalize_phone(row.phone2)
            if p2:
                phones.append(p2)

        addrs = [self._normalize_address(row.address1)]
        if row.address2:
            addrs.append(self._normalize_address(row.address2))

        key = self._make_dedup_key(row.full_name, phones, addrs)

        if key in existing_keys:
            return ImportErrorKind.DUPLICATE_IN_DB, None
        if key in seen_in_file:
            return (
                ImportErrorKind.DUPLICATE_IN_FILE,
                f"рядок {seen_in_file[key]}",
            )
        seen_in_file[key] = row.row_number
        return None

    def _build_client(
        self,
        row: ParsedClientRow,
        shop_id: ShopId,
        district_map: dict[str, DistrictId],
    ) -> Client | None:
        phone1 = self._normalize_phone(row.phone1)
        if phone1 is None:
            return None

        phone2 = self._normalize_phone(row.phone2) if row.phone2 else None

        client = create_client(
            client_id=self._client_gateway.next_id(),
            shop_id=shop_id,
            full_name=row.full_name,
        )

        client.phones = [
            create_phone(number=phone1, is_primary=True, shop_id=shop_id),
        ]
        if phone2:
            client.phones.append(
                create_phone(number=phone2, is_primary=False, shop_id=shop_id)
            )

        client.addresses = [
            self._build_address(
                row.address1, is_primary=True, district_map=district_map
            ),
        ]
        if row.address2:
            client.addresses.append(
                self._build_address(
                    row.address2, is_primary=False, district_map=district_map
                ),
            )

        return client

    async def _build_existing_keys(
        self,
        shop_id: ShopId,
        parsed_rows: list[ParsedClientRow],
    ) -> set[DedupKey]:
        all_phones: set[str] = set()
        all_addresses: set[tuple[str, str]] = set()

        for row in parsed_rows:
            phone1 = self._normalize_phone(row.phone1)
            if phone1:
                all_phones.add(phone1)
            if row.phone2:
                phone2 = self._normalize_phone(row.phone2)
                if phone2:
                    all_phones.add(phone2)
            all_addresses.add(self._normalize_address(row.address1))
            if row.address2:
                all_addresses.add(self._normalize_address(row.address2))

        candidate_ids = (
            await self._client_gateway.find_candidate_ids_for_dedup(
                shop_id, all_phones, all_addresses
            )
        )
        if not candidate_ids:
            return set()

        candidates = await self._client_gateway.load_candidates_for_dedup(
            candidate_ids
        )
        return {
            self._make_dedup_key(
                c.full_name,
                [p.number for p in c.phones],
                [
                    (normalize_street(a.street), normalize_house(a.house))
                    for a in c.addresses
                ],
            )
            for c in candidates
        }

    @staticmethod
    def _make_dedup_key(
        full_name: str,
        phones: list[str],
        addresses: list[tuple[str, str]],
    ) -> tuple[str, tuple[str, ...], tuple[tuple[str, str], ...]]:
        name = " ".join(full_name.strip().lower().split())
        return (
            name,
            tuple(sorted(phones)),
            tuple(sorted(addresses)),
        )

    @staticmethod
    def _normalize_address(addr: ParsedAddress) -> tuple[str, str]:
        return normalize_street(addr.street), normalize_house(addr.house)

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
