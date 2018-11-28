import logging
from multiprocessing.pool import ThreadPool
import time
from service.news_source import Nasdaq, Zacks, NYT, TheGuardian, IEX
from service.models import Stock, Article

class NewsCollector(object):

    def __init__(self):

        self.news_sources = [Nasdaq(),Zacks(), NYT(), TheGuardian(), IEX()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_news_for_stock(self,stock):

        self.logger.info('Collecting articles for ' + stock.ticker)

        thread_pool = ThreadPool(processes=len(self.news_sources))

        workers = []

        articles = []

        for news_source in self.news_sources: workers.append(thread_pool.apply_async(news_source.collect_articles,(stock,)))

        for worker in workers:

            for article in worker.get(): articles.append(article)

        self.__review_articles(articles)

        return articles

    def __review_articles(self,articles):

        for index, article in enumerate(articles):

            existing_article = Article.get_or_none(url=article.url)

            articles[index] = existing_article if existing_article is not None else article