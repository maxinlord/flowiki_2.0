from aiogram.utils.keyboard import ReplyKeyboardBuilder
from own_utils import get_button_text


def main_menu_user():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button_text("balance"))
    builder.button(text=get_button_text("top"))
    builder.button(text=get_button_text("history_transfer"))
    builder.adjust(2, 1)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )


def main_menu_admin():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button_text("flownomika"))
    builder.button(text=get_button_text("top"))
    builder.adjust(2)
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )

def cancel():
    builder = ReplyKeyboardBuilder()
    builder.button(text=get_button_text("cancel"))
    return builder.as_markup(
        resize_keyboard=True, input_field_placeholder="Бог тебя любит ♡"
    )