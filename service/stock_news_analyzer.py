import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from peewee import IntegrityError
import requests
import html
from service.news_analysis.news_collector import NewsCollector
from service.news_analysis.news_rater import NewsRater
from service.util.stock_rater import StockRater
from service.data_sources.models import JOIN, fn # The PeeWee specific items.
from service.data_sources.models import Stock, Rating, StockRating, ArticleScore, Article, StockArticle # The database specific items.

class StockNewsAnalyzer(object):
    '''Analyzes the news for a given stock.
    
    At the moment, also provides a "Rating" which is an average of the "Buy/Hold/Sell" ratings
    across 5 sources. See rating_sources.py for the exact rating sources.
    '''

    # Constants for identifying the report sections.
    AVG_RATING = 'avg_rating'

    AVG_SCORE = 'avg_score'

    def __init__(self):
        '''Constructor'''

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.stock_rater = StockRater()

        self.logger = logging.getLogger()

        self.logger.info('StockNewsAnalzer Loaded.')

    def analyze_stock(self,stock_ticker):
        '''Analyzes the news for a given stock.
        
        Arguments:
            stock_ticker {str} -- The stock ticker of the stock to be analyzed.
        
        Returns:
            list -- The analysis report, containing the stock rating and the stock news anlysis. In the report, the first value is an average of the Buy/Hold/Sell rating across 5 "rating_sources" which will be a 1/0/-1 respectively. The second value is the news analysis, a value between 1 and -1. Closer to 1 is more positive, closer to 0 is more neutral, closer to -1 is more negative.
        '''
        # Gather a Stock object for the given ticker.
        stock = self.__gather_stock_for_ticker(stock_ticker)

        self.logger.info('Rating ' + stock.ticker)

        # Perform the analysis
        articles = self.news_collector.collect_news_for_stock(stock)

        self.news_rater.rate_news(articles,stock)

        self.stock_rater.rate_stock(stock)

        # Generate and return your report
        return self.__generate_report(stock)

    def __gather_stock_for_ticker(self,stock_ticker):
        '''Gathers a Stock object from the Database for the given ticker. If one can't be found, data is gathered from the IEX API and saved instead. If the IEX API can't provide data, then an error is thrown.
        
        Arguments:
            stock_ticker {str} -- The stock ticker to gather a Stock object for.
        
        Raises:
            Exception -- Thrown if a stock can't be found for the given ticker in either the database or the IEX API.
        
        Returns:
            Stock -- The Stock object for the given stock ticker.
        '''

        stock = Stock.get_or_none(ticker=stock_ticker)

        if stock is None: # No stock in database associated with the given ticker.

            stock_name, stock_market = self.__gather_stock_data(stock_ticker) # From IEX API

            if stock_name is None: raise Exception("Unable to find stock in database or IEX.") # No stock in IEX API associated with given ticker.

            else: # Stock found in IEX API 
                
                '''
                NOTE
                At first glance it looks like you could just call:

                stock = Stock.create(ticker=stock_ticker, name=stock_name, market=stock_market).save()

                but .save() saves the given object to the database and returns the generated id. This is why the stock is first created, then saved- so you can have a handle on the object to return it.
                '''

                # Create/save stock record
                stock = Stock.create(ticker=stock_ticker, name=stock_name, market=stock_market)

                stock.save()

        return stock

    def __gather_stock_data(self,stock_ticker):
        '''Gathers the Stock data from the IEX API associated with a given stock's ticker.
        
        Arguments:
            stock_ticker {str} -- The stock ticker to gather data for.
        
        Returns:
            str -- The stock's name according to the IEX API, or None if nothing was found.
            str -- The stock's market according to the IEX API, or None if nothing was found.
        '''

        name = None

        market = None

        try:

            response = requests.get('https://api.iextrading.com/1.0/stock/{}/company'.format(stock_ticker))

            json_data = response.json()

            name = json_data['companyName']

            market = json_data['exchange']

        except Exception as e: # No data found.

            self.logger.error(e)

        return name, market

    def __generate_report(self,stock):
        '''Generates a Post-Analysis report for the given Stock.
        
        Arguments:
            stock {Stock} -- The stock to generate the report for.
        
        Returns:
            set(str,str) -- The generated report. The first value is an average of the Buy/Hold/Sell rating across 5 "rating_sources" which will be a 1/0/-1 respectively. The second value is the news analysis, a value between 1 and -1. Closer to 1 is more positive, closer to 0 is more neutral, closer to -1 is more negative.
        '''

        report_data = {}

        '''
        SELECT AVG(r.value)
        FROM Rating r

        INNER JOIN StockRating sr
        ON r.id = sr.rating_id

        WHERE r.rating_date = 'TODAYS DATE IN Y-M-D FORMAT'
        '''
        rating = Rating.select(fn.AVG(Rating.value)).join(StockRating, JOIN.INNER).where((StockRating.stock_ticker == stock) & (Rating.rating_date == date.today().strftime('%Y-%m-%d'))).scalar()


        '''
        SELECT AVG(arsc.score)
        FROM ArticleScore arsc

        INNER JOIN Article a
        ON arsc.article_id = a.id

        INNER JOIN StockArticle sa
        ON a.id = sa.article_id

        WHERE sa.stock_ticker = 'STOCK TICKER'
        AND a.save_date = 'TODAYS DATE IN Y-M-D FORMAT'
        '''

        avg_score = ArticleScore.select(fn.AVG(ArticleScore.score)).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d'))).scalar()

        report_data[self.AVG_RATING] = rating

        report_data[self.AVG_SCORE] = avg_score

        return report_data