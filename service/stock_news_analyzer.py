import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from service.news_collector import NewsCollector
from service.news_rater import NewsRater
from service.models import *
from service.histogram_generator import HistogramGenerator
from peewee import IntegrityError
import requests
import html
from service.stock_rater import StockRater

class StockNewsAnalyzer(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.histogram_generator = HistogramGenerator()

        self.stock_rater = StockRater()

        self.logger = logging.getLogger()

        self.logger.info('StockNewsAnalzer Loaded.')

    def analyze_stock(self,stock_ticker=None, target_stock=None):

        if stock_ticker is None and target_stock is None: raise Exception('Please provide either a Stock or Stock Ticker.')

        if stock_ticker is not None and target_stock is not None: raise Exception('Please provide only a Stock or a Stock Ticker, not both.')

        stock = target_stock if target_stock is not None else Stock.get_or_none(ticker=stock_ticker)

        if stock is None:

            stock_name, stock_market = self.__gather_stock_data(stock_ticker)

            if stock_name is None: raise Exception("Unable to find name for stock that doesn't exist in the database.")

            else: 
                
                stock = Stock.create(ticker=stock_ticker, name=stock_name, market=stock_market)

                stock.save()

        self.logger.info('Rating ' + stock.ticker)

        articles = self.news_collector.collect_news_for_stock(stock)

        self.news_rater.rate_news(articles,stock)

        self.histogram_generator.generate_histogram_for_stock(stock)

    def __gather_stock_data(self,stock_ticker):

        name = None

        market = None

        try:

            response = requests.get('https://api.iextrading.com/1.0/stock/{}/company'.format(stock_ticker))

            json_data = response.json()

            name = json_data['companyName']

            market = json_data['exchange']

        except Exception as e:

            self.logger.error(e)

        return name, market
