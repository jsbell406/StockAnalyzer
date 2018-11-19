import feedparser
import requests
import re
import logging
from service.stock_article import StockArticle
from service.news_source import Nasdaq, Zacks

class StockNewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq(),Zacks()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_articles_for_stock(self,stock_ticker):

        self.logger.info('Collecting articles for ' + stock_ticker)

        stock_articles = []

        for news_source in self.news_sources:

            self.logger.debug('Collecting articles for {} via {}'.format(stock_ticker,news_source))

            news_source_url = news_source.construct_url(stock_ticker)

            if news_source.is_rss: stock_articles = self.__gather_articles_rss(stock_ticker,news_source_url)

            else: stock_articles = self.__gather_articles_requests(stock_ticker,news_source_url,news_source.article_regex)

        return stock_articles

    def __gather_articles_rss(self,stock_ticker,news_source_url):

        stock_articles = []

        try:

            feed = feedparser.parse(news_source_url)

            for entry in feed.entries: stock_articles.append(StockArticle(stock_ticker,entry.link))
            
        except Exception as e: self.logger.error(e)

        return stock_articles

    def __gather_articles_requests(self,stock_ticker,news_source_url,article_regex):

        stock_articles = []

        try:

            response = requests.get(news_source_url)

            response_text = response.text

            for stock_article_url in re.findall(article_regex,response_text): stock_articles.append(StockArticle(stock_ticker,stock_article_url))

        except Exception as e: self.logger.error(e)

        return stock_articles




