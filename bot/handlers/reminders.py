from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from bot.models import Reminder

router = Router()

@router.message(Command("add"))
async def add_reminder(message: Message,
                       **kwargs):
    session: AsyncSession = kwargs["session"]

    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Используйте /add YYYY-MM-DD HH:MM TEXT")
        return
    _, date_str, time_str, text = parts
    try:
        remind_at = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    except ValueError:
        await message.answer("Неправильынй формат даты и времени. \n" 
        "                     Используйте /add YYYY-MM-DD HH:MM TEXT")
        return
    reminder = Reminder(
        user_id=message.from_user.id,
        text=text,
        remind_at=remind_at
    )
    session.add(reminder)
    await session.commit()
    await message.answer(f"Напоминание сохранено на {remind_at}")

@router.message(Command("list"))
async def list_reminders(message: Message, 
                         **kwargs):
    session: AsyncSession = kwargs["session"]

    result = await session.execute(
        select(Reminder).where(
            Reminder.user_id == message.from_user.id,
            Reminder.is_active == True
        )
    )
    reminders = result.scalars().all()
    if not reminders:
        await message.answer("Список напоминаний пуст")
        return
    text = "Ваши напоминания:\n"
    for remind in reminders:
        text += f"ID: {remind.id} | {remind.remind_at} - {remind.text}\n"
    await message.answer(text)

@router.message(Command("remove"))
async def remove_reminders(message: Message, 
                         **kwargs):
    session: AsyncSession = kwargs["session"]
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Неверный формат ввода. Попробуйте /remove ID")
        return
    _, remind_id = parts
    if not remind_id.isdigit():
        await message.answer("ID должно быть числом")
        return
    remind_id = int(remind_id)
    result = await session.execute(
        select(Reminder).where(
            Reminder.id == remind_id,
            Reminder.is_active == True
        )
    )
    reminders = result.scalars().all()
    for rem in reminders:
        rem.is_active = False
    
    if reminders:
        await session.commit()
        await message.answer("Напоминание успешно удалено")
    else:
        await message.answer("Напоминание не найдено. Попробуйте /remove ID")