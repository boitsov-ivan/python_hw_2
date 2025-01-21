import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
weather_api_key = os.getenv("weather_api_key")

if not TOKEN:
    raise  ValueError("Переменная окружения BOT_TOKEN не установлена!")


if not weather_api_key:
    raise  ValueError("Переменная окружения weather_api_key не установлена!")