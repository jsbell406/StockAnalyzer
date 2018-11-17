from datetime import datetime
import logging
from service.db_connection import DatabaseConnection

class DatabaseUtility(object):

    # 2018-11-16 19:39:12
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self):

        self.db_connection = DatabaseConnection()

        self.logger = logging.getLogger()

        self.logger.info('DatabaseUtility Loaded')

    def is_article_saved(self,stock_article):

        self.logger.debug('Checking if article has been saved: ' + stock_article.url)

        statement = '''SELECT COUNT(*) FROM stock_article WHERE url = ?'''

        params = (stock_article.url,)

        results = self.db_connection.execute_query(statement,params)

        article_saved = results.fetchone()[0] > 0

        return article_saved

    def save_article(self,stock_article):

        self.logger.debug('Saving article: ' + stock_article.url)

        statement = '''INSERT INTO stock_article (stock_ticker,url,publish_date,article_score) VALUES (?,?,?,?)'''

        params = (stock_article.stock_ticker,stock_article.url,datetime.strftime(stock_article.publish_date,self.DATETIME_FORMAT),stock_article.article_score)

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

    def shutdown(self):

        self.db_connection.close_connection()
