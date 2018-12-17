import argparse
import logging
from logging.config import fileConfig
from multiprocessing.pool import ThreadPool
import time
import requests
from datetime import date
from service.rating.rating_data_sources import Zacks, TheStreet, StockHelpIsland, SuperStockScreener, MarketBeat
from service.data_sources.models import JOIN, fn # The PeeWee specific items.
from service.data_sources.models import Stock, Rating, StockRating # The Database specific items.

class StockRater(object):
    '''Rates a given stock (Buy/Hold/Sell) based on the aggregate rating from a group of RatingDataSources.'''

    def __init__(self):
        '''Constructor'''

        fileConfig('logging_config.ini')

        self.logger = logging.getLogger()

        self.rating_data_sources = [Zacks(),TheStreet(),StockHelpIsland(),SuperStockScreener(),MarketBeat()]

        self.logger.info('StockRater Loaded.')

    def rate_stocks(self,stock_tickers):
        '''Rates a set of Stocks.
        
        Arguments:
            stock_tickers {list} -- The Stocks to rate.
        '''

        self.logger.info('Rating Stocks: ' + ', '.join(stock_tickers))

        stock_ticker_rating_map = {}

        for index,stock_ticker in enumerate(stock_tickers):

            stock_ticker_rating_map[stock_ticker] = self.rate_stock(stock_ticker)

            if index < len(stock_tickers) - 1: 
                
                self.logger.info('Sleeping for five seconds.')
                
                time.sleep(5)

        return stock_ticker_rating_map

    def rate_stock(self,stock_ticker):
        '''Rates a given Stock. Stock is given a (1/0/-1) rating for (Buy/Hold/Sell) respectively.

        Rating based on the aggregate rating for the Stock across a group of RatingDataSources.

        Rating Process is multithreaded, one Thread per RatingDataSource.

        Arguments:
            stock {Stock} -- The Stock to rate.
        '''

        # Gather a Stock object for the given ticker.
        stock = self.__gather_stock_for_ticker(stock_ticker)

        self.logger.info('Rating ' + stock.ticker)

        # Create the thread pool, indicating that you want a thread for each NewsDataSource.
        thread_pool = ThreadPool(processes=len(self.rating_data_sources))

        workers = []

        ratings = []

        # Create a thread for each RatingDataSource, start it working.
        for rating_data_source in self.rating_data_sources: workers.append(thread_pool.apply_async(rating_data_source.collect_data_from_source_for_stock, (stock,)))

        # Wait for each Thread to complete its work, then save the Ratings it collected in the Ratings list.
        for worker in workers: ratings.append(worker.get())

        self.__save_ratings(stock,ratings)

        '''
        SELECT AVG(r.value)
        FROM Rating r

        INNER JOIN StockRating sr
        ON r.id = sr.rating_id

        WHERE r.rating_date = 'TODAYS DATE IN Y-M-D FORMAT'
        '''
        avg_rating = Rating.select(fn.AVG(Rating.value)).join(StockRating, JOIN.INNER).where((StockRating.stock_ticker == stock) & (Rating.rating_date == date.today().strftime('%Y-%m-%d'))).scalar()

        return avg_rating

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

    def __save_ratings(self,stock,ratings):
        '''Saves the gathered ratings to the database.
        
        Arguments:
            stock {Stock} -- The Stock the ratings are for.
            ratings {list} -- The list of Ratings to save.
        '''

        for rating in ratings:

            if rating is not None: 

                # Make sure you don't save what's already saved.
                existing_rating = Rating.get_or_none(value=rating.value,source=rating.source,rating_date=rating.rating_date)

                if existing_rating is None: 
                    
                    rating.save()

                    StockRating.create(stock_ticker=stock,rating_id=rating)

# MAIN METHOD ============================================

def create_arg_parser():

    arg_parser = argparse.ArgumentParser(description='Rates a Stock based on what other Rating sources are saying. The average rating is returned, whose value is in the range of 1 to -1. 1 = Buy, 0 = Hold, -1 = Sell. ')

    arg_parser.add_argument('stock_tickers', type=str, nargs='+', help='One or more Stock tickers identifying the stock(s) to rate.')

    return arg_parser

if __name__ == "__main__":
    
    arg_parser = create_arg_parser()

    args = arg_parser.parse_args()

    stock_tickers = args.stock_tickers

    if len(stock_tickers) == 1:

        avg_rating = StockRater().rate_stock(stock_tickers[0])

        print('Average Buy/Hold/Sell rating for {}: {}'.format(stock_tickers[0],avg_rating))

    else:

        stock_ticker_rating_map = StockRater().rate_stocks(stock_tickers)

        for stock_ticker in stock_ticker_rating_map.keys(): print('Average Sentiment Score for {}: {}'.format(stock_ticker,stock_ticker_rating_map[stock_ticker]))