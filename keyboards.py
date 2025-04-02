from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.request import get_users, get_work_time


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пользователи')],
    [KeyboardButton(text='Рабочее время')]
], resize_keyboard=True)


async def users():
    users_kb = InlineKeyboardBuilder()
    all_users = await get_users()
    for user in all_users:
        users_kb.add(InlineKeyboardButton(text=user.first_name, callback_data=f'user_{user.id}'))

    return users_kb.adjust(2).as_markup()


async def work_times(user_id):
    users_kb = InlineKeyboardBuilder()
    all_work_times = await get_work_time(user_id)
    for work_time in all_work_times:
        work = str(work_time.day), str(work_time.work_start), str(work_time.work_end)
        users_kb.row(InlineKeyboardButton(text=str(work), callback_data=f'work_time_{work_time.id}'))
    return users_kb.adjust(2).as_markup()
