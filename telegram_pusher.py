import config
import telebot


bot = telebot.TeleBot(config.WINLINE_BOT_TOKEN)


def post_message_in_channel(message):
    try:
        bot.send_message(chat_id=config.WINLINE_ALERT_CHANNEL_NAME, text='[BOT] %s' % message)
    except Exception as e:
        config.logger.error('Could not send message [{message}] in channel: {exception}'.format(message, e))


