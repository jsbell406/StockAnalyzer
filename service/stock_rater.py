import re
import newspaper
import time
import logging
import datetime
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.stock_news_collector import StockNewsCollector
from service.models import AggScore, StockTickerNameXref, StockArticle, AggScoreStockArticleXref

class StockRater(object):

    def __init__(self):

        self.stock_news_collector = StockNewsCollector()

        self.analyzer = SentimentIntensityAnalyzer()

        self.article_config = newspaper.configuration.Configuration()

        self.article_config.browser_user_agent = 'My User Agent 1.0'

        self.article_config.headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        self.logger = logging.getLogger()

        self.logger.info('StockRater loaded')

    def rate_stock(self,stock_ticker):

        self.logger.info('Rating ' + stock_ticker)

        agg_score = AggScore.get_or_none(stock_ticker=stock_ticker,score_date=datetime.date.today().strftime('%F'))

        if agg_score is None:

            stock_articles = self.stock_news_collector.collect_articles_for_stock(stock_ticker)

            self.logger.info('Reviewing {} collected articles.'.format(len(stock_articles)))

            for stock_article in stock_articles:

                existing_stock_article = StockArticle.get_or_none(url=stock_article.url)
                
                if existing_stock_article is None:

                    try:

                        newspaper_article = newspaper.Article(stock_article.url,config=self.article_config)

                        newspaper_article.download()

                        newspaper_article.parse()

                        stock_article.publish_date = newspaper_article.publish_date

                        stock_article.article_score = self.__score_text(newspaper_article.text)

                        # Don't want to overdo it.
                        time.sleep(5)

                        stock_article.save()

                    except Exception as e:

                        self.logger.error(e)

                else: stock_article = existing_stock_article

            agg_score = self.__build_agg_score(stock_ticker,stock_articles)

            agg_score.save()

            for stock_article in stock_articles: AggScoreStockArticleXref.create(agg_score=agg_score.id,score_date=datetime.date.today().strftime('%F'),stock_article=stock_article.id)

        return agg_score

    def __score_text(self,text):

        sentences = tokenize.sent_tokenize(text)

        total_compound_score = 0

        for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

        return total_compound_score / len(sentences)

    def __build_agg_score(self,stock_ticker,stock_articles):

        self.logger.info('Building Agg Score for {}s {} articles.'.format(stock_ticker,len(stock_articles)))

        agg_score = AggScore(stock_ticker=stock_ticker)

        total_score = 0

        max_score = -1

        min_score = 1

        for stock_article in stock_articles: 

            article_score = stock_article.article_score

            if article_score is not None:

                total_score += article_score

                max_score = article_score if article_score > max_score else max_score

                min_score = article_score if article_score < min_score else min_score

        agg_score.avg_score = total_score / len(stock_articles)

        agg_score.max_score = max_score

        agg_score.min_score = min_score

        return agg_score