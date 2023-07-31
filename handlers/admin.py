import json

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from regex import regex

from filters.all_filters import IsAdmin
from func_utils import get_current_time
from handlers.edit import arr_del_msg
from loader import dp
import sqlite_utils
from aiogram.types import *
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.types import InlineKeyboardMarkup as IKMarkup

from state import admin

arr_timeout_warning_del_collection = {}
arr_timeout_warning_del_full_collection = {}
arr_timeout_warning_del_costume = {}

warning_del_collection = "⚠️ ВНИМАНИЕ!\n\nУдаляя таким образом коллекцию Вы БЕЗВОЗВРАТНО стираете ее из списка, СОХРАНЯЯ КОСТЮМЫ В АРХИВ (🗂️).\n\nИНСТРУКЦИЯ\nЕсли уверены в своих действиях, нажмите еще раз на кнопку."
warning_del_full_collection = "⚠️ ВНИМАНИЕ!\n\nУдаляя таким образом коллекцию Вы БЕЗВОЗВРАТНО УДАЛЯЕТЕ И КОСТЮМЫ.\n\nИНСТРУКЦИЯ\nЕсли уверены в своих действиях, нажмите еще раз на кнопку."
warning_del_costume = "⚠️ ВНИМАНИЕ!\n\nПосле этого Вы БЕЗВОЗВРАТНО УДАЛЯЕТЕ все данные о костюме\n\nИНСТРУКЦИЯ\nЕсли уверены в своих действиях, нажмите еще раз на кнопку."


@dp.callback_query_handler(lambda c: c.data == "close_admin_panel")
async def close_admin_panel(cbq: CallbackQuery):
    await cbq.message.delete()


@dp.callback_query_handler(lambda c: c.data.startswith("del_collectionID"))
async def del_collectionID(cbq: CallbackQuery):
    id_user = cbq.from_user.id

    # Предупреждение об удалении
    if arr_timeout_warning_del_collection.get(id_user) is None:
        await cbq.answer(warning_del_collection, True)
        arr_timeout_warning_del_collection[id_user] = datetime.now() + timedelta(minutes=2)
        return
    elif arr_timeout_warning_del_collection[id_user] < datetime.now():
        await cbq.answer(warning_del_collection, True)
        arr_timeout_warning_del_collection[id_user] = datetime.now() + timedelta(minutes=2)
        return

    # проверка cbq data
    if cbq.data.split("del_collectionID")[1].isdigit() is False:
        await cbq.message.answer("⛔️ Ошибка (#28gyh79ef34). Воспользуйтесь /start и повторите попытку")
        return

    id_collection = int(cbq.data.split("del_collectionID")[1])
    name_collection = sqlite_utils.get_name_collection(id_collection)[0]
    count_collection = sqlite_utils.remove_collection(id_collection)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Посмотреть коллекции", callback_data="show_collection_page1"))
    kb.add(InlineKeyboardButton("Посмотреть костюмы", callback_data="show_collection_id0"))
    kb.add(InlineKeyboardButton("Открыть меню", callback_data="back_menu"))

    if count_collection:
        link = 'Ее костюмы перемещены <a href="t.me/zhekahelp_bot?start=collection0">сюда</a>.'
    else:
        link = ''

    await cbq.message.edit_text(f"🗑 Коллекция <b>«{name_collection}»</b> удалена. {link}", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("del_full_collectionID"))
async def del_full_collectionID(cbq: CallbackQuery):
    id_user = cbq.from_user.id

    # Предупреждение об удалении
    if arr_timeout_warning_del_full_collection.get(id_user) is None:
        await cbq.answer(warning_del_full_collection, True)
        arr_timeout_warning_del_full_collection[id_user] = datetime.now() + timedelta(minutes=2)
        return
    elif arr_timeout_warning_del_full_collection[id_user] < datetime.now():
        await cbq.answer(warning_del_full_collection, True)
        arr_timeout_warning_del_full_collection[id_user] = datetime.now() + timedelta(minutes=2)
        return

    arr_timeout_warning_del_full_collection[id_user] = datetime.now() + timedelta(minutes=2)

    # проверка cbq data
    if cbq.data.split("del_full_collectionID")[1].isdigit() is False:
        await cbq.message.answer("⛔️ Ошибка (#Z123978V). Воспользуйтесь /start и повторите попытку")
        return

    id_collection = int(cbq.data.split("del_full_collectionID")[1])
    name_collection = sqlite_utils.get_name_collection(id_collection)[0]
    sqlite_utils.remove_full_collection(id_collection)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Посмотреть коллекции", callback_data="show_collection_page1"))
    kb.add(InlineKeyboardButton("Открыть меню", callback_data="back_menu"))

    await cbq.message.edit_text(f"🔥 Коллекция <b>«{name_collection}»</b> и ее костюмы удалены.", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("del_costumeID"))
async def del_costumeID(cbq: CallbackQuery):
    id_user = cbq.from_user.id

    # Предупреждение об удалении
    if arr_timeout_warning_del_costume.get(id_user) is None:
        await cbq.answer(warning_del_costume, True)
        arr_timeout_warning_del_costume[id_user] = datetime.now() + timedelta(minutes=2)
        return
    elif arr_timeout_warning_del_costume[id_user] < datetime.now():
        await cbq.answer(warning_del_costume, True)
        arr_timeout_warning_del_costume[id_user] = datetime.now() + timedelta(minutes=2)
        return

    arr_timeout_warning_del_costume[id_user] = datetime.now() + timedelta(minutes=2)

    # проверка cbq data
    if cbq.data.split("del_costumeID")[1].isdigit() is False:
        await cbq.message.answer("⛔️ Ошибка (#X203X18). Воспользуйтесь /start и повторите попытку")
        return

    id_costume = int(cbq.data.split("del_costumeID")[1])

    costume = sqlite_utils.get_costume(id_costume)
    id_collection = int(costume[1])
    name_collection = costume[2]
    sqlite_utils.remove_costume(id_costume)

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(f"Открыть {name_collection}", callback_data=f"show_collection_id{id_collection}"))
    kb.add(InlineKeyboardButton("Открыть коллекции", callback_data="show_collection_page1"))
    kb.add(InlineKeyboardButton("Открыть костюмы", callback_data="show_collection_id0"))
    kb.add(InlineKeyboardButton("Открыть меню", callback_data="back_menu"))

    await cbq.message.edit_text(f"🗑 Костюм <b>«{name_collection}»</b> успешно удален!", reply_markup=kb)


# =====================================================================================================================

@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "admin_panel", state="*")
async def open_admin_panel(cbq: CallbackQuery, state: FSMContext):
    try:
        await state.finish()
        text = "Выберите действие"
        kb = IKMarkup()
        kb.add(IKButton("Добавить модератора", callback_data="admin_add_moderator"))
        kb.add(IKButton("Удалить модератора", callback_data="admin_del_moderator"))
        kb.add(IKButton("Изменить ссылку менеджера", callback_data="admin_edit_contact"))
        kb.add(IKButton("Назад", callback_data="back_menu"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {open_admin_panel}", f"({cbq.from_user.mention})", ex)


# =====================================================================================================================


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "admin_add_moderator")
async def admin_add_moderator(cbq: CallbackQuery, state: FSMContext):
    try:
        await admin.Panel.wait_add_moderator.set()
        text = "Введите ID нового модератора"
        kb = IKMarkup()
        kb.add(IKButton("Как получить ID?", callback_data="help_admin_add_moderator"))
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {admin_add_moderator}", f"({cbq.from_user.mention})", ex)


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "help_admin_add_moderator", state="*")
async def help_admin_add_moderator(cbq: CallbackQuery, state: FSMContext):
    try:
        text = "Введите ID нового модератора\n\n<b>Как узнать ID модератора?</b>\n"
        text += "<code>Вариант 1. </code>Переслать любое сообщение из диалога с модератором "
        text += "в <a href='t.me/getidsbot'>GetIDs Bot</a>. Вы получите сообщение, где будет указан <code>id</code>;\n"
        text += "<code>Вариант 2. </code>Модер сам напишет в <a href='t.me/getidsbot'>GetIDs Bot</a> "
        text += "и отправит вам полученый ID."
        kb = IKMarkup()
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {help_admin_add_moderator}", f"({cbq.from_user.mention})", ex)


@dp.message_handler(IsAdmin(), lambda m: m.text.isdigit(), state=admin.Panel.wait_add_moderator)
async def input_admin_add_moderator(msg: Message, state: FSMContext):
    try:
        kb = IKMarkup()
        if sqlite_utils.its_moder(msg.text):
            kb.add(IKButton("Как получить ID?", callback_data="help_admin_add_moderator"))
            kb.add(IKButton("Назад", callback_data="admin_panel"))
            text = "😳 Пользователь уже назначен модератором (или является администратором)"
        else:
            sqlite_utils.add_moder(msg.from_user.id)
            kb.add(IKButton("От", callback_data="admin_panel"))
            text = f"✅ Модератор {sqlite_utils.get_username(msg.from_user.id)} добавлен!"
            await state.finish()
        await msg.answer(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {input_admin_add_moderator}", f"({msg.from_user.mention})", ex)


# =====================================================================================================================


@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "admin_del_moderator")
async def admin_del_moderator(cbq: CallbackQuery, state: FSMContext):
    try:
        text = "Выберите модератора, которого нужно удалить"
        kb = IKMarkup()

        for id_moder in json.loads(sqlite_utils.get_one("config", "value", "name = 'arr_moder_id'", True)[0]):
            kb.add(IKButton(sqlite_utils.get_username(id_moder), callback_data=f"admin_del_moderator_id{id_moder}"))

        if len(kb.inline_keyboard) == 0:
            text = "У вас пока что нету ни одного модератора (если не считать вас)..."
            kb.add(IKButton("Добавить модератора", callback_data="admin_add_moderator"))
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {admin_del_moderator}", f"({cbq.from_user.mention})", ex)


@dp.callback_query_handler(IsAdmin(), lambda c: c.data.startswith("admin_del_moderator_id"))
async def admin_del_moderator_id(cbq: CallbackQuery, state: FSMContext):
    try:
        sqlite_utils.del_moder(int(cbq.data.split("admin_del_moderator_id")[1]))
        text = "✅ Модератор удален!"
        kb = IKMarkup()
        kb.add(IKButton("Удалить еще модератора", callback_data="admin_del_moderator"))
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {admin_del_moderator_id}", f"({cbq.from_user.mention})", ex)


# =====================================================================================================================

@dp.callback_query_handler(IsAdmin(), lambda c: c.data == "admin_edit_contact")
async def admin_edit_contact(cbq: CallbackQuery, state: FSMContext):
    try:
        await admin.Panel.wait_edit_contact.set()
        text = "<b>Введите адрес (@username) пользователя Telegram или "
        text += "ссылку на контакт с менеджером с другого ресурса (например, ВКонтакте).</b>\n\n"
        text += "При нажатии на кнопку, наподобие <code>Написать нам</code>, клиент будет переадрессован на адрес, "
        text += "который вы можете указать прямо сейчас"
        kb = IKMarkup()
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        await cbq.message.edit_text(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {admin_edit_contact}", f"({cbq.from_user.mention})", ex)


@dp.message_handler(IsAdmin(), state=admin.Panel.wait_edit_contact)
async def input_admin_edit_contact(msg: Message, state: FSMContext):
    try:
        stroka = msg.text
        res_url = ""
        text = "✅ Ссылка на контакт c менеджером изменена!"
        kb = IKMarkup()
        kb.add(IKButton("Назад", callback_data="admin_panel"))
        if regex.match(r'(https?://|www.|)t.me/[A-Za-z0-9]', stroka):
            res_url = "t.me/" + stroka.split('/').pop()
        elif regex.match(r'@[A-Za-z0-9]', stroka):
            res_url = "t.me/" + stroka[1:]
        elif regex.match(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", stroka):
            res_url = stroka
        if res_url == "":
            text = "⁉️ Ссылка не распознана. Проверьте корректность и повторите попытку"
        else:
            sqlite_utils.update("config", "value", res_url, "name = 'contact_url'")
            await state.finish()
        await msg.answer(text, reply_markup=kb)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {input_admin_edit_contact}", f"({msg.from_user.mention})", ex)

# =====================================================================================================================
