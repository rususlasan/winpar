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
from selenium.webdriver.common.action_chains import ActionChains


class Controller:

    FIREFOX_BIN = '/usr/bin/firefox'
    URL = config.WINLINE_LIVE_URL

    def __init__(self):
        logger.info('Start application...')
        pass

    def __init_variables(self):
        self.driver = webdriver.Chrome(executable_path='/home/ruslansh/soft/browsers/chromedriver')
        self.wait = WebDriverWait(self.driver, config.WAIT_ELEMENT_TIMEOUT_SEC)

    def __run(self):
        while True:
            data = self.get_data()
            pairs = self.data_analyzer(data)
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
        self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "table__item")))
        self.driver.get('https://winline.ru/now')

        uniq = set()
        while True:
            current_finds = self.driver.find_elements_by_class_name('table__item')
            uniq |= set(current_finds)  # add new element from current_finds to uniq
            new_events = set(current_finds) - uniq
            last_element = current_finds[-1]

            if not new_events:
                logger.info('scrolled down....\nTotal find events - %d' % len(uniq))
                break

            ActionChains(self.driver).move_to_element(last_element).perform()
            time.sleep(5)
            # TODO заменить "while True" на что-нибудь не бесконечное, отрегулировать sleep
        return list(uniq)

    @staticmethod
    def get_data_from_element_in_dom(webelements):
        urls = []
        for el in webelements:
            url = el.find_elements_by_xpath(".//a")[0]
            urls.append(url.get_attribute('innerHTML'))

        return urls

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
    print('START PROGRAMM')
    Controller.get_data()
    # post_message_in_channel('test message from app!!!')

