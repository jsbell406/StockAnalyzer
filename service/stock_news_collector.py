import feedparser
import logging
from service.stock_article import StockArticle
from service.news_source import Nasdaq

class StockNewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_articles_for_stock(self,stock_ticker):

        self.logger.info('Collecting articles for ' + stock_ticker)

        stock_articles = []

        for news_source in self.news_sources:

            try:

                self.logger.debug('Collecting articles for {} via {}'.format(stock_ticker,news_source))

                news_source_url = news_source.construct_url(stock_ticker)

                feed = feedparser.parse(news_source_url)

                for entry in feed.entries: stock_articles.append(StockArticle(stock_ticker,entry.link))

            except Exception as e:

                self.logger.error(e)

        return stock_articles
