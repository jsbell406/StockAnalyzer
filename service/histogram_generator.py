import logging
from logging.config import fileConfig
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from datetime import date
from peewee import JOIN
from service.models import Stock, ContentType, Score, ContentScore, Content, ArticleContent, Article, StockArticle

class HistogramGenerator(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.logger = logging.getLogger()

        self.logger.info('HistogramGenerator Loaded.')

    def generate_histogram_for_stock(self,stock_ticker):

        stock = Stock.get_or_none(ticker=stock_ticker)

        if stock is not None:

            self.logger.info('Generating histogram for ' + stock.ticker)

            content_type_headline = ContentType.get(type='headline')

            content_type_body = ContentType.get(type='body')

            headline_scores = [score.value for score in Score.select().join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_headline) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')))]

            body_scores = [score.value for score in Score.select().join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_body) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')))]

            headline_body_scores = headline_scores + body_scores

            fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)

            self.__create_subplot(axs,0,headline_scores,'Headline Scores ({})'.format(len(headline_scores)))

            self.__create_subplot(axs,1,headline_body_scores,'Headline & Body Scores ({})'.format(len(headline_body_scores)))

            self.__create_subplot(axs,2,body_scores,'Body Scores ({})'.format(len(body_scores)))

            fig.canvas.set_window_title(stock.ticker)

            plt.show()    

    def __create_subplot(self,axs,index,dataset,title):

        axs[index].hist(dataset, bins=10)

        axs[index].set_xlim([-1,1])

        axs[index].set_title(title)