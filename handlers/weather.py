import datetime
import logging
from textwrap import dedent

import aiohttp
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, Text
from db.models import CallsCount
from filters.some_filters import (CheckMinuteCounts, CheckMonthCounts,
                                  CheckOneCallCounts)
from middlewares.throttling import rate_limit


@rate_limit("city")
async def city_name(m: types.Message, state: FSMContext):
    await m.answer("Укажите город")
    await state.set_state("city")

    if (m.text == "/current") or (m.text == "🕚Погода сейчас"):
        async with state.proxy() as data:
            data["weather"] = "current"
    else:
        async with state.proxy() as data:
            data["weather"] = "daily"


@rate_limit("request")
async def weather_cmd(m: types.Message, state: FSMContext):
    db_ssn = m.bot.get("db")

    icons = {
        "02d": "⛅",
        "02n": "⛅",
        "03d": "☁️",
        "03n": "☁️",
        "04d": "☁️",
        "04n": "☁️",
        "05d": "☁️",
        "05n": "☁️",
        "09d": "🌧️",
        "09n": "🌧️",
        "10d": "🌧️",
        "10n": "🌧️",
        "11d": "⛈️",
        "11n": "⛈️",
        "13d": "🌨️",
        "13n": "🌨️",
        "50d": "🌫️",
        "50n": "🌫️"
    }

    city = m.text.strip()

    api_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": "9ee5c2b908f9fdb008f0a35e229fd488",
        "units": "metric",
        "lang": "ru"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=params) as response:
            response_data = await response.json()

    async with db_ssn() as ssn:
        stat: CallsCount = await ssn.get(CallsCount, 1)

        if stat:
            stat.day_calls += 1
            stat.month_calls += 1
            count_day = stat.day_calls
            count_month = stat.month_calls
            one_call = stat.daily
        else:
            await ssn.merge(
                CallsCount(
                    id=1,
                    day_calls=1,
                    month_calls=1
                )
            )
            count_day = 1
            count_month = 1
            one_call = 0
        await ssn.commit()

    if response_data["cod"] == 200:

        city_data = await state.get_data()

        if city_data["weather"] == "current":

            icon = icons.get(response_data["weather"][0]["icon"], "☀️")

            text = """
            В городе <b>{city}</b> на данный момент
            {icon}{description}.

            Температура <b>{temp}℃</b>. Ощущается как <b>{feels_like}℃</b>.

            Скорость ветра <b>{speed}м/с</b>.
            """
            await m.answer(dedent(text).format(
                city=response_data["name"],
                icon=icon,
                description=response_data["weather"][0]["description"],
                temp=int(response_data["main"]["temp"]),
                feels_like=int(response_data["main"]["feels_like"]),
                speed=int(response_data["wind"]["speed"])
            ))
            await state.finish()
            logging.info(
                f"ID: {m.from_user.id} - {city} - daily: {count_day} - monthly: {count_month} - one_call: {one_call}")
            return

        else:
            api_url_daily = "https://api.openweathermap.org/data/2.5/onecall"

            lat_coord = response_data["coord"]["lat"]
            lon_coord = response_data["coord"]["lon"]

            params_daily = {
                "lat": lat_coord,
                "lon": lon_coord,
                "appid": "9ee5c2b908f9fdb008f0a35e229fd488",
                "units": "metric",
                "lang": "ru"
            }
            async with aiohttp.ClientSession() as session_daily:
                async with session_daily.get(api_url_daily, params=params_daily) as response_d:
                    response_daily = await response_d.json()

            async with db_ssn() as ssn:
                stats: CallsCount = await ssn.get(CallsCount, 1)
                stats.daily += 1
                await ssn.commit()

            text = "\n".join(
                [
                    "\n<i>{time}</i>\n<b>{temp}℃</b> {icon}<i>{description}</i> Ветер <b>{speed}м/с</b>".format(
                        time=str(datetime.datetime.fromtimestamp(
                            hour["dt"])).split(' ')[1][:-2],
                        temp=int(hour["temp"]),
                        icon=icons.get(
                            hour["weather"][0]["icon"], "☀️"),
                        description=hour["weather"][0]["description"],
                        speed=int(hour["wind_speed"])
                    ) for hour in response_daily["hourly"][:24]
                ]
            )
            await m.answer(f"Погода в городе {city} на 24 часа:\n" + text)
            await state.finish()
            logging.info(
                f"ID: {m.from_user.id} - {city} - daily: {stats.day_calls} - monthly: {stats.month_calls} - one_call: {stats.daily}")

    else:
        await m.answer("Такой город не найден.")

    await state.finish()


def weather_handlers(dp: Dispatcher):
    dp.register_message_handler(
        city_name,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        CheckMonthCounts(),
        CheckMinuteCounts(),
        commands="current"
    )
    dp.register_message_handler(
        city_name,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        CheckMonthCounts(),
        CheckMinuteCounts(),
        Text(equals="🕚Погода сейчас")
    )
    dp.register_message_handler(
        city_name,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        CheckMonthCounts(),
        CheckMinuteCounts(),
        CheckOneCallCounts(),
        commands="daily"
    )
    dp.register_message_handler(
        city_name,
        ChatTypeFilter(chat_type=[types.ChatType.PRIVATE]),
        CheckMonthCounts(),
        CheckMinuteCounts(),
        CheckOneCallCounts(),
        Text(equals="🌓Погода на сутки")
    )
    dp.register_message_handler(weather_cmd, state="city")
