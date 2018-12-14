import sys
import os
from service.util.histogram_generator import HistogramGenerator
from service.stock_news_analyzer import StockNewsAnalyzer
from service.data_sources.models import Stock

def provide_usage():
    '''Provides simple usage text.'''

    print("You'll need to provide a stock ticker to use the StockNewsAnalyzer, E.g.\npython3 MainApp.py ABCDE")

if __name__ == '__main__':
    ''' Main Method/Driver'''

    # Check if DB exists, creating it if not.
    if os.path.exists('service/data_sources/StockNews.db') == False:

        # WARNING Only been tested on Linux 18.04
        os.system('sqlite3 service/StockNews.db < CREATE_DB.sql')


    # Gather the stock ticker to analyze.

    try:

        stock_ticker = sys.argv[1]

    except:
        
        # Don't need to throw the error since we know what went wrong.
        pass


    if stock_ticker is None: provide_usage()

    else:

        # Generate and provide the report
        report = StockNewsAnalyzer().analyze_stock(stock_ticker=stock_ticker)

        print(report)

        # Generate Histogram for stock

        # Single Stock
        HistogramGenerator().generate_histogram_for_stock(stock_ticker)

        # Multiple stocks (Note that the stock should have already been analyzed for each stock.)
        # HistogramGenerator().generate_histogram_for_stocks(['AMD','NVDA'])
