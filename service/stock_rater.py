import re
import newspaper
import time
import logging
import datetime
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.stock_news_collector import StockNewsCollector
from service.db_utility import DatabaseUtility
from service.agg_score import AggScore

class StockRater(object):

    def __init__(self):

        self.stock_news_collector = StockNewsCollector()

        self.db_utility = DatabaseUtility()

        self.analyzer = SentimentIntensityAnalyzer()

        self.article_config = newspaper.configuration.Configuration()

        self.article_config.browser_user_agent = 'My User Agent 1.0'

        self.article_config.headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        self.logger = logging.getLogger()

        self.logger.info('StockRater loaded')

    def rate_stock(self,stock_ticker):

        self.logger.info('Rating ' + stock_ticker)

        agg_score = self.db_utility.gather_agg_score_for_stock_on_date(stock_ticker,datetime.datetime.now())

        if agg_score is None:

            stock_articles = self.stock_news_collector.collect_articles_for_stock(stock_ticker)

            self.logger.info('Reviewing {} collected articles.'.format(len(stock_articles)))

            for stock_article in stock_articles:

                self.db_utility.gather_stock_article(stock_article)
                
                if stock_article.stock_article_id is None:

                    try:

                        newspaper_article = newspaper.Article(stock_article.url,config=self.article_config)

                        newspaper_article.download()

                        newspaper_article.parse()

                        stock_article.publish_date = newspaper_article.publish_date

                        stock_article.article_score = self.__score_text(newspaper_article.text)

                        # Don't want to overdo it.
                        time.sleep(5)

                        self.db_utility.save_article(stock_article)

                    except Exception as e:

                        self.logger.error(e)

            agg_score = self.__build_agg_score(stock_ticker,stock_articles)

            self.db_utility.save_agg_score(agg_score)

        return agg_score

    def __score_text(self,text):

        sentences = tokenize.sent_tokenize(text)

        total_compound_score = 0

        for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

        return total_compound_score / len(sentences)

    def __build_agg_score(self,stock_ticker,stock_articles):

        self.logger.info('Building Agg Score for {}s {} articles.'.format(stock_ticker,len(stock_articles)))

        agg_score = AggScore(stock_ticker,stock_articles)

        total_score = 0

        max_score = 0

        min_score = 1000

        for stock_article in stock_articles: 

            article_score = stock_article.article_score

            total_score += article_score

            max_score = article_score if article_score > max_score else max_score

            min_score = article_score if article_score < min_score else min_score

        agg_score.avg = total_score / len(stock_articles)

        agg_score.max = max_score

        agg_score.min = min_score

        self.logger.info(agg_score)

        return agg_score

    def shutdown(self):

        self.db_utility.shutdown()
