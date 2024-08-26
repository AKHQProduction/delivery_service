from aiogram import F
from aiogram_dialog.widgets.text import Case, Format, Multi

user_card = Multi(
        Format(
                "<b>🆔 Телеграм ID:</b> "
                "<code>{dialog_data[user][user_id]}</code>"
        ),
        Format("<b>💁🏼‍♂️ Ім'я</b> {dialog_data[user][full_name]}"),
        Case(
                {
                    True: Format(
                            "<b>🪪 Телеграм тег:</b> "
                            "@{dialog_data[user][username]}"
                    ),
                    False: Format(
                            "<b>🪪 Телеграм тег:</b> ",
                            "<i>відсутній</i>"
                    )
                },
                selector=F["dialog_data"]["user"]["username"].cast(bool)
        ),
        Case(
                {
                    True: Format(
                            "<b>📞 Номер телефону:</b> "
                            "{dialog_data[user][phone_number]}"
                    ),
                    False: Format(
                            "<b>📞 Номер телефону:</b> "
                            "<i>відсутній</i>"
                    )
                },
                selector=F["dialog_data"]["user"]["phone_number"].cast(bool)
        )
)
