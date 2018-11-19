import re

class NewsSource(object):

    def __init__(self,source_url,is_rss=True,article_regex=None):

        self.source_url = source_url

        self.is_rss = is_rss

        self.article_regex = article_regex

    def construct_url(self,stock_ticker):

        return self.source_url.format(stock_ticker)

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# Implementations

class Nasdaq(NewsSource):

    def __init__(self):

        super().__init__('http://articlefeeds.nasdaq.com/nasdaq/symbols?symbol={}')

class Zacks(NewsSource):

    def __init__(self):

        super().__init__('https://www.zacks.com/data_handler/stocks/stock_quote_news.php?provider=others&cat={}&limit=30&record=1',is_rss=False,article_regex=r'href=".*?\/\/(.+?)"')