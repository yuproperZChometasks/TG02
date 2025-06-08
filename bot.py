import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher
from aiogram import Router, types, F
from aiogram.types import FSInputFile
from aiogram.filters import Command, CommandObject, CommandStart
from deep_translator import GoogleTranslator
import re
from langdetect import detect, LangDetectException

# Загружаем переменные из файла .env
load_dotenv()
# Получаем значение Константы
API_TOKEN = os.getenv('TGBOT_TOKEN')
# Проверка, что токен получен
if API_TOKEN is None:
    raise ValueError("API_TOKEN не задан в переменных окружения")

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)
# Создание папки для сохранения изображений
if not os.path.exists('img'):
    os.makedirs('img')


@dp.message(Command("start"))
@dp.message(Command("help"))
async def start_command(message: types.Message):
    print ("Обработка /start")
    await message.answer(
        "мои команды:\n"
        "start - получение звукового файла\n"
        "voice - получение звукового файла\n"
        "кроме того осуществляю следующие действия\n"
        "- получение фото (.jpg) от пользователя и возврат его клиенту\n"
        "- перевод текста введенного в поле ввода на английский"
    )

    
# Обработчик для сохранения фото
#@router.message(content_types=types.ContentType.PHOTO)
@router.message(F.photo)
async def save_photo(message: types.Message):
    print ("Обработка фото")
    # создаем папку `img/` при необходимости:
    os.makedirs("img", exist_ok=True)
    print (types.Message)
    # Получаем самую большую версию фото
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        print(f"Получено фото с file_id: {file_id}")
        file = await bot.get_file(file_id)
        file_path = file.file_path
        print(f"File path: {file_path}")
        # Сохраняем фото локально
        download_path = f"img/{file_id}.jpg"
        await bot.download(file=file, destination=download_path)
        print(f"Файл сохранен: {download_path}")
        await message.reply(f"Фото сохранено: {download_path}")

# Обработчик для отправки голосового сообщения
#@dp.message(F.voice)
@dp.message(Command("voice"))
async def send_voice(message: types.Message):
    print ("Обработка /voice")
    # Путь к вашему голосовому файлу (например, "example.ogg")
    voice_file = r"C:\work\ZC_python_and_GPT\Zerocoder_courses\Python_and_GPT\TG02\voice1.ogg"
    # Создаём объект FSInputFile
    voice_file_inner = FSInputFile(voice_file)
    if os.path.exists(voice_file):
        await message.reply_voice(voice_file_inner)
    else:
        await message.reply("Голосовой файл не найден!")

@dp.message(F.text)
async def translate_text(message: types.Message):
    # Проверяем наличие текста
    if not message.text:
        return  # или можно пропустить

    # Проверяем, что сообщение не команда
    if message.text.startswith('/'):
        return
    text = message.text
    if not text:
        await message.reply("Получено пустое сообщение для перевода.")
        return
    
    # Проверяем, содержит ли текст только русский или определённый процент русского
    try:
        lang = detect(text)
    except LangDetectException:
        # Не удалось определить язык
        await message.reply("Не удалось определить язык текста.")
        return

    # Если язык не русский, не переводим
    if lang != 'ru':
        return  # или можете отправить сообщение или пропустить

    # Переводим только если текст на русском
    try:
        # Переводим текст на английский
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None,
            lambda: GoogleTranslator(source='ru', target='en').translate(text)
        )
        await message.reply(f"Перевод: {translated}")
    except Exception as e:
        await message.reply(f"Ошибка при переводе: {e}")

"""
# Обработчик для перевода текста
@dp.message(F.text)
async def translate_text(message: types.Message):
    text = message.text
    if not text:
        await message.reply("Получено пустое сообщение для перевода.")
        return
    try:
        # Переводим текст на английский
        # Используем run_in_executor, чтобы не блокировать event loop
        loop = asyncio.get_running_loop()
        translated = await loop.run_in_executor(
            None,
            lambda: GoogleTranslator(source='auto', target='en').translate(text)
        )
        await message.reply(f"Перевод: {translated}")
    except Exception as e:
        await message.reply(f"Ошибка при переводе: {e}")

"""        
"""
**Объяснение:**

- Мы используем `GoogleTranslator` из `deep-translator`.
- `source='auto'` — автоматическое определение языка.
- `target='en'` — перевод на английский.
- Для асинхронной работы используем `run_in_executor`, чтобы не блокировать основной цикл.
"""

"""
# Обработчик для перевода текста
@dp.message(content_types=['text'])
async def translate_text(message: types.Message):
    #async with Translator() as translator:
    text = message.text
    if text is None:
        await message.reply("Получено пустое сообщение для перевода.")
        return
    try:
        # Переводим текст на английский
        #translated = await translator.translate(None,text, destination='en')
        loop = asyncio.get_running_loop()
        #translated = translator.translate(text, src='ru')

        translated = await loop.run_in_executor(None, translator.translate(text, src='ru')) # type: ignore
        await message.reply(f"Перевод: {translated.text}")
    except Exception as e:
        await message.reply(f"Ошибка при переводе: {e}")
"""
    
"""
import asyncio

def my_sync_func():
    # тяжелая синхронная операция
    return "результат"

async def my_async_func():
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, my_sync_func)
    # дальше работаете с результатом
"""
"""
def translate_text(text, from_lang='ru', to_lang='en'):
    # Создаем объект Translator, указывая исходный язык и язык перевода
    #translator = Translator(from_lang=from_lang, to_lang=to_lang)
    try:
        # Пытаемся перевести текст
        translated_text = translator.translate(text)
        return translated_text  # Возвращаем переведенный текст
    except Exception as e:
        # Если возникает ошибка, возвращаем сообщение об ошибке
        return f"Error: {e}"
    
# Пример использования функции

    text_to_translate = "Привет, как дела?"  # Текст для перевода
    translated_text = translate_text(text_to_translate)  # Переводим текст
    print(f"Перевод: {translated_text}")  # Выводим переведенный текст
"""


# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
 