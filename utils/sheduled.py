import logging

from aiogram import Dispatcher
from db.models import CallsCount


async def reset_calls(dp: Dispatcher):
    db_ssn = dp.bot.get("db")

    async with db_ssn() as ssn:
        stats: CallsCount = await ssn.get(CallsCount, 1)

        stats.daily = 0
        stats.day_calls = 0

        await ssn.commit()

    logging.info("Minute calls reset DONE")


async def reset_month_calls(dp: Dispatcher):
    db_ssn = dp.bot.get("db")

    async with db_ssn() as ssn:
        stats: CallsCount = await ssn.get(CallsCount, 1)

        stats.month_calls = 0

        await ssn.commit()

    logging.info("Month calls reset DONE")
