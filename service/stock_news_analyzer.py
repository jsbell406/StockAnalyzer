import re
import time
import logging
from logging.config import fileConfig
from datetime import datetime, date
from service.news_collector import NewsCollector
from service.news_rater import NewsRater
from service.models import *
from service.histogram_generator import HistogramGenerator

class StockNewsAnalyzer(object):

    def __init__(self):

        fileConfig('logging_config.ini')

        self.news_collector = NewsCollector()

        self.news_rater = NewsRater()

        self.histogram_generator = HistogramGenerator()

        self.logger = logging.getLogger()

        self.logger.info('StockRater loaded')

    def analyze_stock(self,stock_ticker):

        stock = Stock.get_or_none(ticker=stock_ticker)

        if stock is not None:

            self.logger.info('Rating ' + stock.ticker)

            articles = self.news_collector.collect_news_for_stock(stock)

            self.news_rater.rate_news(articles)

            content_type_headline = ContentType.get(type='headline')

            content_type_body = ContentType.get(type='body')

            headline_scores = Score.select(Score.value).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_headline) & (Stock == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')))

            body_scores = Score.select(Score.value).join(ContentScore, JOIN.INNER).join(Content, JOIN.INNER).join(ArticleContent, JOIN.INNER).join(Article, JOIN.INNER).join(StockArticle, JOIN.INNER).where((Content.content_type == content_type_body) & (Stock == stock) & (Article.save_date == date.today().strftime('%Y-%m-%d')))

            headline_body_scores = headline_scores + body_scores

            title_dataset_map = {}

            title_dataset_map['HEADLINE'] = headline_scores

            title_dataset_map['BODY'] = body_scores

            title_dataset_map['HEADLINE & BODY'] = headline_body_scores

            self.histogram_generator.generate_histogram(title_dataset_map)