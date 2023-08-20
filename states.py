from telebot.asyncio_handler_backends import State, StatesGroup


class AddExcerciseStates(StatesGroup):
    enter_name = State()
    enter_unit = State()
    track_rpe = State()


class StartExcerciseStates(StatesGroup):
    choose_excercise = State()
    choose_excercise_after_query = State()
    accept_menu_choice = State()
    enter_reps = State()
    enter_weight = State()
    enter_rpe = State()
    rest = State()
    timer_stopped = State()  # one more set or cancel 
    timed_set = State()


class AnalyticsStates(StatesGroup):
    analytics_choice = State()
    enter_weeks = State()
    select_excercise = State()