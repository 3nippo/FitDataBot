from telebot.asyncio_handler_backends import State, StatesGroup


class AddExcerciseStates(StatesGroup):
    enter_name = State()
    enter_unit = State()
    track_rpe = State()


class StartExcerciseStates(StatesGroup):
    choose_excercise = State()
    accept_menu_choice = State()
    enter_reps = State()
    enter_rpe = State()
    rest = State()
    timer_stopped = State()  # one more set or cancel 