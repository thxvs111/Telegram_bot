import asyncio
import aiohttp
import json
from aiogram import Bot, Dispatcher, types

BOT_TOKEN = ""  # past you`re telegram token
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

                    # extra string for new info

extra_string = """          
                        
"""

async def ask_ollama(prompt: str):
    """Відправляє запит до Ollama AI (Phi) і отримує відповідь."""
    
    full_prompt = f"{extra_string}\n{prompt}"

    payload = {"model": OLLAMA_MODEL, "prompt": full_prompt}
    result = ""

    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as response:
            if response.status != 200:
                return f"error: {response.status}"

            async for line in response.content:
                try:
                    data = json.loads(line.decode('utf-8').strip())  
                    if "response" in data:
                        result += data["response"]
                    if data.get("done", False):
                        break  
                except json.JSONDecodeError:
                    continue  

    return result.strip() if result else "😕 Вибач, я не можу відповісти."


@dp.message()
async def ai_handler(message: types.Message):
    """Обробник повідомлень у Telegram."""
    await message.answer("think...")
    response = await ask_ollama(message.text)

    if not response.strip():
        response = "😕 Вибач, я не можу відповісти."  
    await message.answer(response)


async def main():
    print("✅ Бот запущено!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
