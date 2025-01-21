from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activities = State()
    city = State()


class Form_2(StatesGroup):
    product = State()
    weight = State()