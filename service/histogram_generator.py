import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from datetime import date
from service.models import *

class HistogramGenerator(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.logger.info('HistogramGenerator Loaded')

    def generate_histogram_for_stock(self,stock):

        self.logger.info('Generating histogram for ' + stock.ticker)

        content_type_headline = ContentType.get(type='headline')

        content_type_body = ContentType.get(type='body')

        raw_headline_scores = Score.select(Score.value).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_headline) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')) & (Score.value != 0))

        raw_body_scores = Score.select(Score.value).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_body) & (StockArticle.stock_ticker == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')) & (Score.value != 0))

        headline_scores = [raw_headline_score.value for raw_headline_score in raw_headline_scores]

        body_scores = [raw_body_score.value for raw_body_score in raw_body_scores]

        headline_body_scores = headline_scores + body_scores

        fig, axs = plt.subplots(1, 3, sharey=True, tight_layout=True)

        self.__create_subplot(axs,0,headline_scores,'Headline Scores')

        self.__create_subplot(axs,1,headline_body_scores,'Headline & Body Scores')

        self.__create_subplot(axs,2,body_scores,'Body Scores')

        fig.canvas.set_window_title(stock.ticker)

        plt.show()    

    def __create_subplot(self,axs,index,dataset,title):

        axs[index].hist(dataset, bins=20)

        axs[index].set_xlim([-1,1])

        axs[index].set_title(title)