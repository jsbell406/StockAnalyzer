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

            fig, axs = plt.subplots(1, sharey=True, tight_layout=True)

            axs.hist(scores, bins=10)

            axs.set_xlim([-1,1])

            axs.set_title('Scores ({})'.format(len(scores)))

            fig.canvas.set_window_title(stock.ticker)

            plt.show()    