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
        self._bot_current_elapsed_time = time.time()
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
            logger.error('Could not initialized web driver. {err}'.format(err=e))
            return

        self.wait = WebDriverWait(self._driver, config.WAIT_ELEMENT_TIMEOUT_SEC)

    def __init_driver_in_separate_thread_with_attempts(self):
        current_attempt = 1
        while current_attempt <= config.WEBDRIEVR_INIT_ATTEMPTS_MAX:
            t = threading.Thread(target=self.__init_driver, args=())
            logger.info('Start thread for driver initializing, current_attempt = %d' % current_attempt)
            t.start()
            t.join(10)
            if t.is_alive():
                self.__run_bash_command(cmd='./scripts/stop_gecko.sh')
                current_attempt += 1
            else:
                break
        else:
            logger.error('Exit program due to driver has not been initialized due to errors above. ')
            self.__run_bash_command(cmd='./scripts/stop_gecko.sh')
            exit(111)

    def __destroy_driver(self):
        try:
            self._driver.quit()
        except Exception as e:
            logger.info('Could not destroy driver: {err}'.format(err=e))

        self.__run_bash_command(cmd='./scripts/stop_gecko.sh')

    @staticmethod
    def __run_bash_command(cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        (out, err) = p.communicate()
        ret_code = p.returncode
        if ret_code != 0:
            logger.info('CMD [{cmd}] finished with return code - {ret_code} and output below'
                        .format(cmd=cmd, ret_code=ret_code))
            if out:
                logger.info(out.decode('utf-8'))
            if err:
                logger.warning(err.decode('utf-8'))

    def __bot_checker(self, current_iteration=-1):
        if time.time() - self._bot_current_elapsed_time >= config.SEND_ALIVE_MESSAGE_TIMEOUT_SEC:
            self._bot.post_message_in_channel(message='I am still here! Current iteration #%d' % current_iteration,
                                              channel=config.WINLINE_ALIVE_MESSAGE_CHANNEL)
            self._bot_current_elapsed_time = time.time()

    def run(self):
        """
        infinite: init driver, search events, analyze results, destroy driver
        :return:
        """
        logger.info('Start infinite parsing...')
        counter = 1
        while True:
            logger.info('Begin iteration #%d...' % counter)

            self.__init_driver_in_separate_thread_with_attempts()
            events_mapping = self.get_data()
            self.__destroy_driver()

            if events_mapping:
                self.search_statistic_logging(curr_iter=counter, events_dict=events_mapping)

                for kind in events_mapping:
                    events = events_mapping[kind]
                    if events:
                        logger.debug('search duplicate in ')
                        pairs = self.data_analyzer(events)
                        if pairs:
                            logger.info('Same events were found({count}) in sport \"{kind}\". There are: \n{pairs}'
                                        .format(count=len(pairs), kind=kind), pairs)
                            self.telegram_connector(pairs=pairs, kind=kind)
                            # self._bot.post_message_in_channel('\n'.join([p.__repr__() for p in pairs]))

            else:
                logger.info('Empty dict was returned')

            self.__bot_checker(current_iteration=counter)

            time.sleep(config.DATA_EXPORT_TIMEOUT_SEC)
            counter += 1

    @staticmethod
    def search_statistic_logging(curr_iter, events_dict):
        mes = 'Iteration #{ci} results: '.format(ci=curr_iter)
        import collections
        od = collections.OrderedDict(sorted(events_dict.items()))
        for key in od:
            mes += '{title}({count}), '.format(title=key, count=len(od[key]))
        logger.info(mes[0:-2])

    def get_data(self):
        """
        :return: dict where, key - kind of sport title, value - related Event instances
        """
        try:
            self._driver.get(self.URL)
            logger.info('Url %s loaded successfully.' % self.URL)
        except Exception as e:
            logger.error('Could not load url {url}: {err}.'.format(url=config.WINLINE_LIVE_URL, err=e))
            return {}

        kind_of_sports = self.get_sports_elements()

        kind_of_sports_events_mapping = {}
        previous_element = None

        # for each title of sports search events
        for title in kind_of_sports:
            if previous_element:
                self.click_to_top_element(element=previous_element, title='PREV_EL')

            current_element = kind_of_sports[title]
            previous_element = current_element
            self.click_to_top_element(element=current_element, title=title)

            events = self.event_searching(title)             # MAIN LINE
            # events = self.event_searching_by_xpath(title)  # ALTERNATIVE

            # logger.info('For sport \"{title}\" found {count} events'.format(title=title, count=len(events)))
            kind_of_sports_events_mapping[title] = events

        return kind_of_sports_events_mapping

    def get_sports_elements(self):
        """

        :return: dict where: key - string title, value - related web element
        """
        kind_of_sports = {}
        try:
            self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, config.WINLINE_SPORT_KIND_CLASS_NAME)))
            sport_kind_items = self._driver.find_elements_by_class_name(config.WINLINE_SPORT_KIND_CLASS_NAME)  # sorting__item

            non_interest_title = ['Показать все', 'elst.TRANSLATION_ON_SITE', 'Трансляция на сайте', '']
            # collect sport titles
            for el in sport_kind_items:
                title = el.get_attribute("title")
                if title not in non_interest_title:
                    kind_of_sports[title] = el
        except Exception as e:
            logger.exception('Could not get titles element or parse some element: {err}'.format(err=e))

        return kind_of_sports

    # !!! MAIN LINE !!!
    def event_searching(self, title):
        """
        :param title: title of sport kind
        :return: list of parse events
        """
        uniq = set()
        events = []
        start_time = time.time()

        while time.time() - start_time < config.DATA_SEARCHING_TIMEOUT_SEC:
            # search all events placed in page
            time.sleep(3)
            ev = []
            try:
                # ev = self._driver.find_elements_by_xpath("//div[@class='statistic__wrapper']")
                # htmls = [el.get_attribute('innerHTML') for el in ev]
                ev = self._driver.find_elements_by_class_name(config.WINLINE_EVENT_CLASS_NAME)
            except Exception as e:
                logger.exception('Could not find element with class name {class_name}: {err}.'
                                 .format(class_name=config.WINLINE_EVENT_CLASS_NAME, err=e))
            finally:
                if not ev:
                    return events

            current_finds = set(ev)
            new_events = current_finds - uniq
            uniq |= current_finds

            if new_events:

                errors = 0
                for el in new_events:
                    event = self.parse_element_to_event(el)
                    if not event:
                        errors += 1
                        continue
                    events += [event]
                if errors:
                    logger.warning('Tried to parse {all} events but got {err} errors.'
                                   .format(all=len(new_events), err=errors))
            else:
                break

            self.scroll_to("document.body.scrollHeight")

        else:
            logger.warning('Timeout %d exceeded, maybe all or some data of \"%s\" has not been collected!!!'
                           % (config.DATA_SEARCHING_TIMEOUT_SEC, title))

        return events

    # !!! ALTERNATIVE !!!
    def event_searching_by_xpath(self, title):
        """
        :param title: title of sport kind
        :return: list of parse events
        """
        uniq = set()
        events = []
        start_time = time.time()
        htmls = []
        while time.time() - start_time < config.DATA_SEARCHING_TIMEOUT_SEC:
            time.sleep(2)  # config.DOCUMENT_SCROLL_TIMEOUT_SEC
            # search all events placed in page
            try:
                ev = self._driver.find_elements_by_xpath("//div[@class='statistic__wrapper']") # also may write 2 classes 'table ng_scope'
                for el in ev:
                    htmls.append(el.get_attribute('innerHTML'))
            except Exception as e:
                logger.exception('Could not find element with class name {class_name}: {err}.'
                                 .format(class_name=config.WINLINE_EVENT_CLASS_NAME, err=e))
            finally:
                if not ev:
                    logger.warning('For {title} could not find any HTML elements'.format(title=title))
                    return []

            current_finds = set(htmls)
            new_events = current_finds - uniq
            uniq |= current_finds

            if new_events:

                errors = 0
                for el in new_events:
                    event = self.parse_html_element_to_event(el)
                    if not event:
                        errors += 1
                        continue
                    events.append(event)
                if errors:
                    percent = errors * 100 / len(new_events)
                    logger.warning('Tried to parse {all} events but got {err} errors [{percent}%]'
                                   .format(all=len(new_events), err=errors, percent=percent))
            else:
                # logger.info('Scrolled down....\nTotal find events - %d' % len(uniq))
                break

            self.scroll_to("document.body.scrollHeight")

        else:
            logger.warning('Timeout %d exceeded, maybe all or some data of \"%s\" has not been collected!!!'
                           % (config.DATA_SEARCHING_TIMEOUT_SEC, title))

        return events

    # !!! ALTERNATIVE !!!
    @staticmethod
    def parse_html_element_to_event(html):
        import re
        findings = re.search(r'title=\".{1,200}\"\shref=\"(/.{1,50}){1,20}\">', html)
        if not findings:
            logger.warning('Could not parse HTML element via regex')
            return None

        title_and_href_parts = findings.group(0).split('href=')

        raw_title = title_and_href_parts[0].split('title')[1].strip()
        raw_title = raw_title.replace('\"', '')
        first, second = raw_title.split(' - ')

        raw_href = re.sub(r'[\">]', '', title_and_href_parts[1])
        url = 'https://winline.ru{appendix}'.format(appendix=raw_href)
        e = Event(first_member=first, second_member=second, url=url)
        logger.info('Created: %s' % e)
        return e

    def click_to_top_element(self, element, title):
        try:
            self.scroll_to(to='0')
            element.click()
            time.sleep(2)
        except Exception as e:
            logger.error('Could not click on the element with title {title} : {err}'.format(title=title, err=e))

    def scroll_to(self, to):
        script = "window.scrollTo(0, %s);" % to
        try:
            self._driver.execute_script(script)
        except Exception as e:
            logger.error('Could not execute javascript for scrolling: {err}'.format(err=e))
        time.sleep(2)

    def wait_ajax(self):
        curr = 0

        while curr < 10:
            res = self._driver.execute_script(script='return jQuery.active')
            if res != 0:
                logger.warning('There is/are {count} jQuery requests'.format(count=res))
                curr += 1
                time.sleep(0.5)
            else:
                break

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
            logger.info('Created: {}/{}:[{}]'.format(first, second, url))
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

        :param pairs: array of arrays: [[ev1, ev2],...]
        :return:
        """
        # get url from each event
        for pair in pairs:
            mes = '{kind}: {events)'.format('\n'.join([e.__repr__() for e in pair]))
            self._bot.post_message_in_channel(message=mes, channel=config.WINLINE_ALERT_CHANNEL)


if __name__ == "__main__":
    telegram_pusher = TelegramPusher(config.WINLINE_BOT_TOKEN, config.WINLINE_ALERT_CHANNEL_NAME)
    c = Controller(bot=telegram_pusher)
    c.run()
    # Controller(bot='STUB').run()

