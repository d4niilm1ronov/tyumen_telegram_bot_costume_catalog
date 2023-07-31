from aiogram.dispatcher.filters.state import State, StatesGroup



class Panel(StatesGroup):
    wait_add_moderator = State()
    wait_edit_contact = State()
