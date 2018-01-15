import telebot


WINLINE_ALERT_BOT_TOKEN = 'SOME_TIKEN_HERE'
CHANNEL_NAME = '@test_winline_alert'


bot = telebot.TeleBot(WINLINE_ALERT_BOT_TOKEN)


def post_message_in_channel(message):
    bot.send_message(chat_id=CHANNEL_NAME, text=message)


