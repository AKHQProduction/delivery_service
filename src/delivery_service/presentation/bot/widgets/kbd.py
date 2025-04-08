from aiogram.fsm.state import State
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, SwitchTo
from aiogram_dialog.widgets.kbd.button import OnClick
from aiogram_dialog.widgets.text import Const
from magic_filter import MagicFilter


def get_back_btn(
    btn_text: str | None = None,
    *,
    back_to_prev_dialog: bool = False,
    when: MagicFilter | None = None,
    state: State | None = None,
    on_click: OnClick | None = None,
) -> Button:
    text = Const("🔙 Назад") if not btn_text else Const(btn_text)

    if state:
        return SwitchTo(
            text=text, id="base_switch_to", state=state, on_click=on_click
        )

    return (
        Cancel(text=text, id="base_cancel_btn", when=when, on_click=on_click)
        if back_to_prev_dialog
        else Back(text=text, id="base_back_btn", when=when, on_click=on_click)
    )
