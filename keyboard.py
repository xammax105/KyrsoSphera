from aiogram import Bot, Dispatcher, Router, types
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder, \
    ReplyKeyboardMarkup
from conf import cur,conn


def get_admin_keyboard():
    buttons = [
        [
            types.KeyboardButton(text='Рассылка'),
            types.KeyboardButton(text='Добавить курс'),
            types.KeyboardButton(text='Редактировать курсы')
        ],
        [
         types.KeyboardButton(text='Выйти')
         ]

    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True,
                                         input_field_placeholder="Ваши полномочия, всемогущий")
    return keyboard


# кнопка вызова меню
kb = [
    [
        types.KeyboardButton(text='Меню📄'),
        types.KeyboardButton(text='Разработчики🥴')
    ],
]
kb_keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# клавиатура меню
menu_kb = [
    [
        types.InlineKeyboardButton(text='👤 Профиль', callback_data='profile'),
        types.InlineKeyboardButton(text='📚 Курсы', callback_data='instructions')
    ],
    [
        types.InlineKeyboardButton(text='🏆 Наш топ', callback_data='top')
    ],
    [
        types.InlineKeyboardButton(text="💼 admin", callback_data="admin")

    ]
]
menu_keyboard = types.InlineKeyboardMarkup(inline_keyboard=menu_kb,
                                           resize_keyboard=True
                                           )


# def get_profile_kb(user_id):
#     # клава в профиль
#     cur.execute(f"SELECT notifications from Users WHERE user_id = {user_id}")
#     res = cur.fetchone()[0]
#
#     notif = ''
#     if res == 0:
#         notif = '🔔 Включить'
#     elif res == 1:
#         notif = '🔕 Выключить'
#
#     profile_kb = InlineKeyboardBuilder()
#     profile_kb.add(types.InlineKeyboardButton(text="✏Редактировать", callback_data="edit_ins_ans"))
#     profile_kb.add(types.InlineKeyboardButton(text="📫 Мои подписки", callback_data="my_subscriptions"))
#     profile_kb.add(types.InlineKeyboardButton(text=f"{notif} уведомления", callback_data="ofonnotifs"))
#     profile_kb.row(types.InlineKeyboardButton(text='🗑 Удалить аккаунт♯', callback_data='DeleteProfile'))
#     profile_kb.row(types.InlineKeyboardButton(text='🚫 Сделать дроп', callback_data='DeleteDB'))
#
#     return profile_kb.as_markup()



men_kb = [
    [
        types.InlineKeyboardButton(text='➕ Поиск', callback_data='search'),
        types.InlineKeyboardButton(text='👀 Посмотреть', callback_data='view_instructions'),
    ]
]
keyboard_inst = types.InlineKeyboardMarkup(inline_keyboard=men_kb, resize_keyboard=True)