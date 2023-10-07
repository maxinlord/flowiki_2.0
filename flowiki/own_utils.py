import datetime
from db_func import flow_db


def get_current_date(format="%Y-%m-%d"):
    """
    Возвращает текущую дату в указанном формате.

    Параметры:
    format (строка): Формат даты (по умолчанию "%Y-%m-%d").

    Возвращает:
    строка: Текущая дата в указанном формате.
    """
    current_date = datetime.datetime.now()
    return current_date.strftime(format)


def get_message_text(unique_name, d=None) -> str:
    if d is None:
        d = {}
    mode = flow_db.get(
        key="box",
        where="name",
        meaning="program_mode_for_text",
        table="values",
    )
    try:
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="message_texts"
        )
    except Exception:
        flow_db.add_new_message_text(name=unique_name)
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="message_texts"
        )
    text_true = text.format(**d)
    return f"[{unique_name}]\n{text_true}" if mode == "on" else text_true


def get_button_text(unique_name, d=None) -> str:
    if d is None:
        d = {}
    mode = flow_db.get(
        key="box",
        where="name",
        meaning="program_mode_for_text",
        table="values",
    )
    try:
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="button_texts"
        )
    except Exception:
        flow_db.add_new_button_text(name=unique_name)
        text = flow_db.get(
            key="text", where="name", meaning=unique_name, table="button_texts"
        )
    text_true = text.format(**d)
    return f"[{unique_name}]\n{text_true}" if mode == "on" else text_true


def update_dict_users(name: str, dict_users: list) -> list:
    for num, i in enumerate(dict_users):
        if i["name"] == name:
            dict_users[num]["select"] = not dict_users[num]["select"]
    return dict_users

def count_page(size_one_page, quantity_users) -> int:
    return (quantity_users // size_one_page) + 1