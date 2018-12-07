import logging
import re
import time
from datetime import datetime, date, timedelta
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.models import Article, Stock, StockArticle, ArticleScore

class NewsRater(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.analyzer = SentimentIntensityAnalyzer()

        self.logger.info('StockNewsRater Loaded.')

    def rate_news(self,articles,stock):

        self.logger.info('Rating News')

        for article in articles:

            if Article.get_or_none(url=article.url) is not None: continue

            if self.__publish_date_valid(article):

                self.logger.info('Scoring ' + article.url)

                title_score = self.__score_content(article.title)

                summary_score = self.__score_content(article.summary)

                if title_score != 0 or summary_score != 0:

                    article.save()

                    if title_score != 0: self.__save_content(stock,article,title_score,article.title)

                    if summary_score != 0: self.__save_content(stock,article,summary_score,article.summary)

    def __publish_date_valid(self,article):

        publish_date_valid = False

        pub_date = datetime.strptime(article.publish_date,'%Y-%m-%d').date()

        publish_date_valid = (date.today() - pub_date).days <= 7

        return publish_date_valid

    def __score_content(self,content_text):

        raw_score = 0

        sentences = tokenize.sent_tokenize(content_text)

        if len(sentences) > 0:

            total_compound_score = 0

            for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

            raw_score = total_compound_score / len(sentences)

        return raw_score

    def __save_content(self, stock, article, score, scored_content):

        ArticleScore.create(article=article,score=score,scored_content=scored_content).save()

        if StockArticle.get_or_none(stock_ticker=stock,article=article) is None: StockArticle.create(article=article,stock_ticker=stock).save()