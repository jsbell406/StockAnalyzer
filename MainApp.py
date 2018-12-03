import sys
from service.histogram_generator import HistogramGenerator
from service.stock_news_analyzer import StockNewsAnalyzer
from service.models import Stock
from service.stock_recommender import StockRecommender
from service.histogram_generator import HistogramGenerator

if __name__ == '__main__':

    # Analyze one stock of your choice

    # stock_ticker = sys.argv[1]

    stock_ticker = 'NVDA'
    
    # Testing
    # report = StockNewsAnalyzer().analyze_stock(stock_ticker=stock_ticker)

    # print(report)


    # Recommend stocks

    # recommended_stocks = StockRecommender().recommend_stocks()


    # Generate Histogram for stock

    # HistogramGenerator().generate_histogram_for_stock(stock_ticker) # Also takes a stock object