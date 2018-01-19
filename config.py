import logging

# winline telegram parameters
WINLINE_BOT_TOKEN = 'some token here'
WINLINE_ALERT_CHANNEL_NAME = '@test_winline_alert'  # format - @CHANNEL_NAME

# common telegram parameters
SEND_MESSAGE_ATTEMPT_TIMEOUT_SEC = 10
SEND_MESSAGE_ATTEMPT_MAX = 5
SEND_ALIVE_MESSAGE_TIMEOUT_SEC = 60 * 60

# winline data scrapping parameters
WINLINE_LIVE_URL = 'https://winline.ru/now/'
WINLINE_EVENT_CLASS_NAME = 'statistic__match'
WAIT_ELEMENT_TIMEOUT_SEC = 60
DATA_SEARCHING_TIMEOUT_SEC = 300    # max time that allocated for searching, if timeout exceeded method interrupts
DATA_EXPORT_TIMEOUT_SEC = 300       # timeout between data searching

# system settings
# PATH_TO_LOGS = '/var/log/winline.log'
PATH_TO_LOGS = './winline.log'

# logger settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)
LOGS_FORMAT = '%(asctime)s - %(levelname)s - [%(funcName)s] - %(message)s'
formatter = logging.Formatter(LOGS_FORMAT)
file_handler = logging.FileHandler(PATH_TO_LOGS)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
