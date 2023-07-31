from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message

from sqlite_utils import its_moder, its_admin


class IsModerator(BoundFilter):
    async def check(self, msg: Message):
        if its_moder(msg.from_user.id):
            return True
        else:
            return False


class IsAdmin(BoundFilter):
    async def check(self, msg: Message):
        if its_admin(msg.from_user.id):
            return True
        else:
            return False
