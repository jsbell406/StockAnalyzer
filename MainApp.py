import sys
import os
from service.util.histogram_generator import HistogramGenerator
from service.stock_news_analyzer import StockNewsAnalyzer
from service.data_sources.models import Stock

if __name__ == '__main__':

    # pass

    # Check if DB exists, creating it if not.
    # if os.path.exists('service/StockNews.db') == False:

    #     os.system('sqlite3 service/StockNews.db < CREATE_DB.sql')


    # Analyze one stock of your choice

    stock_ticker = sys.argv[1]

    # stock_ticker = 'AMD'
    
    # Testing
    report = StockNewsAnalyzer().analyze_stock(stock_ticker=stock_ticker)

    print(report)



    # Generate Histogram for stock

    # Single Stock
    # HistogramGenerator().generate_histogram_for_stock(stock_ticker)

    # Multiple stocks (Note that the stock should have already been analyzed for each stock.)
    # HistogramGenerator().generate_histogram_for_stocks(['AMD','NVDA'])
