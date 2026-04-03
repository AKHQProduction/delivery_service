import asyncio
import logging
from dataclasses import dataclass

from backend.infrastructure.xlsx.client_xlsx_preview import (
    PreviewResult,
    preview_xlsx,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PreviewImportXlsxQuery:
    file_bytes: bytes


class PreviewImportXlsxQueryHandler:
    async def handle(
        self,
        query: PreviewImportXlsxQuery,
    ) -> PreviewResult:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, preview_xlsx, query.file_bytes
        )

        logger.info(
            "Preview XLSX: %d columns, ~%d data rows",
            len(result.columns),
            result.total_rows,
        )

        return result
