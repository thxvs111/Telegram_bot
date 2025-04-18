import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command


BOT_TOKEN = ""        #  paste you token
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

text_chunks = []
CHUNK_SIZE = 1000  # Розмір  тексту 

async def ask_ollama(prompt: str):
    """Відправляє запит до Ollama AI (Gemma 3) і отримує відповідь."""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as response:
            if response.status != 200:
                return f"Помилка сервера: {response.status}"
            
            data = await response.json()
            return data.get("response", "не можу відповісти.").strip()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привіт! Ви можете спілкуватися зі мною або завантажити .txt файл для аналізу.")

@dp.message(Command("reset"))
async def reset_handler(message: types.Message):
    """Очищення завантажених даних."""
    global text_chunks
    text_chunks = []
    await message.answer("Дані очищені. Можете завантажити новий файл.")

@dp.message(lambda message: message.document)  
async def handle_document(message: types.Message):
    """Обробка отриманого файлу."""
    global text_chunks
    document = message.document
    if not document.file_name.endswith(".txt"):
        await message.answer("Будь ласка, надішліть файл у форматі .txt.")
        return

    file = await bot.download(document)
    text = file.read().decode("utf-8")
    file.close()

    text_chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    await message.answer(f"Файл '{document.file_name}' завантажено! Тепер можете ставити питання.")

@dp.message()
async def ai_handler(message: types.Message):
    """Обробка питань користувача."""
    if not text_chunks:
        response = await ask_ollama(message.text)
        await message.answer(response)
    else:
        
        query = message.text.lower()
        best_chunk = max(text_chunks, key=lambda chunk: chunk.lower().count(query))
        
        prompt = f"Ось уривок з файлу: {best_chunk}\n\nЗапит: {message.text}"
        response = await ask_ollama(prompt)
        await message.answer(response)

async def main():
    print("Бот працює")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
