import telebot
import states
import schema
import storage


USER_CTX = None
ENGINE = None


async def add_excercise(message, bot):
    await bot.set_state(message.from_user.id, states.AddExcerciseStates.enter_name, message.chat.id)
    await bot.send_message(message.chat.id, 'Enter excercise name, e.g. "Spider curl"')


async def on_enter_excercise_name(message, bot):
    excercise = schema.Excercise()
    excercise.user_id = message.from_user.id
    excercise.name = message.text

    USER_CTX[message.from_user.id] = excercise

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

    for el in schema.ExcerciseUnit:
        keyboard.add(telebot.types.KeyboardButton(el.name.title()))

    await bot.set_state(message.from_user.id, states.AddExcerciseStates.enter_unit, message.chat.id)
    await bot.send_message(message.chat.id, 'Choose unit', reply_markup=keyboard)


async def on_excercise_created(message, bot):
    excercise = USER_CTX.pop(message.from_user.id)
    storage.save_record(ENGINE, excercise)

    await bot.delete_state(message.from_user.id, message.chat.id)
    await bot.send_message(
        message.chat.id, 
        'Excercise created!', 
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )


async def on_enter_unit(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.unit = schema.ExcerciseUnit[message.text.lower()]

    if ctx.unit == schema.ExcerciseUnit.repetitions:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.add(
            telebot.types.KeyboardButton('Yes'),
            telebot.types.KeyboardButton('No')
        )

        await bot.set_state(message.from_user.id, states.AddExcerciseStates.track_rpe, message.chat.id)
        await bot.send_message(message.chat.id, 'Would you like to track RPE?', reply_markup=keyboard)
    elif ctx.unit == schema.ExcerciseUnit.seconds:
        await on_excercise_created(message, bot)
    else:
        assert False, "Unreachable"


async def on_enter_track_rpe(message, bot):
    track_rpe = True if message.text == 'Yes' else False
    USER_CTX[message.from_user.id].track_rpe = track_rpe
    
    await on_excercise_created(message, bot)


def register_handlers(bot, user_ctx, engine):
    global USER_CTX, ENGINE
    USER_CTX = user_ctx
    ENGINE = engine

    bot.register_message_handler(
        add_excercise, 
        commands=['add_excercise'], 
        pass_bot=True
    )
    bot.register_message_handler(
        on_enter_excercise_name, 
        state=states.AddExcerciseStates.enter_name, 
        pass_bot=True
    )
    bot.register_message_handler(
        on_enter_unit,
        state=states.AddExcerciseStates.enter_unit,
        pass_bot=True
    )
    bot.register_message_handler(
        on_enter_track_rpe,
        state=states.AddExcerciseStates.track_rpe,
        pass_bot=True
    )