
from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext

import keyboard as kb
from states import *
import sqlite3
import os
import logging
from conf import TOKEN
import func as f
import re
#
from conf import cur,conn

#
# роутер
router = Router()
bot = Bot(token=TOKEN)




@router.callback_query(lambda a: a.data == 'search')
async def search_for_tags(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback_query.from_user.id, "🔎 Введите ключевое слово, чтобы найти курсы, содержащие его:")
    await state.set_state(RasStates.waiting_for_tag_search)

    @router.message(RasStates.waiting_for_tag_search)
    async def search_tags(message: types.Message, state: FSMContext):
        tag = message.text


        if tag[0] == "#":
            tag = tag[1:]

        cur.execute(f"SELECT * FROM Courses WHERE Description LIKE '%{tag}%' ")
        res = cur.fetchall()

        # Ищем инструкции по тегу
        instructions = res

        # Отправляем результат пользователю
        if instructions:
            for instruction in instructions:
                answer = [
                    [
                        types.InlineKeyboardButton(text=f"✉ Записаться", callback_data=f"reply_{instruction[0]}"),
                        types.InlineKeyboardButton(text="📑 Отзывы",
                                                   callback_data=f"viewAnswer_{instruction[0]}"),
                        types.InlineKeyboardButton(text="Меню", callback_data=f"Menu")
                    ]
                ]

                keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True)
                await message.reply(f"Найден курс:\n"
                                    f"Название: {instruction[1]}\n"
                                    f"Содержание: {instruction[2]}\n"
                                    f"Стоимость: {instruction[4]}", reply_markup=keyboard_answer)
        else:
            await message.reply("По вашему запросу ничего не найдено.",reply_markup=kb.menu_keyboard)
        await state.clear()


instructions_data = {}

# просмотр всех инструкций
@router.callback_query(lambda a: a.data == 'view_instructions')
async def to_sort_callback(message: types.Message, state: FSMContext):
    sort_kb = [

        [
            types.InlineKeyboardButton(text='👥 Весь список', callback_data='View'),
            types.InlineKeyboardButton(text='🆕 Дешевые', callback_data='Date'),
        ]

    ]

    keyboard_sord = types.InlineKeyboardMarkup(inline_keyboard=sort_kb,
                                               resize_keyboard=True,
                                               input_field_placeholder="Фильтр"
                                               )

    await bot.send_message(message.from_user.id, f"Выберите параметр вывода курсов📋", reply_markup=keyboard_sord)

@router.callback_query(F.data == 'Menu')
async def menu(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "📄 Вы покинули этот раздел. Выберите, что вам подходит:",
                           reply_markup=kb.menu_keyboard)


@router.callback_query(F.data == 'Date')
async def date_sort(message: types.Message):
    cur.execute("""
                    SELECT * FROM Courses
                    ORDER BY Cost ASC;
                """)
    all_instructions = cur.fetchall()

    index = 0  # Индекс текущей инструкции пользователя

    instructions_data[message.from_user.id] = {'index': index, 'all_instructions': all_instructions}

    await send_next_instruction(message.from_user.id)


async def send_next_instruction(user_id):
    user_data = instructions_data.get(user_id)
    if user_data:
        index = user_data.get('index')
        all_instructions = user_data.get('all_instructions')
        print(all_instructions)
        if index < len(all_instructions):
            instruction = all_instructions[index]
            print(instruction, '289--------------------------------------------------------')
            instruction_id,Name, Description, Web, Cost = instruction
            user = await bot.get_chat(user_id)
            username = user.username

            answer = [
                [
                    types.InlineKeyboardButton(text="✉ Записаться", callback_data=f"reply_{instruction_id}"),
                    types.InlineKeyboardButton(text="📑 Отзывы",
                                               callback_data=f"viewAnswer_{instruction_id}"),
                    types.InlineKeyboardButton(text="➡ Пропустить", callback_data="skip")
                ]
            ]
            keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True,
                                                         input_field_placeholder="Ты кем будешь, вацок")
            await bot.send_message(user_id,
                                       f"<b>Название:</b> {Name}\nОписание:  <code>{Description}</code>\nСтоисмоть <i>{Cost}</i>",
                                       reply_markup=keyboard_answer,parse_mode='html')
        else:
            await bot.send_message(user_id, "🫡 Вы просмотрели все инструкции.")
    else:
        await bot.send_message(user_id, "Начните сначала, чтобы просмотреть инструкции.")


@router.callback_query(F.data == 'View')
async def view_instructions(message: types.Message):
    cur.execute("""
                    SELECT * FROM Courses
            """)
    all_instructions = cur.fetchall()
    index = 0  # Индекс текущей инструкции пользователя
    instructions_data[message.from_user.id] = {'index': index, 'all_instructions': all_instructions}
    await send_next_instruction(message.from_user.id)



@router.callback_query(lambda a: a.data == 'skip')
async def skip_instruction(message: types.Message):
    user_id = message.from_user.id

    user_data = instructions_data.get(user_id)
    if user_data:
        index = user_data.get('index')
        instructions_data[user_id]['index'] = index + 1

        await send_next_instruction(user_id)
    else:
        await bot.send_message(user_id, "Начните сначала, чтобы просмотреть инструкции.")

@router.callback_query(lambda c: c.data.startswith('viewAnswer_'))
async def process_add_rewiev(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[1]
    cur.execute("SELECT * FROM Review WHERE Id_cours=?", (cont_1,))
    res = cur.fetchall()
    if len(res) > 0:
        for review in res:
            formatted_review = f"<b>Отзыв:</b> {review[0]}"
            await bot.send_message(callback_query.from_user.id, formatted_review, parse_mode="HTML")
    else:
        await bot.send_message(callback_query.from_user.id, "Тут нет отзывов")




