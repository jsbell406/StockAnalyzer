import logging
import sys
from logging.config import fileConfig
from service.stock_rater import StockRater
from service.models import AggScore

if __name__ == '__main__':

    fileConfig('logging_config.ini')

    logger = logging.getLogger()

    logger.info('Starting MainApp')

    # stock_ticker = sys.argv[1]
    
    # Testing
    stock_ticker = 'NVDA'

    stock_rater = StockRater()
    
    agg_score = stock_rater.rate_stock(stock_ticker)

    print(agg_score)