from aiogram import Bot, Router, types, F
from aiogram.fsm.context import FSMContext

import keyboard as kb
from states import *
import sqlite3
import os
import logging
from conf import TOKEN, admin_token
import func as f
from conf import cur,conn

# роутер
router = Router()
bot = Bot(token=TOKEN)


@router.message(F.text.lower() == 'выйти')
async def leave(message: types.Message):
    await bot.send_message(message.from_user.id, "📄 Вы покинули этот раздел. Выберите, что вам подходит:",
                           reply_markup=kb.kb_keyboard)


@router.message(F.text.lower() == 'рассылка')
async def admin_ras(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите сообщение для рассылки🧐:')
    await state.set_state(RasStates.waiting_for_message)

@router.message(RasStates.waiting_for_message)
async def ras(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Рассылка создана!')
    await broadcast_message(f"🔔 Уведомление от администратора: {message.text}")
    await state.clear()


async def broadcast_message(message: types.Message):
    # Функция для рассылки сообщения всем пользователям бота.
    cur.execute("SELECT User_id FROM Users")
    user_ids = cur.fetchall()

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id[0], text=message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

#логика добавления курса

@router.message(F.text.lower() == 'добавить курс')
async def add_course(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Введите название курса:')
    await state.set_state(RasStates.AddCourseStates)

    @router.message(RasStates.AddCourseStates)
    async def kyrs(message: types.Message, state: FSMContext):
        name_kyrs = message.text
        await state.update_data(name_kyrs=name_kyrs)

        await bot.send_message(message.from_user.id, 'Введите описание курса:')
        await state.set_state(RasStates.AddDescription)

    @router.message(RasStates.AddDescription)
    async def description(message: types.Message, state: FSMContext):
        description = message.text
        await state.update_data(description=description)
        await bot.send_message(message.from_user.id, 'Введите ссылку курса:')
        await state.set_state(RasStates.AddSourseState)

    @router.message(RasStates.AddSourseState)
    async def Url(message: types.Message, state: FSMContext):
        sourse = message.text
        await state.update_data(sourse=sourse)
        await bot.send_message(message.from_user.id, 'Введите стоимость курса:')
        await state.set_state(RasStates.AddCostState)

    @router.message(RasStates.AddCostState)
    async def cost(message: types.Message, state: FSMContext):
        cost = message.text
        await state.update_data(cost=cost)

        data = await state.get_data()
        print(data)
        name_kyrs = data.get('name_kyrs')
        description = data.get('description')
        sourse = data.get('sourse')
        cost = data.get('cost')

        print(name_kyrs,description,sourse,cost)
        try:
            cur.execute("INSERT INTO Courses (Name, Description, Web, Cost) VALUES (?, ?, ?, ?)",
                    (name_kyrs, description, sourse, cost))
            conn.commit()
            await state.clear()
            await bot.send_message(message.from_user.id, 'Добавил брат', reply_markup=kb.get_admin_keyboard())
        except:
            await state.clear()
            await bot.send_message(message.from_user.id, 'Марасишь брат', reply_markup=kb.get_admin_keyboard())
#работа с курсами

@router.message(F.text.lower() == 'редактировать курсы')
async def select_edit(callback_query: types.CallbackQuery):
        men_kb = [
            [
                types.InlineKeyboardButton(text='Изменить Курсы ✍️', callback_data='editinstr'),

            ]
        ]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=men_kb,
                                              resize_keyboard=True,
                                              input_field_placeholder="Выберите действие"
                                              )
        await bot.send_message(callback_query.from_user.id, f"Для потверждения нажмите кнопку 🛠️", reply_markup=keyboard)

@router.callback_query(lambda a: a.data.startswith('editinstr'))
async def process_edit_answer_callback(callback_query: types.CallbackQuery, state: FSMContext):
    offset = int(callback_query.data.split('_')[-1]) if '_' in callback_query.data else 0
    sql_query = f"SELECT * FROM Courses"
    cur.execute(sql_query)
    answers = cur.fetchall()
    await show_course(callback_query, answers, offset)

@router.callback_query(lambda c: c.data.startswith('skipe'))
async def process_skip_callback(callback_query: types.CallbackQuery, state: FSMContext):
    offset = int(callback_query.data.split('_')[-1])
    sql_query = f"SELECT * FROM Courses"
    cur.execute(sql_query)
    answers = cur.fetchall()
    await show_course(callback_query, answers, offset)

@router.callback_query(lambda c: c.data.startswith('Delete_instr'))
async def process_delete_callback(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[2]
    ans_id = int(cont_1)
    cur.execute("DELETE FROM Courses WHERE ID = ?", (ans_id,))
    conn.commit()
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
    await bot.answer_callback_query(callback_query.id, "Запись удалена.")

    sql_query = f"SELECT * FROM Courses"
    cur.execute(sql_query)
    answers = cur.fetchall()
    offset = int(callback_query.data.split('_')[3]) if '_' in callback_query.data else 0
    await show_course(callback_query, answers, offset)

async def show_course(callback_query, answers, offset):
    if offset < len(answers):
        answer = answers[offset]
        idd = answer[0]
        answer_title = answer[1]
        answer_text = answer[2]
        answer_web = answer[3]
        answer_cost = answer[4]

        more_kb = [
            [
                types.InlineKeyboardButton(text='Редактировать', callback_data=f'EditInsrtact_{idd}'),
                types.InlineKeyboardButton(text='Удалить', callback_data=f'Delete_instr_{idd}_{offset}'),
                types.InlineKeyboardButton(text='Пропустить', callback_data=f'skipe_{offset+1}')
            ]
        ]
        upd_answer = types.InlineKeyboardMarkup(inline_keyboard=more_kb)

        await bot.send_message(callback_query.from_user.id,
                               f"Заголовок: {answer_title}\nСодержание: {answer_text} \nСсылка: {answer_web}\nСтоимость: {answer_cost} ",
                               reply_markup=upd_answer)
        new_offset = offset + 1
        if new_offset < len(answers):
            await bot.answer_callback_query(callback_query.id,
                                            f"Следующий курс ({new_offset + 1}/{len(answers)})")
    else:
        await bot.send_message(callback_query.from_user.id, "Все курсы просмотрены.")


@router.callback_query(lambda c: c.data.startswith('EditInsrtact'))
async def process_edit_answer_callback(callback_query: types.CallbackQuery, state: FSMContext):
    cont_1 = callback_query.data.split('_')[1]
    ans_id = int(cont_1)
    await state.update_data(ans_id=ans_id)
    await bot.send_message(callback_query.from_user.id, 'Введите название курса:')
    await state.set_state(RasStates.AddNewCourseStates)

    @router.message(RasStates.AddNewCourseStates)
    async def kyrs(message: types.Message, state: FSMContext):
        name_kyrs = message.text
        await state.update_data(name_kyrs=name_kyrs)
        print(name_kyrs)

        await bot.send_message(message.from_user.id, 'Введите описание курса:')
        await state.set_state(RasStates.AddNewDescription)
    @router.message(RasStates.AddNewDescription)
    async def description(message: types.Message, state: FSMContext):
        description = message.text
        await state.update_data(description=description)
        print(description)
        await bot.send_message(message.from_user.id, 'Введите ссылку курса:')
        await state.set_state(RasStates.AddNewSourseState)


    @router.message(RasStates.AddNewSourseState)
    async def url(message: types.Message,state: FSMContext):
        sourse = message.text
        await state.update_data(sourse=sourse)
        print(sourse)

        await bot.send_message(message.from_user.id, 'Введите стоимость курса:')
        await state.set_state(RasStates.AddNewCostState)

    @router.message(RasStates.AddNewCostState)
    async def cost(message: types.Message, state: FSMContext):
        cost = message.text
        await state.update_data(cost=cost)

        data = await state.get_data()
        name_kyrs = data.get('name_kyrs')
        description = data.get('description')
        sourse = data.get('sourse')
        cost = data.get('cost')
        ans_id = data.get('ans_id')
        print(name_kyrs, description, sourse, cost, ans_id)
        query = """UPDATE Courses
                   SET Name = ?, Description = ?, Web = ?, Cost = ?
                   WHERE ID = ?;"""
        try:
            cur.execute(query, (name_kyrs, description, sourse, cost, ans_id))
            conn.commit()
            await state.clear()
            await bot.send_message(message.from_user.id, 'Успешно обновлено')
        except Exception as e:
            await bot.send_message(message.from_user.id, f'Ошибка: {e}')
            await state.clear()

