import feedparser
import logging
import requests
from datetime import datetime, date, timedelta
import time
import re
from service.models import Article
from service.data_sources import NewsSource

class NewsSourceRss(NewsSource):

    def __init__(self,source_url):

        super().__init__(source_url)

    def collect_data_from_source_for_stock(self,stock):

        self.logger.info('Collecting articles via RSS')

        articles = []

        try:

            feed = feedparser.parse(self.construct_url(stock))

            for entry in feed.entries: 

                article_url = entry.link

                article_title = entry.title

                article_summary = entry.description

                publish_date_tuple = entry.published_parsed

                pub_date = '-'.join([str(x) for x in publish_date_tuple[0:3]])

                saved_article = Article.get_or_none(url=article_url)

                articles.append(Article(url=article_url,publish_date=pub_date,title=article_title,summary=article_summary))

        except Exception as e: self.logger.error(e)

        return articles

# ==================================================

class NewsSourceRegex(NewsSource):

    def __init__(self,source_url,collection_regex):

        super().__init__(source_url)

        self.collection_regex = collection_regex

    def collect_data_from_source_for_stock(self,stock):

        self.logger.info('Collecting Articles via Requests/Regex')

        articles = []

        try:

            headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}

            response = requests.get(self.construct_url(stock),headers = headers)

            response_text = response.text

            for match in re.search(self.collection_regex,response): articles.append(self.build_article_from_match(match))

        except Exception as e: self.logger.error(e)

        return articles

    def build_article_from_match(self,match):

        article_url = match.group(1).strip()

        article_title = match.group(2).strip()

        article_summary = match.group(3).strip()

        article_pub_date = self.parse_pub_date(match.group(4).strip())

        return Article(title=article_title,summary=article_summary,publish_date=article_pub_date,url=article_url)

    def parse_pub_date(self,raw_pub_date):

        pass

# ==================================================

class NewsSourceJSON(NewsSource):

    def __init__(self,source_url,api_key=''):

        super().__init__(source_url)

        self.api_key = api_key

    def collect_data_from_source_for_stock(self,stock):

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

    def construct_headers(self):

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

class TheStreet(NewsSourceRegex):

    def __init__(self):

        super().__init__('https://www.thestreet.com/quote/{}/details/news',r'<div class="news-list-compact__item"[\s\S]+?href="(.+?)"[\s\S]+?class="news-list-compact__headline ">(.+?)<[\s\S]+?<p class="news-list-compact__callout">(.+?)<[\s\S]+?<time datetime="(.+?)"')

    def parse_pub_date(self,raw_pub_date):

        return raw_pub_date.split('T')[0]

class DailyStocks(NewsSourceRegex):

    def __init__(self):

        super().__init__('http://search.dailystocks.com/?q={}',r'<div class="clear leftFloat result">[\s\S]+?href="(.+?)".+?> (.+?) <[\s\S]+?<span class="pubDate">(.+?) - </span>(.+?)</span>')

    def build_article_from_match(self,match):

        article_url = match.group(1).strip()

        article_title = match.group(2).strip()

        article_pub_date = self.parse_pub_date(match.group(3).strip())

        article_summary = match.group(4).strip()

        return Article(title=article_title,summary=article_summary,publish_date=article_pub_date,url=article_url)

    def parse_pub_date(self,raw_pub_date):

        return datetime.striptime(raw_pub_date,'%b %d, %Y').strftime('%Y-%m-%d')

## Json


class IEX(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://api.iextrading.com/1.0/stock/{}/news')

    def construct_headers(self):

        return None

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json: 

                article_url = article_data['url']
                
                pub_date = article_data['datetime'].split('T')[0]

                article_title = article_data['headline']

                article_summary = article_data['summary']

                articles.append(Article(url=article_url,publish_date=pub_date,title=article_title,summary=article_summary))

        except Exception as e: self.logger.error(e)

        return articles

class RobinHood(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://midlands.robinhood.com/news/{}/')

    def construct_headers(self,stock_param):

        return None

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json['results']: 

                article_url = article_data['url']
                
                pub_date = article_data['published_at'].split('T')[0]

                article_title = article_data['title']

                article_summary = article_data['summary']

                articles.append(Article(url=article_url,publish_date=pub_date,title=article_title,summary=article_summary))

        except Exception as e: self.logger.error(e)

        return articles

class NewsApi(NewsSourceJSON):

    def __init__(self):

        super().__init__('https://newsapi.org/v2/everything?q={}&sources=bloomberg,business-insider,cnbc,fortune,the-wall-street-journal&sortBy=publishedAt')

    def construct_headers(self,stock_param):

        return {'apiKey':'ac38010a4adf48169ac1d2493a433a29'}

    def convert_json_to_articles(self,response_json):

        articles = []

        try:

            for article_data in response_json['articles']: 

                article_url = article_data['url']
                
                pub_date = article_data['publishedAt'].split('T')[0]

                article_title = article_data['title']

                article_summary = article_data['description']

                articles.append(Article(url=article_url,publish_date=pub_date,title=article_title,summary=article_summary))

        except Exception as e: self.logger.error(e)

        return articles