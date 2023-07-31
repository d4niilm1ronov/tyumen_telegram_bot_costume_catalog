from datetime import datetime

from aiogram import Bot, Dispatcher, executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from regex import regex

import sqlite_utils
from func_utils import get_current_time
from loader import dp

# сначала импортируем обработчики
import handlers.cleaner, handlers.main, handlers.collection, handlers.costume, handlers.admin, handlers.edit

async def timed_task():
    now = datetime.now()
    if now.minute % 5 == 0:
        print(get_current_time(), "[Помогатор] Бот работает исправно, все хорошо!")

async def on_startup(dp):
    print(get_current_time(), "[Помогатор] Бот запущен!")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(timed_task, "interval", seconds=60)
    scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)