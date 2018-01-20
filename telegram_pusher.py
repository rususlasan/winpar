import time
import telebot

import config

from config import logger


class TelegramPusher:

    def __init__(self, bot_token, channel):
        logger.info('Init telegram bot...')
        self._bot_token = bot_token
        self._channel = channel
        try:
            self._bot = telebot.TeleBot(config.WINLINE_BOT_TOKEN)
        except:
            logger.exception('Bot was not initialized!')
            exit(50)
        if not self.post_message_in_channel('I am here!'):
            logger.error('Bot could not send alive message, initializing failed.')
            exit(25)

    @property
    def bot_token(self):
        return self._bot_token

    @property
    def channel(self):
        return self._channel

    @property
    def bot(self):
        return self._bot

    def post_message_in_channel(self, message):
        """
        :param message:
        :return: True if message successfully, else - False
        """
        current_attempt = 1
        config.logger.info('Try to send message: \n [{message}] in telegram...'.format(message=message))
        while current_attempt <= config.SEND_MESSAGE_ATTEMPT_MAX:
            try:
                self.bot.send_message(chat_id=config.WINLINE_ALERT_CHANNEL_NAME, text='[BOT] %s' % message)
                config.logger.info('Message send successfully.')
                return True
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
            return False
