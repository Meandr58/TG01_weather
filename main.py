import random
import asyncio
import aiohttp  # для асинхронных запросов
import logging  # для логирования
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton  # для создания кнопок
from config import TOKEN, WEATHER_API_KEY

# Установим базовое логирование
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Функция для получения прогноза погоды
async def get_weather(city: str, city_ru: str):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&cnt=16&appid={WEATHER_API_KEY}&lang=ru"
    logging.info(f"Запрос к API: {url}")  # Логируем URL запроса
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                logging.info(f"Ответ от API: {data}")  # Логируем ответ от API
                if resp.status == 200:
                    # Получаем данные на следующий день (по индексу 8 для 3-часовых прогнозов)
                    forecast = data['list'][8]
                    temp = forecast['main']['temp']
                    weather_description = forecast['weather'][0]['description']
                    return f"Прогноз на завтра для {city_ru}:\nТемпература: {temp}°C\nОписание: {weather_description}"
                else:
                    logging.error(f"Ошибка API: {data}")
                    return f"Не удалось получить прогноз погоды для {city_ru}."
    except Exception as e:
        logging.error(f"Ошибка при запросе погоды: {e}")
        return f"Произошла ошибка при получении прогноза погоды для {city_ru}."


# Команда /weather с кнопками для выбора города
@dp.message(Command(commands=["weather"]))
async def weather_command(message: Message):
    # Создаем инлайн-кнопки для выбора города
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Москва", callback_data="weather-Moscow")],
        [InlineKeyboardButton(text="Санкт-Петербург", callback_data="weather-SaintPetersburg")]
    ])
    await message.answer("Выберите город:", reply_markup=keyboard)


# Обработка нажатия на кнопку с выбором города
@dp.callback_query(lambda c: c.data and c.data.startswith("weather-"))
async def process_weather_callback(callback_query: CallbackQuery):
    city_data = callback_query.data.split("-")[1]  # Извлекаем название города из callback_data
    logging.info(f"Обработка запроса для города: {city_data}")

    if city_data == "Moscow":
        forecast = await get_weather("Moscow", "Москвы")
    elif city_data == "SaintPetersburg":
        forecast = await get_weather("Saint Petersburg", "Санкт-Петербурга")
    else:
        forecast = "Неизвестный город."

    await callback_query.message.answer(forecast)
    await callback_query.answer()


@dp.message(F.photo)
async def react_photo(message: Message):
    responses = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(responses)
    await message.answer(rand_answ)


@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer(
        'Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека.')


@dp.message(Command(commands=["start"]))
async def start_command(message: Message):
    await message.answer("Привет, я знаю прогноз погоды на завтра для Москвы и Санкт-Петербурга!\n/weather")


@dp.message(Command(commands=["help"]))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/weather")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
