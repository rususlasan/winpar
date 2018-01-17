import time
import telebot

import config


bot = telebot.TeleBot(config.WINLINE_BOT_TOKEN)


def post_message_in_channel(message):
    current_attempt = 1
    config.logger.info('Try to send message: \n [{message}] in telegram...'.format(message=message))
    while current_attempt <= config.SEND_MESSAGE_ATTEMPT_MAX:
        try:
            bot.send_message(chat_id=config.WINLINE_ALERT_CHANNEL_NAME, text='[BOT] %s' % message)
            config.logger.info('Message send successfully.')
            break
        except Exception as e:
            config.logger.error(
                'Could not send message in channel: {exception}. Attempt {current_attempt} in {max_attempt}'
                .format(message=message,
                        exception=e,
                        current_attempt=current_attempt,
                        max_attempt=config.SEND_MESSAGE_ATTEMPT_MAX))
            current_attempt += 1
            time.sleep(config.SEND_MESSAGE_ATTEMPT_TIMEOUT_SEC)
    else:
        config.logger.error('Could not send message in 5 attempts!!!')
