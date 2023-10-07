import asyncio
import html
import logging
import sys
from typing import Any, Dict

from aiogram import F, Router, html
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

from db_func import flow_db
import config
from own_utils import *
import keyboard_inline
import keyboard_markup

TOKEN = config.TOKEN
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)

form_router = Router()
main_router = Router()


class FormReg(StatesGroup):
    fio = State()
    pending_review = State()


class Admin(StatesGroup):
    main = State()
    enter_reason = State()
    enter_another_quantity = State()


class Ban(StatesGroup):
    void = State()


def state_is_none(func):
    async def wrapper(message: Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is not None:
            return
        await func(message, state)

    return wrapper


@form_router.message(CommandStart())
@state_is_none
async def command_start(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if flow_db.user_exists(id_user):
        return await message.answer(
            get_message_text("hi"),
            reply_markup=ReplyKeyboardRemove(),
        )
    await state.set_state(FormReg.fio)
    await message.answer(
        get_message_text("hi_reg"),
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(FormReg.fio)
async def process_fio(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    photo = await message.from_user.get_profile_photos()
    photo_id = photo.photos[0][0].file_id
    await bot.send_photo(
        chat_id=config.CHAT_ID,
        message_thread_id=config.THREAD_ID_PENDING_REVIEW,
        photo=photo_id,
        caption=get_message_text("request", d={"fio": message.text}),
        reply_markup=keyboard_inline.keyboard_for_rule(id_user),
    )
    await state.update_data(fio=message.text)
    await state.set_state(FormReg.pending_review)
    await message.answer(get_message_text("pending_wait"))


@form_router.callback_query(
    FormReg.pending_review, F.data.split(":") == ["action", "confirm_reg", "admin"]
)
async def process_confirm_reg_admin(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    data = await state.get_data()
    flow_db.add_user(id_user)
    flow_db.update(
        key="username", where="id", meaning=id_user, data=f"@{query.from_user.username}"
    )
    flow_db.update(key="fio", where="id", meaning=id_user, data=data["fio"].strip())
    flow_db.update(
        key="date_reg",
        where="id",
        meaning=id_user,
        data=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update(key="rule", where="id", meaning=id_user, data="admin")
    await state.set_state(Admin.main)
    await bot.edit_message_text(
        chat_id=id_user,
        message_id=query.message.message_id,
        text=get_message_text("registered"),
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_message_text("congratulation_reg_admin"),
        reply_markup=keyboard_markup.main_menu_admin(),
    )


@form_router.callback_query(
    FormReg.pending_review, F.data.split(":") == ["action", "confirm_reg", "user"]
)
async def process_confirm_reg_user(query: CallbackQuery, state: FSMContext) -> None:
    id_user = query.from_user.id
    data = await state.get_data()
    flow_db.add_user(id_user)
    flow_db.update(
        key="username", where="id", meaning=id_user, data=f"@{query.from_user.username}"
    )
    flow_db.update(key="fio", where="id", meaning=id_user, data=data["fio"].strip())
    flow_db.update(
        key="date_reg",
        where="id",
        meaning=id_user,
        data=get_current_date("%Y-%m-%d, %H:%M:%S"),
    )
    flow_db.update(key="rule", where="id", meaning=id_user, data="user")
    await state.clear()
    await bot.edit_message_text(
        chat_id=id_user,
        message_id=query.message.message_id,
        text=get_message_text("registered"),
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_message_text("congratulation_reg_user"),
        reply_markup=keyboard_markup.main_menu_user(),
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "admin"
)
async def process_answer_on_request_admin(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_message_text("you_admin"),
        reply_markup=keyboard_inline.confirm_reg_admin(),
    )
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_message_text("answer_on_request_admin", d={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "user"
)
async def process_answer_on_request_user(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_message_text("you_user"),
        reply_markup=keyboard_inline.confirm_reg_user(),
    )
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_message_text("answer_on_request_user", d={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "rule", F.data.split(":")[1] == "ban"
)
async def process_answer_on_request_ban(
    query: CallbackQuery, state: FSMContext
) -> None:
    id_user_to_ban = query.data.split(":")[2]
    flow_db.add_user(id_user_to_ban)
    flow_db.update(
        key="username",
        where="id",
        meaning=id_user_to_ban,
        data=f"@{query.from_user.username}",
    )
    flow_db.update(key="rule", where="id", meaning=id_user_to_ban, data="ban")
    await bot.send_message(
        chat_id=id_user_to_ban,
        text=get_message_text("ban"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(Ban.void)
    old_caption = query.message.caption
    await bot.edit_message_caption(
        chat_id=config.CHAT_ID,
        message_id=query.message.message_id,
        caption=get_message_text("answer_on_request", d={"text": old_caption}),
        reply_markup=None,
    )


@form_router.callback_query(
    F.data.split(":")[0] == "action", F.data.split(":")[1] == "repeat_fio"
)
async def process_repeat_fio(query: CallbackQuery, state: FSMContext) -> None:
    await bot.delete_message(
        chat_id=config.CHAT_ID, message_id=query.message.message_id
    )
    await bot.send_message(
        chat_id=query.data.split(":")[2],
        text=get_message_text("repeat_fio"),
        reply_markup=keyboard_inline.confirm_repeat_fio(),
    )


@form_router.callback_query(
    FormReg.pending_review,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "enter_repeat_fio",
)
async def process_enter_repeat_fio(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        text=get_message_text("enter_repeat_fio"),
        message_id=query.message.message_id,
    )
    await state.set_state(FormReg.fio)


@main_router.message(F.text == get_button_text("balance"))
@state_is_none
async def balance_flow(message: Message, state: FSMContext) -> None:
    quantity_flow = flow_db.get(
        key="balance_flow", where="id", meaning=message.from_user.id
    )
    await message.answer(get_message_text("balance_info", d={"flowiki": quantity_flow}))


@main_router.message(F.text == get_button_text("top"))
async def top_flow(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_alls_with_order(
        keys="fio, balance_flow", order="balance_flow"
    )
    tops = [
        get_message_text(
            "pattern_line_top", d={"fio": i[0], "balance": i[1], "place": place}
        )
        for place, i in enumerate(raw_data, start=1)
    ]
    tops_text = "\n".join(tops)
    await message.answer(get_message_text("top_info", d={"list_top": tops_text}))


@main_router.message(Admin.main, F.text == get_button_text("flownomika"))
async def flownomika(message: Message, state: FSMContext) -> None:
    await message.answer(
        get_message_text("flownomika_menu"),
        reply_markup=keyboard_inline.flownomika_menu(),
    )


@main_router.message(F.text == get_button_text("history_transfer"))
async def history_transfer(message: Message, state: FSMContext) -> None:
    raw_data = flow_db.get_alls_with_order(
        keys="id, reason, owner_reason, date, num",
        order="date",
        table="history_reasons",
    )
    if not raw_data:
        return await message.answer(get_message_text("history_not_exists"))
    historys = [
        get_message_text(
            "pattern_line_history_transfer",
            d={
                "date": i[3],
                "num": i[-1],
                "reason": i[1],
                "owner_reason": flow_db.get(key="fio", where="id", meaning=i[2]),
            },
        )
        for i in raw_data
        if i[0] == str(message.from_user.id)
    ]
    history_text = "\n".join(historys)
    await message.answer(
        get_message_text("history_info", d={"list_historys": history_text})
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "select"
)
async def process_select_side(query: CallbackQuery, state: FSMContext) -> None:
    side = query.data.split(":")[-1]
    await state.update_data(side=side)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_menu(side),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "num"
)
async def process_select_num(query: CallbackQuery, state: FSMContext) -> None:
    num = query.data.split(":")[-1]
    await state.update_data(num=num)
    l_users = flow_db.get_alls_with_order(keys="fio, id", order="fio")
    d_users = [{"name": i[0], "select": False, "id": i[1]} for i in l_users]
    await state.update_data(d_users=d_users)
    await state.update_data(page=1)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(d_users),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "many_selects"
)
async def process_select_num(query: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(many_selects=True)
    data = await state.get_data()
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=data["d_users"], many_selects=True, page_num=data["page"]
        ),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "select_user"
)
async def process_select_user(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    name = query.data.split(":")[2]
    d_users = update_dict_users(name, data["d_users"])
    await state.update_data(d_users=d_users)
    if not data.get("many_selects", False):
        await bot.edit_message_reply_markup(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=None,
        )
        await bot.send_message(
            chat_id=query.from_user.id,
            text=get_message_text("enter_reason"),
            reply_markup=keyboard_markup.cancel(),
        )
        return await state.set_state(Admin.enter_reason)

    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=d_users, many_selects=True, page_num=data["page"]
        ),
    )


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "end_choise_selects",
)
async def process_end_choise_selects(query: CallbackQuery, state: FSMContext) -> None:
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=None,
    )
    await bot.send_message(
        chat_id=query.from_user.id,
        text=get_message_text("enter_reason"),
        reply_markup=keyboard_markup.cancel(),
    )
    await state.set_state(Admin.enter_reason)


@main_router.message(Admin.enter_reason)
async def enter_reason(message: Message, state: FSMContext) -> None:
    if get_button_text("cancel") == message.text:
        data = await state.get_data()
        await state.update_data(many_selects=True)
        await message.answer(
            get_message_text("flownomika_menu"),
            reply_markup=keyboard_inline.flownomika_list_users(data["d_users"], many_selects=True),
        )
        return await state.set_state(Admin.main)
    data = await state.get_data()
    for user in data["d_users"]:
        if not user["select"]:
            continue
        date = get_current_date("%Y-%m-%d, %H:%M:%S")
        flow_db.add_new_reason(
            user["id"], message.text, message.from_user.id, date, data["num"]
        )
        flow_db.add(
            key="balance_flow", where="id", meaning=user["id"], num=int(data["num"])
        )
    names = [user["name"] for user in data["d_users"] if user["select"]]
    await message.answer(
        get_message_text(
            "reason_recorded",
            d={"name": ",".join(names).strip(","), "num": data["num"]},
        ), reply_markup=keyboard_markup.main_menu_admin()
    )
    await state.set_state(Admin.main)


@main_router.callback_query(
    Admin.main,
    F.data.split(":")[0] == "action",
    F.data.split(":")[1] == "enter_another_quantity",
)
async def process_enter_another_quantity(
    query: CallbackQuery, state: FSMContext
) -> None:
    await bot.edit_message_text(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        text=get_message_text("enter_another_quantity"),
        reply_markup=None,
    )
    await state.set_state(Admin.enter_another_quantity)


@main_router.message(Admin.enter_another_quantity)
async def enter_another_quantity(message: Message, state: FSMContext) -> None:
    if not message.text.isnumeric():
        return
    data = await state.get_data()
    side = data["side"]
    await state.update_data(num=f"{side}{message.text}")
    l_users = flow_db.get_alls_with_order(keys="fio, id", order="fio")
    d_users = [{"name": i[0], "select": False, "id": i[1]} for i in l_users]
    await state.update_data(d_users=d_users)
    await state.update_data(page=1)
    await message.answer(
        get_message_text("flownomika_menu"),
        reply_markup=keyboard_inline.flownomika_list_users(d_users),
    )
    await state.set_state(Admin.main)


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "turn_left"
)
async def process_turn_left(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1])
    page = page - 1 if page > 1 else q_page
    await state.update_data(page=page)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=data["d_users"], many_selects=True, page_num=page
        ),
    )


@main_router.callback_query(
    Admin.main, F.data.split(":")[0] == "action", F.data.split(":")[1] == "turn_right"
)
async def process_turn_right(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    q_page = count_page(5, len(data["d_users"]))
    if q_page == 1:
        return
    page = int(query.data.split(":")[-1])
    page = page + 1 if page < q_page else 1
    await state.update_data(page=page)
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_inline.flownomika_list_users(
            list_users=data["d_users"], many_selects=True, page_num=page
        ),
    )


@main_router.message()
@state_is_none
async def all_mes(message: Message, state: FSMContext) -> None:
    id_user = message.from_user.id
    if not flow_db.user_exists(id_user):
        return await command_start(message, state)
    if not flow_db.rule_exists(id_user):
        return await process_fio(message, state)
    rule = flow_db.get(key="rule", where="id", meaning=id_user)
    if rule == "admin":
        await state.set_state(Admin.main)
        return await message.answer(
            get_message_text("again_work"),
            reply_markup=keyboard_markup.main_menu_admin(),
        )
    if rule == "ban":
        return await state.set_state(Ban.void)
    await message.answer(
        get_message_text("again_hello"), reply_markup=keyboard_markup.main_menu_user()
    )


async def main() -> None:
    dp = dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(form_router)
    dp.include_router(main_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
