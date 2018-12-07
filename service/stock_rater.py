import logging
import threading
import time
from service.rating_sources import *

class StockRater(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.sources = [Zacks(),TheStreet(),StockHelpIsland(),SuperStockScreener()]

        self.sources = [Zacks()]

        self.logger.info('StockRater Loaded.')

    def rate_stocks(self, stocks):

        self.logger.info('Rating Stocks ' + ', '.join([stock.ticker for stock in stocks]))

        for stock in stocks:

            self.rate_stock(stock)

            time.sleep(5)

    def rate_stock(self,stock):

        self.logger.info('Rating ' + stock.ticker)

        threads = []

        for source in self.sources:

            thread = threading.Thread(target=source.collect_data_from_source_for_stock, args=(stock,))

            thread.daemon = True

            threads.append(thread)

            thread.start()

        for thread in threads: thread.join()