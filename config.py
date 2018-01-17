import logging

# winline telegram parameters
WINLINE_BOT_TOKEN = 'some token here'
WINLINE_ALERT_CHANNEL_NAME = '@test_winline_alert'  # format - @CHANNEL_NAME

# common telegram parameters
SEND_MESSAGE_ATTEMPT_TIMEOUT_SEC = 10
SEND_MESSAGE_ATTEMPT_MAX = 5

# winline data scrapping parameters
WINLINE_LIVE_URL = 'https://winline.ru/now/'
DATA_EXPORT_TIMEOUT_SEC = 300

# system settings
PATH_TO_LOGS = '/var/log/winline.log'

# logger settings
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # TODO change to INFO
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(PATH_TO_LOGS)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
