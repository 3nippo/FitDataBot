import telebot
from telebot.async_telebot import AsyncTeleBot
import asyncio
import tools
import states
import schema


BOT_TOKEN = None
with open('bot_token') as f:
    BOT_TOKEN = f.read().strip()

BOT = AsyncTeleBot(BOT_TOKEN, state_storage=telebot.asyncio_storage.StateMemoryStorage())


ENGINE = None


USER_CB = {}
USER_CTX = {}


@BOT.message_handler(commands=['howdy'])
async def send_welcome(message):
    await BOT.reply_to(message, "Howdy, partner! 🤠")


@BOT.message_handler(commands=['timer'])
async def timer(message):
    async def send_passed_time(ts):
        await BOT.send_message(message.chat.id, "{:0>2}:{:0>2}".format(int(ts/60), int(ts % 60)))

    timer = tools.AsyncTimer(send_passed_time, 3, 60)
    def timer_stop():
        timer.cancel()
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(telebot.types.KeyboardButton('Stop'))

    await BOT.reply_to(message, 'Timer started!', reply_markup=keyboard)
    USER_CB[message.from_user.id] = tools.TextCallback(timer_stop, 'Stop')
    try:
        await timer.start()
    except asyncio.CancelledError:
        pass
    await BOT.send_message(message.chat.id, "Completed!", reply_markup=telebot.types.ReplyKeyboardRemove())


@BOT.message_handler(commands=['add_excercise'])
async def add_excercise(message):
    await BOT.set_state(message.from_user.id, states.AddExcerciseStates.enter_name, message.chat.id)
    await BOT.send_message('Enter excercise name, e.g. "Spider curl"')


@BOT.message_handler(state=states.AddExcerciseStates.enter_name)
async def on_enter_excercise_name(message):
    excercise = schema.Excercise()
    excercise.user_id = message.form_user.id
    excercise.name = message.text

    USER_CTX[message.from_user.id] = excercise

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    for el in schema.ExcerciseUnit:
        keyboard.add(telebot.types.KeyboardButton(el.name.title()))

    await BOT.set_state(message.from_user.id, states.AddExcerciseStates.enter_unit, message.chat.id)
    await BOT.send_message('Choose unit', reply_markup=keyboard)


@BOT.message_handler(state=states.AddExcerciseStates.enter_unit)
async def on_enter_unit(message):
    USER_CTX[message.from_user.id].unit = schema.ExcerciseUnit[message.text.lower()]

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        telebot.types.KeyboardButton('Yes'),
        telebot.types.KeyboardButton('No')
    )

    await BOT.set_state(message.from_user.id, states.AddExcerciseStates.track_rpe, message.chat.id)
    await BOT.send_message('Would you like to track RPE?', reply_markup=keyboard)
    

@BOT.message_handler(state=states.AddExcerciseStates.track_rpe)
async def on_enter_track_rpe(message):
    track_rpe = True if message.text == 'Yes' else False
    USER_CTX[message.from_user.id].track_rpe = track_rpe
    
    excercise = USER_CTX.pop(message.from_user.id)
    tools.save_record(ENGINE, excercise)

    await BOT.send_message('Excercise created!')

@BOT.message_handler(func=lambda msg: True)
async def process_message(message):
    text_callback = USER_CB.get(message.from_user.id)
    if text_callback and text_callback.call_back(message.text):
        USER_CB.pop(message.from_user.id)


async def main():
    await BOT.set_my_commands([
        telebot.types.BotCommand('timer', 'timer with suggestions'),
        telebot.types.BotCommand('howdy', 'says howdy'),
        telebot.types.BotCommand('add_excercise', 'create and save excercise')
    ])

    BOT.add_custom_filter(telebot.asyncio_filters.StateFilter(BOT))

    await BOT.polling()

asyncio.run(main())