import aiogram
from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageNotModified

from func_utils import get_current_time
from loader import dp
import loader
import sqlite_utils
from aiogram.types import *
import keyboard.collection
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.types import InlineKeyboardMarkup as IKMarkup


@dp.callback_query_handler(lambda q: q.data.startswith("show_collection_id"))
async def show_costume_collection(cbq: CallbackQuery):
    id = 0
    if cbq.data[18:].isdigit():
        id = int(cbq.data[18:])

    kb = keyboard.collection.page_costume_collection(id)
    if id == 0:
        kb.add(IKButton("Вернуться", callback_data="back_menu"))
    else:
        kb.add(IKButton("Вернуться", callback_data="show_collection_page1"))

    if id:
        text = f"<b>Коллекция «{sqlite_utils.get_name_collection(id)[0]}»</b>\n\n"
        text += "Для просмотра костюма выберите соответствующую кнопку снизу"
    else:
        text = "<b>🗂️Архив\n\nДля просмотра костюма выберите соответствующую кнопку снизу</b>"

    # ------------------------------------------------------------------------------------------------------------------

    if sqlite_utils.its_moder(cbq.from_user.id):
        kb.add(IKButton(text="🔽 ПАНЕЛЬ УПРАВЛЕНИЯ 🔽", callback_data="null"))
        kb.add(IKButton(text="Создать костюм", callback_data=f"newCostume_setName_collectionID{id}"))
        if id != 0:
            kb.add(IKButton(text="Удалить коллекцию (костюмы в архив)", callback_data=f"del_collectionID{id}"))
            kb.add(IKButton(text="Удалить коллекцию + костюмы", callback_data=f"del_full_collectionID{id}"))
            text += "\n\n<b>⚙️ Техническая информация</b>"
            text += f'<a href="t.me/zhekahelp_bot?start=collection{id}">Ссылка на коллекцию для клиента</a>\n'
            text += f"costume_collection_id: <code>{id}</code>\n"

    # ------------------------------------------------------------------------------------------------------------------

    await cbq.message.edit_text(text, reply_markup=kb)
    sqlite_utils.set_state(cbq.from_user.id, f"costume_collection_id{id}")


# ======================================================================================================================


@dp.callback_query_handler(lambda q: q.data.startswith("show_collection_page"))
async def show_collection_page(callback_query: CallbackQuery):
    try:
        page = 1

        if callback_query.data[20:].isdigit():
            page = int(callback_query.data[20:])

        await callback_query.message.edit_text(
            text="Выберите коллекцию костюмов",
            reply_markup=keyboard.collection.page_all_collection(page, sqlite_utils.its_moder(callback_query.from_user.id))
        )

        sqlite_utils.set_state(callback_query.from_user.id, f"collection_page{page}")
    except MessageNotModified:
        pass
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {show_collection_page}", f"({callback_query.from_user.mention})", ex)


@dp.callback_query_handler(lambda q: q.data.startswith("show_edit_collection"))
async def show_edit_costume_collection(cbq: CallbackQuery):
    id_collection = int(cbq.data.split("ID")[1].split('_')[0])
    page = int(cbq.data.split("page")[1])
    await cbq.message.edit_text(
        text="Выберите новую коллекцию костюма",
        reply_markup=keyboard.collection.page_all_collection(page, False, id_collection)
    )

# =====================================================================================================================

@dp.callback_query_handler(lambda q: q.data.startswith("new_collection_setName"))
async def new_collection_setName(cbq: CallbackQuery):
    if sqlite_utils.its_moder(cbq.from_user.id) == False:
        loader.bot.answer_callback_query(cbq.id, text="⛔️ Отказано в доступе", show_alert=True)
        return

    text = "<b>Создание новой коллекции</b>\n\nВведите название новой коллекции"
    kb = IKMarkup()
    kb.add(IKButton(text="Назад", callback_data="show_collection_page1"))

    await cbq.message.edit_text(text=text, reply_markup=kb)

    sqlite_utils.set_state(cbq.from_user.id, cbq.data)


@dp.message_handler(lambda m: sqlite_utils.get_state(m.from_user.id) == "new_collection_setName")
async def creat_collection(msg: Message):
    if sqlite_utils.its_moder(msg.from_user.id) == False:
        await msg.answer(text="⛔️ Отказано в доступе")
        return

    if sqlite_utils.unique_collection_name(msg.text) == False:
        await msg.answer(text="⛔️ Такое название коллекции уже есть, выберите другое")
        return

    sqlite_utils.set_collection(msg.text)
    await msg.answer(text="✅ Создана новая коллекций")

    msg_cbq = await msg.answer(text="<i>Загрузка...</i>", parse_mode="HTML")

    cbq = CallbackQuery()
    cbq.data = "show_collection_page1"
    cbq.from_user = msg.from_user
    cbq.message = msg_cbq
    cbq.message.from_user = msg.from_user

    await show_collection_page(callback_query=cbq)

