import io
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.application.interfaces.gateways.order_gateway import (
    OrderReadModel,
)
from backend.application.interfaces.pdf_generator import OrdersPDFGenerator
from backend.application.vars import TimePreference

FONT_DIR = Path(__file__).parent / "fonts"


class ReportLabOrdersPDFGenerator(OrdersPDFGenerator):
    def __init__(self) -> None:
        self._register_fonts()
        self._styles = self._create_styles()

    def _register_fonts(self) -> None:
        font_path = FONT_DIR / "DejaVuSans.ttf"
        font_bold_path = FONT_DIR / "DejaVuSans-Bold.ttf"

        if font_path.exists():
            pdfmetrics.registerFont(TTFont("DejaVu", str(font_path)))
        if font_bold_path.exists():
            pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(font_bold_path)))

    def _create_styles(self) -> dict[str, ParagraphStyle]:
        base_styles = getSampleStyleSheet()

        font_name = (
            "DejaVu"
            if "DejaVu" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica"
        )
        font_bold = (
            "DejaVu-Bold"
            if "DejaVu-Bold" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica-Bold"
        )

        return {
            "title": ParagraphStyle(
                "Title",
                parent=base_styles["Title"],
                fontName=font_bold,
                fontSize=16,
                alignment=1,
                spaceAfter=10 * mm,
            ),
            "heading": ParagraphStyle(
                "Heading",
                parent=base_styles["Heading2"],
                fontName=font_bold,
                fontSize=12,
                spaceBefore=5 * mm,
                spaceAfter=3 * mm,
            ),
            "normal": ParagraphStyle(
                "Normal",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=10,
            ),
            "small": ParagraphStyle(
                "Small",
                parent=base_styles["Normal"],
                fontName=font_name,
                fontSize=9,
                textColor=colors.grey,
            ),
        }

    def handle(
        self,
        orders: list[OrderReadModel],
        delivery_date: date,
        shop_name: str,
    ) -> bytes:
        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        elements: list = []

        # Title
        date_str = delivery_date.strftime("%d.%m.%Y")
        title = Paragraph(
            f"Замовлення на {date_str}",
            self._styles["title"],
        )
        elements.append(title)

        subtitle = Paragraph(
            f"Магазин: {shop_name} | Всього замовлень: {len(orders)}",
            self._styles["normal"],
        )
        elements.extend((subtitle, Spacer(1, 5 * mm)))

        if not orders:
            no_orders = Paragraph(
                "Немає замовлень на цю дату",
                self._styles["normal"],
            )
            elements.append(no_orders)
        else:
            # Summary table at the beginning
            elements.extend(self._build_summary_section(orders, delivery_date))

            # Group by time preference
            first_half = [
                o
                for o in orders
                if o.time_preference == TimePreference.FIRST_HALF
            ]
            second_half = [
                o
                for o in orders
                if o.time_preference == TimePreference.SECOND_HALF
            ]

            if first_half:
                elements.append(
                    Paragraph("Перша половина дня", self._styles["heading"])
                )
                elements.extend(self._build_orders_section(first_half))

            if second_half:
                elements.append(
                    Paragraph("Друга половина дня", self._styles["heading"])
                )
                elements.extend(self._build_orders_section(second_half))

        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    def _build_orders_section(self, orders: list[OrderReadModel]) -> list:
        elements: list = []

        font_name = (
            "DejaVu"
            if "DejaVu" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica"
        )

        for idx, order in enumerate(orders, 1):
            # Build order elements to keep together
            order_elements: list = []

            # Order header
            order_elements.append(
                Paragraph(
                    f"<b>#{idx}. {order.client_name}</b>",
                    self._styles["normal"],
                )
            )

            # Address
            addr = order.delivery_address
            address_parts = [addr.street, f"буд. {addr.house}"]
            if addr.apartment:
                address_parts.append(f"кв. {addr.apartment}")
            if addr.entrance:
                address_parts.append(f"під. {addr.entrance}")
            if addr.floor:
                address_parts.append(f"пов. {addr.floor}")
            if addr.intercom:
                address_parts.append(f"домофон: {addr.intercom}")

            address_str = ", ".join(address_parts)
            order_elements.extend((
                Paragraph(f"Адреса: {address_str}", self._styles["small"]),
                Paragraph(
                    f"Телефон: {order.delivery_phone}", self._styles["small"]
                ),
            ))

            # Comment
            if order.comment:
                order_elements.append(
                    Paragraph(
                        f"Коментар: {order.comment}",
                        self._styles["small"],
                    )
                )

            # Items table
            items_data = [["Товар", "К-сть", "Ціна", "Сума"]]
            total = 0
            for item in order.items:
                item_total = item.quantity * item.price_per_item
                total += item_total
                items_data.append([
                    item.name,
                    str(item.quantity),
                    f"{item.price_per_item} грн",
                    f"{item_total} грн",
                ])
            items_data.append(["", "", "Разом:", f"{total} грн"])

            table = Table(
                items_data,
                colWidths=[90 * mm, 20 * mm, 30 * mm, 30 * mm],
            )
            table.setStyle(
                TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), font_name),
                    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                    ("LINEABOVE", (2, -1), (-1, -1), 1, colors.black),
                    ("FONTNAME", (2, -1), (-1, -1), font_name),
                ])
            )

            order_elements.extend((
                Spacer(1, 2 * mm),
                table,
            ))

            # Wrap entire order in KeepTogether to prevent page breaks
            elements.extend((KeepTogether(order_elements), Spacer(1, 5 * mm)))

        return elements

    def _build_summary_section(
        self, orders: list[OrderReadModel], delivery_date: date
    ) -> list:
        elements: list = []

        date_str = delivery_date.strftime("%d.%m.%Y")
        elements.append(
            Paragraph(f"Звіт замовлень на {date_str}", self._styles["heading"])
        )

        # Aggregate items across all orders
        items_summary: dict[str, dict] = defaultdict(
            lambda: {"quantity": 0, "total": Decimal(0)}
        )

        for order in orders:
            for item in order.items:
                items_summary[item.name]["quantity"] += item.quantity
                items_summary[item.name]["total"] += (
                    item.quantity * item.price_per_item
                )

        # Build summary table
        summary_data = [["Товар", "Загальна к-сть", "Загальна сума"]]
        grand_total = Decimal(0)

        for name, data in sorted(items_summary.items()):
            summary_data.append([
                name,
                str(data["quantity"]),
                f"{data['total']} грн",
            ])
            grand_total += data["total"]

        summary_data.append([
            f"Всього замовлень: {len(orders)}",
            "",
            f"{grand_total} грн",
        ])

        font_name = (
            "DejaVu"
            if "DejaVu" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica"
        )

        summary_table = Table(
            summary_data,
            colWidths=[100 * mm, 35 * mm, 35 * mm],
        )
        summary_table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -2), 0.5, colors.grey),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#D9E2F3")),
                ("FONTNAME", (0, -1), (-1, -1), font_name),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
            ])
        )

        # Wrap summary in KeepTogether to prevent page breaks
        return [
            KeepTogether([
                elements[0],  # heading
                Spacer(1, 3 * mm),
                summary_table,
            ])
        ]
