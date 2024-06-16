import json

from aiogram import Bot, Router, types, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, WebAppInfo, PreCheckoutQuery, LabeledPrice
from aiogram.utils.keyboard import InlineKeyboardBuilder

import func
import func as f
import kyrs_hand
import keyboard as kb
from states import *
import sqlite3
import os
import logging
from conf import TOKEN, admin_token,Pay_token,leter_fisrt
# import functions as f
from conf import cur,conn
# подключение к базе данных

# роутер
router = Router()
bot = Bot(token=TOKEN)



@router.message(F.text.lower() == 'меню📄')
async def user(message: types.Message):
    await bot.send_message(message.from_user.id, f"Меню: ", reply_markup=kb.menu_keyboard)


@router.message(F.text.lower() == 'разработчики🥴')
async def history(message: types.Message):
    photo_maks =  await bot.get_user_profile_photos(989808944, limit=10)
    photo_file_maks = photo_maks.photos[0][-1].file_id


    await bot.send_photo(chat_id=message.from_user.id, photo=photo_file_maks,caption=f"<b>Максим Каничев</b>\n18 "
                                                                                     f"годиков\nстудент ПК "
                                                                                     f"БГТУ\nномер карты "
                                                                                     f"<code>2202201367764954</code>",
                         parse_mode='HTML')



@router.callback_query(F.data == 'admin')
async def admin(message: types.Message, state: FSMContext):
    if message.from_user.id == admin_token:
        await bot.send_message(message.from_user.id, "Введите пароль: 🔐")
        # Ожидаем ответ с паролем
        await state.set_state(RasStates.waiting_for_password)
    else:
        await bot.send_message(message.from_user.id, "Вы не являетесь <b>админом</b>🤔", parse_mode='HTML')

    @router.message(RasStates.waiting_for_password)
    async def process_password(message: types.Message, state: FSMContext):
        password = message.text
        if password == "123":  # Замените "your_password" на реальный пароль
            await bot.send_message(message.from_user.id, "Добро пожаловать в админ-панель💪",
                                   reply_markup=kb.get_admin_keyboard())
        else:
            await bot.send_message(message.from_user.id, "Неправильный пароль🔒")
            # Вызываем функцию user(message)
            await user(message)
        # Сброс состояния после проверки пароля
        await state.clear()


@router.callback_query(F.data == 'profile')
async def profile_command(message: types.Message):
    # Получение количества ответов пользователя
    query = """SELECT COUNT(cp.UserId)
                FROM CourseParticipants cp
                WHERE cp.UserId = (
                    SELECT ID
                    FROM Users
                    WHERE user_id = ?
                )"""
    cur.execute(query, str(message.from_user.id,))
    answers_count = cur.fetchone()[0]
    try:
        photos = await bot.get_user_profile_photos(message.from_user.id, limit=10)
        photo_file = photos.photos[0][-1].file_id
        await bot.send_photo(message.from_user.id, photo_file, caption=f'👤 Ваш профиль:\n'
                                                                       f'Имя: {message.from_user.first_name}\n'
                                                                       f'Юзернейм: @{message.from_user.username}\n\n'
                                                                        f'Курсов: {answers_count}', reply_markup=kb.get_profile_kb(message.from_user.id))

    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, f'👤 Ваш профиль:\n'
                                                     f'Имя: {message.from_user.first_name}\n'
                                                     f'Юзернейм: @{message.from_user.username}\n\n'
                                                     f'Курсов: {answers_count}', reply_markup=kb.get_profile_kb(message.from_user.id))
@router.callback_query(lambda c: c.data.startswith('my_subscriptions_'))
async def process_delete_callback(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[2]
    cur.execute("""SELECT Id,Name, Description,Web, Cost
        FROM Courses
        WHERE Id IN (
            SELECT cp.CourseID
            FROM CourseParticipants cp
            WHERE cp.UserId = (
            SELECT ID
            FROM Users
            WHERE user_id = ?))""", str(cont_1,))
    res = cur.fetchall()

    # Ищем инструкции по тегу
    instructions = res

    # Отправляем результат пользователю
    if instructions:
        for instruction in instructions:
            answer = [
                [
                   types.InlineKeyboardButton(text="📑 Отзывы",
                                               callback_data=f"AddReview_{instruction[0]}"),
                    types.InlineKeyboardButton(text="Меню", callback_data=f"Menu")
                ]
            ]

            keyboard_user_kyrs = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True)
            await bot.send_message(callback_query.from_user.id,f"Найден курс:\n"
                                f"Название: {instruction[1]}\n"
                                f"Содержание: {instruction[2]}\n"
                                f"Стоимость: {instruction[4]}", reply_markup=keyboard_user_kyrs)


@router.callback_query(F.data == 'instructions')
async def instructions(message: types.Message):
    await bot.send_message(message.from_user.id, f"📚 Инструкции", reply_markup=kb.keyboard_inst)


@router.callback_query(F.data == 'top')
async def Top(callback_query: types.CallbackQuery):
    # получаем информацию о самом популярном курсе
    top_course_info = cur.execute("""
        SELECT c.*, cp.UserCount
        FROM Courses c
        JOIN (
            SELECT TOP 1 CourseId, COUNT(UserId) AS UserCount
            FROM CourseParticipants
            GROUP BY CourseId
            ORDER BY UserCount DESC
        ) cp ON c.ID = cp.CourseId
    """)
    # создаем клавиатуру с информацией о курсе

    for course_info in top_course_info:
        id,name, description,wed, price, user_count = course_info

        answer = [
            [
                types.InlineKeyboardButton(text="✉ Записаться", callback_data=f"reply_{id}"),
                types.InlineKeyboardButton(text="📑 Отзывы",
                                           callback_data=f"viewAnswer_{id}"),
            ]
        ]
        keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True,
                                                     input_field_placeholder="Ты кем будешь, вацок")

    await bot.send_message(callback_query.message.chat.id,
                           f"<b>🏆 Самый популярный курс</b> {name}\n{description}\nСтоимость: {price} руб.\nУчастников: {user_count}",
                           reply_markup=keyboard_answer, parse_mode="HTML")


@router.callback_query(lambda c: c.data.startswith('AddReview_'))
async def process_add_rewiev(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[1]
    await bot.send_message(callback_query.from_user.id, 'Введите ваш отзыв на курс:')
    await state.set_state(RasStates.AddRewievState)

    @router.message(RasStates.AddRewievState)
    async def cost(message: types.Message, state: FSMContext):
        rewiew = message.text
        cur.execute("""INSERT INTO Review (Review, Id_cours) VALUES (?, ?)""", (rewiew,cont_1))
        conn.commit()
        await bot.send_message(callback_query.from_user.id,"Отзыв успешно добавлен")
        state.clear()

@router.callback_query(lambda c: c.data.startswith('reply_'))
async def process_reply(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[1]
    web_app = WebAppInfo(url="https://xammax105.github.io/")

    buttons = [
        [types.KeyboardButton(text="Подтвердить",web_app=web_app)]
    ]
    conf = types.ReplyKeyboardMarkup(keyboard=buttons,
                                         resize_keyboard=True)
    await bot.send_message(callback_query.from_user.id, f'Для подтвержедния нажмите кнопку снизу\n'
                                                        f'<b>Данную цифру используйте в форме регистрации на курс</b> <code>{cont_1}</code>:',parse_mode='html', reply_markup=conf)
message_data = {}


@router.message(F.web_app_data)
async def web_app_data_handler(message: types.Message):
    data = message.web_app_data.data
    await message.answer(f"Получены данные из Web App: {data}", reply_markup=kb.kb_keyboard)
    print(data)

    data = json.loads(data)

    cur.execute(f"Select Name, Cost From Courses Where Id = {data['number']}")
    row = cur.fetchone()

    func.send_email_notification(data,leter_fisrt)
    message_data[message.chat.id] = data
    if row:
        name, cost = row
        PRICE = LabeledPrice(label=name, amount=int(cost) * 100)  # Создание объекта LabeledPrice
        print(PRICE)  # Печать созданного объекта
    else:
        print("Курс с указанным Id не найден.")
        await message.answer("Курс с указанным Id не найден.")
        return

    await bot.send_invoice(message.chat.id,
                           title=f"Оплата курса",
                           description=f"Оплата стоимости {name}",
                           provider_token=Pay_token,
                           currency="RUB",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           need_email=True,
                           need_phone_number=True,
                           prices=[PRICE],
                           start_parameter="start_kyrs",
                           payload='one more kyrs'
                           )

@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    #достал из списка по айдишнику
    data = message_data.get(message.chat.id)
    payment_info = message.successful_payment

    with conn.cursor() as cur:
        # Fetch the course name
        cur.execute(f"SELECT Name FROM Courses WHERE Id = ?", (data['number'],))
        row = cur.fetchone()
        if row:
            course_name = row[0]
            await message.answer(
                f'Оплата прошла курса {course_name} успешно! Спасибо за покупку. \nВ ближайщее время с вами свяжется образовательная площадка!')
        else:
            await message.answer('Курс не найден.')
            return

    with conn.cursor() as cur:
        # Fetch the user ID
        cur.execute(f"SELECT ID FROM Users WHERE User_id = ?", (message.from_user.id,))
        row = cur.fetchone()
        if row:
            id_user = row[0]
            print(id_user, "UserIDDDDDDDDDDDDDDDDDDDDDDDDDDD")
        else:
            await message.answer('Пользователь не найден.')
            return

    with conn.cursor() as cur:
        # Insert into CourseParticipants
        cur.execute("INSERT INTO CourseParticipants (UserID, CourseID) VALUES (?, ?)", (id_user, data['number']))
        conn.commit()

    body = f"""
       Уважаемый пользователь,

       Спасибо за оплату курса {course_name}!

    Детали оплаты:
    - Название курса: {course_name}
    - Сумма оплаты: {payment_info.total_amount / 100} {payment_info.currency}
    - Имя плательщика: {message.from_user.username}
    - Email плательщика: {payment_info.order_info.email if payment_info.order_info else 'Не указано'}
    - Телефон плательщика: {payment_info.order_info.phone_number if payment_info.order_info else 'Не указано'}


       Спасибо за покупку. В ближайшее время с вами свяжется образовательная площадка.

       С уважением,
       Ваша команда KyrsoSphera
       """

    func.send_email_notification(data, body)

    print(message_data)



