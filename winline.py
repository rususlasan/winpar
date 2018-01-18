import os
import time

import config
from telegram_pusher import post_message_in_channel

from config import logger
from data import Event

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


class Controller:

    FIREFOX_BIN = '/usr/bin/firefox'
    URL = config.WINLINE_LIVE_URL

    def __init__(self):
        logger.info('==================== Start application... ====================')
        post_message_in_channel('I am here and parse!!!')
        os.environ['MOZ_HEADLESS'] = '1'
        self.driver = webdriver.Firefox(firefox_binary=self.FIREFOX_BIN,
                                        executable_path='/usr/bin/geckodriver')
        self.wait = WebDriverWait(self.driver, config.WAIT_ELEMENT_TIMEOUT_SEC)
        # self.driver.implicitly_wait(30) # seconds

    def run(self):
        while True:
            events = self.get_data()
            if not events:
                logger.warning('events is None!!!')
                continue
            pairs = self.data_analyzer(events)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)

    def get_data(self):
        """
        :return: raw html of element for each event
        """
        try:
            self.driver.get(config.WINLINE_LIVE_URL)
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, config.WINLINE_EVENT_CLASS_NAME)))
            logger.info('Url %s successfully downloaded.' % config.WINLINE_LIVE_URL)
        except Exception as e:
            logger.error('Could not load url {url}: {err}'.format(url=config.WINLINE_LIVE_URL, err=e))
            return None

        uniq = set()
        events = []
        start_time = time.time()
        elapsed_time = 0
        previous_finds = []
        while elapsed_time < config.DATA_SEARCHING_TIMEOUT_SEC:
            # search all events placed in page
            try:
                current_finds = self.driver.find_elements_by_class_name(config.WINLINE_EVENT_CLASS_NAME)
            except Exception as e:
                logger.error('Could not find element with class name {class_name}: {err}'
                             .format(class_name=config.WINLINE_EVENT_CLASS_NAME, err=e))
                return None

            new_events = set(current_finds) - uniq
            uniq |= set(current_finds)

            if new_events:
                for el in new_events:
                    events += [self.parse_element_to_event(el)]
            else:
                logger.info('scrolled down....\nTotal find events - %d' % len(uniq))
                break

            # moving action
            try:
                logger.info('Moving to next document')
                if current_finds == previous_finds:
                    raise Exception
                # ActionChains(self.driver).move_to_element(last_element).perform()
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                previous_finds = current_finds
            except Exception as e:
                logger.error('Could not move to the provided element: {err}'.format(err=e))
                return events

            time.sleep(5)
            elapsed_time = time.time() - start_time
        else:
            logger.warning('get_data timeout %d exceeded, data has not been collected!!!'
                           % config.DATA_SEARCHING_TIMEOUT_SEC)
        return events

    def parse_element_to_event(self, element):
        try:
            url = element.get_attribute("href")
            title = element.get_attribute("title")
            first, second = title.split(" - ")
            logger.info('created: %s | %s - %s' % (first, second, url))
            return Event(first, second, url)
        except Exception as e:
            logger.error('Could not get attribute: {err}'.format(err=e))
            # TODO handle exception
            import ipdb; ipdb.set_trace()

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

    @staticmethod
    def telegram_connector(pairs):
        """

        :param pairs:
        :return:
        """
        # get url from each event
        for pair in pairs:
            urls = []
            for event in pair:
                urls.append(event.url)
            post_message_in_channel('\n'.join(urls))


if __name__ == "__main__":
    Controller().run()
    # post_message_in_channel('test message from app!!!')

