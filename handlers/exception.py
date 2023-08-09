from aiogram import types
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound, NetworkError, TelegramAPIError, \
    MessageNotModified
from aiohttp import ClientOSError

from loader import bot


@bot.dp.errors_handler(exception=MessageCantBeDeleted)
async def otlov_excp1(update: types.Update, exception: MessageCantBeDeleted):
    return True

@bot.dp.errors_handler(exception=MessageToDeleteNotFound)
async def otlov_excp2():
    return True

@bot.dp.errors_handler(exception=ClientOSError)
async def otlov_excp3():
    return True

@bot.dp.errors_handler(exception=NetworkError)
async def otlov_excp4():
    return True

@bot.dp.errors_handler(exception=TelegramAPIError)
async def otlov_excp5():
    return True

@bot.dp.errors_handler(exception=MessageNotModified)
async def otlov_excp6():
    return True

