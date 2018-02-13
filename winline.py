import os
import time
import threading
import subprocess

import config
from telegram_pusher import TelegramPusher

from config import logger
from data import Event

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Controller:

    FIREFOX_BIN = config.FIREFOX_BIN
    # FIREFOX_EXECUTABLE = '/usr/bin/geckodriver'
    URL = config.WINLINE_LIVE_URL

    def __init__(self, bot):
        logger.info('==================== Start application... ====================')
        self._bot = bot
        self._bot_check_elapsed_time = time.time()
        os.environ['MOZ_HEADLESS'] = '1'

    @property
    def driver(self):
        return self._driver

    @property
    def bot(self):
        return self._bot

    def __init_driver(self):
        try:
            self._driver = webdriver.Firefox(firefox_binary=self.FIREFOX_BIN,
                                             executable_path='/usr/bin/geckodriver')
            logger.info('Driver init successfully.')
        except Exception as e:
            logger.exception('Could not initialize driver: {err}.'.format(err=e))

        self.wait = WebDriverWait(self._driver, config.WAIT_ELEMENT_TIMEOUT_SEC)

    def __init_driver_in_separate_thread_with_attempts(self):
        current_attempt = 1
        while current_attempt <= config.WEBDRIEVR_INIT_ATTEMPTS_MAX:
            t = threading.Thread(target=self.__init_driver, args=())
            logger.info('Start thread for driver initializing, current_attempt = %d' % current_attempt)
            t.start()
            t.join(10)
            # time.sleep(0.5)
            if t.is_alive():
                logger.warning('Driver is still has not been initializing, run bash script and terminate process.')
                self.__run_bash_command(cmd='./stop_gecko.sh')
                current_attempt += 1
            else:
                break
        else:
            logger.error('Exit program due to webdriver has not been initialized cause errors above. '
                         'Will try find and kill geckodriver and firefox processes...')
            self.__run_bash_command(cmd='./stop_gecko.sh')
            exit(111)

    def __destroy_driver(self):
        try:
            self._driver.quit()
            logger.info('Driver quit successfully. Will try find and kill geckodriver and firefox processes...')
            self.__run_bash_command(cmd='./stop_gecko.sh')
            ret_code = os.system('/root/git_project/winpar/stop_gecko.sh')
            logger.info('stop_gecko.sh finished with ret_code=%d' % ret_code)
        except Exception as e:
            logger.info('Could not destroy driver: {err}'.format(err=e))

    @staticmethod
    def __run_bash_command(cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (out, err) = p.communicate()
        ret_code = p.returncode
        logger.info('CMD [{cmd}] finished with return code - {ret_code} and output below'
                    .format(cmd=cmd, ret_code=ret_code))
        if out:
            logger.info(out.decode('utf-8'))
        if err:
            logger.warning(err.decode('utf-8'))

    def __bot_checker(self, current_iteration=-1):
        if time.time() - self._bot_check_elapsed_time >= config.SEND_ALIVE_MESSAGE_TIMEOUT_SEC:
            self._bot.post_message_in_channel('I am still here! Current iteration #%d' % current_iteration)
            self._bot_check_elapsed_time = time.time()

    def run(self):
        logger.info('Start infinite parsing...')
        counter = 1
        while True:
            logger.info('Begin iteration #%d...' % counter)
            counter += 1
            kind_of_sports_events_mapping = self.get_data()

            for kind in kind_of_sports_events_mapping:
                events = kind_of_sports_events_mapping[kind]
                if events:
                    pairs = self.data_analyzer(events)
                    if pairs:
                        logger.info('Same events were found({count}) in sport \"{kind}\". There are: \n{pairs}'
                                    .format(count=len(pairs), kind=kind), pairs)
                        self.telegram_connector(pairs=pairs, kind=kind)
                        # self._bot.post_message_in_channel('\n'.join([p.__repr__() for p in pairs]))
                else:
                    logger.warning('events is empty due to errors above!!!')

            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)
            self.__bot_checker(current_iteration=counter)

    def get_data(self):
        """
        :return: dict where
                            key - kind of sports,
                            value - list of Event objects or empty list.
        Empty dict may be returned
        """
        self.__init_driver_in_separate_thread_with_attempts()
        try:
            self._driver.get(self.URL)
            logger.info('Url %s successfully loaded.' % self.URL)
        except Exception as e:
            logger.error('Could not load url {url}: {err}.'.format(url=config.WINLINE_LIVE_URL, err=e))
            self.__destroy_driver()
            return []

        kind_of_sports = self.get_kind_of_sports_elements()
        if not kind_of_sports:
            return []

        kind_of_sports_events_mapping = {}
        previous_element = None

        # for each title of sports search events
        for title in kind_of_sports:
            self.scroll_to('0')  # scroll to the top of window
            time.sleep(1)
            try:
                if previous_element:
                    previous_element.click()
                previous_element = kind_of_sports[title]
                kind_of_sports[title].click()
            except Exception as e:
                logger.error('Want to click {title}. Could not click on the element : {err}'.format(title=title, err=e))
                continue

            events = self.event_searching(title)
            logger.info('For sport \"{title}\" found {count} events'.format(title=title, count=len(events)))
            kind_of_sports_events_mapping[title] = events

        self._driver.quit()
        logger.info('End iteration, count of find events see below')

        exit(0)
        return kind_of_sports_events_mapping

    def get_kind_of_sports_elements(self):
        """

        :return: dict where: key - string title, value - related web element
        """
        kind_of_sports = {}
        try:
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, config.WINLINE_SPORT_KIND_CLASS_NAME)))
            sport_kind_items = self._driver.find_elements_by_class_name(config.WINLINE_SPORT_KIND_CLASS_NAME)

            non_interest_title = ['Показать все', 'elst.TRANSLATION_ON_SITE', 'Трансляция на сайте']
            # collect sport titles
            for el in sport_kind_items:
                title = el.get_attribute("title")
                if title not in non_interest_title:
                    kind_of_sports[title] = el
        except:
            logger.exception('Error occurred: ')

        return kind_of_sports

    def event_searching(self, title):
        """
        :param title: title of sport kind
        :return: list of parse events
        """
        uniq = set()
        events = []
        start_time = time.time()

        while time.time() - start_time < config.DATA_SEARCHING_TIMEOUT_SEC:
            time.sleep(2)  # config.DOCUMENT_SCROLL_TIMEOUT_SEC
            # search all events placed in page
            try:
                ev = self._driver.find_elements_by_class_name(config.WINLINE_EVENT_CLASS_NAME)
                current_finds = set(ev)
                logger.info('%s find %d events' % (title, len(current_finds)))
            except Exception as e:
                logger.error('Could not find element with class name {class_name}: {err}'
                             .format(class_name=config.WINLINE_EVENT_CLASS_NAME, err=e))
                self.__destroy_driver()
                return []

            new_events = current_finds - uniq
            uniq |= current_finds

            if new_events:

                errors = 0
                for el in new_events:
                    event = self.parse_element_to_event(el)
                    if not event:
                        errors += 1
                        continue
                    events.append(event)
                if errors:
                    percent = errors * 100 / len(new_events)
                    logger.warning('Tried to parse {all} events but got {err} errors [{percent}%]'
                                   .format(all=len(new_events), err=errors, percent=percent))
            else:
                logger.info('Scrolled down....\nTotal find events - %d' % len(uniq))
                break

            self.scroll_to("document.body.scrollHeight")

        else:
            logger.warning('Timeout %d exceeded, maybe all or some data of %s has not been collected!!!'
                           % (config.DATA_SEARCHING_TIMEOUT_SEC, title))

        return events

    def scroll_to(self, to):
        script = "window.scrollTo(0, %s);" % to
        try:
            self._driver.execute_script(script)
        except Exception as e:
            logger.error('Could not execute javascript for scrolling: {err}'.format(err=e))

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
            # logger.info('Created: {}/{}:[{}]'.format(first, second, url))
            return Event(first, second, url)
        except Exception as e:
            logger.error('Could not took some info from element: {err}. None will be returned.'.format(err=e))
            return None

    @staticmethod
    def data_analyzer(events):
        """
        search same pairs from events array
        :param events: array of Event objects
        :return: array of arrays, each tuple a same Event object or None
        """
        res = []

        seen = set()
        seen_add = seen.add
        seen_twice = set(x for x in events if x in seen or seen_add(x))

        for duplicate in seen_twice:
            same_events = []
            for e in events:
                if duplicate == e and duplicate.url != e.url:
                    same_events.append(e)

            if same_events:
                same_events.append(duplicate)
                res.append(same_events)

        return res

    def telegram_connector(self, pairs, kind):
        """

        :param pairs:
        :param kind: kind of sport
        :return:
        """
        # get url from each event
        for pair in pairs:
            urls = []
            for event in pair:
                urls.append(event.url)
            urls = '\n'.join(urls)
            message = '{kind}: {urls}'.format(kind=kind, urls=urls)
            self._bot.post_message_in_channel(message)


if __name__ == "__main__":
    telegram_pusher = TelegramPusher(config.WINLINE_BOT_TOKEN, config.WINLINE_ALERT_CHANNEL_NAME)
    c = Controller(bot=telegram_pusher)
    c.run()
