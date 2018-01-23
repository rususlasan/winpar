from config import logger


class Event:

    def __init__(self, first_member, second_member, url):
        self._first_member = first_member.strip()
        self._second_member = second_member.strip()
        self._url = url.strip()

    def __eq__(self, other):
        return {self.first_member, self.second_member} == {other.first_member, other.second_member}

    def eq_by_url(self, other):
        return self.url == other.url

    def __hash__(self):
        return ''.join(sorted([self.first_member, self.second_member])).__hash__()

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


