import aiogram
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound

import handlers.costume
from loader import bot
from func_utils import get_current_time
from handlers.costume import dict_show_costume_mediagroup


class cleaner_image(BoundFilter):
    async def check(self, msg: Message):
        user_id = msg.from_user.id
        try:
            if dict_show_costume_mediagroup.get(user_id) is not None:
                # print(dict_show_costume_mediagroup[user_id])
                for id_img in dict_show_costume_mediagroup[user_id]:
                    try:
                        await bot.delete_message(user_id, id_img)
                    except aiogram.exceptions.MessageToDeleteNotFound:
                        pass
                dict_show_costume_mediagroup[user_id] = []
            return False
        except (MessageCantBeDeleted, MessageToDeleteNotFound):
            pass
        except Exception as ex:
            print(get_current_time(), "[ОШИБКА] {cleaner_image}", f"({msg.from_user.mention}|{user_id})", ex)
            return False


class cleaner_image_msg(BoundFilter):
    global dict_show_costume_mediagroup
    async def check(self, msg: Message):
        user_id = msg.from_user.id
        try:
            if (dict_show_costume_mediagroup.get(user_id) is not None) and (msg.text.startswith('/start')):
                for id_img in dict_show_costume_mediagroup[user_id]:
                    try:
                        await bot.delete_message(user_id, id_img)
                    except aiogram.exceptions.MessageToDeleteNotFound:
                        pass
                dict_show_costume_mediagroup[user_id] = []
            return False
        except (MessageCantBeDeleted, MessageToDeleteNotFound):
            pass
        except Exception as ex:
            print(get_current_time(), "[ОШИБКА] {cleaner_image_msg}", f"({msg.from_user.mention}|{user_id})", ex)
            return False


