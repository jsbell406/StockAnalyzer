import re
import feedparser
import logging
import requests
from datetime import date, timedelta
import time
from service.models import Article

class NewsSource(object):

    def __init__(self,source_url):

        self.source_url = source_url

        self.logger = logging.getLogger()

        self.logger.info('Loaded NewsSource: ' + self.__str__())

    def construct_url(self,stock):

        return self.source_url.format(stock.ticker)

    def collect_articles(self,stock):

        pass

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# ==================================================

class NewsSourceRss(NewsSource):

    def __init__(self,source_url):

        super().__init__(source_url)

    def collect_articles(self,stock):

        self.logger.info('Collecting articles via RSS')

        articles = []

        try:

            feed = feedparser.parse(self.construct_url(stock))

            for entry in feed.entries: 

                article_url = entry.link

                publish_date_tuple = entry.published_parsed

                pub_date = '-'.join([str(x) for x in publish_date_tuple[0:3]])

                saved_article = Article.get_or_none(url=article_url)

                articles.append(saved_article if saved_article is not None else Article(url=article_url,publish_date=pub_date))

        except Exception as e: self.logger.error(e)

        return articles

# ==================================================

class NewsSourceRegex(NewsSource):

    def __init__(self,source_url,collection_regex):

        super().__init__(source_url)

        self.collection_regex = collection_regex

    def collect_articles(self,stock):

        self.logger.info('Collecting Articles via Requests/Regex')

        articles = []

        try:

            response = requests.get(self.construct_url(stock))

            response_text = response.text

            for article_url in re.findall(self.collection_regex,response_text): articles.append(Article(url=article_url))

        except Exception as e: self.logger.error(e)

        return articles

# ==================================================

class NewsSourceJSON(NewsSource):

    def __init__(self,source_url,api_key=''):

        super().__init__(source_url)

        self.api_key = api_key

    def collect_articles(self,stock):

        self.logger.info('Collecting Articles via JSON')

        articles = []

        try:
            
            for i in range(2):

                stock_param = stock.ticker if i == 0 else stock.name

                headers = self.construct_headers(stock_param)

                response = requests.get(self.construct_url(stock), headers=headers)

                response_json = response.json()

                articles += self.convert_json_to_articles(response_json)

                time.sleep(5)

        except Exception as e: self.logger.error(e)

        return articles

    def construct_headers(self,stock_param):

        pass

    def convert_json_to_articles(self,response_json):

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

class SwingTradeBot(NewsSourceRegex):

    def __init__(self):

        super().__init__('https://swingtradebot.com/equities/{}',r'<td><a target="_blank" rel="noopener" href="(.+?)"')

## Json

class NYT(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://api.nytimes.com/svc/search/v2/articlesearch.json','f8ed562261ea48a1871e9988f957a9c8')

    def construct_headers(self,stock_param):

          headers = {}

          headers['api-key'] = self.api_key

          headers['q'] = stock_param

          headers['begin_date'] = (date.today() - timedelta(days=10)).strftime('%Y%m%d')

          headers['sort'] = 'newest'

          headers['fl'] = 'web_url,pub_date'

          return headers

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json['response']['docs']: 

                article_url = article_data['web_url']
                
                pub_date = article_data['pub_date']

                articles.append(Article(url=article_url,publish_date=pub_date))

        except Exception as e: self.logger.error(e)

        return articles


class TheGuardian(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://content.guardianapis.com/search','233d61f8-ed2a-400d-ac40-7e5424e07cf6')

    def construct_headers(self,stock_param):

          headers = {}

          headers['section'] = 'business'

          headers['from-date'] = (date.today() - timedelta(days=10)).strftime('%Y%m%d')

          headers['order-by'] = 'newest'

          headers['q'] = stock_param

          headers['api-key'] = self.api_key

          return headers

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json['response']['results']: 

                article_url = article_data['webUrl']
                
                pub_date = article_data['webPublicationDate']

                articles.append(Article(url=article_url,publish_date=pub_date))

        except Exception as e: self.logger.error(e)

        return articles


class IEX(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://api.iextrading.com/1.0/stock/{}/news')

    def construct_headers(self,stock_param):

        return None

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json: 

                article_url = article_data['url']
                
                pub_date = article_data['datetime']

                articles.append(Article(url=article_url,publish_date=pub_date))

        except Exception as e: self.logger.error(e)

        return articles


