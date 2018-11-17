import re

class NewsSource(object):

    def __init__(self,source_url,source_regex):

        self.source_url = source_url

        self.source_regex = source_regex

    def construct_url(self,stock_ticker):

        return self.source_url.format(stock_ticker)

    def gather_article_urls(self,text):

        return re.findall(self.source_regex,text)

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# Implementations

class MarketWatch(NewsSource):

    def __init__(self):

        super().__init__('https://www.marketwatch.com/investing/stock/{}',r'<div class="article__content">[\s\S]+?<a class="link".+?href="(.+?)"')

class SeekingAlpha(NewsSource):

    def __init__(self):

        super().__init__('https://seekingalpha.com/symbol/{}',r'<div class="symbol_article".+?<a href="(.+?)"')

    def gather_article_urls(self,text):

        article_urls = re.findall(self.source_regex,text)

        for index,article_url in enumerate(article_urls):

            if '://' not in article_url: article_urls[index] = 'https://seekingalpha.com/' + article_url

        return article_urls

class Benzinga(NewsSource):

    def __init__(self):

        super().__init__('https://www.benzinga.com/stock/{}',r'<li class="story"[\s\S]+?<a href="(.+?)"')