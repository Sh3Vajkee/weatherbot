from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from keyboars import start_kb
from middlewares.throttling import rate_limit


@rate_limit("default")
async def start_cmd(m: types.Message):
    await m.answer(
        "Вы можете узнать погоду на данный момент или на сутки, указав город.\n"
        "Чтобы убрать клавиатуру нажмите /stop",
        reply_markup=start_kb
    )


async def stop_cmd(m: types.Message):
    await m.answer("Клавиатура удалена. Чтобы вернуть клавиатуру нажмите /start")


def start_handlers(dp: Dispatcher):
    dp.register_message_handler(
        start_cmd,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        commands="start"
    )
    dp.register_message_handler(
        stop_cmd,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        commands="stop"
    )
    dp.register_message_handler(
        stop_cmd,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        Text(equals="❌Убрать клавиатуру")
    )
