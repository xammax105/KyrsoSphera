
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import func as f
import kyrs_hand
import keyboard as kb
from states import *
import sqlite3
import os
import logging
from conf import TOKEN, admin_token
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
    course_keyboard = InlineKeyboardBuilder()
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