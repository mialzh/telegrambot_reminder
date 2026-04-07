from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import User

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, **kwargs):
    print("DEBUG: cmd_start called, data keys:", kwargs.keys())
    session: AsyncSession = kwargs["session"]
    user = await session.get(User, message.from_user.id)
    if not user:
        user = User(id=message.from_user.id, username=message.from_user.username)
        session.add(user)
        await session.commit()
        await message.answer("Вы зарегистрированы!")
    else:
        await message.answer("Рад видеть снова!")