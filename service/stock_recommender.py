import re
import requests
from service.models import Stock

class StockRecommender(object):

    def recommend_stocks(self):

        stocks = []

        page_number = 1

        while len(stocks) < 10:

            url = 'https://walletinvestor.com/stock-forecast?sort=-forecast_percent_change_14d&page={}'.format(page_number)

            page_number += 1

            response = requests.get(url)

            text = response.text

            for match in re.finditer(r'class="currency-rate currency-rate([\s\S]+?)data-col-seq="8">',text):

                stock, grade, price = self.__gather_stock_data_from_match(match)

                if stock is not None and self.__stock_is_acceptable(grade,price): stocks.append(stock)

            time.sleep(3)

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