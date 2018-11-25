import logging
from multiprocessing.pool import ThreadPool
import time
from service.news_source import Nasdaq, Zacks, NYT, TheGuardian, IEX
from service.models import StockTickerNameXref

class StockNewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq(),Zacks(), NYT(), TheGuardian(), IEX()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_articles_for_stock(self,ticker):

        self.logger.info('Collecting articles for ' + ticker)

        stock_articles = []

        stock_ticker_name_xref = StockTickerNameXref.get_or_none(stock_ticker=ticker)

        for stock_article in self.__collect_articles_with_param(ticker): stock_articles.append(stock_article)

        if stock_ticker_name_xref is not None:

            time.sleep(5) # Let the resources rest

            for stock_article in self.__collect_articles_with_param(stock_ticker_name_xref.stock_name): 

                stock_article.stock_ticker = ticker

                stock_articles.append(stock_article)

        return stock_articles

    def __collect_articles_with_param(self,param):

        thread_pool = ThreadPool(processes=len(self.news_sources))

        workers = []

        for news_source in self.news_sources: workers.append(thread_pool.apply_async(self.__collect_articles_from_news_source,(news_source,param)))

        stock_articles = []

        for worker in workers:

            for stock_article in worker.get(): stock_articles.append(stock_article)

        return stock_articles

    def __collect_articles_from_news_source(self,news_source,param):

        return news_source.collect_articles(param)

    



