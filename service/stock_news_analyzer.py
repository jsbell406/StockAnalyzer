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
import requests
import html

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

        url = 'https://www.marketwatch.com/tools/quotes/lookup.asp?Lookup=' + stock_ticker

        response = requests.get(url)

        response_text = response.text

        for match in re.findall(r'<div class="results">[\s\S]+?<td class="bottomborder">([^<].+?)<\/td>[\s\S]+?<td class="bottomborder">(.+?)<\/td>',response_text):

            name = html.unescape(match[0])

            market = html.unescape(match[1])

        # Sometimes you get redirected to the Stock's primary MarketWatch page.
        if name is None:

            for match in re.findall(r'<title>.+?- (.+?) Stock Quote .+?: (.+?) .+?-',response_text):

                name = html.unescape(match[0])

                market = html.unescape(match[1])

        return name, market
