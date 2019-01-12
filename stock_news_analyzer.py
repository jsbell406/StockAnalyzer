import argparse
import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from peewee import IntegrityError
import requests
from service.news.news_collector import NewsCollector
from service.news.news_rater import NewsRater
from service.data_sources.models import JOIN, fn # The PeeWee specific items.
from service.data_sources.models import Stock, Rating, StockRating, ArticleScore, Article, StockArticle # The database specific items.

class StockNewsAnalyzer(object):
    '''Analyzes the news for a given stock.'''

    def __init__(self):
        '''Constructor'''

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.logger = logging.getLogger()

        self.logger.info('StockNewsAnalzer Loaded.')

    def analyze_stocks(self,stock_tickers):
        '''Analyzes the news for a set of stocks.
        
        Arguments:
            stock_tickers {list} -- The stock tickers to analyze the news for.
        '''
        self.logger.info('Analyzing Stocks: ' + ', '.join(stock_tickers))

        stock_ticker_avg_score_map = {}

        for index, stock_ticker in enumerate(stock_tickers):

            stock_ticker_avg_score_map[stock_ticker] = self.analyze_stock(stock_ticker)

            self.logger.info('Sleeping for five seconds.')

            if index < len(stock_tickers) - 1: time.sleep(5)

        return stock_ticker_avg_score_map


    def analyze_stock(self,stock_ticker):
        '''Analyzes the news for a given stock.
        
        Arguments:
            stock_ticker {str} -- The stock ticker of the stock to be analyzed.
        
        Returns:
            float -- The avg compound sentiment score for Articles gathered for the Stock.
        '''
        # Gather a Stock object for the given ticker.
        stock = self.__gather_stock_for_ticker(stock_ticker)

        self.logger.info('Analyzing ' + stock.ticker)

        # Perform the analysis
        articles = self.news_collector.collect_news_for_stock(stock)

        self.news_rater.rate_news(articles,stock)

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

        avg_score = ArticleScore.select(fn.AVG(ArticleScore.score)).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((StockArticle.stock_ticker == stock.ticker) & (Article.publish_date.in_(self.__get_past_dates(0)))).scalar()

        return avg_score

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

                # Create/save stock record
                stock = Stock.create(ticker=stock_ticker, name=stock_name, market=stock_market)

        return stock

    def __gather_stock_data(self,stock_ticker):
        '''Gathers a Stock's name and market from the IEX API associated with a given stock's ticker.
        
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

    def __get_past_dates(self,num_days_back):

        today = date.today()

        date_strings = [today.strftime('%Y-%m-%d'),]

        for i in range(num_days_back):

            prev_date = today - timedelta(days=i + 1)

            date_strings.append(prev_date.strftime('%Y-%m-%d'))

        return date_strings

# MAIN METHOD ============================================

def parse_args():

    arg_parser = argparse.ArgumentParser(description='Performs text analysis and scores Articles written for, or mentioning a particular Stock. The average of all scores is returned, whose value is in the range of 1 to -1. A score closer to 1 is more positive and vice versa.')

    arg_parser.add_argument('stock_tickers', type=str, nargs='+', help='One or more Stock tickers identifying the stock(s) to analyze.')

    args = arg_parser.parse_args()

    return args.stock_tickers

if __name__ == "__main__":

    stock_tickers = parse_args()

    if len(stock_tickers) == 1:

        avg_score = StockNewsAnalyzer().analyze_stock(stock_tickers[0])

        print('Average Sentiment Score for {}: {}'.format(stock_tickers[0],avg_score))

    else:

        stock_ticker_avg_score_map = StockNewsAnalyzer().analyze_stocks(stock_tickers)

        for stock_ticker in stock_ticker_avg_score_map.keys(): print('Average Sentiment Score for {}: {}'.format(stock_ticker,stock_ticker_avg_score_map[stock_ticker]))

