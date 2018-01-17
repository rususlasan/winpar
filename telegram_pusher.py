import config
import telebot


bot = telebot.TeleBot(config.WINLINE_BOT_TOKEN)


def post_message_in_channel(message):
    bot.send_message(chat_id=config.WINLINE_ALERT_CHANNEL_NAME, text=message)


