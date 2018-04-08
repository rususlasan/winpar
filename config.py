import logging


# winline telegram parameters
WINLINE_BOT_TOKEN = 'some token here'                     # telegram bot token
WINLINE_ALERT_CHANNEL = '@test_winline_alert'             # found events will be sending here
WINLINE_ALIVE_MESSAGE_CHANNEL = '@winline_bot_alive_mes'  # alive messages will be sending here

# common telegram parameters
SEND_MESSAGE_ATTEMPT_TIMEOUT_SEC = 10                     # timeout before next attempt of sending message
SEND_MESSAGE_ATTEMPT_MAX = 5                              # count of attempts for sending message in channel
SEND_ALIVE_MESSAGE_TIMEOUT_SEC = 60 * 60 * 2                 # timeout after which alive message will be send

# winline data scrapping parameters
WINLINE_LIVE_URL = 'https://winline.ru/now/'
WINLINE_EVENT_CLASS_NAME = 'statistic__match'
WINLINE_SPORT_KIND_CLASS_NAME = 'sorting__item'
WAIT_ELEMENT_TIMEOUT_SEC = 60
DATA_SEARCHING_TIMEOUT_SEC = 150         # max time that allocated for searching, if timeout exceeded method interrupts
DATA_EXPORT_TIMEOUT_SEC = 5            # timeout between data searching(iteration)
DOCUMENT_SCROLL_TIMEOUT_SEC = 2          # timeout between document scrolling

# driver settings
FIREFOX_BIN = '/usr/bin/firefox'
GECKODRIVER_LOG_PATH = '/var/log/geckodriver.log'
WEBDRIVER_INIT_TIMEOUT_SEC = 5
WEBDRIEVR_INIT_ATTEMPTS_MAX = 5

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
