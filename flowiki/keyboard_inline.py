from aiogram.utils.keyboard import InlineKeyboardBuilder
from own_utils import get_button_text


def keyboard_for_rule(id_user):
    builder = InlineKeyboardBuilder()

    builder.button(text=get_button_text("admin"), callback_data=f"rule:admin:{id_user}")
    builder.button(text=get_button_text("ban"), callback_data=f"rule:ban:{id_user}")
    builder.button(text=get_button_text("user"), callback_data=f"rule:user:{id_user}")
    builder.button(
        text=get_button_text("repeat_fio"), callback_data=f"action:repeat_fio:{id_user}"
    )

    builder.adjust(2, 1, 1)
    return builder.as_markup()


def confirm_repeat_fio():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button_text("enter_repeat"), callback_data="action:enter_repeat_fio"
    )
    return builder.as_markup()


def confirm_reg_user():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button_text("end_reg"), callback_data="action:confirm_reg:user"
    )
    return builder.as_markup()


def confirm_reg_admin():
    builder = InlineKeyboardBuilder()

    builder.button(
        text=get_button_text("end_reg"), callback_data="action:confirm_reg:admin"
    )
    return builder.as_markup()


def flownomika_menu(side="+"):
    builder = InlineKeyboardBuilder()
    emoji_plus = "🔘" if side == "+" else ""
    emoji_minus = "🔘" if side == "-" else ""
    num1 = get_button_text("num1", d={"side": side})
    num2 = get_button_text("num2", d={"side": side})
    num3 = get_button_text("num3", d={"side": side})
    builder.button(
        text=get_button_text("another_quantity"),
        callback_data=f"action:enter_another_quantity:{side}",
    )
    builder.button(text=num1, callback_data=f"action:num:{side}10")
    builder.button(text=num2, callback_data=f"action:num:{side}20")
    builder.button(text=num3, callback_data=f"action:num:{side}30")
    builder.button(
        text=get_button_text("menu_plus", d={"emoji": emoji_plus}),
        callback_data="action:select:+",
    )
    builder.button(
        text=get_button_text("menu_minus", d={"emoji": emoji_minus}),
        callback_data="action:select:-",
    )
    builder.adjust(1, 3, 2)
    return builder.as_markup()


def flownomika_list_users(
    list_users: list,
    size_one_page: int = 5,
    page_num: int = 1,
    many_selects: bool = False,
):
    builder = InlineKeyboardBuilder()
    grid_size = 0
    for num, user in enumerate(list_users):
        user: dict
        if (size_one_page * page_num) - size_one_page <= num < size_one_page * page_num:
            emoji = "🔘" if user['select'] else ""
            builder.button(
                text=get_button_text("pattern_line_button_user", d={"name": user['name'], 'emoji':emoji}),
                callback_data=f"action:select_user:{user['name']}:{user['select']}",
            )
            grid_size+=1
    if many_selects:
        builder.button(
            text=get_button_text("end_choise"),
            callback_data="action:end_choise_selects",
        )
    else:
        builder.button(
            text=get_button_text("many_selects"), callback_data="action:many_selects"
        )
    builder.button(text=get_button_text("arrow_left"), callback_data=f"action:turn_left:{page_num}")
    builder.button(
        text=get_button_text("arrow_right"), callback_data=f"action:turn_right:{page_num}"
    )
    # q_users = len(list_users) 
    # len_users = q_users if q_users <= size_one_page else size_one_page + (q_users - size_one_page * page_num)
    builder.adjust(*[1 for _ in range(grid_size)], 1, 2)
    return builder.as_markup()
