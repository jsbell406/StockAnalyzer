import logging
import re
import requests
from datetime import date
from service.models import Rating, StockRating

class DataSource(object):

    def __init__(self,source_url):

        self.source_url = source_url

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding' : 'gzip, deflate, br'}

        self.logger = logging.getLogger()

    def construct_url(self,stock):

        return self.source_url.format(stock.ticker)

    def collect_data_from_source_for_stock(self,stock):

        pass

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# =========================================================

class NewsSource(DataSource):

    def __init__(self, source_url):

        super().__init__(source_url)

        self.logger.info('Loaded NewsSource: ' + self.__str__())      

# =========================================================

class RatingSource(DataSource):

    def __init__(self, source_url,regex_string):

        super().__init__(source_url)

        self.regex_string = regex_string

        self.logger.info('Loaded RatingSource: ' + self.__str__())

    def collect_data_from_source_for_stock(self,stock):

        url = self.construct_url(stock)

        response = requests.get(url,allow_redirects=True,headers=self.headers)

        text = response.text

        if response.status_code == 200:

            rating_data = re.findall(self.regex_string,text)

            if len(rating_data) > 0:

                rating_value = self.parse_rating(rating_data[0].strip().upper())

                if rating_value is not None: 

                    existing_rating = Rating.get_or_none(value=rating_value,source=self.__str__(),rating_date=date.today().__str__())

                    if existing_rating is None: 
                        
                        rating = Rating.create(value=rating_value,source=self.__str__(),rating_date=date.today().__str__())

                        rating.save()

                        StockRating.create(stock_ticker=stock,rating_id=rating).save()

        else: self.logger.error('Status Code for {} was not 200: {}'.format(self.__str__(),response.status_code))

    def parse_rating(self,raw_rating):

        if 'BUY' in raw_rating: return 1

        if 'HOLD' in raw_rating or 'Neutral' in raw_rating: return 0

        if 'SELL' in raw_rating: return -1

        return None