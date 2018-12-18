import logging
import re
import time
from datetime import datetime, date, timedelta
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.data_sources.models import Article, Stock, StockArticle, ArticleScore

class NewsRater(object):
    '''Rates News Articles via sentiment analysis.'''

    def __init__(self):
        '''Constructor'''

        self.logger = logging.getLogger()

        self.analyzer = SentimentIntensityAnalyzer()

        self.logger.info('StockNewsRater Loaded.')

    def rate_news(self,articles,stock):
        '''Rates a list of Stock Articles.
        
        Arguments:
            articles {list} -- The articles to rate.
            stock {Stock} -- The Stock the Articles relate to.
        '''

        self.logger.info('Rating News')

        for article in articles:

            # Don't rate articles you've already rated.
            if Article.get_or_none(url=article.url) is not None: continue

            if self.__publish_date_acceptable(article):

                self.logger.info('Scoring ' + article.url)

                # Rate the title and summary.
                title_score = self.__score_content(article.title) if article.title is not None else 0

                summary_score = self.__score_content(article.summary) if article.summary is not None else 0

                if title_score != 0 or summary_score != 0:

                    # Save all the ratings.
                    article.save()

                    if title_score != 0: self.__save_content(stock,article,title_score,article.title)

                    if summary_score != 0: self.__save_content(stock,article,summary_score,article.summary)

    def __publish_date_acceptable(self,article):
        '''Determines if the publish date for a given Article is within an acceptable range.
        
        Arguments:
            article {Article} -- The Article whose publish date to review.
        
        Returns:
            bool -- True if the Article's publish date is acceptable.
        '''

        publish_date_valid = False

        # Create a date object from the Article's publish date.
        pub_date = datetime.strptime(article.publish_date,'%Y-%m-%d').date()

        # TODO Determine the best range to use. 1 week may be too long.
        # Determine the number of days between today and the publish date.
        # The subtraction results in a datetime.timedelta object, which is why the .days property is called on the result of date.today() - pub_date.
        publish_date_valid = (date.today() - pub_date).days <= 7

        return publish_date_valid

    def __score_content(self,content_text):
        '''Scores the given text content.
        
        Arguments:
            content_text {str} -- The text content to score.
        
        Returns:
            float -- The score of the text content.
        '''

        avg_score = 0

        # Converts a chunk of text into individual sentences.
        sentences = tokenize.sent_tokenize(content_text)

        if len(sentences) > 0:

            total_score = 0

            # Score each sentence in the text individually.
            # The polarity_scores method returns a variety of values, 'compound' is the composite of them all.
            for sentence in sentences: total_score += self.analyzer.polarity_scores(sentence)['compound']

            # Average all the sentence scores.
            avg_score = total_score / len(sentences)

        return avg_score

    def __save_content(self, stock, article, score, scored_content):
        '''Saves the scored content in the database.
        
        Arguments:
            stock {Stock} -- The Stock associated with the content.
            article {Article} -- The Article associated with the content.
            score {float} -- The content score.
            scored_content {str} -- The content that was scored.
        '''

        # Only saves the data if it hasn't already been saved.
        if ArticleScore.get_or_none(article=article,score=score,scored_content=scored_content) is None: ArticleScore.create(article=article,score=score,scored_content=scored_content).save()

        if StockArticle.get_or_none(stock_ticker=stock,article=article) is None: StockArticle.create(article=article,stock_ticker=stock).save()