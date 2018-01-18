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
        logger.info('Start application...')
        self.driver = webdriver.Chrome(executable_path='/home/ruslansh/soft/browsers/chromedriver')
        self.wait = WebDriverWait(self.driver, config.WAIT_ELEMENT_TIMEOUT_SEC)
        # self.driver.implicitly_wait(30) # seconds

    def __run(self):
        while True:
            data = self.get_data2()     # list of raw HTML of each element
            events = self.__parse_raw_html_to_events(data)
            pairs = self.data_analyzer(events)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)

    def get_data(self):
        """
        :param: url
        :return: raw html
        """
        os.environ['MOZ_HEADLESS'] = '1'
        driver = webdriver.Firefox(firefox_binary=self.FIREFOX_BIN)
        driver.get(self.URL)
        wait = WebDriverWait(driver, 5)
        # TODO choose optimal classname
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "statistic__team")))
        # import ipdb; ipdb.set_trace()
        # наброски:
        driver.find_elements_by_class_name('table_item')  # Поиск всех ключевых элементов на странице
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # эта штука промотает внис ровно на один экран (аналог Pagedown)
        driver.find_element_by_class_name('partners brand')  # Имя класса футера. Будем скроллить до тех пор пока футер не будет виден

    def get_data2(self):
        """

        :return: raw element of each event
        """
        self.driver.get('https://winline.ru/now')
        # wait until element is visible in DOM
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, config.WINLINE_EVENT_CLASS_NAME)))

        uniq = set()
        uniq_raw_html = set()
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < config.DATA_EXPORT_TIMEOUT_SEC:
            current_finds = self.driver.find_elements_by_class_name('table__item')
            uniq |= set(current_finds)  # add new element from current_finds to uniq

            new_events = set(current_finds) - uniq
            if new_events:
                for element in uniq:
                    uniq_raw_html.add(element.get_attribute('innerHTML'))
            else:
                logger.info('scrolled down....\nTotal find events - %d' % len(uniq))
                break

            shift = 4 if len(current_finds) > 8 else len(current_finds)/3  # why 8, why /3 ????
            last_element = current_finds[-shift]

            ActionChains(self.driver).move_to_element(last_element).perform()
            # time.sleep(5)
            elapsed_time = time.time() - start_time
        else:
            logger.warning('get_data timeout %d exceeded, data has not been collected!!!'
                           % config.DATA_SEARCHING_TIMEOUT_SEC)
        return list(uniq_raw_html)

    def __parse_raw_html_to_events(self, raw_html):
        return [Event('', '', '')]

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
    Controller.get_data()
    # post_message_in_channel('test message from app!!!')

