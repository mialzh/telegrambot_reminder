import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config import BOT_TOKEN, DATABASE_URL
from bot.models import Base
from bot.middlewares import DbSessionMiddleware
from bot.handlers import start, reminders
from bot.scheduler import run_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота и зарегестрироваться"),
        BotCommand(command="add", description="Добавить напоминание (формат :/add ГГГГ-ММ-ДД ЧЧ:ММ Текст))"),
        BotCommand(command="list", description="Показать активные напоминания"),
        BotCommand(command="remove", description="Удалите ненвжное напоминание (формат: /remove ID)")
    ]
    await bot.set_my_commands(commands)

async def main():

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(DbSessionMiddleware(async_session_maker))

    dp.include_router(start.router)
    dp.include_router(reminders.router)

    await set_commands(bot)
    asyncio.create_task(run_scheduler(async_session_maker, bot))
    logger.info("бот запущен")

    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()
        logger.info("бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())