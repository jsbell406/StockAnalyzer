import re
import feedparser
import logging
import requests
from datetime import date, timedelta
from service.models import StockArticle

class NewsSource(object):

    def __init__(self,source_url):

        self.source_url = source_url

        self.logger = logging.getLogger()

        self.logger.info('Loaded NewsSource: ' + self.__str__())

    def construct_url(self,stock_ticker):

        return self.source_url.format(stock_ticker)

    def collect_articles(self,stock_ticker):

        pass

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# ==================================================

class NewsSourceRss(NewsSource):

    def __init__(self,source_url):

        super().__init__(source_url)

    def collect_articles(self,stock_ticker):

        self.logger.info('Collecting articles via RSS')

        stock_articles = []

        try:

            feed = feedparser.parse(self.construct_url(stock_ticker))

            for entry in feed.entries: stock_articles.append(StockArticle(stock_ticker=stock_ticker,url=entry.link))

        except Exception as e: self.logger.error(e)

        return stock_articles

# ==================================================

class NewsSourceRegex(NewsSource):

    def __init__(self,source_url,collection_regex):

        super().__init__(source_url)

        self.collection_regex = collection_regex

    def collect_articles(self,stock_ticker):

        self.logger.info('Collecting Articles via Requests/Regex')

        stock_articles = []

        try:

            response = requests.get(self.construct_url(stock_ticker))

            response_text = response.text

            for stock_article_url in re.findall(self.collection_regex,response_text): stock_articles.append(StockArticle(stock_ticker=stock_ticker,url=stock_article_url))

        except Exception as e: self.logger.error(e)

        return stock_articles

# ==================================================

class NewsSourceJSON(NewsSource):

    def __init__(self,source_url,api_key=''):

        super().__init__(source_url)

        self.api_key = api_key

    def collect_articles(self,stock_ticker):

        self.logger.info('Collecting Articles via JSON')

        stock_articles = []

        try:

            headers = self.construct_headers(stock_ticker)

            response = requests.get(self.construct_url(stock_ticker)) if headers is None else requests.get(self.construct_url(stock_ticker), headers)

            response_json = response.json()

            stock_articles = self.convert_json_to_articles(stock_ticker,response_json)

        except Exception as e: self.logger.error(e)

        return stock_articles

    def construct_headers(self,stock_ticker):

        pass

    def convert_json_to_articles(self,stock_ticker,response_json):

        pass

# ==================================================

# Implementations


## RSS

class Nasdaq(NewsSourceRss):

    def __init__(self):

        super().__init__('http://articlefeeds.nasdaq.com/nasdaq/symbols?symbol={}')


## Regex

class Zacks(NewsSourceRegex):

    def __init__(self):

        super().__init__('https://www.zacks.com/data_handler/stocks/stock_quote_news.php?provider=others&cat={}&limit=30&record=1',r'href=".*?\/\/(.+?)"')


## Json

class NYT(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://api.nytimes.com/svc/search/v2/articlesearch.json?','f8ed562261ea48a1871e9988f957a9c8')

    def construct_headers(self,stock_ticker):

          headers = {}

          headers['api-key'] = self.api_key

          headers['q'] = stock_ticker

          headers['begin_date'] = (date.today() - timedelta(days=10)).strftime('%Y%m%d')

          headers['sort'] = 'newest'

          headers['fl'] = 'web_url,pub_date'

          return headers

    def convert_json_to_articles(self,stock_ticker,response_json):

        stock_articles = []

        try:

            for article in response_json['response']['docs']: 

                web_url = article['web_url']
                
                publish_date = date.fromtimestamp(article['pub_date'])

                stock_article = StockArticle(stock_ticker=stock_ticker,url=web_url)

                stock_article.publish_date = publish_date

                stock_articles.append(stock_article)

        except Exception as e: self.logger.error(e)

        return stock_articles


class TheGuardian(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://content.guardianapis.com/search?section=business&from-date={}&order-by=newest&q={}&api-key={}','233d61f8-ed2a-400d-ac40-7e5424e07cf6')

    def construct_headers(self,stock_ticker):

          headers = {}

          headers['section'] = 'business'

          headers['from-date'] = (date.today() - timedelta(days=10)).strftime('%Y%m%d')

          headers['order-by'] = 'newest'

          headers['q'] = stock_ticker

          headers['api-key'] = self.api_key

          return headers

    def convert_json_to_articles(self,stock_ticker,response_json):

        stock_articles = []

        try:

            for article in response_json['response']['results']: 

                web_url = article['webUrl']
                
                publish_date = date.fromtimestamp(article['webPublicationDate'])

                stock_article = StockArticle(stock_ticker=stock_ticker,url=web_url)

                stock_article.publish_date = publish_date

                stock_articles.append(stock_article)

        except Exception as e: self.logger.error(e)

        return stock_articles


class IEX(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://api.iextrading.com/1.0/stock/{}/news')

    def convert_json_to_articles(self,stock_ticker,response_json):

        stock_articles = []

        try:

            for article in response_json: 

                web_url = article['url']
                
                publish_date = date.fromtimestamp(article['datetime'])

                stock_article = StockArticle(stock_ticker=stock_ticker,url=web_url)

                stock_article.publish_date = publish_date

                stock_articles.append(stock_article)

        except Exception as e: self.logger.error(e)

        return stock_articles


