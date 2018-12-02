import re
import requests
import time
import logging
from datetime import datetime
from logging.config import fileConfig
from service.models import Stock, StockRecommendation
from peewee import *

class StockRecommender(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.logger = logging.getLogger()

        self.logger.info('StockRecommender Loaded.')

    def recommend_stocks(self, num_stocks=10):

        self.logger.info('Recommending Stocks')

        if num_stocks > 50: raise Exception('') # TODO Add appropriate message

        existing_recommendations = Stock.select().join(StockRecommendation, JOIN.INNER).where(StockRecommendation.recommendation_date == datetime.today().strftime('%Y-%m-%d'))

        stocks = []

        if len(existing_recommendations) >= num_stocks:

            stocks = existing_recommendations

        else:

            page_number = 1

            while len(stocks) < num_stocks:

                url = 'https://walletinvestor.com/stock-forecast?sort=-forecast_percent_change_14d&page={}'.format(page_number)

                page_number += 1

                response = requests.get(url)

                text = response.text

                for match in re.finditer(r'class="currency-rate currency-rate([\s\S]+?)data-col-seq="8">',text):

                    stock, grade, price = self.__gather_stock_data_from_match(match)

                    if stock is not None and self.__stock_is_acceptable(grade,price): stocks.append(stock)

                time.sleep(3)

            self.__save_recommendations(stocks)

        self.logger.info('Recommending ' + ', '.join([stock.ticker for stock in stocks]))

        return stocks

    def __gather_stock_data_from_match(self,match):

        data = match.group(1)

        grade = re.findall(r'">(.+?)</span>',data)[0]

        stock_ticker = re.findall(r'class="detail">\((.+?)\)',data)[0]

        price = float(re.findall(r'data-col-seq="2">(.+?)<',data)[0])

        two_wk_price_change = re.findall(r'data-col-seq="3">.+?</i>(.+?)<',data)[0]

        stock  = Stock.get_or_none(ticker=stock_ticker)

        return stock, grade, float(price)

    def __stock_is_acceptable(self,grade,price):

        return price > 2 and ('A' in grade or 'B' in grade)

    def __save_recommendations(self,stocks):

        for stock in stocks: StockRecommendation.create(stock_ticker=stock).save()