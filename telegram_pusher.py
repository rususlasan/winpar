import telebot


WINLINE_ALERT_BOT_TOKEN = '512466759:AAHQ-LqRYZ6KLxlHI4s0S9s1CnGJ8glyISk'
bot = telebot.TeleBot(WINLINE_ALERT_BOT_TOKEN)


@bot.message_handler(commands=['alive'])
def handle_alive_request(mes):
    bot.send_message(mes.chat.id, 'I am here!')


