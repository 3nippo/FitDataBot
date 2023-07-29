import telebot
from telebot.async_telebot import AsyncTeleBot
import asyncio
import tools

import add_excercise
import start_excercise


ENGINE = None


USER_CB = {}
USER_CTX = {}


async def main():
    bot_token = None
    with open('bot_token') as f:
        bot_token = f.read().strip()

    bot = AsyncTeleBot(bot_token, state_storage=telebot.asyncio_storage.StateMemoryStorage())

    await bot.set_my_commands([
        telebot.types.BotCommand('timer', 'timer with suggestions'),
        telebot.types.BotCommand('howdy', 'says howdy'),
        telebot.types.BotCommand('add_excercise', 'create and save excercise'),
        telebot.types.BotCommand('start_excercise', 'mine train data!')
    ])

    bot.add_custom_filter(telebot.asyncio_filters.StateFilter(bot))

    add_excercise.register_handlers(bot, USER_CTX, ENGINE)
    start_excercise.register_handlers(bot, USER_CTX, ENGINE)

    await bot.polling()


asyncio.run(main())