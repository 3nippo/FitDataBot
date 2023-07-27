from telebot.asyncio_handler_backends import State, StatesGroup


class AddExcerciseStates(StatesGroup):
    enter_name = State()
    enter_unit = State()
    track_rpe = State()