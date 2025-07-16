from aiogram import types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter

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


@router.callback_query(SimpleCalendarCallback.filter())
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

    # Здесь вызов функции добавления графика в БД
    # await rq.add_work_schedule(**full_data)  # Замени на свою реализацию

    # user = await rq.get_user(full_data['user_id'])
    date_str = full_data['date'].strftime("%d.%m.%Y")
    # await callback.message.edit_text(f"График для {user.first_name} на {date_str} успешно добавлен!")
    # await state.clear()
    # await callback.answer()
    user = await rq.get_user(data['user_id'])
    all_work_time= await rq.get_work_time(data['user_id'])
    for work_time in all_work_time:
        if work_time.date == full_data['date']:
            await callback.message.answer(f"График для {user.first_name} на {date_str} уже существует")
            break

        else:

            await rq.add_work_schedule(**full_data)

            print('USEEEEEEEEEEEER', user)

            print('ВРЕМЯЯЯЯ', work_time.user_id)
            await callback.message.answer(f"График для {user.first_name} на {date_str} успешно добавлен!")
            break
            await state.clear()


# @router.callback_query(F.data.startswith("day_"))
# async def select_day(callback: CallbackQuery, state: FSMContext):
#     day = callback.data.split("_")[1]
#     await state.update_data(day=day)
#     await callback.message.answer("Введите время начала:", reply_markup=kb.get_hours_keyboard())
#     await callback.answer()

# router.callback_query(F.data.startswith("hour_"))
# async def select_day(callback: CallbackQuery, state: FSMContext):
#     day = callback.data.split("_")[1]
#     await state.update_data(day=day)
#     await callback.message.answer("Введите время начала:", reply_markup=kb.get_hours_keyboard)
#     await callback.answer()

# @router.callback_query(F.data.startswith("hour_"))
# async def process_time(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     print(data)
#
#     if 'work_start' not in data:
#         try:
#             print(callback.data)
#             work_start = datetime.strptime(callback.data.replace('hour_', ''), "%H:%M").time()
#
#             await state.update_data(work_start=work_start)
#             await callback.message.answer("Введите время окончания:", reply_markup=kb.get_hours_keyboard())
#         except ValueError:
#             await callback.message.answer("Неверный формат времени. Попробуйте снова.")
#     else:
#         try:
#             work_end = datetime.strptime(callback.data.replace('hour_', ''), "%H:%M").time()
#             work_start = data['work_start']
#             if work_end <= work_start and work_end != time(0, 0):
#                 await callback.message.answer(
#                     "Время окончания должно быть позже времени начала (кроме 00:00). "
#                     "Попробуйте снова."
#                 )
#                 return
#             else:
#                 await state.update_data(work_end=work_end)
#                 data = await state.get_data()
#
#             await rq.add_work_schedule(**data)
#             user = await rq.get_user(data['user_id'])
#             await callback.message.answer(f"График для {user.first_name} успешно добавлен!")
#             await state.clear()
#             # Очищаем состояние
#         except ValueError:
#             await callback.message.answer("Неверный формат времени. Попробуйте снова.")
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
