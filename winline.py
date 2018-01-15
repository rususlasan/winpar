import os
import time

import telegram_pusher

from data import Event

from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Controller:

    DATA_EXPORT_TIMEOUT_SEC = 60
    URL = 'https://winline.ru/now/'
    FIREFOX_BIN = '/usr/local/bin'

    def __init__(self):
        pass

    def run(self):
        while True:
            data = self.export_data('some_urp')
            pairs = self.data_analyzer(data)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(self.DATA_EXPORT_TIMEOUT_SEC)

    def export_data(self, url):
        """
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

        print ('seen_twice = %s' % seen_twice)

        for same in seen_twice:
            pairs = ()
            for e in events:
                if e == same and e.url != same.url:
                    pairs = pairs + (e, )
                    pairs = pairs + (same, )
            res.append(pairs)

            # TODO if same object more than 2, works bad, see example_data


        return res

    def telegram_connector(self, pairs):
        """

        :param pairs:
        :return:
        """
        pass


c = Controller()
example_data = [Event('1', 'wer', 'GGGGG'),
      Event('4', 'wer', 'http'),
      Event('9', 'wer', 'G'),
      Event('1', 'wer', 'ffff'),
      Event('9', 'wer', 'bbb'),
      Event('11', 'wer', 'vvv'),
      Event('1', 'wer', 'sss')]

print(c.data_analyzer(example_data))

time.sleep(5)
telegram_pusher.post_message_in_channel('TEST!!!')

