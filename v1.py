import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types

BOT_TOKEN = ""              # paste you token
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def ask_ollama(prompt: str):
    """Відправляє запит до Ollama AI (Gemma 3) і отримує відповідь."""
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as response:
            if response.status != 200:
                return f"Помилка сервера: {response.status}"

            data = await response.json()
            return data.get("response", "не можу відповісти.").strip()

@dp.message()
async def ai_handler(message: types.Message):
    """Обробник повідомлень у Telegram."""
    await message.answer("...")
    response = await ask_ollama(message.text)
    await message.answer(response)

async def main():
    print("Бот працює")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

