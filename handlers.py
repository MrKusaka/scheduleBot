from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

import keyboards as kb
import database.request as rq
from datetime import datetime, time

from calendarbot import GoogleCalendar
from database.request import get_users

router = Router()
calendar = GoogleCalendar()


@router.message(Command("add_schedule"))
async def cmd_add_schedule(message: Message):
    users = await rq.get_users()
    await message.answer(
        "Выберите сотрудника:",
        reply_markup=kb.get_employees_keyboard(users, mode='add')
    )

@router.callback_query(F.data.startswith("add_user_"))
async def select_employee(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[2])
    await state.update_data(user_id=user_id)
    await callback.message.answer(
        "Выберите день недели:",
        reply_markup=kb.get_days_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("day_"))
async def select_day(callback: CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    await state.update_data(day=day)
    await callback.message.answer("Введите время начала:", reply_markup=kb.get_hours_keyboard())
    await callback.answer()

# router.callback_query(F.data.startswith("hour_"))
# async def select_day(callback: CallbackQuery, state: FSMContext):
#     day = callback.data.split("_")[1]
#     await state.update_data(day=day)
#     await callback.message.answer("Введите время начала:", reply_markup=kb.get_hours_keyboard)
#     await callback.answer()

@router.callback_query(F.data.startswith("hour_"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)

    if 'work_start' not in data:
        try:
            print(callback.data)
            work_start = datetime.strptime(callback.data.replace('hour_', ''), "%H:%M").time()

            await state.update_data(work_start=work_start)
            await callback.message.answer("Введите время окончания:", reply_markup=kb.get_hours_keyboard())
        except ValueError:
            await callback.message.answer("Неверный формат времени. Попробуйте снова.")
    else:
        try:
            work_end = datetime.strptime(callback.data.replace('hour_', ''), "%H:%M").time()
            work_star = data['work_start']
            if work_end <= work_star and work_end != time(0, 0):
                await callback.message.answer(
                    "Время окончания должно быть позже времени начала (кроме 00:00). "
                    "Попробуйте снова."
                )
                return
            else:
                await state.update_data(work_end=work_end)
                data = await state.get_data()

            await rq.add_work_schedule(**data)
            user = await rq.get_user(data['user_id'])
            await callback.message.answer(f"График для {user.first_name} успешно добавлен!")
            await state.clear()
            # Очищаем состояние
        except ValueError:
            await callback.message.answer("Неверный формат времени. Попробуйте снова.")
            #
            # # Создаем событие в Google Calendar
            # user = await get_users(data['user_id'])
            # start_datetime = datetime.combine(datetime.today(), data['work_start'])
            # end_datetime = datetime.combine(datetime.today(), work_end)
            #
            # event_id = await calendar.create_event(
            #     user.full_name,
            #     start_datetime,
            #     end_datetime,
            #     f"Рабочая смена {user.position}"
            # )

            # # Обновляем запись в БД с ID события
            # await update_work_schedule(schedule_id, google_event_id=event_id)

            # await message.answer("График успешно добавлен!")
        #     await state.clear()
        # except ValueError:
        #     await message.answer("Неверный формат времени. Попробуйте снова.")


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


# @router.message(F.text == 'Пользователи')
# async def users(message: Message):
#     await message.answer(f'Выбери работника', reply_markup= await kb.users())


# @router.callback_query(F.data.startswith('user_'))
# async def user(callback: CallbackQuery):
#     work_time_data = await rq.get_work_time(int(callback.data.split('_')[1]))
#     await callback.answer(f'Вы выбрали пользователя:')
#     if work_time_data != []:
#         await callback.message.answer(f'Время работы',
#                                       reply_markup= await kb.work_times(int(callback.data.split('_')[1])))
#     else:
#         await callback.message.answer('У пользователя нет графика')
#
#
#
@router.message(F.text == 'Рабочее время')
async def set_schedule(message: types.Message):
    users = await rq.get_users()
    await message.answer(
        "Выберите сотрудника:",
        reply_markup=kb.get_employees_keyboard(users, mode='view')
    )

@router.callback_query(F.data.startswith("view_user_"))
async def get_schedule(callback: CallbackQuery):
    print(await rq.get_work_time(int(callback.data.split("_")[2])))
    work_time_data = await rq.get_work_time(int(callback.data.split("_")[2]))
    print(work_time_data)
    await callback.answer(f'Вы выбрали пользователя:')
    if work_time_data != []:
        await callback.message.answer(f'Время работы',
                                      reply_markup=await kb.work_times(work_time_data))
    else:
        await callback.message.answer('У пользователя нет графика')

# @router.message(F.text == 'Рабочее время')
# async def set_schedule(message: types.Message):
#     """
#     Установка графика работы с выбором дня.
#     """
#     now = datetime.now()
#     calendar = kb.generate_calendar(now.year, now.month)
#     await message.answer(f"Выберите день для графика в месяце {now.strftime("%B, %Y")}:", reply_markup=calendar)
#
#
# @router.callback_query(F.data.startswith('day_'))
# async def handle_calendar(callback_query: types.CallbackQuery):
#     """
#     Обработка выбора дня из календаря.
#     """
#     day = int(callback_query.data.split("_")[1])
#     await callback_query.message.reply(f"Вы выбрали день: {day}. Выбери рабочую смену")

# @router.message(F.text == "Мой график")
# async def view_my_schedule(message: types.Message):
#     conn = get_db_connection()
#     try:
#         employee = get_employee_by_telegram(conn, message.from_user.id)
#         if not employee:
#             await message.answer("Вы не зарегистрированы как сотрудник.")
#             return
#
#         schedules = get_employee_schedule(conn, employee.id)
#         await message.answer(format_schedule(schedules))
#     finally:
#         conn.close()
