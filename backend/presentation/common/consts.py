from entities.employee.models import EmployeeRole

EMPLOYEE_BTN_TXT = "👥 Співробітники"
GOODS_BTN_TEXT = "📦 Товари"

CREATE_ORDER_BTN_TXT = "🛒 Створити замовлення"
MY_ORDERS_BTN_TXT = "🗄 Мої замовлення"

PROFILE_BTN_TXT = "👤 Профіль"

CREATE_SHOP_BTN_TXT = "🏪 Створити магазин"
FAQ_BTN_TXT = "ℹ️ FAQ"

BACK_BTN_TXT = "🔙 Назад"
CANCEL_BTN_TXT = "❌ Скасувати"

ACTUAL_ROLES = {
    EmployeeRole.ADMIN: "🤴 Адміністратор",
    EmployeeRole.MANAGER: "🧑‍💻 Менеджер",
    EmployeeRole.DRIVER: "🚚 Водій",
}
