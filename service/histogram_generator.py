import logging
from logging.config import fileConfig
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from datetime import datetime, date, timedelta
from peewee import JOIN
from service.models import Stock, ArticleScore, Article, StockArticle

class HistogramGenerator(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.logger = logging.getLogger()

        self.logger.info('HistogramGenerator Loaded.')

    def generate_histogram_for_stock(self,stock_ticker):

        stock = Stock.get_or_none(ticker=stock_ticker)

        if stock is not None:

            self.logger.info('Generating histogram for ' + stock.ticker)

            scores = [article_score.score for article_score in ArticleScore.select().join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((StockArticle.stock_ticker == stock_ticker) & (Article.save_date == date.today().__str__()))]

            plt.hist(scores, bins=10, range=(-1,1),label='Scores ({})'.format(len(scores)))

            plt.suptitle(stock_ticker)

            plt.show()    

    def generate_histogram_for_stocks(self,stock_tickers):

        stocks = [Stock.get_or_none(ticker=stock_ticker) for stock_ticker in stock_tickers if Stock.get_or_none(ticker=stock_ticker) is not None]

        target_stocks = [stock.ticker for stock in stocks]

        if len(stocks) > 0:

            target_stocks_title = ', '.join(target_stocks)

            self.logger.info('Generating histogram for ' + target_stocks_title)

            scores = []

            for stock in stocks:

                stock_scores = [article_score.score for article_score in ArticleScore.select().join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((StockArticle.stock_ticker == stock) & (Article.save_date == date.today().__str__()))]

                scores.append(stock_scores)

            plt.hist(scores, bins=10, range=(-1,1), label=target_stocks)

            plt.legend(prop={'size' : 10})

            plt.suptitle(target_stocks_title)

            plt.show()    