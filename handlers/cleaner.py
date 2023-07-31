from aiogram import Dispatcher

import sqlite_utils
import handlers
from filters.cleaner import cleaner_image, cleaner_image_msg
from aiogram.types import *
from loader import dp


@dp.callback_query_handler(cleaner_image())
async def clean_photos_costume(cbq: CallbackQuery):
    # Эта функция нужна для того, чтобы удалять медиагруппу фотографий костюма,
    # при просмотре в def show_costume, т.к. она идет отдельным сообщением.
    #
    # Удаление происходит через фильтр этого обработчика
    #
    # Надеюсь здесь будет более элегантное решение :-)
    pass


@dp.message_handler(cleaner_image_msg())
async def clean_photos_costume(msg: Message):
    # Также ловлю /start чтобы почистить
    pass

