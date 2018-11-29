import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from service.news_collector import NewsCollector
from service.news_rater import NewsRater
from service.models import Stock, StockArticle
from service.histogram_generator import HistogramGenerator
from peewee import IntegrityError

class StockNewsAnalyzer(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.histogram_generator = HistogramGenerator()

        self.logger = logging.getLogger()

        self.logger.info('StockRater loaded')

    def analyze_stock(self,stock_ticker):

        stock = Stock.get_or_none(ticker=stock_ticker)

        if stock is not None:

            self.logger.info('Rating ' + stock.ticker)

            articles = self.news_collector.collect_news_for_stock(stock)

            self.news_rater.rate_news(articles,stock)

            self.histogram_generator.generate_histogram_for_stock(stock)