from aiogram import types
from aiogram.types import message
from sqlalchemy.exc import IntegrityError

from config import ADMIN_ID
from database.db import User, WorkTime, async_session_maker
from sqlalchemy import select, insert, update, delete

async def register_users(message: types.Message):
    async with async_session_maker() as session:
        try:
            user = User(
                user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            session.add(user)
            await session.commit()
            await message.reply("Вы успешно зарегистрированы!")
        except IntegrityError:
            await message.reply("Вы уже зарегистрированы")
        # return result


async def add_user(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    try:
        _, user_id, first_name, last_name = message.text.split()
        user_id = int(user_id)

        async with async_session_maker() as session:
            user = User(user_id=user_id, first_name=first_name, last_name=last_name)
            session.add(user)
            await session.commit()

        await message.reply(f"Пользователь {first_name} успешно добавлен.")
    except ValueError:
        await message.reply("Используйте формат: /add_user user_id first_name last_name")


async def list_users(message: types.Message):
    # if message.from_user.id != ADMIN_ID:
        # return await message.reply("У вас нет прав для выполнения этой команды.")


    async with async_session_maker() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()

        if users:
            user_list = "\n".join([f"{user.user_id}, {user.first_name} {user.last_name}" for user in users])
            await message.reply(f"Список пользователей:\n{user_list}")
        else:
            await message.reply("Пользователи не найдены.")


async def get_users():
    async with async_session_maker() as session:
        result = await session.scalars(select(User))
        return result


async def get_work_time(user_id):
    async with async_session_maker() as session:
        result = await session.scalars(select(WorkTime).where(WorkTime.user_id == user_id))
        return result.all()