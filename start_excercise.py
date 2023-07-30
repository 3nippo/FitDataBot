import asyncio
import telebot
import storage
import states
import schema
import tools


class Context:
    def __init__(self, selected_excercise, user_id):
        self.selected_excercise = selected_excercise
        self.timer = None
        self.user_id = user_id
        self.set = None
    
    def new_set(self):
        if self.set:
            storage.save_record(ENGINE, self.set)

        self.set = schema.Set()
        self.set.excercise = self.selected_excercise
        self.set.user_id = self.user_id


TIMEOUT = 60 * 30
TIME_STEP = 5
USER_CTX = {}
ENGINE = {}


async def start_excercise(message, bot):
    excercises = storage.fetch_excercises(ENGINE, message.from_user.id)
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for idx, excercise in enumerate(excercises):
        keyboard.add(telebot.types.InlineKeyboardButton(excercise.name, callback_data=str(idx)))

    USER_CTX[message.from_user.id] = excercises

    await bot.set_state(message.from_user.id, states.StartExcerciseStates.choose_excercise, message.chat.id)
    await bot.send_message(message.chat.id, 'Select excercise', reply_markup=keyboard)


async def on_new_set_started(user_id, chat_id, bot):
    ctx = USER_CTX[user_id]

    ctx.new_set()
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton('Cancel'))

    await bot.set_state(user_id, states.StartExcerciseStates.enter_reps, chat_id)
    await bot.send_message(chat_id, 'Enter reps done', reply_markup=keyboard)


async def on_excercise_completed_or_cancelled(message, bot, completed):
    await bot.delete_state(message.from_user.id, message.chat.id)

    ctx = USER_CTX.pop(message.from_user.id)

    text = 'Excercise completed' if completed else 'Excercise cancelled'

    if not ctx.set.empty():
        storage.save_record(ENGINE, ctx.set)

    await bot.send_message(message.chat.id, text, reply_markup=telebot.types.ReplyKeyboardRemove())


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


async def on_excercise_selected(call, bot):
    excercises = USER_CTX[call.from_user.id]

    selected_excercise = excercises[int(call.data)]
    
    USER_CTX[call.from_user.id] = Context(selected_excercise, call.from_user.id) 

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