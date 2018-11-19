import re

class NewsSource(object):

    def __init__(self,source_url):

        self.source_url = source_url

    def construct_url(self,stock_ticker):

        return self.source_url.format(stock_ticker)

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# Implementations

class Nasdaq(NewsSource):

    def __init__(NewsSource):

        super().__init__('http://articlefeeds.nasdaq.com/nasdaq/symbols?symbol={}')