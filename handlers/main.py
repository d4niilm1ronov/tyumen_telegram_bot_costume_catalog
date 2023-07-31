import json
import time

import aiogram.utils.exceptions
from aiogram.dispatcher import FSMContext

import sqlite_utils
import keyboard.main
import handlers
from aiogram.types import *

from filters.all_filters import IsAdmin
from func_utils import get_current_time
from loader import dp
from state.main import TransportingImage


@dp.message_handler(commands=['start'])
async def command_start(msg: Message):
    try:
        sqlite_utils.update_username(msg.from_user.id, msg.from_user.full_name)
        arg = msg.get_args()
        if arg is None:
            await msg.answer("Выберите действие", reply_markup=keyboard.main.menu(msg.from_user.id))
            sqlite_utils.set_state(msg.from_user.id, "main_menu")

        elif (arg[:7] == "costume"):
            if (arg[7:].isdigit()):
                temp_msg = await msg.answer("<i>Загрузка...</i>")
                tempCQ = CallbackQuery()
                tempCQ.data = f"show_costume_id{int(arg[7:])}"
                tempCQ.from_user = msg.from_user
                tempCQ.message = temp_msg
                await handlers.costume.show_costume(tempCQ)
            else:
                await msg.answer("Выберите действие", reply_markup=keyboard.main.menu(msg.from_user.id))
                sqlite_utils.set_state(msg.from_user.id, "main_menu")

        elif arg[:10] == "collection":
            if arg[10:].isdigit():
                temp_msg = await msg.answer("<i>Загрузка...</i>")
                tempCQ = CallbackQuery()
                tempCQ.data = f"show_collection_id{int(arg[10:])}"
                tempCQ.from_user = msg.from_user
                tempCQ.message = temp_msg
                await handlers.collection.show_costume_collection(tempCQ)
            else:
                await msg.answer("Выберите действие", reply_markup=keyboard.main.menu(msg.from_user.id))
                sqlite_utils.set_state(msg.from_user.id, "main_menu")

        else:
            await msg.answer("Выберите действие", reply_markup=keyboard.main.menu(msg.from_user.id))
            sqlite_utils.set_state(msg.from_user.id, "main_menu")

        await msg.delete()
    except aiogram.utils.exceptions.MessageCantBeDeleted:
        pass
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {command_start}", f"({msg.from_user.mention})", ex)



# ======================================================================================================================

@dp.callback_query_handler(text='open_collection')
async def open_collection(callback_query: CallbackQuery):
    await handlers.collection.show_collection_page(callback_query)


# ======================================================================================================================

# @dp.message_handler(commands=['test'])
# async def set_test_state1(msg: Message):
#     print("test 1")

# ======================================================================================================================

@dp.callback_query_handler(text="back_menu")
async def back(callback_query: CallbackQuery):
    try:
        callback_query.message.from_user = callback_query.from_user
        await command_start(callback_query.message)
        await callback_query.message.delete()
    except aiogram.utils.exceptions.MessageToDeleteNotFound:
        pass
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {back}", f"({callback_query.from_user.mention})", ex)

# ======================================================================================================================


# except aiogram.utils.exceptions.WrongFileIdentifier:

@dp.message_handler(IsAdmin(), commands=['get_all_photo'])
async def transpoting_photo(msg: Message, state: FSMContext):
    for costume in sqlite_utils.get_all("costume"):
        for img in json.loads(costume[4]):
            json_data_img = {"id": img, "id_costume": costume[0]}
            await msg.answer_photo(img, caption=json.dumps(json_data_img))
            time.sleep(1)


@dp.message_handler(IsAdmin(), commands=['start_import_photo'])
async def start_import_photo(msg: Message, state: FSMContext):
    await state.finish()
    await TransportingImage.wait_img.set()
    await msg.answer("⏬ Включен режим импорта фото. Перешлите фото из прошлого бота.")


@dp.message_handler(IsAdmin(), state=TransportingImage.wait_img, content_types='photo')
async def import_photo(msg: MediaGroup, state: FSMContext):
    msg_json = json.loads(msg.as_json())
    json_data_img = json.loads(msg_json["caption"])
    new_id_photo = msg_json["photo"].pop()["file_id"]
    old_id_photo = json_data_img["id"]
    id_costume = json_data_img["id_costume"]
    costume = sqlite_utils.get_costume(id_costume)
    arr_photo: list[str] = json.loads(costume[4])
    arr_photo.remove(old_id_photo)
    arr_photo.append(new_id_photo)
    sqlite_utils.update("costume", "json_arr_img", arr_photo, f"id_costume={id_costume}", True)
    await dp.bot.delete_message(msg_json["from"]["ind"], msg_json["message_id"])
    await dp.bot.send_message(msg_json["from"]["id"], "👍 Фотография была импортирована")
    time.sleep(1)


@dp.message_handler(IsAdmin(), state=TransportingImage.wait_img, commands=['stop_import_photo'])
async def start_import_photo(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer("✅ Импорт фото завершен")

