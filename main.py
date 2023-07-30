import telebot
from telebot.async_telebot import AsyncTeleBot
import asyncio
from sqlalchemy import create_engine

import add_excercise
import start_excercise
import schema


USER_CB = {}
USER_CTX = {}


def get_telegram_token():
    with open('bot_token') as f:
        return f.read().strip()


def get_db_pwd():
    with open('db_pwd') as f:
        return f.read().strip()


async def main():
    bot_token = get_telegram_token()
    bot = AsyncTeleBot(bot_token, state_storage=telebot.asyncio_storage.StateMemoryStorage())

    await bot.set_my_commands([
        telebot.types.BotCommand('add_excercise', 'create and save excercise'),
        telebot.types.BotCommand('start_excercise', 'mine train data!')
    ])

    bot.add_custom_filter(telebot.asyncio_filters.StateFilter(bot))

    db_pwd = get_db_pwd()
    engine = create_engine(
        'postgresql+psycopg://fitdatabot:{}@localhost:5432/fit_data_bot_db'.format(db_pwd), 
        echo=True
    )
    # schema.Base.metadata.drop_all(engine)
    schema.Base.metadata.create_all(engine)

    add_excercise.register_handlers(bot, USER_CTX, engine)
    start_excercise.register_handlers(bot, USER_CTX, engine)

    await bot.polling()


asyncio.run(main())