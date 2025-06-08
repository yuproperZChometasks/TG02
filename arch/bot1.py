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
# Получаем значение Константы
API_TOKEN = os.getenv('TGBOT_TOKEN')
# Проверка, что токен получен
if API_TOKEN is None:
    raise ValueError("API_TOKEN не задан в переменных окружения")

# Создаем бота и диспетчера
bot = Bot(token=API_TOKEN) 

# Создаем диспетчера, передавая бота в конструктор
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.name}')

"""
@dp.message()
async def start(message: Message):
    await message.send_copy(chat_id=message.chat.id)
"""
"""
@dp.message()
async def start(message: Message):
    await message.answer("Я тебе ответил")
"""

 
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())