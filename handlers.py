from aiogram import types, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import keyboards as kb
import database.request as rq

router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(f"Привет, {message.chat.first_name}!"
                         f"\nЧтобы создать пользователя введите /add_user"
                         f"\nЧтобы зарегистрироваться введите /register"
                         f"\nЧтобы посмотреть список пользователей введите /list_users", reply_markup=kb.main)

@router.message(Command('register'))
async def register_handler(message: Message):
    await rq.register_users(message)

@router.message(Command('add_user'))
async def register_handler(message: Message):
    await rq.add_user(message)


@router.message(Command('list_users'))
async def register_handler(message: Message):
    await rq.list_users(message)


@router.message(F.text == 'Пользователи')
async def users(message: Message):
    await message.answer(f'Выбери работника', reply_markup= await kb.users())



@router.callback_query(F.data.startswith('user_'))
async def user(callback: CallbackQuery):
    work_time_data = await rq.get_work_time(int(callback.data.split('_')[1]))
    await callback.answer(f'Вы выбрали пользователя:')
    if work_time_data != []:
        await callback.message.answer(f'Время работы',
                                      reply_markup= await kb.work_times(int(callback.data.split('_')[1])))
    else:
        await callback.message.answer('У пользователя нет графика')

