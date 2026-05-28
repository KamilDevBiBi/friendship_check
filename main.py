import asyncio
from aiogram import Bot, Dispatcher

from config import settings
from bot.handlers import router

from bd.models import main as create_db

dp = Dispatcher()

async def main():
    await create_db()

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp.include_router(router)
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass