import telebot
import storage
import states
import matplotlib.pyplot as plt
import tempfile


class Context:
    def __init__(self) -> None:
        self.selected_analytics = None
        self.weeks = None
        self.excercises = None


USER_CTX = None
ENGINE = None
TOTAL_ANALYTICS = ['Total volume', 'Total RPE']
EXCERCISE_ANALYTICS = ['Excercise volume', 'Excercise RPE', 'Excercise max weight']


async def draw_analytics(message, bot):
    analytics = TOTAL_ANALYTICS + EXCERCISE_ANALYTICS
    keyboard = telebot.types.InlineKeyboardMarkup()
    for analytics_choice in analytics:
        keyboard.add(telebot.types.InlineKeyboardButton(analytics_choice, callback_data=analytics_choice))

    await bot.set_state(message.from_user.id, states.AnalyticsStates.analytics_choice, message.chat.id)
    await bot.send_message(message.chat.id, 'Choose analytics', reply_markup=keyboard)


async def on_analytics_choice(call, bot):
    ctx = Context()
    ctx.selected_analytics = call.data
    USER_CTX[call.from_user.id] = ctx

    await bot.set_state(call.from_user.id, states.AnalyticsStates.enter_weeks, call.message.chat.id)
    await bot.answer_callback_query(callback_query_id=call.id)
    await bot.send_message(call.message.chat.id, 'Enter weeks to analyze')


async def ask_excercise(message, bot, only_rpe_tracked):
    excercises = storage.fetch_excercises(ENGINE, message.from_user.id, only_rpe_tracked)
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for idx, excercise in enumerate(excercises):
        keyboard.add(telebot.types.InlineKeyboardButton(excercise.name, callback_data=str(idx)))

    ctx = USER_CTX[message.from_user.id]
    ctx.excercises = excercises

    await bot.set_state(message.from_user.id, states.AnalyticsStates.select_excercise, message.chat.id)
    await bot.send_message(message.chat.id, 'Select excercise', reply_markup=keyboard)


async def draw_result(chat_id, bot, result):
    keys, result = result
    tmp_file = tempfile.NamedTemporaryFile(suffix='.png')

    fig, ax = plt.subplots(figsize=(16, 12), nrows=1, ncols=1)
    ax.scatter(*zip(*result), c='r')
    ax.plot(*zip(*result))
    ax.set_xlabel(keys[0])
    ax.set_ylabel(keys[1])
    fig.savefig(tmp_file)

    await bot.send_document(chat_id, telebot.types.InputFile(tmp_file.name))

    tmp_file.close()


async def on_excercise_selected(call, bot):
    await bot.answer_callback_query(callback_query_id=call.id)

    ctx = USER_CTX[call.from_user.id]

    excercise = ctx.excercises[int(call.data)]

    result = None
    if ctx.selected_analytics == 'Excercise volume':
        result = storage.fetch_excercise_volume(ENGINE, call.from_user.id, ctx.weeks, excercise.id)
    elif ctx.selected_analytics == 'Excercise RPE':
        result = storage.fetch_excercise_rpe(ENGINE, call.from_user.id, ctx.weeks, excercise.id)
    elif ctx.selected_analytics == 'Excercise max weight':
        result = storage.fetch_excercise_max_weight(ENGINE, call.from_user.id, ctx.weeks, excercise.id)
    else:
        assert False, "Unreachable"

    await draw_result(call.chat.id, bot, result)

    await bot.delete_state(call.from_user.id, call.message.chat.id)


async def on_weeks_entered(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.weeks = int(message.text)

    result = None
    if ctx.selected_analytics == 'Total volume':
        result = storage.fetch_total_volume(ENGINE, message.from_user.id, ctx.weeks)
    elif ctx.selected_analytics == 'Total RPE':
        result = storage.fetch_total_rpe(ENGINE, message.from_user.id, ctx.weeks)
    elif ctx.selected_analytics in EXCERCISE_ANALYTICS:
        await ask_excercise(message, bot, only_rpe_tracked='RPE' in ctx.selected_analytics)
        return
    else:
        assert False, "Unreachable"

    await draw_result(message.chat.id, bot, result)

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
    bot.register_callback_query_handler(
        on_analytics_choice,
        lambda call: True,
        state=states.AnalyticsStates.analytics_choice,
        pass_bot=True
    )
    bot.register_message_handler(
        on_weeks_entered,
        state=states.AnalyticsStates.enter_weeks,
        pass_bot=True
    )
    bot.register_callback_query_handler(
        on_excercise_selected,
        lambda call: True,
        state=states.AnalyticsStates.select_excercise,
        pass_bot=True
    )