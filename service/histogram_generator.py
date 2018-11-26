import logging
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from service.models import AggScoreStockArticleXref, StockArticle

class HistogramGenerator(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.logger.info('HistogramGenerator Loaded')

    def generate_histogram(self,agg_score):

        xrefs = AggScoreStockArticleXref.select().where(AggScoreStockArticleXref.agg_score == agg_score.id)

        scores = []
        
        for xref in xrefs: 

            stock_article = StockArticle.get(id=xref.stock_article)

            if stock_article.article_score is not None: scores.append(stock_article.article_score)

        N_points = len(scores)

        n_bins = 10

        fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)

        # # We can set the number of bins with the `bins` kwarg
        axs.hist(scores, bins=n_bins)

        plt.show()    