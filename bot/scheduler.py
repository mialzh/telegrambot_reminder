import asyncio 
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from aiogram import Bot

from bot.models import Reminder

async def run_scheduler(session_maker: async_sessionmaker,
                        bot: Bot):
    while True:
        await asyncio.sleep(59)
        async with session_maker() as session:
            now = datetime.now()

            request = select(Reminder).where(
                Reminder.remind_at <= now,
                Reminder.is_active == True
            )
            
            result = await session.execute(request)
            reminders = result.scalars().all()

            for rem in reminders:
                try:
                    await bot.send_message(
                        rem.user_id,
                        f"Напоминание: {rem.text}"
                    )
                except Exception as e:
                    print(f"Ошибка отправки {e}")
                rem.is_active = False
            if reminders:
                await session.commit()