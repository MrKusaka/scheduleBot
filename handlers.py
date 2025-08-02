from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from sqlalchemy.testing.suite.test_reflection import users

import keyboards as kb
import database.request as rq
import locale

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import datetime, time
from calendarbot import GoogleCalendar
from database.request import get_users

router = Router()
calendar = GoogleCalendar()


@router.message(F.text == 'Пользователи')
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
        "Выберите дату:",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state("waiting_for_date")
    await callback.answer()


@router.callback_query(StateFilter("waiting_for_date"),SimpleCalendarCallback.filter())
async def process_calendar(callback: CallbackQuery, callback_data: dict, state: FSMContext):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        # Сохраняем дату в состояние
        await state.update_data(date=date.date())

        await callback.message.answer("Выберите начало работы:", reply_markup=kb.get_hours_keyboard())
        await state.set_state("waiting_for_start_time")


# @router.message(StateFilter("waiting_for_start_time"))
# async def process_work_start(message: Message, state: FSMContext):
#     try:
#         work_start = datetime.strptime(message.text, "%H:%M").time()
#         await state.update_data(work_start=work_start)
#         await message.answer("Введите время окончания работы (например, 18:00):")
#         await state.set_state("waiting_for_end_time")
#     except ValueError:
#         await message.answer("Неверный формат времени. Пожалуйста, введите как HH:MM (например, 09:00).")

@router.callback_query(StateFilter("waiting_for_start_time"))
async def process_work_start(callback: CallbackQuery, state: FSMContext):
    time_str = callback.data.replace("hour_", "")
    work_start = datetime.strptime(time_str, "%H:%M").time()
    data = await state.get_data()


    await state.update_data(work_start=work_start)

    print('DATA000', data)
    await callback.message.answer(f"Выбрано время начала: {time_str}\nТеперь выберите время окончания:",
                                     reply_markup=kb.get_hours_keyboard())
    await state.set_state("waiting_for_end_time")
    await callback.answer()



@router.callback_query(StateFilter("waiting_for_end_time"))
async def process_work_end(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    time_str = callback.data.replace("hour_", "")
    work_end = datetime.strptime(time_str, "%H:%M").time()

    data = await state.get_data()
    date = data.get("date")
    # locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
    day = date.strftime("%a")
    print('DATA', data)
    work_start = data["work_start"]

    if work_end <= work_start and work_end != time(0, 0):
        await callback.message.answer("Время окончания должно быть позже начала (кроме 00:00).")
        return
    else:
        await state.update_data(work_end=work_end, day=day)
        full_data = await state.get_data()


    print('DATA22222', full_data)
    date_str = full_data['date'].strftime("%d.%m.%Y")
    user = await rq.get_user(data['user_id'])
    all_work_time= await rq.get_work_time(data['user_id'])
    for work_time in all_work_time:
        if work_time.date == full_data['date']:
            await callback.message.answer(f"График для {user.first_name} на {date_str} уже существует")
            await state.clear()  # Очищаем состояние
            return

    await rq.add_work_schedule(**full_data)
    await callback.message.answer(f"График для {user.first_name} на {date_str} успешно добавлен!")
    await state.clear()


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

@router.message(F.text == 'Рабочее время')
async def set_schedule(message: types.Message):
    users = await rq.get_users()
    await message.answer(
        "Выберите сотрудника:",
        reply_markup=kb.get_employees_keyboard(users, mode='view')
    )

@router.callback_query(F.data.startswith("view_user_"))
async def get_schedule(callback: CallbackQuery, state: FSMContext):
    print(await rq.get_work_time(int(callback.data.split("_")[2])))
    user_id = int(callback.data.split("_")[2])
    work_time_data = await rq.get_work_time(user_id)
    await state.update_data(schedules=work_time_data, user_id=user_id)
    print(work_time_data)
    await callback.answer(f'Вы выбрали пользователя:')
    if work_time_data != []:
        await callback.message.answer(f'Время работы работника',
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

@router.callback_query(F.data.startswith("work_time_"))
async def edit_work_time(callback: CallbackQuery, state: FSMContext):
    work_time_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    schedules = data.get("schedules", [])

    # Находим смену по ID
    work_time = next((s for s in schedules if s.id == work_time_id), None)

    if not work_time:
        await callback.message.answer("Смена не найдена.")
        await callback.answer()
        return

    # Сохраняем ID смены
    await state.update_data(work_time_id=work_time_id)

    await callback.message.answer(
        f"🔧 Редактирование смены:\n"
        f"Дата: {work_time.date.strftime('%d.%m.%Y')}\n"
        f"Время: {work_time.work_start.strftime('%H:%M')} – {work_time.work_end.strftime('%H:%M')}\n\n"
        f"Выберите новую дату:",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await state.set_state('waiting_for_new_date')
    await callback.answer()

@router.callback_query(StateFilter('waiting_for_new_date'), SimpleCalendarCallback.filter())
async def edit_date(callback: CallbackQuery, callback_data, state: FSMContext):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        await state.update_data(new_date=date.date())
        await callback.message.answer("Выберите новое время начала:", reply_markup=kb.get_hours_keyboard())
        await state.set_state('waiting_for_new_start_time')

@router.callback_query(StateFilter('waiting_for_new_start_time'), F.data.startswith("hour_"))
async def edit_start_time(callback: CallbackQuery, state: FSMContext):
    new_start = datetime.strptime(callback.data.replace("hour_", ""), "%H:%M").time()
    await state.update_data(new_start=new_start)
    await callback.message.answer("Выберите новое время окончания:", reply_markup=kb.get_hours_keyboard())
    await state.set_state('waiting_for_new_end_time')
    await callback.answer()

@router.callback_query(StateFilter('waiting_for_new_end_time'), F.data.startswith("hour_"))
async def edit_end_time(callback: CallbackQuery, state: FSMContext):
    print('NYJNOE IISHKEE', await state.get_data())
    try:
        data = await state.get_data()
        work_time_id = data.get("work_time_id")
        new_end_str = callback.data.replace("hour_", "")
        new_end = datetime.strptime(new_end_str, "%H:%M").time()
        new_start = data["new_start"]

        if new_end <= new_start and new_end != time(0, 0):
            await callback.message.answer("Время окончания должно быть позже начала (кроме 00:00).")
            return
        # Формируем данные для обновления
        update_data = {
            'work_time_id': work_time_id,
            'user_id': data['user_id'],
            'date': data['new_date'],
            'day': data['new_date'].strftime("%a"),  # или кастомный список ["ПН", ...]
            'work_start': new_start,
            'work_end': new_end
        }

        success = await rq.update_work_time(**update_data)
        if success:
            await callback.message.answer("✅ Смена успешно обновлена!")
        else:
            await callback.message.answer("❌ Ошибка при обновлении смены.")
        await state.clear()
        await callback.answer()

    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        await state.clear()
        await callback.answer()
