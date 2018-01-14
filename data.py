

class Event:

    def __init__(self, first_member, second_member, url):
        self._first_member = first_member
        self._second_member = second_member
        self._url = url

    def __eq__(self, other):
        return self.first_member == other.first_member and self.second_member == other.second_member

    def eq_by_url(self, other):
        return self.url == other.url

    def __hash__(self) -> int:
        return (self.first_member + self.second_member).__hash__()

    def __repr__(self) -> str:
        return '%s - %s: %s' % (self.first_member, self.second_member, self.url)

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


