
from aiogram.types import *

import sqlite_utils
from sqlite_utils import its_moder, its_admin


def menu(id_user: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Коллекции", callback_data="open_collection"))
    kb.add(InlineKeyboardButton("Написать нам 👋", url=sqlite_utils.get_contact_manager()))
    if its_moder(id_user):
        kb.add(InlineKeyboardButton("🔽 ПАНЕЛЬ-УПРАВЛЕНИЯ 🔽", callback_data="null"))
        kb.add(InlineKeyboardButton("🗂️ АРХИВ КОСТЮМОВ", callback_data="show_collection_id0"))
    if its_admin(id_user):
        kb.add(InlineKeyboardButton("👑 АДМИН-ПАНЕЛЬ", callback_data="admin_panel"))

    return kb