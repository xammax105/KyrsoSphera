
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

        cur.execute(f"SELECT * FROM Instructions WHERE tags LIKE '%{tag}%' AND is_active = 1")
        res = cur.fetchall()

        # Ищем инструкции по тегу
        instructions = res

        # Отправляем результат пользователю
        if instructions:
            for instruction in instructions:
                answer = [
                    [
                        types.InlineKeyboardButton(text="Ответить", callback_data=f"reply_{instruction[0]}"),
                        types.InlineKeyboardButton(text="Посмотреть ответы", callback_data="viewAnswer")
                    ],
                    [types.InlineKeyboardButton(text="Отдать голос", callback_data=f"voteQuestion_{instruction[0]}")]
                ]

                keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True)
                await message.reply(f"Найдена инструкция:\n"
                                    f"Название: {instruction[1]}\n"
                                    f"Содержание: {instruction[2]}\n"
                                    f"Автор: @{instruction[4]}", reply_markup=keyboard_answer)
        else:
            await message.reply("По вашему запросу ничего не найдено.")
        await state.clear()

instructions_data = {}

# просмотр всех инструкций
@router.callback_query(lambda a: a.data == 'view_instructions')
async def to_sort_callback(message: types.Message, state: FSMContext):
    sort_kb = [

        [
            types.InlineKeyboardButton(text='👥 Популярные', callback_data='View'),
            types.InlineKeyboardButton(text='🆕 Новые', callback_data='Date'),
        ]

    ]

    keyboard_sord = types.InlineKeyboardMarkup(inline_keyboard=sort_kb,
                                               resize_keyboard=True,
                                               input_field_placeholder="Фильтр"
                                               )

    await bot.send_message(message.from_user.id, f"Выберите параметр вывода инструкций📋", reply_markup=keyboard_sord)


@router.callback_query(F.data == 'Date')
async def date_sort(message: types.Message):
    cur.execute("""
                    SELECT author_id, content, title, id, addition_date FROM Instructions
                    WHERE is_active > 0
                    ORDER BY addition_date DESC;
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
            author_id, content, title, instruction_id, vote_count = instruction
            user = await bot.get_chat(user_id)
            username = user.username
            if vote_count is None:
                votes = 0
            else:
                votes = vote_count
            answer = [
                [
                    types.InlineKeyboardButton(text="✉ Ответить", callback_data=f"reply_{instruction_id}"),
                    types.InlineKeyboardButton(text="📑 Посмотреть ответы",
                                               callback_data=f"viewAnswer_{instruction_id}"),
                    types.InlineKeyboardButton(text="➡ Пропустить", callback_data="skip")
                ],
                [types.InlineKeyboardButton(text="👍 Отдать голос", callback_data=f"voteQuestion_{instruction_id}")]
            ]
            keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True,
                                                         input_field_placeholder="Ты кем будешь, вацок")
            if content.isdigit():
                message_id = int(content)
                await bot.copy_message(user_id, from_chat_id=author_id, message_id=message_id, caption=title)
                await bot.send_message(user_id,
                                       f"{instruction_id}\n Автор @{username} \nДата Создания  {votes}",
                                       reply_markup=keyboard_answer)
            else:
                await bot.send_message(user_id,
                                       f"{instruction_id} \n{title}: {content}\n Количество голосов {votes}",
                                       reply_markup=keyboard_answer)
        else:
            await bot.send_message(user_id, "🫡 Вы просмотрели все инструкции.")
    else:
        await bot.send_message(user_id, "Начните сначала, чтобы просмотреть инструкции.")


@router.callback_query(F.data == 'View')
async def view_instructions(message: types.Message):
    cur.execute("""
                    SELECT i.author_id, i.content, i.title, i.id, (iv.user) as votes_count
                    FROM Instructions i
                    LEFT JOIN InstructionsVotes iv ON i.id = iv.instruction_id
                    WHERE i.is_active > 0
                    GROUP BY i.id
                    ORDER BY votes_count DESC;
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
            author_id, content, title, instruction_id, vote_count = instruction
            user = await bot.get_chat(user_id)
            username = user.username
            if vote_count is None:
                votes = 0
            else:
                votes = vote_count

            answer = [
                [
                    types.InlineKeyboardButton(text="✉ Ответить", callback_data=f"reply_{instruction_id}"),
                    types.InlineKeyboardButton(text="📑 Посмотреть ответы",
                                               callback_data=f"viewAnswer_{instruction_id}"),
                    types.InlineKeyboardButton(text="➡ Пропустить", callback_data="skip")
                ],
                [types.InlineKeyboardButton(text="👍 Отдать голос", callback_data=f"voteQuestion_{instruction_id}")]
            ]

            keyboard_answer = types.InlineKeyboardMarkup(inline_keyboard=answer, resize_keyboard=True,
                                                         input_field_placeholder="Ты кем будешь, вацок")

            if content.isdigit():
                message_id = int(content)
                await bot.copy_message(user_id, from_chat_id=author_id, message_id=message_id, caption=title,
                                       reply_markup=keyboard_answer)
                # await bot.send_message(user_id,
                #                        f"{instruction_id}\n author @{username} \nКоличество голосов {votes}",
                #                        reply_markup=keyboard_answer)
            else:

                await bot.send_message(user_id, f"{instruction_id} \n{title}: {content}\n Количество голосов {votes}",
                                       reply_markup=keyboard_answer)
        else:
            await bot.send_message(user_id, "🫡 Вы просмотрели все инструкции.")
    else:
        await bot.send_message(user_id, "Начните сначала, чтобы просмотреть инструкции.")


@router.callback_query(lambda a: a.data == 'skip')
async def skip_instruction(message: types.Message):
    user_id = message.from_user.id

    user_data = instructions_data.get(user_id)
    if user_data:
        index = user_data.get('index')
        instructions_data[user_id]['index'] = index + 1

        await f.send_next_instruction(user_id, bot, instructions_data)
    else:
        await bot.send_message(user_id, "Начните сначала, чтобы просмотреть инструкции.")





@router.callback_query(lambda c: c.data.startswith('voteQuestion'))
async def vote_question(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    cont_1 = callback_query.data.split('_')[1]
    print(cont_1)
    ans_id = int(cont_1)
    cur.execute('UPDATE Users SET instructions = instructions + 1 WHERE user_id = ?', (user_id,))

    # Check if the answer has been already rated by the user
    cur.execute('SELECT * FROM InstructionsVotes WHERE instruction_id = ?', (ans_id,))
    existing_vote = cur.fetchone()

    if existing_vote:
        # If the user has already voted for this answer, update the user's vote count
        cur.execute('UPDATE InstructionsVotes SET user = user + 1 WHERE instruction_id = ?', (ans_id,))
    else:
        last_id = cur.execute('SELECT MAX(id) FROM InstructionsVotes').fetchone()

        if last_id[0] is None:
            id = 1
        else:
            id = last_id[0] + 1
        # If the user has not voted for this answer yet, insert a new vote record
        cur.execute('INSERT INTO InstructionsVotes (id,user,instruction_id) VALUES (?,1, ?)',
                    (id, ans_id))

    conn.commit()
    await bot.answer_callback_query(callback_query.id, "✅ Ваш голос засчитан")