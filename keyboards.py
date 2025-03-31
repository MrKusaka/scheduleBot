from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.request import get_users


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пользователи')],
    [KeyboardButton(text='Рабочее время')]
])


async def users():
    users_kb = InlineKeyboardBuilder
    users = await get_users()
    for user in users:
        users_kb.add(InlineKeyboardButton(text=user.first_name, callback_data=f'user_{user.first_name}'))
    return users_kb.adjust(2).as_markup()

