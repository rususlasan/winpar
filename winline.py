import os
import time

import config
from telegram_pusher import TelegramPusher

from config import logger
from data import Event

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Controller:

    FIREFOX_BIN = '/usr/bin/firefox'
    URL = config.WINLINE_LIVE_URL

    def __init__(self, bot):
        logger.info('==================== Start application... ====================')
        self._bot = bot
        os.environ['MOZ_HEADLESS'] = '1'
        try:
            self._driver = webdriver.Firefox(firefox_binary=self.FIREFOX_BIN,
                                             executable_path='/usr/bin/geckodriver')
        except:
            logger.exception('Could not initialize driver:')
            self._driver = None
            return

        self.wait = WebDriverWait(self._driver, config.WAIT_ELEMENT_TIMEOUT_SEC)
        # self.driver.implicitly_wait(30) # seconds

    @property
    def driver(self):
        return self._driver

    @property
    def bot(self):
        return self._bot

    def run(self):
        logger.info('Start infinite parsing...')
        while True:
            events = self.get_data()
            if not events:
                logger.warning('events is empty due to errors above!!!')
            pairs = self.data_analyzer(events)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)

    def get_data(self):
        """
        :return: list of event objects
        """
        try:
            self._driver.get(self.URL)
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, config.WINLINE_EVENT_CLASS_NAME)))
            logger.info('Url %s successfully downloaded.' % self.URL)
        except Exception as e:
            logger.error('Could not load url {url}: {err}'.format(url=config.WINLINE_LIVE_URL, err=e))
            return None

        uniq = set()
        events = []
        start_time = time.time()
        elapsed_time = 0

        while elapsed_time < config.DATA_SEARCHING_TIMEOUT_SEC:
            # search all events placed in page
            try:
                current_finds = set(self._driver.find_elements_by_class_name(config.WINLINE_EVENT_CLASS_NAME))
            except Exception as e:
                logger.error('Could not find element with class name {class_name}: {err}'
                             .format(class_name=config.WINLINE_EVENT_CLASS_NAME, err=e))
                return []

            new_events = current_finds - uniq
            uniq |= current_finds

            if new_events:
                for el in new_events:
                    event = self.parse_element_to_event(el)
                    if not event:
                        continue
                    events += [event]
            else:
                logger.info('Scrolled down....\nTotal find events - %d' % len(uniq))
                break

            # scroll down by one screen
            try:
                logger.info('Scroll down')
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except Exception as e:
                logger.error('Could not execute javascript to scroll down: {err}'.format(err=e))

            elapsed_time = time.time() - start_time
        else:
            logger.warning('get_data timeout %d exceeded, data has not been collected!!!'
                           % config.DATA_SEARCHING_TIMEOUT_SEC)
        self._driver.close()
        return events

    @staticmethod
    def parse_element_to_event(element):
        """
            extract data from DOM-element
            :param element: DOM-object, WebElement type
            :return: event object
        """
        try:
            url = element.get_attribute("href")
            title = element.get_attribute("title")
            first, second = title.split(" - ")
            logger.info('Created: {} | {} - {}'.format(first, second, url))
            return Event(first, second, url)
        except Exception as e:
            logger.error('{err}. None will be returned.'.format(err=e))
            return None

    @staticmethod
    def data_analyzer(events):
        """
        search same pairs from data array
        :param events: array of Event objects
        :return: array of tuples, each tuple a same Event object or None
        """
        res = []

        seen = set()
        seen_add = seen.add
        seen_twice = set(x for x in events if x in seen or seen_add(x))

        for duplicate in seen_twice:
            same_events = [duplicate]
            for e in events:
                if duplicate == e and duplicate.url != e.url:
                    same_events.append(e)

            res.append(same_events)

        return res

    def telegram_connector(self, pairs):
        """

        :param pairs:
        :return:
        """
        # get url from each event
        for pair in pairs:
            urls = []
            for event in pair:
                urls.append(event.url)
            self._bot.post_message_in_channel('\n'.join(urls))


if __name__ == "__main__":
    telegram_pusher = TelegramPusher(config.WINLINE_BOT_TOKEN, config.WINLINE_ALERT_CHANNEL_NAME)
    c = Controller(bot=telegram_pusher)
    ret = c.data_analyzer([])
    if not c.driver:
        logger.error('Driver was not initialized, interrupt application!')
        exit(100)
    c.run()

