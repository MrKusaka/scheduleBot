from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.request import get_users, get_work_time, add_user

from calendar import monthrange


# def get_main_keyboard(is_admin=False):
#     buttons = [
#         [KeyboardButton(text="Мой график")],
#         [KeyboardButton(text="Запросить отгул")]
#     ]
#     if is_admin:
#         buttons.extend([
#             [KeyboardButton(text="Добавить сотрудника")],
#             [KeyboardButton(text="Управление графиками")]
#         ])
#     return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Пользователи')],
    [KeyboardButton(text='Рабочее время')]
], resize_keyboard=True)


# async def users():
#     users_kb = InlineKeyboardBuilder()
#     all_users = await get_users()
#     for user in all_users:
#         users_kb.add(InlineKeyboardButton(text=user.first_name, callback_data=f'user_{user.id}'))
#
#     return users_kb.adjust(2).as_markup()
#
#

#
#
# def generate_calendar(year: int, month: int):
#     """
#     Генерация календаря для выбора дней месяца.
#     """
#     days_in_month = monthrange(year, month)[1]
#     keyboard = InlineKeyboardBuilder()
#     for day in range(1, days_in_month + 1):
#         keyboard.add(InlineKeyboardButton(text=str(day), callback_data=f"day_{day}"))
#     return keyboard.adjust(5).as_markup()

def get_days_keyboard():
    days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
    builder = InlineKeyboardBuilder()
    for day in days:
        builder.add(InlineKeyboardButton(text=day, callback_data=f"day_{day}"))
    builder.adjust(2)
    return builder.as_markup()

# определенные часы
def get_hours_keyboard():
    hours = ['07:00', '09:00', '10:00', '12:00', '15:00', '16:00', '18:00', '19:00', '21:00', '00:00']
    builder = InlineKeyboardBuilder()
    for hour in hours:
        builder.add(InlineKeyboardButton(text=hour, callback_data=f"hour_{hour}"))
    builder.adjust(5)
    return builder.as_markup()

# более широкий выбор времени
# def get_hours_keyboard():
#     builder = InlineKeyboardBuilder()
#     for hour in range(0, 24):
#         for minute in [0, 30]:
#             time_str = f"{hour:02d}:{minute:02d}"
#             builder.button(text=time_str, callback_data=f"hour_{time_str}")
#     builder.adjust(4)  # 4 кнопки в ряд
#     return builder.as_markup()

def get_employees_keyboard(users, mode):
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.add(InlineKeyboardButton(
            text=user.first_name,
            callback_data=f"{mode}_user_{user.user_id}"
        ))
    builder.adjust(1)
    return builder.as_markup()

async def work_times(users):
    users_kb = InlineKeyboardBuilder()
    # all_work_times = await get_work_time(user_id)
    for user in users:
        date = str(user.date)
        day = user.day
        time_range = f'{user.work_start.strftime('%H:%M')} - {user.work_end.strftime('%H:%M')}'
        users_kb.row(InlineKeyboardButton(text=f'{date}, {day}: {time_range}', callback_data=f'work_time_{user.id}'))
    return users_kb.adjust(3).as_markup()