import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.types.bot_command_scope import BotCommandScopeAllPrivateChats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config_loader import Config, load_config
from db.base import Base
from handlers.start import start_handlers
from handlers.weather import weather_handlers
from middlewares.throttling import ThrottlingMiddleware
from updatesworker import get_handled_updates_list
from utils.sheduled import reset_calls, reset_month_calls


async def set_bot_commands(bot: Bot):

    commands_private = [
        BotCommand(command="start", description="Получить клавиатуру"),
        BotCommand(command="stop", description="Удалить клавиатуру"),
        BotCommand(command="current", description="Погода сейчас"),
        BotCommand(command="daily", description="Погода на сутки"),
    ]

    await bot.set_my_commands(commands_private, scope=BotCommandScopeAllPrivateChats())


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    config: Config = load_config()

    engine = create_async_engine(
        f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}/{config.db.db_name}",
        future=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_sessionmaker = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    storage = MemoryStorage()
    bot = Bot(config.bot.token, parse_mode="HTML")
    bot["db"] = async_sessionmaker
    dp = Dispatcher(bot, storage=storage)
    sheduler = AsyncIOScheduler()
    sheduler.add_job(
        reset_calls,
        'interval',
        minutes=1,
        args=(dp,)
    )
    sheduler.add_job(
        reset_month_calls,
        'cron',
        hour="23",
        minute="59",
        second='59',
        args=(dp,)
    )
    sheduler.start()

    dp.middleware.setup(ThrottlingMiddleware())

    weather_handlers(dp)
    start_handlers(dp)

    await set_bot_commands(bot)

    try:
        await dp.skip_updates()
        await dp.start_polling(allowed_updates=get_handled_updates_list(dp))
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logging.error("Bot stopped!")
