import time
import requests
import re
from service.rater import Rater
from service.stock import Stock

class StockProvider(object):

    def __init__(self):

        self.__load_available_tickers()

    def provide_stocks(self):

        stocks = []

        page_number = 1

        while len(stocks) < 10:

            url = 'https://walletinvestor.com/stock-forecast?sort=-forecast_percent_change_14d&page={}'.format(page_number)

            page_number += 1

            response = requests.get(url)

            text = response.text

            for match in re.finditer(r'class="currency-rate currency-rate([\s\S]+?)data-col-seq="8">',text):

                stock = self.__convert_match_to_stock(match)

                if stock.market is not None and self.__stock_is_acceptable(stock): stocks.append(stock)

            time.sleep(3)

        return stocks

    def __load_available_tickers(self):

        self.available_tickers = {}

        self.available_tickers['NASDAQ'] = self.__get_tickers_from_file('nasdaq.csv')

        self.available_tickers['NYSE'] = self.__get_tickers_from_file('nyse.csv')

    def __get_tickers_from_file(self,file_name):

        tickers = []

        data = open(file_name).readlines()

        for item in data: tickers.append(item.strip())

        return tickers

    def __convert_match_to_stock(self,match):

        data = match.group(1)

        grade = re.findall(r'">(.+?)</span>',data)[0]

        ticker = re.findall(r'class="detail">\((.+?)\)',data)[0]

        price = float(re.findall(r'data-col-seq="2">(.+?)<',data)[0])

        two_wk_price_change = re.findall(r'data-col-seq="3">.+?</i>(.+?)<',data)[0]

        market = self.get_market_for_ticker(ticker)

        return Stock(grade,ticker,market,price,two_wk_price_change)

    def get_market_for_ticker(self,ticker):

        if ticker in self.available_tickers['NASDAQ']: return 'NASDAQ'

        elif ticker in self.available_tickers['NYSE']: return 'NYSE'

        else: return None

    def __stock_is_acceptable(self,stock):

        return stock.price > 2 and ('A' in stock.grade or 'B' in stock.grade)