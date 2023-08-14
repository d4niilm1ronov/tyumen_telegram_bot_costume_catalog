import json

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from loader import dp, bot
import sqlite_utils
from filters.all_filters import IsModerator
from func_utils import get_current_time
from keyboard.collection import page_all_collection
from aiogram.types import *
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.types import InlineKeyboardMarkup as IKMarkup
from datetime import datetime, timedelta

from state.moderator import EditCostume

arr_del_msg: dict = {}


@dp.message_handler(IsModerator(), state=EditCostume.wait_new_name)
async def costume_edit_input_name(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        costume_id = data['costume_id']
    user_id = msg.from_user.id
    if arr_del_msg.get(user_id) is not None:
        await bot.delete_message(user_id, arr_del_msg[user_id])
        arr_del_msg[user_id] = None
    costume = sqlite_utils.get_costume(costume_id)
    if costume is None:
        await msg.answer(f"⁉️ Ошибка. Данный костюм (id{costume_id}) не найден в Базе Данных")
        await state.finish()
        return
    kb = IKMarkup()
    kb.add(IKButton("Назад к костюму", callback_data=f"show_costume_id{costume_id}"))
    if not sqlite_utils.unique_costume_name(msg.text):
        new_msg = await msg.answer("⛔️ Такое название уже есть", reply_markup=kb)
        arr_del_msg[user_id] = new_msg.message_id
    elif len(msg.text.encode("utf-8")) > 64:
        new_msg = await msg.answer("⛔️ Длина названия слишком длинное", reply_markup=kb)
        arr_del_msg[user_id] = new_msg.message_id
    else:
        sqlite_utils.update("costume", "name", msg.text, f"id_costume={costume_id}")
        await msg.answer("✅ Новое название для костюма установлено!", reply_markup=kb)
        await state.finish()
    await msg.delete()


@dp.message_handler(IsModerator(), state=EditCostume.wait_new_description)
async def costume_edit_input_description(msg: Message, state: FSMContext):
    async with state.proxy() as data:
        costume_id = data['costume_id']
    user_id = msg.from_user.id
    if arr_del_msg.get(user_id) is not None:
        await bot.delete_message(user_id, arr_del_msg[user_id])
        arr_del_msg[user_id] = None
    costume = sqlite_utils.get_costume(costume_id)
    if costume is None:
        await msg.answer(f"⁉️ Ошибка. Данный костюм (id{costume_id}) не найден в Базе Данных")
        await state.finish()
        return
    kb = IKMarkup()
    kb.add(IKButton("Назад к костюму", callback_data=f"show_costume_id{costume_id}"))
    sqlite_utils.update("costume", "description", msg.parse_entities(), f"id_costume={costume_id}")
    await msg.answer("✅ Новое описание для костюма установлено!", reply_markup=kb)
    await state.finish()
    await msg.delete()



@dp.message_handler(IsModerator(), content_types='photo', state=EditCostume.wait_new_photo)
async def costume_edit_add_photo(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    async with state.proxy() as data:
        costume_id = data['costume_id']
    costume = sqlite_utils.get_costume(costume_id)
    arr_photo: list[str] = json.loads(costume[4])
    if arr_del_msg.get(user_id) is not None:
        await bot.delete_message(user_id, arr_del_msg[user_id])
        arr_del_msg[user_id] = None
    kb = IKMarkup()
    data_ikb = f"costume_edit_photo_ID{costume_id}" if len(arr_photo) else f"show_costume_id{costume_id}"
    kb.add(IKButton("Отмена", callback_data=data_ikb))
    if len(arr_photo) >= 10:
        await msg.answer("⛔️ У костюма не может быть больше 10 фотографий", reply_markup=kb)
        return
    arr_photo.append(msg.photo.pop().file_id)
    sqlite_utils.update("costume", "json_arr_img", json.dumps(arr_photo), f"id_costume = {costume_id}")
    new_msg = await msg.answer("<i>Загрузка...</i>")
    new_cbq = CallbackQuery()
    new_cbq.message, new_cbq.from_user = new_msg, msg.from_user
    new_cbq.data = f"costume_edit_photo_num{len(arr_photo)}_ID{costume_id}"
    await msg.delete()
    await state.finish()
    await costume_edit_photo(new_cbq, state)


@dp.callback_query_handler(IsModerator(), lambda c: c.data.startswith("costume_edit_photo"))
async def costume_edit_photo(cbq: CallbackQuery, state: FSMContext):
    try:
        user_id = cbq.from_user.id
        costume_id = int(cbq.data.split("ID")[1])
        costume = sqlite_utils.get_costume(costume_id)
        if costume is None:
            await cbq.answer(f"⁉️ Ошибка. Костюма (id{costume_id}) больше нету в базе данных", show_alert=True)
            return
        arr_photo: list[str] = json.loads(costume[4])
        if cbq.data.find("input") != -1:
            if len(arr_photo) >= 10:
                await cbq.answer("🚫 Ограничение на максимальное кол-во фотографий у костюма: 10", show_alert=True)
                return
            else:
                kb = IKMarkup()
                data_ikb = f"costume_edit_photo_ID{costume_id}" if len(arr_photo) else f"show_costume_id{costume_id}"
                kb.add(IKButton("Отмена", callback_data=data_ikb))
                new_msg = await bot.send_message(user_id, "Отправьте фото, которое хотите добавить", reply_markup=kb)
                arr_del_msg[user_id] = new_msg.message_id
                async with state.proxy() as data:
                    await EditCostume.wait_new_photo.set()
                    data['costume_id'] = costume_id
                await cbq.message.delete()
                return

        elif cbq.data.find("del") != -1:
            num = int(cbq.data.split("num")[1].split('_')[0])
            arr_photo.pop(num - 1)
            sqlite_utils.update("costume", "json_arr_img", json.dumps(arr_photo), f"id_costume = {costume_id}")
            await cbq.answer("🗑️ Фото удалено")
            if num <= len(arr_photo) and len(arr_photo):
                pass
            elif len(arr_photo):
                cbq.data = cbq.data.replace(f"num{num}", "num1")
            else:
                kb = IKMarkup()
                kb.add(IKButton("Добавить фото", callback_data=f"costume_edit_photo_add_ID{costume_id}"))
                kb.add(IKButton("Назад", callback_data=f"show_costume_id{costume_id}"))
                await cbq.message.delete()
                await bot.send_message(user_id, "<b>Изменить фото костюма</b>\n\nВыберите действие", reply_markup=kb)
                return
        elif cbq.data.find("favorite") != -1:
            num = int(cbq.data.split("num")[1].split('_')[0])
            arr_photo.insert(0, arr_photo.pop(num - 1))
            sqlite_utils.update("costume", "json_arr_img", json.dumps(arr_photo), f"id_costume = {costume_id}")
            await cbq.answer("🌟 Выбрано титульное фото")
            cbq.data = f"costume_edit_photo_num1_ID{costume_id}"
        if len(arr_photo) == 0:
            pass
        else:
            if cbq.data.find("num") != -1:
                num = int(cbq.data.split("num")[1].split('_')[0])
            else:
                num = 1
            if num > len(arr_photo) or num < 1:
                num = 1
            kb = IKMarkup()
            cb_txt = "costume_edit_photo_num"
            if len(arr_photo) > 1:
                prev_num = num - 1 if num > 1 else len(arr_photo)
                next_num = num + 1 if num < len(arr_photo) else 1
                kb.add(
                    IKButton("◀️", callback_data=f"{cb_txt}{prev_num}_ID{costume_id}"),
                    IKButton(f"{num} из {len(arr_photo)}", callback_data="null"),
                    IKButton("▶️", callback_data=f"{cb_txt}{next_num}_ID{costume_id}")
                )
            if len(arr_photo) < 10:
                kb.add(IKButton("Добавить еще фото", callback_data=f"costume_edit_photo_input_ID{costume_id}"))
            if num == 1:
                kb.add(IKButton("[ТИТУЛЬНОЕ ФОТО]", callback_data="null"))
            else:
                kb.add(IKButton("Cделать фото титульным", callback_data=f"{cb_txt}{num}_favorite_ID{costume_id}"))
            kb.add(IKButton("Удалить фото", callback_data=f"{cb_txt}{num}_del_ID{costume_id}"))
            kb.add(IKButton("Назад", callback_data=f"show_costume_id{costume_id}"))
            await cbq.message.answer_photo(arr_photo[num - 1], caption="Выберите действие", reply_markup=kb)
            await cbq.message.delete()
            return
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {costume_edit_photo}", f"({cbq.from_user.mention}|{cbq.from_user.id})", ex)


@dp.callback_query_handler(IsModerator(), lambda c: c.data.startswith("costume_edit"))
async def costume_edit(cbq: CallbackQuery, state: FSMContext):
    try:
        text = "Error"
        costume_id = int(cbq.data.split("ID")[1])
        costume = sqlite_utils.get_costume(costume_id)
        if costume is None:
            await cbq.answer(f"⁉️ Ошибка. Костюма (id{costume_id}) больше нету в базе данных", show_alert=True)
            return

        kb = IKMarkup()
        kb.add(IKButton("Отмена", callback_data=f"show_costume_id{costume_id}"))
        arr_parameter = cbq.data.split("costume_edit_")[1].split("_")
        first_par = arr_parameter[0]
        await state.finish()
        # Начало ввода
        if first_par == "name":
            text = "Введите новое название"
            await EditCostume.wait_new_name.set()
            async with state.proxy() as data:
                data['costume_id'] = costume_id
        elif first_par == "description":
            text = "Введите новое описание"
            await EditCostume.wait_new_description.set()
            async with state.proxy() as data:
                data['costume_id'] = costume_id
        elif first_par == "category":
            arr_collection, count = sqlite_utils.get_all("collection"), 0
            if len(arr_collection) == 0:
                text = "У вас нету ни одной коллекции..."
                kb.inline_keyboard.insert(0, [IKButton("Создать коллекцию", callback_data="new_collection_setName")])
            else:
                text = "Выберите новую категорию"
                kb.inline_keyboard = page_all_collection(1, costume_id=costume_id).inline_keyboard + kb.inline_keyboard
        elif first_par == "photo":
            await costume_edit_photo(cbq, state)
            return
        elif first_par == "input":
            kb = IKMarkup()
            kb.add(IKButton("Назад к костюму", callback_data=f"show_costume_id{costume_id}"))
            second_par = arr_parameter[1]
            if second_par == "collection":
                id_collection = int(arr_parameter[2][2:])
                if sqlite_utils.get_one("collection", where=f"id={id_collection}") is None and (id_collection != 0):
                    await cbq.answer(f"⁉️ Ошибка. Коллекции (id{id_collection}) нету в базе данных", show_alert=True)
                    return
                sqlite_utils.update("costume", "id_collection", id_collection, f"id_costume={costume_id}")
                if id_collection:
                    text = "✅ Костюм успешно перемещен в другую коллекцию!"
                else:
                    text = "🗂️ Костюм успешно архивирован!"
                kb.add(IKButton("Открыть новую коллекцию", callback_data=f"show_collection_id{id_collection}"))
                kb.add(IKButton("Открыть прошлую коллекцию", callback_data=f"show_collection_id{costume[1]}"))
            else:
                raise Exception(f"Ошибка аргументов: cbq.data={cbq.data}")
        else:
            raise Exception(f"Ошибка аргументов: cbq.data={cbq.data}")
        new_msg = await cbq.message.edit_text(text, reply_markup=kb)
        arr_del_msg[cbq.from_user.id] = new_msg.message_id
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {costume_edit}", f"({cbq.from_user.mention}|{cbq.from_user.id})", ex)
