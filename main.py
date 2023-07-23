import telebot

BOT = None

@BOT.message_handler(commands=['hello'])
def send_welcome(message):
    BOT.reply_to(message, "Howdy, how are you doing?")

def main():
    bot_token = None
    with open('bot_token') as f:
        bot_token = f.read().strip()

    BOT = telebot.TeleBot(bot_token)

    BOT.infinity_polling()

if __name__ == '__main__':
    main()