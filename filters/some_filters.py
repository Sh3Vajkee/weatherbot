from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from db.models import CallsCount


class IsAdmin(BoundFilter):
    key = 'is_admin'

    async def check(self, message: types.Message):
        admins = [746461090]
        return message.from_user.id in admins


class CheckMonthCounts(BoundFilter):
    key = "check_month_counts"

    async def check(self, m: types.Message):
        db_ssn = m.bot.get("db")

        async with db_ssn() as ssn:
            stats: CallsCount = await ssn.get(CallsCount, 1)

            if stats:
                return stats.month_calls < 1000000
            else:
                await ssn.merge(
                    CallsCount(
                        id=1,
                        day_calls=1,
                        month_calls=1
                    )
                )
                await ssn.commit()


class CheckMinuteCounts(BoundFilter):
    key = "check_minute_counts"

    async def check(self, m: types.Message):
        db_ssn = m.bot.get("db")

        async with db_ssn() as ssn:
            stats: CallsCount = await ssn.get(CallsCount, 1)

        return stats.day_calls < 60


class CheckOneCallCounts(BoundFilter):
    key = "check_one_call_counts"

    async def check(self, m: types.Message):
        db_ssn = m.bot.get("db")

        async with db_ssn() as ssn:
            stats: CallsCount = await ssn.get(CallsCount, 1)

        return stats.daily < 1000
