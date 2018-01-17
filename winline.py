import os
import time

import config
from telegram_pusher import post_message_in_channel

from config import logger
from data import Event

from lxml import etree  # ????
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary  # ????
from selenium.webdriver.support.select import Select  # ????
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Controller:

    FIREFOX_BIN = '/usr/bin/firefox'
    URL = config.WINLINE_LIVE_URL

    def __init__(self):
        logger.info('Start application...')
        pass

    def run(self):
        while True:
            data = self.export_data(config.WINLINE_LIVE_URL)
            pairs = self.data_analyzer(data)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)

    def get_data(self):
        """
        :param: url
        :return: raw html
        """
        # TODO add try, catch, logging
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
        return

    def data_analyzer(self, events):
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
            post_message_in_channel('\n'.join(urls))


if __name__ == "__main__":
    time.sleep(5)
    post_message_in_channel('test message from app!!!')

