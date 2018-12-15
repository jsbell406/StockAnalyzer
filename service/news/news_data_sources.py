import feedparser
import logging
import requests
from datetime import datetime, date, timedelta
import time
import re
from service.data_sources.models import Article
from service.data_sources.data_sources import NewsDataSource
from service.news.api_keys import news_api_key

class RssNewsDataSource(NewsDataSource):
    '''A Rss Source for News-Specific Data.
    
    Arguments:
        NewsDataSource {NewsDataSource} -- The NewsDataSource class, which extends DataSource.
    '''

    def __init__(self,source_url):
        '''Constructor
        
        Arguments:
            source_url {str} -- The base url the RssNewsDataSource should use when gathering data, prepared for formatting. E.g. 'rssfeed.com/{}'
        '''

        super().__init__(source_url)

    def collect_data_from_source_for_stock(self,stock):
        '''Collects data from the NewsDataSource for the given Stock. Overidden from DataSource.
        
        Arguments:
            stock {Stock} -- The Stock to gather the data for.

        Returns:
            list -- A list of Articles, built from the data collected via the RSS feed.
        '''

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

class RegexNewsDataSource(NewsDataSource):
    '''A Source of News-Specific data, collected by applying regex to a webpage's html.
    
    Arguments:
        NewsDataSource {NewsDataSource} -- The NewsDataSource class, which extends DataSource.
    '''

    def __init__(self,source_url,collection_regex):
        '''Constructor
        
        Arguments:
            source_url {str} -- The base url the RegexNewsDataSource should use when gathering data, prepared for formatting. E.g. 'newssite.com/{}'
            collection_regex {str} -- The regex string the RegexNewsDataSource will use when extracting data from the source's webpage html.
        '''

        super().__init__(source_url)

        self.collection_regex = collection_regex

    def collect_data_from_source_for_stock(self,stock):
        '''Collects data from the NewsDataSource for the given Stock. Overrides the same method in DataSource.
        
        Arguments:
            stock {Stock} -- The Stock to gather the data for.
        
        Returns:
            list -- A list of Articles, built from the data extracted from the webpage's html via regex.
        '''

        self.logger.info('Collecting Articles via Requests/Regex')

        articles = []

        try:
            # Collect the webpage html
            response = requests.get(self.construct_url(stock),headers = self.headers)

            if response.status_code == 200:

                # Extract the data, build Articles from it and save them.
                for match in re.findall(self.collection_regex,response.text): articles.append(self.build_article_from_match(match))

            else: self.logger.error('Status Code for {} was not 200: {}'.format(self.__str__(),response.status_code))

        except Exception as e: self.logger.error(e)

        return articles

    def build_article_from_match(self,match):
        '''Builds an Article from a re.Match.
        
        Arguments:
            match {re.Match} -- The re.Match object that contains the data to be converted to an Article. See: https://docs.python.org/3/library/re.html#match-objects
        
        Returns:
            Article -- The Article built from the data contained in the re.Match object.
        '''

        article_url = match[0].strip()

        article_title = match[1].strip()

        article_summary = match[2].strip()

        article_pub_date = self.convert_pub_date(match[3].strip())

        return Article(title=article_title,summary=article_summary,publish_date=article_pub_date,url=article_url)

    def convert_pub_date(self,raw_pub_date):
        '''Converts the raw Article 'published date' to a version savable in the database.
        
        Arguments:
            raw_pub_date {str} -- The raw Article publish date to parse.
        '''

        pass

# ==================================================

class JsonNewsDataSource(NewsDataSource):
    '''A Json Data Source for News-Specific data.
    
    Arguments:
        NewsDataSource {NewsDataSource} -- The NewsDataSource class, which extends DataSource.
    '''

    def __init__(self,source_url):
        '''Constructor
        
        Arguments:
            source_url {str} -- The base url the JsonNewsDataSource should use when gathering data, prepared for formatting. E.g. 'jsonsource.com/{}'
        '''

        super().__init__(source_url)

    def collect_data_from_source_for_stock(self,stock):
        '''Collects data from the NewsDataSource for the given Stock. Overrides the same method in DataSource.
        
        Arguments:
            stock {Stock} -- The Stock to gather the data for.
        
        Returns:
            list -- A list of Articles, built from the collected json.
        '''

        self.logger.info('Collecting Articles via JSON')

        articles = []

        try:
            # Collect the json
            response = requests.get(self.construct_url(stock))

            # Collect the JSON, convert to Article objects and save it.
            if response.status_code == 200: articles = self.convert_json_to_articles(response.json())

            else: self.logger.error('Status Code for {} was not 200: {}'.format(self.__str__(),response.status_code))

        except Exception as e: self.logger.error(e)

        return articles

    def convert_json_to_articles(self,response_json):
        '''Converts the provided JSON to a list of Articles.
        
        Arguments:
            response_json {str} -- The JSON content to convert.
        '''

        pass

# ==================================================

# Implementations


## RSS

class Nasdaq(RssNewsDataSource):
    '''Nasdaq.com's Stock-specific RSS feed, used as a DataSource.
    
    Arguments:
        RssNewsDataSource {RssNewsDataSource} -- The RssNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('http://articlefeeds.nasdaq.com/nasdaq/symbols?symbol={}')


## Regex

class TheStreet(RegexNewsDataSource):
    '''TheStreet.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RegexNewsDataSource {RegexNewsDataSource} -- The RegexNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://www.thestreet.com/quote/{}/details/news',r'<div class="news-list-compact__item"[\s\S]+?href="(.+?)"[\s\S]+?class="news-list-compact__headline ">(.+?)<[\s\S]+?<p class="news-list-compact__callout">(.+?)<[\s\S]+?<time datetime="(.+?)"')

    def convert_pub_date(self,raw_pub_date):
        '''Converts the raw Article 'published date' to a version savable in the database. Overrides the same method in RegexNewsDataSource. 
        
        Arguments:
            raw_pub_date {str} -- The raw Article publish date to parse.
        '''

        return raw_pub_date.split('T')[0]

class DailyStocks(RegexNewsDataSource):
    '''DailyStocks.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RegexNewsDataSource {RegexNewsDataSource} -- The RegexNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('http://search.dailystocks.com/?q={}',r'<div class="clear leftFloat result">[\s\S]+?href="(.+?)".+?> (.+?) <[\s\S]+?<span class="pubDate">(.+?) - </span>(.+?)</span>')

    def build_article_from_match(self,match):
        '''Builds an Article from a re.Match. Overrides the same method in RegexNewsDataSource.
        
        Arguments:
            match {re.Match} -- The re.Match object that contains the data to be converted to an Article. See: https://docs.python.org/3/library/re.html#match-objects
        
        Returns:
            Article -- The Article built from the data contained in the re.Match object.
        '''

        article_url = match[0].strip()

        article_title = match[1].strip()

        article_pub_date = self.convert_pub_date(match[2].strip())

        article_summary = match[3].strip()

        return Article(title=article_title,summary=article_summary,publish_date=article_pub_date,url=article_url)

    def convert_pub_date(self,raw_pub_date):
        '''Converts the raw Article 'published date' to a version savable in the database. Overrides the same method in RegexNewsDataSource. 
        
        Arguments:
            raw_pub_date {str} -- The raw Article publish date to parse.
        '''
        return datetime.strptime(raw_pub_date,'%b %d, %Y').strftime('%Y-%m-%d')

## Json


class IEX(JsonNewsDataSource):
    '''The IEX API DataSource.
    
    Arguments:
        JsonNewsDataSource {JsonNewsDataSource} -- The JsonNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://api.iextrading.com/1.0/stock/{}/news')

    def convert_json_to_articles(self,response_json):
        '''Converts the provided JSON to a list of Articles. Overrides the same method in JsonNewsDataSource.
        
        Arguments:
            response_json {str} -- The JSON content to convert.
        '''

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

class RobinHood(JsonNewsDataSource):
    '''The RobinHood DataSource.
    
    Arguments:
        JsonNewsDataSource {JsonNewsDataSource} -- The JsonNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://midlands.robinhood.com/news/{}/')

    def convert_json_to_articles(self,response_json):
        '''Converts the provided JSON to a list of Articles. Overrides the same method in JsonNewsDataSource.
        
        Arguments:
            response_json {str} -- The JSON content to convert.
        '''

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

class NewsApi(JsonNewsDataSource):
    '''The NewsApi DataSource.
    
    Arguments:
        JsonNewsDataSource {JsonNewsDataSource} -- The JsonNewsDataSource class, which extends NewsDataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://newsapi.org/v2/everything?q={}&sources=bloomberg,business-insider,cnbc,fortune,the-wall-street-journal&sortBy=publishedAt&apiKey=' + news_api_key)

    def convert_json_to_articles(self,response_json):
        '''Converts the provided JSON to a list of Articles. Overrides the same method in JsonNewsDataSource.
        
        Arguments:
            response_json {str} -- The JSON content to convert.
        '''

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