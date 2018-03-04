class Event:

    def __init__(self, first_member, second_member, url):
        self._first_member = first_member.strip()
        self._second_member = second_member.strip()
        self._url = url.strip()
        self.id = self.url.split('/')[-2]

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
        return {self.first_member, self.second_member} == {other.first_member, other.second_member}

    def __hash__(self):
        return ''.join(sorted([self.first_member, self.second_member])).__hash__()

    def __repr__(self):
        return '{}/{}:{}'.format(self.first_member, self.second_member, self.url)

    @property
    def first_member(self):
        return self._first_member

    @property
    def second_member(self):
        return self._second_member

    @property
    def url(self):
        return self._url

    def get_id(self):
        return self.id

    def eq_with_include(self, other, is_url_comparing=False):
        """
        compare with check that some str maybe in another string ("Some Team" == "Some Team(some info)"),
        also compare url if needed
        :param other: Event instance for comparing
        :param is_url_comparing: if True - Event's urls will be compared too
        :return:
        """
        url_influence = True if not is_url_comparing else self.url == other.url

        f1 = self.first_member
        s1 = self.second_member
        f2 = other.first_member
        s2 = other.second_member

        return ((f1 in f2 or f2 in f1) and (s1 in s2 or s2 in s1)) or \
               ((f1 in s2 or s2 in f1) and (s1 in f2 or f2 in s1)) and url_influence
