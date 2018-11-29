import re
import requests
import time
from service.source import *

class Rater(object):

    def __init__(self):

        self.sources = [Zacks(),TheStreet(),StockHelpIsland(),SuperStockScreener()]

    def rate_stocks(self,stocks):

        for stock in stocks:

            for source in self.sources:

                try:

                    headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

                    url = source.construct_url(stock)

                    response = requests.get(url,allow_redirects=True,headers=headers)

                    text = response.text

                    raw_rating = re.findall(source.regex_string,text)[0].strip()

                    stock.ratings.append(source.parse_rating(raw_rating))

                except:

                    print('Failure while rating {} via {}'.format(stock.ticker,source))

                    pass

            time.sleep(5)

    def rate_stock(self,stock):

        for source in self.sources:

            try:

                headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

                url = source.construct_url(stock)

                response = requests.get(url,allow_redirects=True,headers=headers)

                text = response.text

                raw_rating = re.findall(source.regex_string,text)[0].strip()

                stock.ratings.append(source.parse_rating(raw_rating))

            except:

                # print('Failure while rating {} via {}'.format(stock.ticker,source))

                pass