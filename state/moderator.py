from aiogram.dispatcher.filters.state import State, StatesGroup


class EditCostume(StatesGroup):
    wait_new_photo = State()
    wait_new_name = State()
    wait_new_description = State()

