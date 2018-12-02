import logging
import sys
import time
from logging.config import fileConfig
from service.histogram_generator import HistogramGenerator
from service.stock_news_analyzer import StockNewsAnalyzer
from service.models import Stock
from service.stock_recommender import StockRecommender

if __name__ == '__main__':

    # Analyze one stock of your choice

    # stock_ticker = sys.argv[1]

    stock_ticker = 'NVDA'
    
    # Testing
    StockNewsAnalyzer().analyze_stock(stock_ticker=stock_ticker)


    # Recommend stocks

    # recommended_stocks = StockRecommender().recommend_stocks()