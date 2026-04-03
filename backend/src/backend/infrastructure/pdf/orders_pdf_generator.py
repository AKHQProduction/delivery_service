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
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.infrastructure.persistence.tables.orders import Order

FONT_DIR = Path(__file__).parent / "fonts"


class ReportLabOrdersPDFGenerator:
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

    def _build_doc(self, elements: list) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()

    def build_order_list(
        self,
        orders: list[Order],
        delivery_date: date,
    ) -> bytes:
        elements: list = []

        date_str = delivery_date.strftime("%d.%m.%Y")
        elements.append(
            Paragraph(f"Замовлення на {date_str}", self._styles["title"])
        )

        if not orders:
            elements.append(
                Paragraph("Немає замовлень на цю дату", self._styles["normal"])
            )
        else:
            orders_by_slot: dict[str, list[Order]] = defaultdict(list)
            for order in orders:
                slot_label = self._format_time_slot(order)
                orders_by_slot[slot_label].append(order)

            for time_slot in sorted(orders_by_slot.keys()):
                slot_orders = orders_by_slot[time_slot]
                elements.append(Paragraph(time_slot, self._styles["heading"]))
                elements.extend(self._build_orders_section(slot_orders))

        return self._build_doc(elements)

    def build_statistics(
        self,
        orders: list[Order],
        delivery_date: date,
        shop_name: str,
    ) -> bytes:
        elements: list = self._build_summary_section(
            orders, shop_name, delivery_date
        )
        return self._build_doc(elements)

    @staticmethod
    def _format_time_slot(order: Order) -> str:
        return (
            f"{order.delivery_start_time.strftime('%H:%M')}-"
            f"{order.delivery_end_time.strftime('%H:%M')}"
        )

    def _build_orders_section(self, orders: list[Order]) -> list:
        if not orders:
            return []

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

        cell_style = ParagraphStyle(
            "CellStyle",
            fontName=font_name,
            fontSize=8,
            leading=10,
        )

        table_data: list = [["Клієнт", "Деталі", "Товари", "Сума", "Оплата"]]
        table_data.extend(
            self._build_order_row(order, cell_style) for order in orders
        )

        table_data.append(
            self._build_subtotal_row(orders, cell_style, font_bold)
        )

        last_row = len(table_data) - 1
        table = Table(
            table_data,
            colWidths=[30 * mm, 60 * mm, 45 * mm, 22 * mm, 23 * mm],
        )
        table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, 0), font_name),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("ALIGN", (3, 1), (4, -2), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("SPAN", (0, last_row), (1, last_row)),
                ("SPAN", (3, last_row), (4, last_row)),
                (
                    "BACKGROUND",
                    (0, last_row),
                    (-1, last_row),
                    colors.HexColor("#D9E2F3"),
                ),
                ("ALIGN", (2, last_row), (2, last_row), "CENTER"),
                ("ALIGN", (3, last_row), (4, last_row), "RIGHT"),
            ])
        )

        return [table, Spacer(1, 5 * mm)]

    @staticmethod
    def _build_subtotal_row(
        orders: list[Order],
        cell_style: ParagraphStyle,
        font_bold: str,
    ) -> list:
        payment_totals: dict[str, Decimal] = defaultdict(Decimal)
        products: dict[str, int] = defaultdict(int)

        for order in orders:
            method = order.payment_method or ""
            for item in order.items:
                products[item.name] += item.quantity
                item_total = item.quantity * item.price_per_item
                payment_totals[method] += item_total

        grand = sum(payment_totals.values(), Decimal(0))

        subtotal_style = ParagraphStyle(
            "SubtotalStyle",
            fontName=font_bold,
            fontSize=8,
            leading=10,
            alignment=2,
        )
        subtotal_lines = [
            f"{method}: {total} грн"
            for method, total in payment_totals.items()
        ]
        subtotal_lines.append(f"<b>Всього: {grand} грн</b>")
        product_names = "<br/>".join(
            name for name, _ in sorted(products.items())
        )
        qty_style = ParagraphStyle(
            "QtyStyle",
            parent=cell_style,
            alignment=2,
        )
        product_qtys = "<br/>".join(
            str(qty) for _, qty in sorted(products.items())
        )

        return [
            Paragraph(product_names, cell_style),
            "",
            Paragraph(product_qtys, qty_style),
            Paragraph("<br/>".join(subtotal_lines), subtotal_style),
            "",
        ]

    @staticmethod
    def _build_order_row(order: Order, cell_style: ParagraphStyle) -> list:
        client_cell = Paragraph(f"<b>{order.client.full_name}</b>", cell_style)

        addr = order.delivery_address
        details_lines = [f"{addr.street}, {addr.house}"]

        apt_parts = []
        if addr.apartment:
            apt_parts.append(f"кв. {addr.apartment}")
        if addr.entrance:
            apt_parts.append(f"під. {addr.entrance}")
        if addr.floor:
            apt_parts.append(f"пов. {addr.floor}")
        if addr.intercom:
            apt_parts.append(f"домофон: {addr.intercom}")
        if apt_parts:
            details_lines.append(", ".join(apt_parts))
        if addr.comment:
            details_lines.append(f"Нотатка: {addr.comment}")

        details_lines.append(f"Тел: {order.delivery_phone}")
        if order.comment:
            details_lines.append(f"Коментар: {order.comment}")

        details_cell = Paragraph("<br/>".join(details_lines), cell_style)

        products_lines = [
            f"{item.name} × {item.quantity}" for item in order.items
        ]
        products_cell = Paragraph("<br/>".join(products_lines), cell_style)

        total = sum(
            item.quantity * item.price_per_item for item in order.items
        )
        sum_cell = Paragraph(f"<b>{total} грн</b>", cell_style)

        payment_cell = Paragraph(order.payment_method or "", cell_style)

        return [
            client_cell,
            details_cell,
            products_cell,
            sum_cell,
            payment_cell,
        ]

    @staticmethod
    def _collect_summary_data(
        orders: list[Order],
    ) -> list[list[str]]:
        payment_methods: list[str] = list(
            dict.fromkeys(order.payment_method or "" for order in orders)
        )

        items_summary: dict[str, dict] = defaultdict(
            lambda: {
                "quantity": 0,
                "total": Decimal(0),
                **{m: Decimal(0) for m in payment_methods},
            }
        )

        for order in orders:
            method = order.payment_method or ""
            for item in order.items:
                item_total = item.quantity * item.price_per_item
                items_summary[item.name]["quantity"] += item.quantity
                items_summary[item.name]["total"] += item_total
                items_summary[item.name][method] += item_total

        header = ["Товар", "К-сть", *payment_methods, "Разом"]
        rows: list[list[str]] = [header]

        grand_total = Decimal(0)
        grand_total_quantity = 0
        grand_by_method: dict[str, Decimal] = {
            m: Decimal(0) for m in payment_methods
        }

        for name, data in sorted(items_summary.items()):
            row = [name, str(data["quantity"])]
            for m in payment_methods:
                row.append(f"{data[m]} грн")
                grand_by_method[m] += data[m]
            row.append(f"{data['total']} грн")
            rows.append(row)
            grand_total += data["total"]
            grand_total_quantity += data["quantity"]

        rows.append([
            f"Всього замовлень: {len(orders)}",
            str(grand_total_quantity),
            *[f"{grand_by_method[m]} грн" for m in payment_methods],
            f"{grand_total} грн",
        ])

        return rows

    def _build_summary_section(
        self, orders: list[Order], shop_name: str, delivery_date: date
    ) -> list:
        date_str = delivery_date.strftime("%d.%m.%Y")
        title = Paragraph(
            f"Загальна статистика {shop_name} за {date_str}",
            self._styles["title"],
        )

        summary_data = self._collect_summary_data(orders)
        num_payment_cols = len(summary_data[0]) - 3

        font_name = (
            "DejaVu"
            if "DejaVu" in pdfmetrics.getRegisteredFontNames()
            else "Helvetica"
        )

        remaining = 186 * mm - 60 * mm - 20 * mm - 28 * mm
        payment_col_width = (
            remaining / num_payment_cols if num_payment_cols else 28 * mm
        )
        col_widths = [
            60 * mm,
            20 * mm,
            *([payment_col_width] * num_payment_cols),
            28 * mm,
        ]

        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(
            TableStyle([
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
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

        return [title, Spacer(1, 5 * mm), summary_table]
