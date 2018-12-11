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

            # fig.canvas.set_window_title(stock.ticker)

            plt.show()    