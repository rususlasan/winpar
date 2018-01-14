import time


class Controller:

    DATA_EXPORT_TIMEOUT_SEC = 60

    def __init__(self):
        pass

    def run(self):
        while(True):
            data = self.export_data('some_urp')
            pairs = self.data_analyzer(data)
            if pairs:
                self.telegram_connector(pairs)
            time.sleep(self.DATA_EXPORT_TIMEOUT_SEC)

    def export_data(self, url):
        """

        :param url:
        :return: array of Data object
        """
        return [url]

    def data_analyzer(self, *args):
        """
        search same pairs from data array
        :param args:
        :return: pairs or None
        """
        return [args]

    def telegram_connector(self, pairs):
        """

        :param pairs:
        :return: 
        """
        pass


