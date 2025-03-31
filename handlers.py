from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import keyboards as kb
import database.request as rq

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(f"Привет, {message.chat.first_name}! Чтобы создать пользователя введите /add_user")

@router.message(Command('register'))
async def register_handler(message: Message):
    await rq.register_users(message)

@router.message(Command('add_user'))
async def register_handler(message: Message):
    await rq.add_user(message)


@router.message(Command('list_users'))
async def register_handler(message: Message):
    await rq.list_users(message)

#
# router.message(Command('register'))
# async def register_handler(message: Message):
#     await rq.register_users(message)
#


@router.message(F.text == 'Пользователи')
async def users(message: Message):
    await message.answer(f'Ваши пользователи', reply_markup= await kb.users())
#
@router.callback_query(F.data.starswith('users_'))
async def users(callback: CallbackQuery):
    # users_name = ['Илья', 'Pupa']
    # await callback.answer(f'Пользователи:')
    await callback.message.answer('Выберите пользователя', reply_markup= await kb.users(callback.data.split('_')[1]))




# @router.message(Command(['register']))
# async def handle_get_users(message: types.Message):
#     await get_users(message)