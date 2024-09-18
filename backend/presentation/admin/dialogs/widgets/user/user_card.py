from aiogram import F
from aiogram_dialog.widgets.text import Case, Const, Format, Multi

user_card = Multi(
    Const("👀 Картка користувача \n"),
    Format("<b>🆔 Телеграм ID:</b> " "<code>{user[user_id]}</code>"),
    Format("<b>💁🏼‍♂️ Ім'я: </b>{user[full_name]}"),
    Case(
        {
            ...: Format("<b>🪪 Телеграм тег:</b> " "@{user[username]}"),
            None: Format("<b>🪪 Телеграм тег:</b> ", "<i>відсутній</i>"),
        },
        selector=F["user"]["username"],
    ),
    Case(
        {
            ...: Format("<b>📞 Номер телефону:</b> " "{user[phone_number]}"),
            None: Format("<b>📞 Номер телефону:</b> " "<i>відсутній</i>"),
        },
        selector=F["user"]["phone_number"],
    ),
)
