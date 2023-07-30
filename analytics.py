import telebot
import storage
import states


USER_CTX = None
ENGINE = None


async def draw_analytics(message, bot):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    keyboard.add(
        telebot.types.KeyboardButton('Total volume')
    )

    await bot.set_state(message.from_user.id, states.AnalyticsStates.nonspecific_choice, message.chat.id)
    await bot.send_message(message.chat.id, 'Choose analytics', reply_markup=keyboard)


async def on_nonspecific_choice(message, bot):
    if message.text == 'Total volume':
        result = storage.fetch_total_volume(ENGINE, message.from_user.id, 1)
        for el in result:
            print(el._mapping)

    await bot.delete_state(message.from_user.id, message.chat.id)


def register_handlers(bot, user_ctx, engine):
    global USER_CTX, ENGINE
    USER_CTX = user_ctx
    ENGINE = engine

    bot.register_message_handler(
        draw_analytics, 
        commands=['analytics'], 
        pass_bot=True
    )
    bot.register_message_handler(
        on_nonspecific_choice,
        state=states.AnalyticsStates.nonspecific_choice,
        pass_bot=True
    )