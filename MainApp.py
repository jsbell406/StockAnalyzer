import logging
import sys
import time
from logging.config import fileConfig
from service.stock_rater import StockRater
from service.models import AggScore

def create_time_spent_message(start_time):

    end_time = time.time()

    total_time = end_time - start_time

    is_minutes = (total_time / 60) > 1

    total_time = total_time / 60 if is_minutes else total_time

    time_label = 'minutes' if is_minutes else 'seconds'

    return 'It took {0:.1f} {1} to score {2}.'.format(total_time,time_label,stock_ticker)

if __name__ == '__main__':

    start_time = time.time()

    fileConfig('logging_config.ini')

    logger = logging.getLogger()

    logger.info('Starting MainApp')

    # stock_ticker = sys.argv[1]
    
    # Testing
    stock_ticker = 'TSLA'

    stock_rater = StockRater()
    
    agg_score = stock_rater.rate_stock(stock_ticker)

    logger.info(agg_score)

    logger.info(create_time_spent_message(start_time))