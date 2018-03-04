import time
import telebot

import config

from config import logger


class TelegramPusher:

    def __init__(self, bot_token):
        logger.info('Init telegram bot...')
        self._bot_token = bot_token
        try:
            self._bot = telebot.TeleBot(bot_token)
        except Exception as e:
            logger.exception('Bot was not initialized: {err}'.format(err=e))
            exit(50)
        is_alive = self.post_message_in_channel('I am alive! Current iteration #1',
                                                channel=config.WINLINE_ALIVE_MESSAGE_CHANNEL)
        is_info = self.post_message_in_channel('I am here! Alive messages will be sending in \"@winline_bot_alive_mes\"',
                                               channel=config.WINLINE_ALERT_CHANNEL)
        if not (is_alive or is_info):
            logger.error('Bot could not send start messages, initializing failed.')
            exit(25)

    @property
    def bot_token(self):
        return self._bot_token

    @property
    def bot(self):
        return self._bot

    def post_message_in_channel(self, message, channel=config.WINLINE_ALERT_CHANNEL):
        """
        :param message:
        :param channel: channel name
        :return: True if message successfully, else - False
        """
        current_attempt = 1
        logger.info('Try to send message: \"{message}\" in channel \"{channel}\".'
                    .format(message=message, channel=channel))
        while current_attempt <= config.SEND_MESSAGE_ATTEMPT_MAX:
            try:
                self.bot.send_message(chat_id=channel, text='[Second-BOT] %s' % message)
                logger.info('Message send successfully.')
                return True
            except Exception as e:
                logger.exception(
                    'Could not send message in channel \"{channel}\": {exception}. Attempt {current_attempt} in {max_attempt}'
                    .format(channel=channel,
                            message=message,
                            exception=e,
                            current_attempt=current_attempt,
                            max_attempt=config.SEND_MESSAGE_ATTEMPT_MAX))
                current_attempt += 1
                time.sleep(config.SEND_MESSAGE_ATTEMPT_TIMEOUT_SEC)
        else:
            logger.error('Could not send message in 5 attempts!!!')
            return False
