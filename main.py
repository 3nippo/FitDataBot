import telebot
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio

BOT_TOKEN = None
with open('bot_token') as f:
    BOT_TOKEN = f.read().strip()

BOT = AsyncTeleBot(BOT_TOKEN)


@BOT.message_handler(commands=['hello'])
async def send_welcome(message):
    await BOT.reply_to(message, "Howdy, how are you doing?")


@BOT.message_handler(commands=['start'])
@BOT.message_handler(func=lambda msg: True)
async def show_commands(message):
    button_foo = types.InlineKeyboardButton('Foo', callback_data='foo')
    button_bar = types.InlineKeyboardButton('Bar', callback_data='bar')

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_foo)
    keyboard.add(button_bar)

    await BOT.reply_to(message, 'Select action:', reply_markup=keyboard)

asyncio.run(BOT.polling())