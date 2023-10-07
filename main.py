import zoneinfo
from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from regex import regex

import sqlite_utils
from func_utils import get_current_time
from loader import dp


# сначала импортируем обработчики
import handlers.cleaner, handlers.main, handlers.collection, handlers.costume, handlers.admin, handlers.edit

last_check_date = datetime.now()


async def timed_task():
    global last_check_date
    now = datetime.now()
    if now.minute % 5 == 0:
        print(get_current_time(), "[Помогатор] Бот работает исправно, все хорошо!")

    if last_check_date.day != now.day:
        try:
            user_id_admin = sqlite_utils.get_one("config", "value", "name='admin_id'")[0]
            with open('database.db', 'rb') as file:
                await dp.bot.send_document(user_id_admin, file, caption="❤️ Ежедневный дубликат базы данных")
        except Exception as e:
            print(f"An error occurred while sending the file: {e}")
        last_check_date = now


async def on_startup(dp):
    print(get_current_time(), "[Помогатор] Бот запущен!")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(timed_task, "interval", seconds=60)
    scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)