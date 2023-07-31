import sqlite_utils
import keyboard
from aiogram.types import *
from aiogram.types import InlineKeyboardMarkup as IKMarkup
from aiogram.types import InlineKeyboardButton as IKButton
from loader import dp


limit_show_collection = 5

# ======================================================================================================================




# ======================================================================================================================

def page_all_collection(page, itsAdmin = False, costume_id: int = 0) -> InlineKeyboardMarkup:

    res_inlineKeyboard = InlineKeyboardMarkup()
    count_collection = sqlite_utils.get_count_collection()
    max_count_page = int(count_collection / limit_show_collection) + int(bool(count_collection % limit_show_collection))
    arr_collection = sqlite_utils.get_page_collection(page)
    page = max_count_page if page == 0 else page

    if count_collection == 0:
        return res_inlineKeyboard
    elif page < 1 or page > max_count_page:
        return res_inlineKeyboard

    # Добавление кнопок для открытия страницы коллекци
    for collection in arr_collection:
        if costume_id:
            kb_cb_data = f"costume_edit_input_collection_id{collection[0]}_ID{costume_id}"
        else:
            kb_cb_data = f"show_collection_id{collection[0]}"
        res_inlineKeyboard.add(InlineKeyboardButton(str(collection[1]), callback_data=kb_cb_data))

    # Добавление навигации по каталогу коллекций (при необходимости)
    if (max_count_page > 1):

        page_backNavigationButton: int
        if (page == 1):
            page_backNavigationButton = max_count_page
        else:
            page_backNavigationButton = page - 1

        page_nextNavigationButton: int
        if (page == max_count_page):
            page_nextNavigationButton = 1
        else:
            page_nextNavigationButton = page + 1

        if costume_id:
            res_inlineKeyboard.add(
                IKButton("⬅️", callback_data=f"show_edit_collection_ID{costume_id}_page{page_backNavigationButton}"),
                IKButton(f"{page} из {max_count_page} стр.", callback_data="null"),
                IKButton("➡️", callback_data=f"show_edit_collection_ID{costume_id}_page{page_nextNavigationButton}"),
            )
        else:
            res_inlineKeyboard.add(
                IKButton("⬅️", callback_data=f"show_collection_page{page_backNavigationButton}"),
                IKButton(f"{page} из {max_count_page} стр.", callback_data="null"),
                IKButton("➡️", callback_data=f"show_collection_page{page_nextNavigationButton}"),
            )

    if itsAdmin:
        res_inlineKeyboard.add(InlineKeyboardButton("Добавить коллекцию", callback_data="new_collection_setName"))

    if costume_id == 0:
        res_inlineKeyboard.add(InlineKeyboardButton("Вернуться", callback_data="back_menu"))

    return res_inlineKeyboard





# ======================================================================================================================

def page_costume_collection(id_collection) -> InlineKeyboardMarkup:
    res_inlineKeyboard = InlineKeyboardMarkup()

    arr_costume = sqlite_utils.get_costume_collection(id_collection)

    for costume in arr_costume:
        res_inlineKeyboard.add(InlineKeyboardButton(str(costume[2]), callback_data="show_costume_id"+str(costume[0])))





    return res_inlineKeyboard

# ======================================================================================================================