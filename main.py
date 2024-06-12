import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.fsm.context import FSMContext
import logging
import keyboard as kb
import menu_hand, kyrs_hand,admin
from conf import TOKEN
import func as f
from aiogram.filters import CommandStart
from states import *
from conf import cur, conn

async def main():
    # подключаем роутеры
    dp.include_router(admin.router)

    dp.include_router(menu_hand.router)
    dp.include_router(kyrs_hand.router)




    # запускаем поллинг
    loop = asyncio.get_event_loop()

    await bot.delete_webhook(drop_pending_updates=True)  # пропуск обновлений
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    cur.execute("SELECT CASE WHEN EXISTS (SELECT 1 FROM Users WHERE User_id = ?) THEN 1 ELSE 0 END", message.from_user.id)
    in_base_res = cur.fetchone()[0]
    if in_base_res == 0:

        await message.reply(f"Привет, {message.from_user.first_name} 🙋‍♂️! Я твой новый <i>чат-бот</i>. "
                         "Меня создали, чтобы помочь в изучении новых курсов"
                        "с комфортом. Давай начнем!😉", parse_mode='HTML',
                        reply_markup=kb.kb_keyboard)
        f.add_user('NUll', 'NUll', message.from_user.username, message.from_user.id, cur, conn)
    elif in_base_res == 1:
        await bot.send_message(message.from_user.id, f"🗃 Меню:", reply_markup=kb.menu_keyboard)

# бот и диспетчер


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)  # логирование
    asyncio.run(main())

