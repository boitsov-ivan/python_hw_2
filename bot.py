import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN, weather_api_key
from handlers import router
from middleware import LoggingMiddleware



# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(router)
dp.message.middleware(LoggingMiddleware())
dp['weather_api_key'] = weather_api_key


async def main():
    print("Бот запущен!")
    await dp.start_polling(bot, users = dict())



if __name__ == "__main__":
    asyncio.run(main())