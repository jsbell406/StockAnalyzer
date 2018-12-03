import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from peewee import IntegrityError
import requests
import html
from service.news_collector import NewsCollector
from service.news_rater import NewsRater
from service.stock_rater import StockRater
from service.models import *

class StockNewsAnalyzer(object):

    RATING = 'rating'

    AVG_BODY = 'avg_body'

    AVG_HEADLINE = 'avg_headline'

    AVG_HEADLINE_BODY_COMBO = 'avg_headline_body_combo'

    def __init__(self):

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.stock_rater = StockRater()

        self.logger = logging.getLogger()

        self.logger.info('StockNewsAnalzer Loaded.')

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

        self.stock_rater.rate_stock(stock)

        return self.__generate_report(stock)

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

    def __generate_report(self,stock):

        content_type_headline = ContentType.get(type='headline')

        content_type_body = ContentType.get(type='body')

        report_data = {}

        rating = Rating.select(fn.AVG(Rating.value)).join(StockRating, JOIN.INNER).where((StockRating.stock_ticker == stock) & (Rating.rating_date == date.today().strftime('%Y-%m-%d'))).scalar()

        avg_headline = Score.select(fn.AVG(Score.value)).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_headline) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d'))).scalar()
        
        avg_body = Score.select(fn.AVG(Score.value)).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_body) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d'))).scalar()

        avg_headline_body_combo = (avg_headline + avg_body) / 2

        report_data[self.RATING] = rating

        report_data[self.AVG_BODY] = avg_body

        report_data[self.AVG_HEADLINE] = avg_headline

        report_data[self.AVG_HEADLINE_BODY_COMBO] = avg_headline_body_combo

        return report_data