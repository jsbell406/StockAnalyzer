from datetime import datetime
import logging
from service.db_connection import DatabaseConnection
from service.agg_score import AggScore
from service.stock_article import StockArticle

class DatabaseUtility(object):

    # 2018-11-16 19:39:12
    DATETIME_FORMAT = '%Y-%m-%d'

    def __init__(self):

        self.db_connection = DatabaseConnection()

        self.logger = logging.getLogger()

        self.logger.info('DatabaseUtility Loaded')

    def save_article(self,stock_article):

        self.logger.debug('Saving article: ' + stock_article.url)

        statement = '''INSERT INTO stock_article (stock_ticker,url,publish_date,article_score) VALUES (?,?,?,?)'''

        params = (stock_article.stock_ticker,stock_article.url,datetime.strftime(stock_article.publish_date,self.DATETIME_FORMAT) if stock_article.publish_date is not None else None,stock_article.article_score)

        stock_article_id = self.db_connection.execute_return_id(statement,params)

        stock_article.stock_article_id = stock_article_id

    def save_agg_score(self,agg_score):

        self.logger.debug('Saving Agg Score')

        statement = '''INSERT INTO agg_score (stock_ticker,avg,max,min) VALUES (?,?,?,?)'''

        params = (agg_score.stock_ticker,agg_score.avg,agg_score.max,agg_score.min)

        agg_score_id = self.db_connection.execute_return_id(statement,params)

        agg_score.agg_score_id = agg_score_id

        for stock_article in agg_score.stock_articles: self.__save_agg_score_stock_article(agg_score.agg_score_id,stock_article.stock_article_id)

    def __save_agg_score_stock_article(self,agg_score_id,stock_article_id):

        statement = '''INSERT INTO agg_score_stock_article_xref (agg_score,stock_article) VALUES (?,?)'''

        params = (agg_score_id,stock_article_id)

        self.db_connection.execute(statement,params)

    def gather_agg_score_for_stock_on_date(self,stock_ticker,score_date):

        agg_score = None

        statement = '''SELECT * FROM agg_score WHERE stock_ticker = ? AND score_date = ?'''

        params = (stock_ticker,score_date.strftime(self.DATETIME_FORMAT))

        results = self.db_connection.execute_query(statement,params)

        raw_data = results.fetchone()

        if raw_data is not None:

            agg_score = AggScore(stock_ticker,None,raw_data[0])

            agg_score.avg = raw_data[2]

            agg_score.max = raw_data[3]

            agg_score.min = raw_data[4]

        return agg_score

    def gather_stock_article(self,stock_article):

        statement = '''SELECT * FROM stock_article WHERE url = ?'''

        params = (stock_article.url,)

        results = self.db_connection.execute_query(statement,params)

        raw_data = results.fetchone()

        if raw_data is not None:

            stock_article.stock_article_id = raw_data[0]

            stock_article.publish_date = raw_data[3]

            stock_article.article_score = raw_data[4]

    def shutdown(self):

        self.db_connection.close_connection()
