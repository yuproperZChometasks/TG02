import os
from dotenv import load_dotenv

import asyncio
import logging
from typing import Optional

import aiohttp
from aiogram import Bot, types, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.future import select
#from sqlalchemy.orm import select


# Загружаем переменные из файла .env
load_dotenv()
# Получаем значение переменной
# Константы
API_TOKEN = os.getenv('TGBOT_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BASE_WEATHER_URL = os.getenv('BASE_WEATHER_URL')


# Логирование
logging.basicConfig(level=logging.INFO)

# Создаем базу данных и модели
Base = declarative_base()

class UserWeather(Base):
    """
    ORM модель для хранения информации о пользователе и погодных данных.
    """
    __tablename__ = "user_weather"

    id: int = Column(Integer, primary_key=True, autoincrement=True) # type: ignore
    tg_id: int = Column(Integer, unique=True, nullable=False) # type: ignore
    city: str = Column(String(100), nullable=False) # type: ignore
    temperature: str = Column(String(20), nullable=True) # type: ignore
    weather_description: str = Column(String(100), nullable=True) # type: ignore

# Создаем движок и сессию
engine = create_async_engine("sqlite+aiosqlite:///weather_bot.db")
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def init_db() -> None:
    """
    Инициализация базы данных: создание таблиц.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def fetch_weather(city: str) -> Optional[dict]:
    """
    Получает погоду для указанного города через API weatherstack.com.

    :param city: Название города.
    :return: Словарь с данными о погоде или None, если произошла ошибка.
    """
    params = {
        "access_key": WEATHER_API_KEY,
        "query": city
        #"language": 'ru'
    }
    async with aiohttp.ClientSession() as session:
        try:

            if BASE_WEATHER_URL is not None:
                async with session.get(BASE_WEATHER_URL, params=params) as response:

                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при запросе погоды: {e}")
            return None


async def save_user_weather(
    tg_id: int,
    city: str,
    temperature: str,
    description: str
) -> None:
    """
    Сохраняет или обновляет запись о погоде пользователя в базе.

    :param tg_id: Telegram ID пользователя.
    :param city: Название города.
    :param temperature: Температура.
    :param description: Описание погоды.
    """
    print (UserWeather.tg_id)
    async with async_session() as session:
        # Попытка найти существующую запись
        result = await session.execute(
            select(UserWeather).where(UserWeather.tg_id == tg_id) # type: ignore
        )

        user_record = result.scalar_one_or_none()

        if user_record:
            # Обновляем существующую запись
            user_record.city = city
            user_record.temperature = temperature
            user_record.weather_description = description
        else:
            # Создаем новую запись
            new_record = UserWeather(
                tg_id=tg_id,
                city=city,
                temperature=temperature,
                weather_description=description
            )
            session.add(new_record)

        await session.commit()

async def get_user_weather(tg_id: int) -> Optional[UserWeather]:
    """
    Получает сохраненные данные о погоде пользователя.

    :param tg_id: Telegram ID пользователя.
    :return: Объект UserWeather или None.
    """
    async with async_session() as session:
        result = await session.execute(
            UserWeather.__table__.select().where(UserWeather.tg_id == tg_id)
        )
        return result.scalar_one_or_none()

# Обработчики команд
async def start_handler(message: Message) -> None:
    """
    Обработка команды /start.
    """
    await message.answer("Привет! Введите название города, чтобы получить погоду.")

async def weather_handler(message: Message) -> None:
    """
    Обработка текста, предполагающего название города.
    """
    if message.text is not None:
        city = message.text.strip()
    else:
        await start_handler(Message)  # type: ignore

    tg_id = message.from_user.id # type: ignore
    weather_data = await fetch_weather(city)

    print (weather_data)
    #weather_data = weather_data.json() 
    print (weather_data)

    if weather_data:
        temp = weather_data['current']['temperature']
        description = weather_data['current']['weather_descriptions'][0]

        # Сохраняем в БД
        print (tg_id, city, str(temp),description)
        await save_user_weather(tg_id, city, str(temp),description)
        await message.answer(
            f"Погода в городе {city}:\nТемпература: {temp}°C\nОписание: {description}"
        )
    else:
        await message.answer("Не удалось получить погоду для этого города. Попробуйте еще раз.")

async def main() -> None:
    """
    Главная асинхронная функция запуска бота.
    """
    # Инициализация базы
    await init_db()

    # Создаем бота и диспетчера
    bot = Bot(token=API_TOKEN) # type: ignore
    dp = Dispatcher()

    # Регистрация хендлеров
    dp.message.register(start_handler, Command(commands=["start"]))
    dp.message.register(weather_handler)
"""
    async def delete_webhook():
        await bot.delete_webhook()

    asyncio.run(delete_webhook())

    # Запуск бота
    await dp.start_polling(bot)
"""

if __name__ == "__main__":
    asyncio.run(main())