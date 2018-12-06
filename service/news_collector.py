import logging
from multiprocessing.pool import ThreadPool
import time
from service.news_sources import Nasdaq, TheStreet, DailyStocks, IEX, RobinHood, NewsApi
from service.models import Stock, Article

class NewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq(), TheStreet(), DailyStocks(), IEX(), RobinHood(), NewsApi()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded.')

    def collect_news_for_stock(self,stock):

        self.logger.info('Collecting articles for ' + stock.ticker)

        thread_pool = ThreadPool(processes=len(self.news_sources))

        workers = []

        articles = []

        for news_source in self.news_sources: workers.append(thread_pool.apply_async(news_source.collect_data_from_source_for_stock,(stock,)))

        for worker in workers: articles += worker.get()

        self.__review_articles(articles)

        return articles