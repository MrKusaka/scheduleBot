from datetime import time, date, datetime

from aiogram import types
from aiogram.types import message
from sqlalchemy.exc import IntegrityError

from calendarbot import GoogleCalendar
# from calendarbot import parse_schedule_input
from config import ADMIN_ID
from database.db import User, WorkTime, async_session_maker
from sqlalchemy import select, insert, update, delete

calendar = GoogleCalendar()


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
            user = User(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name
            )
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



# async def set_schedule(message: types.Message):
#     try:
#         _, user_id, schedule = message.text.split(", ", 2)
#         user_id = int(user_id)
#         work_start, work_end = parse_schedule_input(schedule)
#
#         async with async_session_maker() as session:
#             schedule = WorkTime(user_id=user_id, work_start=work_start, work_end=work_end)
#             session.add(schedule)
#             await session.commit()
#
#         await message.reply(f"График работы для пользователя с ID {user_id} успешно установлен.")
#     except ValueError as e:
#         await message.reply(str(e))
#

async def add_work_schedule(**kwargs):
    try:
        async with async_session_maker() as session:
            user = await session.scalar(select(User).where(User.user_id == kwargs['user_id']))
            if not user:
                raise ValueError("Работник не найден")

            # event_date = valid_from  # Используем ближайшую дату для примера
            # start_datetime = datetime.combine(event_date, work_start)
            # end_datetime = datetime.combine(event_date, work_end)

            # google_event_id = await calendar.create_event(
            #     user['first_name'],
            #     start_datetime,
            #     end_datetime,
            #     f"Рабочая смена: {user['position']}"
            # )

            schedule = WorkTime(
                user_id=kwargs['user_id'],
                day=kwargs['day'],
                work_start=kwargs['work_start'],
                work_end=kwargs['work_end']
            )
            print(schedule)
            session.add(schedule)
            await session.commit()
            # await message.reply(f"График пользователю {User.first_name}  успешно добавлен.")


    except Exception as e:
        print(f"Ошибка при добавлении графика: {e}")
        return False
