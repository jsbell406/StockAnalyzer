import os
import sqlite3
import logging

class DatabaseConnection(object):

    def __init__(self):

        connection_string = os.path.realpath(__file__).replace('db_connection.py','StockNews.db')

        self.connection = sqlite3.connect(connection_string)

        self.logger = logging.getLogger()

    def execute_query(self,statement,params=None):

        self.logger.debug('Executing Query: ' + statement)

        cursor = self.connection.cursor()

        if params is None: return cursor.execute(statement)

        else: return cursor.execute(statement,params)

    def execute(self,statement,params=None,do_return_id=False):

        self.logger.debug('Executing Statement: ' + statement)

        cursor = self.connection.cursor()

        if params is None: cursor.execute(statement)

        else: cursor.execute(statement,params)

        self.connection.commit()

    def execute_return_id(self,statement,params=None):

        self.logger.debug('Executing Statement and Returning Id: ' + statement)

        cursor = self.connection.cursor()

        if params is None: cursor.execute(statement)

        else: cursor.execute(statement,params)

        self.connection.commit()

        return cursor.lastrowid

    def close_connection(self):

        self.logger.info('Closing DB Connection')

        self.connection.close()

