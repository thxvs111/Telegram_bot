import asyncio
import aiohttp
import os
import base64
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from docx import Document  

BOT_TOKEN = ""    # telegram token
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3"
WEATHER_API_KEY = ""      # paste you openweather token
EXCHANGE_API_KEY = ""     # paste you excahngerate token 
GITHUB_API_URL = "https://api.github.com/repos"
GITHUB_TOKEN = ""         # paste you github token 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

text_chunks = []
CHUNK_SIZE = 1000  

async def ask_ollama(prompt: str):
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_URL, json=payload) as response:
            if response.status != 200:
                return f"Помилка сервера: {response.status}"
            data = await response.json()
            return data.get("response", "не можу відповісти.").strip()

async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ua"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Не вдалося отримати погоду."
            data = await response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            return f"Погода в {city}: {temp}°C, {description}"

async def get_exchange_rate(from_currency: str, to_currency: str):
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_API_KEY}/pair/{from_currency}/{to_currency}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Не вдалося отримати курс валют."
            data = await response.json()
            rate = data["conversion_rate"]
            return f"Курс {from_currency} до {to_currency}: {rate}"

async def get_github_repo_files(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/contents"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Не вдалося отримати список файлів."
            data = await response.json()
            files = [file["name"] for file in data if "type" in file and file["type"] == "file"]
            return "\n".join(files) if files else "Репозиторій порожній або містить лише папки."

async def get_readme_content(owner: str, repo: str):
    url = f"{GITHUB_API_URL}/{owner}/{repo}/contents"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return "Не вдалося отримати список файлів."
            data = await response.json()
            readme_file = next((file for file in data if file["name"].lower().startswith("readme")), None)
            if not readme_file:
                return "README.md не знайдено в репозиторії."
            async with session.get(readme_file["download_url"], headers=headers) as readme_response:
                if readme_response.status != 200:
                    return "Не вдалося отримати README.md."
                content = await readme_response.text()
                return content[:1000]  

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Привіт! Ви можете спілкуватися зі мною, отримувати погоду, курс валют та завантажувати файли.")

@dp.message(Command("github"))
async def github_handler(message: types.Message):
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Використання: /github <owner> <repo>")
        return
    owner, repo = args[1], args[2]
    response = await get_github_repo_files(owner, repo)
    await message.answer(response)

@dp.message(Command("readme"))
async def readme_handler(message: types.Message):
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Використання: /readme <owner> <repo>")
        return
    owner, repo = args[1], args[2]
    response = await get_readme_content(owner, repo)
    await message.answer(response)

async def main():
    print("Бот працює")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
