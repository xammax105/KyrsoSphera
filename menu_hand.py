
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import func as f

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
                                                                        f'Курсов: {answers_count}'
                             )
    except Exception as e:
        print(e)
        await bot.send_message(message.from_user.id, f'👤 Ваш профиль:\n'
                                                     f'Имя: {message.from_user.first_name}\n'
                                                     f'Юзернейм: @{message.from_user.username}\n\n'
                                                     f'Курсов: {answers_count}'

                               )

@router.callback_query(F.data == 'instructions')
async def instructions(message: types.Message):
    await bot.send_message(message.from_user.id, f"📚 Инструкции", reply_markup=kb.keyboard_inst)


@router.callback_query(F.data == 'top')
async def Top(callback_query: types.CallbackQuery):
    # берем топ по интсрукциям
    users_instructions = f.get_users_instructions_count(cur)
    # топ по инструкциям
    inst_keyboard = InlineKeyboardBuilder()
    for user_id, num_instructions in users_instructions:
        user = await bot.get_chat(user_id)
        username = user.username
        button = types.InlineKeyboardButton(text=f"@{username} - {num_instructions} инструкций",
                                            callback_data=f"user_{user_id}")
        inst_keyboard.row(button)
    await bot.send_message(callback_query.message.chat.id,
                               "🏆 Топ пользователей по инструкциям:",
                               reply_markup=inst_keyboard.as_markup())



