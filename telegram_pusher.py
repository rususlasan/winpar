import telebot


WINLINE_ALERT_BOT_TOKEN = '512466759:AAHQ-LqRYZ6KLxlHI4s0S9s1CnGJ8glyISk'
CHANNEL_NAME = '@test_winline_alert'


bot = telebot.TeleBot(WINLINE_ALERT_BOT_TOKEN)


@bot.message_handler(commands=['alive'])
def handle_alive_request(mes):
    bot.send_message(mes.chat.id, 'I am here!')


def post_message_in_channel(message):
    bot.send_message(CHANNEL_NAME, message)


