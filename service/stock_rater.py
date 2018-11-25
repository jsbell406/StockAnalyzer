import re
import time
import logging
import datetime
from service.stock_news_collector import StockNewsCollector
from service.stock_news_rater import StockNewsRater
from service.models import AggScore, StockTickerNameXref, StockArticle, AggScoreStockArticleXref

class StockRater(object):

    def __init__(self):

        self.stock_news_collector = StockNewsCollector()

        self.stock_news_rater = StockNewsRater()

        self.logger = logging.getLogger()

        self.logger.info('StockRater loaded')

    def rate_stock(self,stock_ticker):

        self.logger.info('Rating ' + stock_ticker)

        agg_score = AggScore.get_or_none(stock_ticker=stock_ticker,score_date=datetime.date.today().strftime('%F'))

        if agg_score is None:

            stock_articles = self.stock_news_collector.collect_articles_for_stock(stock_ticker)

            self.stock_news_rater.rate_stock_news(stock_articles)

            for stock_article in stock_articles: stock_article.save()

            agg_score = self.__build_agg_score(stock_ticker,stock_articles)

            agg_score.save()

            for stock_article in stock_articles: AggScoreStockArticleXref.create(agg_score=agg_score.id,score_date=datetime.date.today().strftime('%F'),stock_article=stock_article.id)


        return agg_score

    def __build_agg_score(self,stock_ticker,stock_articles):

        self.logger.info('Building Agg Score for {}s {} articles.'.format(stock_ticker,len(stock_articles)))

        agg_score = AggScore(stock_ticker=stock_ticker)

        total_score = 0

        max_score = -1

        min_score = 1

        for stock_article in stock_articles: 

            article_score = stock_article.article_score

            if article_score is not None:

                total_score += article_score

                max_score = article_score if article_score > max_score else max_score

                min_score = article_score if article_score < min_score else min_score

        agg_score.avg_score = total_score / len(stock_articles)

        agg_score.max_score = max_score

        agg_score.min_score = min_score

        return agg_score