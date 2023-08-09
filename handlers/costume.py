from aiogram import Dispatcher
from aiogram.utils.exceptions import WrongFileIdentifier

from loader import dp, bot
import loader
import json
import sqlite_utils
from func_utils import get_current_time
from aiogram.types import *
from aiogram.types import InlineKeyboardButton as IKButton
from aiogram.types import InlineKeyboardMarkup as IKMarkup
import aiogram

dict_create_costume = {}
dict_show_costume_mediagroup: dict = {}

# {    (id_user)
#      87102936: {
#          "id_collection": INT,
#          "name": STRING,
#          "description": STRING,
#          "arr_photo": [
#                (int)     (int)
#              (ID_PHOTO, ID_MESSAGE)
#          ]
#          "favorit_photo": (ID_PHOTO, ID_MESSAGE)
#      }
# }


# ======================================================================================================================

# Отображение костюма
@dp.callback_query_handler(lambda c: c.data.startswith("show_costume_id"))
async def show_costume(cbq: CallbackQuery, all_photo=False):
    try:
        id_costume = int(cbq.data.split("show_costume_id")[1])
        costume = sqlite_utils.get_costume(id_costume)

        # если костюма нету в бд...
        if costume is None:
            if sqlite_utils.its_moder(cbq.from_user.id):
                await cbq.answer(f"⁉️ Ошибка. Костюма (id{id_costume}) больше нету в базе данных", show_alert=True)
            else:
                await cbq.answer("😓 В данный момент костюм не доступен для просмотра", show_alert=True)
            return
        msg = Message()

        # Отправление фотографий
        arr_idphoto = json.loads(costume[4])
        if len(arr_idphoto):
            if all_photo:
                album = MediaGroup()
                for idphoto in arr_idphoto:
                    album.attach_photo(photo=idphoto)
                msg = await cbq.message.answer_media_group(media=album)
                dict_show_costume_mediagroup[cbq.from_user.id] = [img.message_id for img in msg]
            else:
                msg = await cbq.message.answer_photo(photo=arr_idphoto[0])
                dict_show_costume_mediagroup[cbq.from_user.id] = [msg.message_id]

        # Генерация кнопок
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Зарезервировать 👋", url=sqlite_utils.get_contact_manager()))
        if len(arr_idphoto) > 1 and all_photo is False:
            kb.add(InlineKeyboardButton("Все фотографии 📸", callback_data=f"show_costume_photo_id{id_costume}"))
        kb.add(InlineKeyboardButton("Вернуться ⬅️", callback_data=f"show_collection_id{int(costume[1])}"))
        text = f"<b>{costume[2]}</b>\n\n{costume[3]}"

        # ------------------------------------------------------------------------------------------------------------------

        # Если модератор откроет костюм
        if sqlite_utils.its_moder(cbq.from_user.id):
            text_ikb_photo = "Изменить фото" if len(arr_idphoto) else "Добавить фото"
            data_ikb_photo = f"photo_ID{id_costume}"
            kb.add(IKButton(text="🔽 ПАНЕЛЬ УПРАВЛЕНИЯ 🔽", callback_data=f"null"))
            kb.add(IKButton(text="Изменить имя", callback_data=f"costume_edit_name_ID{id_costume}"))
            kb.add(IKButton(text=text_ikb_photo, callback_data=f"costume_edit_{data_ikb_photo}"))
            kb.add(IKButton(text="Изменить описание", callback_data=f"costume_edit_description_ID{id_costume}"))
            kb.add(IKButton(text="Изменить категорию", callback_data=f"costume_edit_category_ID{id_costume}"))
            kb.add(IKButton(text="Удалить костюм", callback_data=f"del_costumeID{id_costume}"))
            kb.add(IKButton(text="Архивировать", callback_data=f"costume_edit_input_collection_id0_ID{id_costume}"))
            text += "\n\n<b>⚙️ Техническая информация</b>\n"
            text += f'<a href="https://t.me/zhekahelp_bot?start=costume{id_costume}">Ссылка на костюм для клиента</a>\n'
            text += f"costume_id: <code>{id_costume}</code>"

        # ------------------------------------------------------------------------------------------------------------------

        # Отправление описания

        await cbq.message.answer(text=text, reply_markup=kb)
        await cbq.message.delete()
        if all_photo:
            str_arr_id_photo = ""
            for photo in msg:
                str_arr_id_photo += str(photo.message_id) + '_'
            str_arr_id_photo = str_arr_id_photo[:-1]
            sqlite_utils.set_state(cbq.from_user.id, f"costume_id{id_costume}_arrIdMsg{str_arr_id_photo}")
        else:
            sqlite_utils.set_state(cbq.from_user.id, f"costume_id{id_costume}_idMSG{msg.message_id}")
    except WrongFileIdentifier as ex:
        print(get_current_time(), "[ОШИБКА] {show_costume} (WrongFileIdentifier)", ex.args)
        admin_id = sqlite_utils.get_one("config", "value", "name='admin_id'")[0]
        dp.bot.send_message(admin_id, "Ошибка, сообщите системному администратору: WrongFileIdentifier. Ниже ошибка")
        dp.bot.send_message(admin_id, ex.args)
    except Exception as ex:
        print(get_current_time(), "[ОШИБКА] {show_costume}", f"({cbq.from_user.mention})", ex)


@dp.callback_query_handler(lambda c: c.data.startswith("show_costume_photo_id"))
async def show_costume_photo(cbq: CallbackQuery):

    if dict_show_costume_mediagroup.get(cbq.from_user.id) is not None:
        for id_img in dict_show_costume_mediagroup[cbq.from_user.id]:
            try:
                await bot.delete_message(cbq.from_user.id, id_img)
            except aiogram.exceptions.MessageToDeleteNotFound:
                pass
        dict_show_costume_mediagroup[cbq.from_user.id] = []

    if cbq.data[len("show_costume_photo_id"):].isdigit():
        cbq.data = f"show_costume_id{int(cbq.data[len('show_costume_photo_id'):])}"
    else:
        # !!! Напиши потом норм заглушку
        return
    await show_costume(cbq, all_photo=True)


# ======================================================================================================================

# Сообщение об Вводе Названия Костюма
@dp.callback_query_handler(lambda c: c.data.startswith("newCostume_setName_collectionID"))
async def newCostume(cbq: CallbackQuery):
    if not sqlite_utils.its_moder(cbq.from_user.id):
        loader.bot.answer_callback_query(cbq.id, text="⛔️ Отказано в доступе", show_alert=True)
        return

    id_collection = -1

    if cbq.data.split("newCostume_setName_collectionID")[1].isdigit():
        id_collection = int(cbq.data.split("newCostume_setName_collectionID")[1])

    if sqlite_utils.get_name_collection(id_collection) is None and id_collection != 0:
        loader.bot.answer_callback_query(cbq.id, text="⛔️ Коллекция не найдена в Базе Данных")
        return

    dict_create_costume[cbq.from_user.id] = {
        "id_collection": id_collection
    }

    await cbq.message.answer("Введите название костюма")
    sqlite_utils.set_state(cbq.from_user.id, "newCostume_setName")


# Ввод Названия Костюма ->
# Сообщение об вводе Описания Костюма
@dp.message_handler(lambda m: sqlite_utils.get_state(m.from_user.id) == "newCostume_setName")
async def newCostume_1_setName(msg: Message):
    id_user = msg.from_user.id

    # Различные проверки
    if not sqlite_utils.its_moder(id_user):
        await msg.answer("⛔️ Отказано в доступе")
        return

    if dict_create_costume.get(id_user) is None:
        await msg.answer("⛔️ Произошла непредвиденная (701123X), введите /start и попробуйте занова 🙏")
        return

    if dict_create_costume[id_user].get("id_collection") is None:
        await msg.answer("⛔️ Произошла непредвиденная (892W3467), введите /start и попробуйте занова 🙏")
        return

    id_collection = dict_create_costume[id_user]["id_collection"]

    if sqlite_utils.get_name_collection(id_collection) is None and id_collection != 0:
        await msg.answer("⛔️ Произошла непредвиденная (78123D), введите /start и попробуйте занова 🙏")
        return

    if len(msg.text.encode("utf-8")) > 64:
        await msg.answer("⛔️ Длина названия костюма слишком длинное")
        return

    if not sqlite_utils.unique_costume_name(msg.text):
        await msg.answer("⛔️ Такое название костюма уже есть")
        return

    # Добавляем в память информцию о костюме
    dict_create_costume[id_user]["name"] = msg.text

    await msg.answer("✅ <b>Название костюма сохранено!</b>", parse_mode="HTML")

    text_hint = """<b>Введите описание костюма</b>
Для оформления текста можно использовать форматирование, например <i>курсивный шрифт</i> и эмодзи 🤡
<b><a href="https://lifehacker.ru/formatirovanie-teksta-v-telegram/">Инструкции по оформлению текста</a></b>
    """
    await msg.answer(text_hint, parse_mode="HTML", disable_web_page_preview=True)

    sqlite_utils.set_state(msg.from_user.id, "newCostume_setDescription")


# Ввод описания
# Сообщение об Фотографиях Костюма (Медиагруппе)
@dp.message_handler(lambda m: sqlite_utils.get_state(m.from_user.id) == "newCostume_setDescription")
async def newCostume_setDescription(msg: Message):
    id_user = msg.from_user.id

    # Различные проверки
    if not sqlite_utils.its_moder(id_user):
        await msg.answer("⛔️ Отказано в доступе (128679), введите /start и попробуйте занова 🙏")
        return

    if dict_create_costume.get(id_user) is None:
        await msg.answer("⛔️ Произошла непредвиденная (1q2798), введите /start и попробуйте занова 🙏")

    id_collection = dict_create_costume[id_user].get("id_collection")

    if id_collection is None:
        await msg.answer("⛔️ Произошла непредвиденная ошибка (216873), введите /start и попробуйте занова 🙏")

    if sqlite_utils.get_state(id_user)[:31].isdigit():
        id_collection = int(sqlite_utils.get_state(msg.from_user.id)[:31])

    if sqlite_utils.get_name_collection(id_collection) is None and id_collection != 0:
        await msg.answer("⛔️ Произошла непредвиденная ошибка (1276812), введите /start и попробуйте занова 🙏")
        return

    # Добавляем в память информцию о костюме
    dict_create_costume[id_user]["description"] = msg.parse_entities()

    await msg.answer("✅ <b>Описание костюма сохранено!</b>", parse_mode="HTML")

    text_hint = """<b>Отправьте фотографии костюма</b>
    
<b>Важно!</b>
Первая фотография станет титульной."""

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➡️ Пропустить фото", callback_data="newCostume_skipPhoto"))

    await msg.answer(text_hint, parse_mode="HTML", reply_markup=kb)

    dict_create_costume[id_user]["arr_photo"] = []
    dict_create_costume[id_user]["favorit_photo"] = None

    sqlite_utils.set_state(msg.from_user.id, "newCostume_setPhoto")


# Ввод изображения
@dp.message_handler(lambda m: sqlite_utils.get_state(m.from_user.id) == "newCostume_setPhoto", content_types='photo')
async def newCostume_setPhoto(msg: Message):
    user_id = msg.from_user.id

    if len(dict_create_costume[user_id]["arr_photo"]) == 10:
        await msg.answer("⛔️ У костюма не может быть больше 10 фотографий")
        return

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏁 Завершить загрузку фотографий", callback_data="newCostume_finish"))

    photo_id = msg.photo.pop().file_id
    await msg.delete()
    photo_message = await msg.answer_photo(photo_id, reply_markup=kb, caption="✅ Фотография сохранена!")
    photo_message_id = photo_message.message_id

    # Добавление фото костюмов в БД
    dict_create_costume[user_id]["arr_photo"].append((photo_id, photo_message_id))

    if dict_create_costume[user_id].get("favorit_photo") is None:
        dict_create_costume[user_id]["favorit_photo"] = (photo_id, photo_message_id)

    len_arr_photo = len(dict_create_costume[user_id]["arr_photo"])

    if len_arr_photo > 1:
        temp_message = Message()
        temp_message.message_id = dict_create_costume[user_id]["arr_photo"][len_arr_photo - 2][1]
        temp_message.chat = photo_message.chat
        await temp_message.delete_reply_markup()


# Сохранение всех данных в БД
@dp.callback_query_handler(lambda c: c.data == "newCostume_finish")
async def newCostume_finish(cbq: CallbackQuery):
    id_user = cbq.from_user.id

    costume_data = dict_create_costume[id_user]
    dict_create_costume[id_user] = None

    if not sqlite_utils.its_moder(id_user):
        loader.bot.answer_callback_query(cbq.id, text="⛔️ Отказано в доступе (155). Пропишите /start", show_alert=True)

    # [Вот сюда бы проверочек понатыкать]

    arr_photo = costume_data["arr_photo"]
    str_arr_photo = ""
    if len(arr_photo):
        arr_photo.remove(costume_data["favorit_photo"])
        arr_photo = [costume_data["favorit_photo"]] + arr_photo
        for photo in arr_photo:
            str_arr_photo += '"' + str(photo[0]) + '",'
        str_arr_photo = str_arr_photo[:-1]
    str_arr_photo = '[' + str_arr_photo + ']'

    id_costume = sqlite_utils.set_costume(
        costume_data["name"],
        costume_data["description"],
        str_arr_photo,
        costume_data["id_collection"]
    )

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Открыть меню", callback_data="back_menu"))
    kb.add(InlineKeyboardButton("Открыть костюм", callback_data=f"show_costume_id{id_costume}"))
    kb.add(InlineKeyboardButton("Открыть коллекцию", callback_data=f"show_collection_id{id_costume}"))
    await cbq.message.answer(f"✅ Костюм {costume_data['name']} успешно добавлен!", "HTML", reply_markup=kb)

    sqlite_utils.set_state(id_user, "newCostume_finish")


# Пропуск отправки изображения
@dp.callback_query_handler(lambda c: c.data == "newCostume_skipPhoto")
async def newCostume_skipPhoto(cbq: CallbackQuery):
    if len(dict_create_costume[cbq.from_user.id]["arr_photo"]):
        await cbq.answer("Вы уже загрузили фотографию. Нажмите кнопку «Завершить загрузку фотографий»")
    else:
        await newCostume_finish(cbq)