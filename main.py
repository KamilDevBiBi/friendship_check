import asyncio
from aiogram import Bot, Dispatcher

from config import settings
from bot.handlers import router

from bd.models import main as create_db

from flask import Flask
from threading import Thread
import os

dp = Dispatcher()

async def main():
    await create_db()

    bot = Bot(token=settings.bot_token.get_secret_value())
    dp.include_router(router)
    
    await dp.start_polling(bot)


def start_bot():
    asyncio.run(main())


app = Flask(__name__)

@app.route("/")
@app.route("/health")
def check_status():
    return "OK", 200


if __name__ == "__main__":
    try:
        bot_thread = Thread(target=start_bot)
        bot_thread.start()

        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        pass