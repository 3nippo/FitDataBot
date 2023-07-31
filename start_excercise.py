import asyncio
import telebot
import storage
import states
import schema
import tools
from sqlalchemy.orm import Session


class Context:
    def __init__(self, user_id):
        self.selected_excercise = None
        self.timer = None
        self.excercise_timer = None
        self.user_id = user_id
        self.set = None
        self.excercises = None
        self.session = None

    def try_save_set(self):
        if not self.set or self.set.empty():
            return False
        
        storage.save_record_with_session(self.session, self.set)
        return True
    
    def new_set(self):
        self.try_save_set()

        self.set = schema.Set()
        self.set.excercise = self.selected_excercise
        self.set.user_id = self.user_id


TIMEOUT = 60 * 30
TIME_STEP = 5
USER_CTX = {}
ENGINE = {}


async def start_excercise(message, bot):
    session = Session(ENGINE)

    excercises = storage.fetch_excercises_with_session(session, message.from_user.id)
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for idx, excercise in enumerate(excercises):
        keyboard.add(telebot.types.InlineKeyboardButton(excercise.name, callback_data=str(idx)))

    ctx = Context(message.from_user.id)
    ctx.session = session
    ctx.excercises = excercises
    USER_CTX[message.from_user.id] = ctx

    await bot.set_state(message.from_user.id, states.StartExcerciseStates.choose_excercise, message.chat.id)
    await bot.send_message(message.chat.id, 'Select excercise', reply_markup=keyboard)


async def on_timed_set(user_id, chat_id, bot):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Set done'))
    keyboard.add(telebot.types.KeyboardButton('Cancel'))

    await bot.set_state(user_id, states.StartExcerciseStates.timed_set, chat_id)
    await bot.send_message(chat_id, 'Started!', reply_markup=keyboard)

    async def send_passed_time(ts):
        await bot.send_message(chat_id, "{:0>2}:{:0>2}".format(int(ts/60), int(ts % 60)))

    ctx = USER_CTX[user_id]
    ctx.excercise_timer = tools.AsyncTimer(send_passed_time, TIME_STEP, TIMEOUT)

    try:
        await ctx.excercise_timer.start()
    except asyncio.CancelledError:
        pass


async def on_new_set_started(user_id, chat_id, bot):
    ctx = USER_CTX[user_id]

    ctx.new_set()
    
    if ctx.selected_excercise.unit == schema.ExcerciseUnit.repetitions:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(telebot.types.KeyboardButton('Cancel'))

        await bot.set_state(user_id, states.StartExcerciseStates.enter_reps, chat_id)
        await bot.send_message(chat_id, 'Enter reps done', reply_markup=keyboard)
    elif ctx.selected_excercise.unit == schema.ExcerciseUnit.seconds:
        await on_timed_set(user_id, chat_id, bot)
    else:
        assert False, "Unreachable"


async def on_excercise_completed_or_cancelled(message, bot, completed):
    await bot.delete_state(message.from_user.id, message.chat.id)

    ctx = USER_CTX.pop(message.from_user.id)

    ctx.try_save_set()

    text = 'Excercise completed' if completed else 'Excercise cancelled'
    await bot.send_message(message.chat.id, text, reply_markup=telebot.types.ReplyKeyboardRemove())

    ctx.session.close()


async def ask_rpe(message, bot):
    await bot.set_state(message.from_user.id, states.StartExcerciseStates.enter_rpe, message.chat.id)
    await bot.send_message(message.chat.id, 'Enter RPE')


async def on_rpe_entered(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.set.rpe = int(message.text)
    await on_excercise_completed_or_cancelled(message, bot, completed=True)


async def on_rest_ended(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.timer.cancel()

    if message.text == 'Continue':
        ctx.set.rest = ctx.timer.elapsed()
        await on_new_set_started(message.from_user.id, message.chat.id, bot)
        return
    
    if message.text == 'Complete':
        if ctx.selected_excercise.track_rpe:
            await ask_rpe(message, bot)
        else:
            await on_excercise_completed_or_cancelled(message, bot, completed=True)
        return


async def start_timer(message, bot):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Complete'))
    keyboard.add(telebot.types.KeyboardButton('Continue'))

    await bot.set_state(message.from_user.id, states.StartExcerciseStates.rest, message.chat.id)
    await bot.send_message(message.chat.id, 'Rest!', reply_markup=keyboard)

    async def send_passed_time(ts):
        await bot.send_message(message.chat.id, "{:0>2}:{:0>2}".format(int(ts/60), int(ts % 60)))

    ctx = USER_CTX[message.from_user.id]
    ctx.timer = tools.AsyncTimer(send_passed_time, TIME_STEP, TIMEOUT)

    try:
        await ctx.timer.start()
    except asyncio.CancelledError:
        pass


async def on_reps_entered_or_cancel(message, bot):
    if message.text == 'Cancel':
        await on_excercise_completed_or_cancelled(message, bot, completed=False)
        return

    ctx = USER_CTX[message.from_user.id]
    ctx.set.work = int(message.text)

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Cancel'))

    await bot.set_state(message.from_user.id, states.StartExcerciseStates.enter_weight, message.chat.id)
    await bot.send_message(message.chat.id, 'Enter moved weight', reply_markup=keyboard)


async def on_weight_entered_or_cancel(message, bot):
    if message.text == 'Cancel':
        await on_excercise_completed_or_cancelled(message, bot, completed=False)
        return

    ctx = USER_CTX[message.from_user.id]
    ctx.set.weight = int(message.text)

    await start_timer(message, bot)


async def on_timed_set_done_or_cancel(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.excercise_timer.cancel()

    if message.text == 'Cancel':
        await on_excercise_completed_or_cancelled(message, bot, completed=False)
        return
    
    ctx.set.work = ctx.excercise_timer.elapsed()

    await start_timer(message, bot)


async def on_excercise_selected(call, bot):
    ctx = USER_CTX[call.from_user.id]

    excercises = ctx.excercises
    ctx.selected_excercise = excercises[int(call.data)]

    await bot.answer_callback_query(
        callback_query_id=call.id, 
        text='OK! Excercise started'
    )
    await on_new_set_started(call.from_user.id, call.message.chat.id, bot)
    

def register_handlers(bot, user_ctx, engine):
    global USER_CTX, ENGINE
    USER_CTX = user_ctx
    ENGINE = engine

    bot.register_message_handler(
        start_excercise, 
        commands=['start_excercise'], 
        pass_bot=True
    )
    bot.register_callback_query_handler(
        on_excercise_selected,
        lambda call: True,
        state=states.StartExcerciseStates.choose_excercise,
        pass_bot=True
    )
    bot.register_message_handler(
        on_reps_entered_or_cancel,
        state=states.StartExcerciseStates.enter_reps,
        pass_bot=True
    )
    bot.register_message_handler(
        on_weight_entered_or_cancel,
        state=states.StartExcerciseStates.enter_weight,
        pass_bot=True
    )
    bot.register_message_handler(
        on_rest_ended,
        state=states.StartExcerciseStates.rest,
        pass_bot=True
    )
    bot.register_message_handler(
        on_rpe_entered,
        state=states.StartExcerciseStates.enter_rpe,
        pass_bot=True
    )
    bot.register_message_handler(
        on_timed_set_done_or_cancel,
        state=states.StartExcerciseStates.timed_set,
        pass_bot=True
    )