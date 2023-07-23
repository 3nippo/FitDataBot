import telebot

BOT_TOKEN = None
with open('bot_token') as f:
    BOT_TOKEN = f.read().strip()

BOT = telebot.TeleBot(BOT_TOKEN)


@BOT.message_handler(commands=['hello'])
def send_welcome(message):
    BOT.reply_to(message, "Howdy, how are you doing?")


BOT.infinity_polling()