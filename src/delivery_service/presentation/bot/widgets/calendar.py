from datetime import date, datetime

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    DATE_TEXT,
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Format, Text

DAY_OF_WEEK: dict[int, str] = {
    0: "Пн",
    1: "Вт",
    2: "Ср",
    3: "Чт",
    4: "Пт",
    5: "Сб",
    6: "Нд",
}

MONTH: dict[int, str] = {
    1: "Січень",
    2: "Лютий",
    3: "Березень",
    4: "Квітень",
    5: "Травень",
    6: "Червень",
    7: "Липень",
    8: "Серпень",
    9: "Вересень",
    10: "Жовтень",
    11: "Листопад",
    12: "Грудень",
}


def is_day_off(_date: date, manager: DialogManager) -> bool:
    regular_days_off: list[int] = manager.dialog_data.get(
        "regular_days_off", []
    )
    special_days_off_dates: list[date] = [
        datetime.fromisoformat(day).date()
        for day in manager.dialog_data.get("irregular_days_off", [])
    ]

    is_regular_day_off = _date.weekday() in regular_days_off
    is_special_day_off = _date in special_days_off_dates

    return bool(is_special_day_off or is_regular_day_off)


class WeekDay(Text):
    async def _render_text(self, data: dict, manager: DialogManager) -> str:
        selected_date: date = data["date"]

        week_day: int = selected_date.weekday()

        return DAY_OF_WEEK[week_day]


class DaysOff(Text):
    def __init__(self, other: Text):
        super().__init__()
        self.mark = "🟥"
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]

        if is_day_off(current_date, manager):
            return self.mark

        return await self.other.render_text(data, manager)


class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]

        selected_month = selected_date.month

        return MONTH[selected_month]


class ShopAvailabilityCalendar(Calendar):
    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                header_text=Month(),
                weekday_text=WeekDay(),
                next_month_text=Month() + " >>",
                prev_month_text="<< " + Month(),
                date_text=DaysOff(other=DATE_TEXT),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=Month(),
                header_text=Format("{date:%Y}"),
                this_month_text="[" + Month() + "]",
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }
