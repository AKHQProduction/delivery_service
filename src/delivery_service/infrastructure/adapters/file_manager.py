from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from delivery_service.application.ports.file_manager import FileManager
from delivery_service.application.query.ports.address_gateway import (
    AddressReadModel,
)
from delivery_service.application.query.ports.order_gateway import (
    OrderReadModel,
)
from delivery_service.domain.orders.order import DeliveryPreference

CANDIDATE_FONT_PATHS = [
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
]


class PDFFileManager(FileManager):
    def create_order_files(
        self, orders: dict[DeliveryPreference, list[OrderReadModel]]
    ) -> dict[DeliveryPreference, bytes]:
        return {
            preference: self._create_pdf(orders_list)
            for preference, orders_list in orders.items()
            if orders_list
        }

    def _create_pdf(self, orders: list[OrderReadModel]) -> bytes:
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        font_name = self._register_system_cyrillic_font()

        width, height = A4
        y = height - 20 * mm

        for idx, order in enumerate(orders, start=1):
            address_str = self._format_address(order.address)

            pdf.setFont(font_name, 12)
            pdf.drawString(
                20 * mm,
                y,
                f"#{idx} {order.customer.full_name} "
                f"{order.customer.primary_phone}",
            )
            y -= 6 * mm

            pdf.setFont(font_name, 11)
            pdf.drawString(25 * mm, y, address_str)
            y -= 6 * mm

            for line in order.order_lines:
                line_text = (
                    f"• {line.title} — {line.quantity} x "
                    f"{line.price_per_item} UAH"
                )
                pdf.drawString(30 * mm, y, line_text)
                y -= 5 * mm

            pdf.setFont(font_name, 11)
            pdf.drawString(
                25 * mm,
                y,
                f"Всього до оплати: {order.total_order_price} UAH",
            )
            y -= 10 * mm

            if y < 40 * mm:
                pdf.showPage()
                y = height - 20 * mm

        pdf.save()
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def _format_address(address: AddressReadModel | None = None) -> str:
        if address is None:
            return "Адресу не вказано"
        base = f"{address.city}, {address.street} {address.house_number}"
        if address.apartment_number is None:
            return base + " (приватний будинок)"
        fl = f", поверх {address.floor}" if address.floor is not None else ""
        ic = address.intercom_code or "без кода"
        return (
            f"{base}, кв. {address.apartment_number}{fl}, код домофону: {ic}"
        )

    @staticmethod
    def _register_system_cyrillic_font() -> str:
        for font_path in CANDIDATE_FONT_PATHS:
            if font_path.is_file():
                system_font_name = font_path.stem
                pdfmetrics.registerFont(
                    TTFont(system_font_name, str(font_path))
                )
                return system_font_name
        raise RuntimeError("Not find ttf file")
