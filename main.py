import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from database import init_db
from handlers import router

load_dotenv()


async def main():
    """Точка входа."""

    logging.basicConfig(level=logging.INFO)

    # Инициализация БД
    await init_db()

    bot = Bot(
        token=os.getenv("BOT_TOKEN"),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    print("🤖 Бот 'Куда отдать?' запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
