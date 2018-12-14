import logging
from multiprocessing.pool import ThreadPool
import time
from service.data_sources.news_data_sources import Nasdaq, TheStreet, DailyStocks, IEX, RobinHood, NewsApi
from service.data_sources.models import Stock, Article
from service.news_analysis.api_keys import no_news_api_key, news_api_key

class NewsCollector(object):
    '''Collects News'''

    def __init__(self):
        '''Constructor'''

        self.news_data_sources = [Nasdaq(), TheStreet(), DailyStocks(), IEX(), RobinHood()]

        # Only use the NewsApi NewsDataSource if the api key was provided in the api_keys.py file.
        if news_api_key != no_news_api_key and len(news_api_key.strip()) > 0: self.news_data_sources.append(NewsApi())

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded.')

    def collect_news_for_stock(self,stock):
        '''Collects the news for a given Stock from the NewsDataSources in self.news_data_sources.
        
        Process is multi-threaded, one thread per NewsDataSource.

        Arguments:
            stock {Stock} -- The Stock news Articles are being gathered for.
        
        Returns:
            list -- A list of Articles collected from the NewsDataSources in self.news_data_sources.
        '''

        self.logger.info('Collecting articles for ' + stock.ticker)

        # Create the thread pool, indicating that you want a thread for each NewsDataSource.
        thread_pool = ThreadPool(processes=len(self.news_data_sources))

        workers = []

        articles = []

        # Create a thread for each NewsDataSource, start it working.
        for news_source in self.news_data_sources: workers.append(thread_pool.apply_async(news_source.collect_data_from_source_for_stock,(stock,)))

        # Wait for each Thread to complete its work, then save the Articles it collected in the articles list.
        for worker in workers: articles += worker.get()

        return articles