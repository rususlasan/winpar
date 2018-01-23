from config import logger


class Event:

    def __init__(self, first_member, second_member, url):
        self._first_member = first_member.strip()
        self._second_member = second_member.strip()
        self._url = url.strip()

    def __eq__(self, other):
        """
        straight = self.first_member == other.first_member and self.second_member == other.second_member
        revert = self.first_member == other.second_member and self.second_member == other.first_member
        # if compare two same events with different urls, log it info
        if self.url != other.url:
            how = 'STRAIGHT' if straight else 'REVERT'
            logger.info('Found same events with {how} comparing. {first_event} and {second_event}'
                        .format(how=how, first_event=self, second_event=other))

        return straight or revert
        """
        return self.first_member == other.first_member and self.second_member == other.second_member or \
            self.first_member == other.second_member and self.second_member == other.first_member

    def __hash__(self):
        return ' '.join(sorted([self.first_member, self.second_member])).__hash__()

    def __repr__(self):
        return '{} - {}: {}'.format(self.first_member, self.second_member, self.url)

    @property
    def first_member(self):
        return self._first_member

    @property
    def second_member(self):
        return self._second_member

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self.url = url


