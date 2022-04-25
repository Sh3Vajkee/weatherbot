from aiogram import types

start_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [
            types.KeyboardButton(text="🕚Погода сейчас")
        ],
        [
            types.KeyboardButton(text="🌓Погода на сутки")
        ],
        [
            types.KeyboardButton(text="❌Убрать клавиатуру")
        ],
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)
