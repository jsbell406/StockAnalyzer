import requests
import re
import logging
from service.stock_article import StockArticle
from service.news_source import NewsSource, MarketWatch, SeekingAlpha, Benzinga

class StockNewsCollector(object):

    def __init__(self):

        self.news_sources = [MarketWatch(),SeekingAlpha(),Benzinga()]

        self.logger = logging.getLogger()

        self.logger.info('StockNewsCollector Loaded')

    def collect_articles_for_stock(self,stock_ticker):

        self.logger.info('Collecting articles for ' + stock_ticker)

        stock_articles = []

        for news_source in self.news_sources:

            try:

                self.logger.debug('Collecting articles for {} via {}'.format(stock_ticker,news_source))

                news_source_url = news_source.construct_url(stock_ticker)

                headers = {'User-Agent': 'My User Agent 1.0'}

                response = requests.get(news_source_url,allow_redirects=True,headers=headers)

                text = response.text

                article_urls = news_source.gather_article_urls(text)

                for article_url in article_urls: stock_articles.append(StockArticle(stock_ticker,article_url))

            except Exception as e:

                self.logger.error(e)

        return stock_articles
