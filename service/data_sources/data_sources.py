import logging
import re
import requests
from datetime import date
from service.data_sources.models import Rating, StockRating

class DataSource(object):
    '''Represents a "Source" of "Data" for the StockNewsAnalyzer to pull from.'''

    def __init__(self,source_url):
        '''Constructor
        
        Arguments:
            source_url {str} -- The base url the DataSource should use when gathering data, prepared for formatting. E.g. 'nasdaq.com/{}'
        '''

        self.source_url = source_url

        # These are the generic headers used when submitting requests to sites.
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0',
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding' : 'gzip, deflate, br'}

        self.logger = logging.getLogger()

    def construct_url(self,stock):
        '''Uses the provided Stock to construct a url for to extending classes to gather data from.
        
        Arguments:
            stock {Stock} -- The stock to use when constructing the url.
        
        Returns:
            str -- The constructed url. E.g. nasdaq.com/{} -> nasdaq.com/TSLA
        '''

        return self.source_url.format(stock.ticker)

    def collect_data_from_source_for_stock(self,stock):
        '''Collects data from the DataSource for the given Stock.
        
        Arguments:
            stock {Stock} -- The Stock to gather the data for.
        '''

        pass

    def __str__(self):

        return re.findall('://(.+?)/',self.source_url)[0]

# =========================================================

class NewsDataSource(DataSource):
    '''A DataSource for News Data.
    
    Arguments:
        DataSource {DataSource} -- The base DataSource class this class extends.
    '''

    def __init__(self, source_url):
        '''Constructor
        
        Arguments:
            source_url {str} -- source_url {str} -- The base url the NewsDataSource should use when gathering data, prepared for formatting. E.g. 'newssite.com/{}'
        '''

        super().__init__(source_url)

        self.logger.info('Loaded NewsDataSource: ' + self.__str__())      

# =========================================================

class RatingDataSource(DataSource):
    '''A DataSource for Ratings Data.
    
    Arguments:
        DataSource {DataSource} -- The base DataSource class this class extends.
    '''

    def __init__(self, source_url,regex_string):
        '''Constructor
        
        Arguments:
            source_url {str} -- The base url the RatingDataSource should use when gathering data, prepared for formatting. E.g. 'ratingsite.com/{}'
            regex_string {str} -- The regex string the RatingDataSource will use when extracting data from the source's webpage html.
        '''

        super().__init__(source_url)

        self.regex_string = regex_string

        self.logger.info('Loaded RatingDataSource: ' + self.__str__())

    def collect_data_from_source_for_stock(self,stock):
        '''Collects data from the RatingDataSource for the given Stock. Overrides the same method in DataSource.
        
        Arguments:
            stock {Stock} -- The Stock to collect Rating data for.
        '''

        self.logger.info('Rating {} via {}'.format(stock.ticker,self.__str__()))

        rating = None

        # E.g. ratingsite.com/{} -> ratingsite.com/TSLA
        url = self.construct_url(stock)

        # Attempt to gather the webpage html.
        response = requests.get(url,allow_redirects=True,headers=self.headers)

        if response.status_code == 200:

            # Extract the rating data from the webpage html.
            rating_data = re.findall(self.regex_string,response.text)

            if len(rating_data) > 0:

                # Convert the raw rating data to either a 1 for Buy, 0 for Hold, or -1 for Sell.
                rating_value = self.parse_rating(rating_data[0].strip().upper())

                rating = Rating(value=rating_value,source=self.__str__(),rating_date=date.today().__str__())

        else: self.logger.error('Status Code for {} was not 200: {}'.format(self.__str__(),response.status_code))

        return rating

    def parse_rating(self,raw_rating):
        '''Parses raw rating data, returning eithet a 1 for Buy, 0 for Hold, or -1 for Sell.
        
        Arguments:
            raw_rating {str} -- The raw rating data from the RatingDataSource's webpage html.
        
        Returns:
            int -- The rating (1/0/-1) equivalent of the raw rating data.
        '''

        if 'BUY' in raw_rating: return 1

        if 'HOLD' in raw_rating or 'Neutral' in raw_rating: return 0

        if 'SELL' in raw_rating: return -1

        return None 