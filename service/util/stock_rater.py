import logging
from multiprocessing.pool import ThreadPool
import time
from service.data_sources.rating_data_sources import Zacks, TheStreet, StockHelpIsland, SuperStockScreener, MarketBeat
from service.data_sources.models import Rating, StockRating

class StockRater(object):
    '''Rates a given stock (Buy/Hold/Sell) based on the aggregate rating from a group of RatingDataSources.'''

    def __init__(self):
        '''Constructor'''

        self.logger = logging.getLogger()

        self.rating_data_sources = [Zacks(),TheStreet(),StockHelpIsland(),SuperStockScreener(),MarketBeat()]

        self.logger.info('StockRater Loaded.')

    def rate_stocks(self, stocks):
        '''Rates a list of stocks, giving each one a (1/0/-1) rating for (Buy/Hold/Sell) respectively.

        Rating based on the aggregate rating for a Stock across a group of RatingDataSources.
        
        Arguments:
            stocks {list} -- The Stocks to rate.
        '''

        self.logger.info('Rating Stocks ' + ', '.join([stock.ticker for stock in stocks]))

        for stock in stocks:

            self.rate_stock(stock)

            # Cooldown period so the websites used by the RatingDataSources don't ban our ip.
            time.sleep(5)

    def rate_stock(self,stock):
        '''Rates a given Stock. Stock is given a (1/0/-1) rating for (Buy/Hold/Sell) respectively.

        Rating based on the aggregate rating for the Stock across a group of RatingDataSources.

        Rating Process is multithreaded, one Thread per RatingDataSource.

        Arguments:
            stock {Stock} -- The Stock to rate.
        '''

        self.logger.info('Rating ' + stock.ticker)

        # Create the thread pool, indicating that you want a thread for each NewsDataSource.
        thread_pool = ThreadPool(processes=len(self.rating_data_sources))

        workers = []

        ratings = []

        # Create a thread for each RatingDataSource, start it working.
        for rating_data_source in self.rating_data_sources: workers.append(thread_pool.apply_async(rating_data_source.collect_data_from_source_for_stock, (stock,)))

        # Wait for each Thread to complete its work, then save the Ratings it collected in the Ratings list.
        for worker in workers: ratings += worker.get()

        self.__save_ratings(stock,ratings)

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