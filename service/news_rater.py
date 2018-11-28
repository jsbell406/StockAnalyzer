import logging
import re
import threading
import newspaper
import time
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.models import Article, Content, Score, ArticleContent, ContentScore, ContentType

class NewsRater(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.analyzer = SentimentIntensityAnalyzer()

        self.article_config = newspaper.configuration.Configuration()

        self.article_config.browser_user_agent = 'My User Agent 1.0'

        self.article_config.headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        self.logger.info('StockNewsRater Loaded')

    def rate_news(self,articles):

        self.logger.info('Reviewing {} articles.'.format(len(articles)))

        host_articles_map = self.map_articles_to_hosts(articles)

        threads = []

        for host in host_articles_map.keys(): 
            
            thread = threading.Thread(target=self.score_articles, args=(host_articles_map[host],))

            thread.daemon = True

            threads.append(thread)

            thread.start()

        for thread in threads: thread.join()

    def map_articles_to_hosts(self, articles):

        self.logger.info('Mapping articles to hosts.')

        host_articles_map = {}

        for stock_article in articles:

            host = re.findall(r':\/\/(.+?)\/',stock_article.url)[0].replace('www.','').replace('.com','').split('.')[-1]

            if host not in host_articles_map.keys(): host_articles_map[host] = []

            host_articles_map[host].append(stock_article)

        return host_articles_map

    def score_articles(self,articles):

        self.logger.info('Scoring articles.')

        for article in articles:

            if article.id is None: # None means the article doesn't exist in the DB.

                content_type_headline = ContentType.get(type='headline')

                content_type_body = ContentType.get(type='body')

                try:

                    newspaper_article = newspaper.Article(article.url,config=self.article_config)

                    newspaper_article.download()

                    newspaper_article.parse()

                    article.publish_date = newspaper_article.publish_date if article.publish_date is None else article.publish_date

                    article.save()

                    self.__save_content(newspaper_article.title, content_type_headline, article)

                    self.__save_content(newspaper_article.text,content_type_body,article)

                    # Don't want to overdo it.
                    time.sleep(5)

                except Exception as e:

                    self.logger.error(e)

    def __save_content(self, content, content_type, article):

        content = Content.create(text=content,content_type=content_type)

        content.save()

        article_content = ArticleContent.create(article_id=article,content_id=content)

        article_content.save()

        score = self.__score_content(content)

        content_score = ContentScore.create(content_id=content,score_id=score)

        content_score.save()

    def __score_content(self,content):

        sentences = tokenize.sent_tokenize(content.text)

        total_compound_score = 0

        for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

        raw_score = total_compound_score / len(sentences)

        score = Score.create(value=raw_score)

        score.save()

        return score

    