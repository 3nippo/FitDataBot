import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
import tools

BOT_TOKEN = None
with open('bot_token') as f:
    BOT_TOKEN = f.read().strip()

BOT = AsyncTeleBot(BOT_TOKEN)


USER_CB = {}


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


@BOT.message_handler(func=lambda msg: True)
async def process_message(message):
    text_callback = USER_CB.get(message.from_user.id)
    if text_callback and text_callback.call_back(message.text):
        USER_CB.pop(message.from_user.id)


async def main():
    await BOT.set_my_commands([
        telebot.types.BotCommand('timer', 'timer with suggestions'),
        telebot.types.BotCommand('howdy', 'says howdy'),
    ])

    await BOT.polling()

asyncio.run(main())