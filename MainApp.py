import logging
from logging.config import fileConfig
from service.stock_rater import StockRater, AggScore

if __name__ == '__main__':

    fileConfig('logging_config.ini')

    logger = logging.getLogger()

    logger.info('Starting MainApp')

    stock_ticker = 'TSLA'

    stock_rater = StockRater()
    
    agg_score = stock_rater.rate_stock(stock_ticker)

    stock_rater.shutdown()