import os
import time

import telegram_pusher
import config

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

    FIREFOX_BIN = '/usr/local/bin'

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

    def parse_data_to_events(self, url):
        """
        get raw html, find some info and create Events object
        :param: url
        :return: array of Data object
        """
        html = self.get_raw_html(url)
        return [Event('', '', '')]

    def get_raw_html(self, url):
        """
        :param: url
        :return: raw html
        """
        # TODO add try, catch, logging
        os.environ['MOZ_HEADLESS'] = '1'
        driver = webdriver.Firefox(firefox_binary=self.FIREFOX_BIN)
        driver.get(self.URL)
        wait = WebDriverWait(driver, 10)
        # TODO choose optimal classname
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "statistic__team")))
        data = driver.page_source
        return data

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
            telegram_pusher.post_message_in_channel('\n'.join(urls))


time.sleep(5)
telegram_pusher.post_message_in_channel('test message from app!!!')

