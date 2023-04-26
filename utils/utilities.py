import os
import re

from aiogram import types


def make_keyboard_dict(buttons: dict):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons.values():
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_keyboard_list(buttons: list):
    keyboard = types.ReplyKeyboardMarkup()
    for button in buttons:
        keyboard.add(button)
    keyboard.add("ОТМЕНА")
    return keyboard


def make_text(input_text):
    return re.sub(r'<.*?>', '', input_text)


def make_bytes(file_content: str, file_label: str) -> bytes:
    with open(f"temp/{file_label}", "w") as f:
        f.write(file_content)
    with open(f"temp/{file_label}", "rb") as f:
        file = f.read()
        b = bytearray(file)
    os.remove(f"temp/{file_label}")
    return b


def make_dict_output(d: types.User) -> str:
    result = ''
    d = dict(d)
    for key, value in d.items():
        result += "{0}: {1}\n".format(key, value)
    return result


def taxi_fare_price(
        distance,
        duration,
        min_price,
        min_distance,
        min_duration,
        km_price,
        minute_price,
):
    price = min_price
    extra_km = 0
    if distance > min_distance:
        extra_km = distance - min_distance
    extra_minutes = 0
    if duration > min_duration:
        extra_minutes = duration - min_duration
    price += extra_km * km_price
    price += extra_minutes * minute_price
    if price < min_price:
        price = min_price
    return price


def make_rus(input_str: str) -> str:
    input_str = input_str.upper()
    replace_dict = {
        "A": "А",
        "B": "В",
        "E": "Е",
        "K": "К",
        "M": "М",
        "H": "Н",
        "O": "О",
        "P": "Р",
        "C": "С",
        "T": "Т",
        "X": "Х",
        "Y": "У"
    }
    for char in input_str:
        if char in replace_dict.keys():
            input_str = input_str.replace(char, replace_dict[char])
    return input_str
