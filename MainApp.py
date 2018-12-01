import logging
import sys
import time
from logging.config import fileConfig
from service.histogram_generator import HistogramGenerator
from service.stock_news_analyzer import StockNewsAnalyzer
from service.models import Stock

def create_time_spent_message(start_time,stock_ticker):

    end_time = time.time()

    total_time = end_time - start_time

    is_minutes = (total_time / 60) > 1

    total_time = total_time / 60 if is_minutes else total_time

    time_label = 'minutes' if is_minutes else 'seconds'

    return 'It took {0:.1f} {1} to score {2}.'.format(total_time,time_label,stock_ticker)

if __name__ == '__main__':

    # start_time = time.time()

    # # stock_ticker = sys.argv[1]

    # stock_ticker = 'NVDA'
    
    # # Testing
    # StockNewsAnalyzer().analyze_stock(stock_ticker)

    # print(create_time_spent_message(start_time,stock_ticker))



        