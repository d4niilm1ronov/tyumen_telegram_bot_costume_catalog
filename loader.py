from aiogram import Bot, Dispatcher, types
import asyncio

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from regex import regex

import sqlite_utils
from func_utils import get_current_time

print(get_current_time(), "[Помогатор] C возвращением в Помогатор v1.0")
print(get_current_time(), "[Помогатор] Разработчик: https://vk.com/daniil_mironoff\n")
print(get_current_time(), "[Помогатор] Переходим к настройкам запуска бота...")
print(get_current_time(), "[Помогатор] Введите Y(es), если хотите изменить настройки")
print(get_current_time(), "[Помогатор] Введите N(o), если не хотите ничего менять")
print(get_current_time(), "[Помогатор] Введите W(hat), если хотите посмотреть текущие настройки")
while True:
    answer = input()
    answer = answer.lower().strip()
    if answer in ['yes', 'y']:
        print(get_current_time(), "[Настройки] Введите API-TOKEN от бота, которого хотите запустить")
        print(get_current_time(), "[Настройки] Введите N(o), если передумали менять настройки бота")
        print(get_current_time(), "[Настройки] Введите Y(es), если не хотите менять API-TOKEN")
        print(get_current_time(), "[Настройки] Введите W(hat), если не знаете что такое API-TOKEN")
        while True:
            apitoken = input()
            apitoken_answer = apitoken.lower().strip()
            if apitoken_answer in ['w', 'what']:
                print(get_current_time(), "[Помощь] Это ключ, который позволит управлять вашим Telegram ботам")
                print(get_current_time(), "[Помощь] Он выглядит примерно так: ")
                print(get_current_time(), "[Помощь] 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
                print(get_current_time(), "[Помощь] Создать бота и узнать его ключ можно в боте @BotFather")
                print(get_current_time(), "[Помощь] Введите API-TOKEN от бота, которого хотите запустить")
                print(get_current_time(), "[Настройки] Введите Y(es), если не хотите менять API-TOKEN")
                print(get_current_time(), "[Настройки] Введите N(o), если передумали менять настройки")
                continue
            if apitoken_answer in ['y', 'yes']:
                apitoken = sqlite_utils.get_one("config", "value", "name='token'")[0]
            if regex.match(r'[0-9]+:[A-Za-z0-9-_]+', apitoken):
                print(get_current_time(), "[Настройки] Хорошо, теперь введите ID телеграма администратора")
                print(get_current_time(), "[Настройки] Введите N(o), если передумали менять настройки")
                print(get_current_time(), "[Настройки] Введите Y(es), если не хотите менять ID администратора")
                print(get_current_time(), "[Настройки] Введите W(hat), если не знаете что такое ID телеграма")
                while True:
                    new_id = input()
                    new_id = new_id.lower().strip()
                    if new_id in ['w', 'what']:
                        print(get_current_time(), "[Помощь] У каждого пользователя Telegram есть свой ID")
                        # print(get_current_time(), "[Помощь] ID (или идентификатор) — это уникальный номер,")
                        # print(get_current_time(), "[Помощь] который помогает компьютеру распознать ")
                        # print(get_current_time(), "[Помощь] и отличать одну вещь (например, пользователя,")
                        # print(get_current_time(), "[Помощь] объект или запись данных) от другой. Это как")
                        # print(get_current_time(), "[Помощь] уникальный код, который каждый предмет или человек")
                        # print(get_current_time(), "[Помощь] имеет, чтобы их можно было легко найти в большом")
                        # print(get_current_time(), "[Помощь] количестве других предметов или людей.")
                        print(get_current_time(), "[Помощь] Администратор может узнать свой ID, если напишет")
                        print(get_current_time(), "[Помощь] в бота @getidsbot или вы можете переслать в бота")
                        print(get_current_time(), "[Помощь] сообщение администратора из диалога с ним")
                        print(get_current_time(), "[Настройки] Введите N(o), если передумали менять настройки")
                        print(get_current_time(), "[Настройки] Введите Y(es), если не хотите менять ID администр.")
                        continue
                    if new_id in ['y', 'yes']:
                        new_id = sqlite_utils.get_one("config", "value", "name='admin_id'")[0]
                    if new_id in ['n', 'no']:
                        apitoken_answer = 'no'
                        answer = 'no'
                    if new_id.isdigit():
                        sqlite_utils.update("config", "value", apitoken, "name='token'")
                        sqlite_utils.update("config", "value", new_id, "name='admin_id'")
                        print(get_current_time(), "[Настройки] Новые надстройки бота сохранены в базу данных!")
                        apitoken_answer = 'no'
                        break
            if apitoken_answer in ['n', 'no']:
                answer = 'n'
                break
            print(get_current_time(), "[Помогатор] Извините, я не понимаю... введите ключ бота, 'N', 'Y' или 'W'")
    if answer in ['no', 'n']:
        print(get_current_time(), "[Помогатор] Приступаю к запуску бота!")
        break
    if answer in ['what', 'w']:
        token = sqlite_utils.get_one("config", "value", "name='token'")[0]
        admin_id = sqlite_utils.get_one("config", "value", "name='admin_id'")[0]
        print(get_current_time(), f"[Настройки] ADMIN ID: {admin_id}")
        print(get_current_time(), f"[Настройки] API-TOKEN: {token}\n")
        print(get_current_time(), "[Помогатор] Введите Y(es), если хотите изменить настройки")
        print(get_current_time(), "[Помогатор] Введите N(o), если не хотите ничего менять")
    else:
        print(get_current_time(), "[Помогатор] Извините, но я не понимаю... введите Y, N или W для выбора действия")

bot = Bot(token=sqlite_utils.get_one("config", "value", "name='token'")[0], parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=asyncio.get_event_loop())
