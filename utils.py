

import datetime


def is_float(num: str) -> bool:
    if num.isdigit():
        return False
    try:
        float(num)
        return True
    except:
        return False

# def float_transformer(num: float):


def to_str(data: list):
    return list(map(lambda x: str(x), data))

def get_date_now(year_month_day: bool = True, hours: bool = True, minutes: bool = True, seconds: bool = True, sep1: str = ':', sep2: str = '/'):
    result = ''
    if hours:
        result += '%H:'
    if minutes:
        result += '%M:'
    if seconds:
        result += '%S'
    result = result.strip(':').replace(':', sep1)
    if year_month_day:
        result += ' %m/%d/%Y'.replace('/', sep2)
    return datetime.datetime.now().strftime(result.strip(' '))