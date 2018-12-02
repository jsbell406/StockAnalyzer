import logging
import re
import requests
from service.models import Rater, Rating, StockRating, RaterRating

class DataSource(object):

    def __init__(self,source_url):

        self.source_url = source_url

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

        headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        response = requests.get(url,allow_redirects=True,headers=headers)

        text = response.text

        rating = re.findall(self.regex_string,text)[0].strip()

        rating = self.parse_rating(rating)

        if rating is not None: self.__save_rating(stock,rating)

    def parse_rating(self,raw_rating):

        if 'Buy' in raw_rating: return 1

        elif 'Hold' in raw_rating or 'Neutral' in raw_rating: 0

        elif 'Sell' in raw_rating: return -1

        return None

    def __save_rating(self,stock,rating_value):

        rater = Rater.get_or_none(name=self.__str__())

        if rater is None:

            rater = Rater.create(name=self.__str__())

            rater.save()

        rating = Rating.create(value=rating_value)

        rating.save()

        rater_rating = RaterRating.create(rater_id=rater,rating_id=rating)

        rater_rating.save()

        stock_rating = StockRating.create(stock_ticker=stock,rating_id=rating)

        stock_rating.save()