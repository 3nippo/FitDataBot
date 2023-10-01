import telebot
import schema
import storage
import states
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile


class Context:
    def __init__(self) -> None:
        self.selected_analytics = None
        self.weeks = None
        self.excercises = None
        self.state_after_inline_query = None
        self.excercise_search_options = storage.ExcerciseSearchOptions()


def excercise_search_options_from_analytics(selected_analytics):
    search_options = storage.ExcerciseSearchOptions()

    if 'time' in selected_analytics:
        search_options.unit = schema.ExcerciseUnit.seconds
    else:
        search_options.unit = schema.ExcerciseUnit.repetitions

    search_options.only_rpe_tracked = 'RPE' in selected_analytics

    return search_options


USER_CTX = None
ENGINE = None
TOTAL_ANALYTICS = ['Total volume', 'Total RPE']
EXCERCISE_ANALYTICS = ['Excercise volume', 'Excercise RPE', 'Excercise max weight', 'Excercise time']


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


async def draw_result_and_complete(user_id, chat_id, bot, result):
    keys, result = result
    tmp_file = tempfile.NamedTemporaryFile(suffix='.png')

    fig, ax = plt.subplots(figsize=(16, 12), nrows=1, ncols=1)
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.scatter(*zip(*result), c='r')
    ax.plot(*zip(*result))
    ax.set_xlabel(keys[0])
    ax.set_ylabel(keys[1])
    fig.savefig(tmp_file)

    await bot.send_document(chat_id, telebot.types.InputFile(tmp_file.name))

    tmp_file.close()

    USER_CTX.pop(user_id)
    await bot.delete_state(user_id, chat_id)


async def on_excercise_selected(message, bot):
    excercises = storage.fetch_excercises(ENGINE, message.from_user.id)

    selected_excercise = None

    for excercise in excercises:
        if excercise.name == message.text:
            selected_excercise = excercise
            break
    
    assert selected_excercise, "Bad excercise chosen"

    ctx = USER_CTX[message.from_user.id]

    result = None
    # TODO: make storage.fetch_excercise_parameter
    if ctx.selected_analytics == 'Excercise volume':
        result = storage.fetch_excercise_volume(ENGINE, message.from_user.id, ctx.weeks, excercise.id)
    elif ctx.selected_analytics == 'Excercise RPE':
        result = storage.fetch_excercise_rpe(ENGINE, message.from_user.id, ctx.weeks, excercise.id)
    elif ctx.selected_analytics == 'Excercise max weight':
        result = storage.fetch_excercise_max_weight(ENGINE, message.from_user.id, ctx.weeks, excercise.id)
    elif ctx.selected_analytics == 'Excercise time':
        result = storage.fetch_excercise_time(ENGINE, message.from_user.id, ctx.weeks, excercise.id)
    else:
        assert False, "Unreachable"

    await draw_result_and_complete(message.from_user.id, message.chat.id, bot, result)


async def on_weeks_entered(message, bot):
    ctx = USER_CTX[message.from_user.id]
    ctx.weeks = int(message.text)

    result = None
    if ctx.selected_analytics == 'Total volume':
        result = storage.fetch_total_volume(ENGINE, message.from_user.id, ctx.weeks)
    elif ctx.selected_analytics == 'Total RPE':
        result = storage.fetch_total_rpe(ENGINE, message.from_user.id, ctx.weeks)
    elif ctx.selected_analytics in EXCERCISE_ANALYTICS:
        ctx.state_after_inline_query = states.AnalyticsStates.select_excercise
        ctx.excercise_search_options = excercise_search_options_from_analytics(ctx.selected_analytics)
        await bot.send_message(message.chat.id, 'Select excercise from @ menu')
        return
    else:
        assert False, "Unreachable"

    await draw_result_and_complete(message.from_user.id, message.chat.id, bot, result)


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
    bot.register_message_handler(
        on_excercise_selected,
        state=states.AnalyticsStates.select_excercise,
        pass_bot=True
    )