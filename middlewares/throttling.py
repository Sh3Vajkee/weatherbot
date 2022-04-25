from math import inf

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from cachetools import TTLCache

caches = {
    "default": TTLCache(maxsize=inf, ttl=2),
    "city": TTLCache(maxsize=inf, ttl=5),
    "request": TTLCache(maxsize=inf, ttl=10)
}


def rate_limit(key="default"):

    def decorator(func):
        setattr(func, 'throttling_key', key)
        return func
    return decorator


class ThrottlingMiddleware(BaseMiddleware):

    def __init__(self):
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):

        handler = current_handler.get()

        throttling_key = getattr(handler, 'throttling_key', None)

        if throttling_key and throttling_key in caches:
            if not caches[throttling_key].get(message.chat.id):
                caches[throttling_key][message.chat.id] = True
                return
            else:
                if throttling_key == "default":
                    await message.answer("Использовать функцию можно <b>раз в 2 секунды</b>!")
                elif throttling_key == "city":
                    await message.answer("Использовать функцию можно <b>раз в 5 секунд</b>!")
                else:
                    await message.answer("Использовать функцию можно <b>раз в 10 секунд</b>!")

                raise CancelHandler()
