import config
import telebot


bot = telebot.TeleBot(config.WINLINE_BOT_TOKEN)


def post_message_in_channel(message):
    try:
        bot.send_message(chat_id=config.WINLINE_ALERT_CHANNEL_NAME, text='[BOT] %s' % message)
    except:
        config.logger.exception('Could not send message \n [{message}] in channel:'.format(message=message))


