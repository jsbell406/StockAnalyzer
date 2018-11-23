import logging
from multiprocessing.pool import ThreadPool
import time
from service.news_source import Nasdaq, Zacks, NYT, TheGuardian, IEX

class StockNewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq(),Zacks(), NYT(), TheGuardian(), IEX()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_articles_for_stock(self,stock_ticker,stock_name):

        self.logger.info('Collecting articles for ' + stock_ticker)

        stock_articles = []

        for stock_article in self.__collect_articles_with_param(stock_ticker): stock_articles.append(stock_article)

        if stock_name is not None:

            time.sleep(5) # Let the resources rest

            for stock_article in self.__collect_articles_with_param(stock_name): stock_articles.append(stock_name)

        return stock_articles

    def __collect_articles_with_param(self,param):

        thread_pool = ThreadPool(processes=len(self.news_sources))

        workers = []

        for news_source in self.news_sources: workers.append(thread_pool.apply_async(self.__collect_articles_from_news_source,(news_source,param)))

        stock_articles = []

        for worker in workers:

            for stock_article in worker.get(): stock_articles.append(stock_article)

        return stock_articles

    def __collect_articles_from_news_source(self,news_source,stock_ticker):

        return news_source.collect_articles(stock_ticker)

    



