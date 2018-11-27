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

        host_articles_map = {}

        for stock_article in articles:

            host = re.findall(r':\/\/(.+?)\/',stock_article.url)[0].replace('www.','').replace('.com','').split('.')[-1]

            if host not in host_articles_map.keys(): host_articles_map[host] = []

            host_articles_map[host].append(stock_article)

        return host_articles_map

        # https://www.ploggingdev.com/2017/01/multiprocessing-and-multithreading-in-python-3/
        # with Pool(len(host_articles_map.keys())) as process_pool:

        #     for host in host_articles_map.keys(): process_pool.map(self.score_articles, host_articles_map[host])

    def score_articles(self,articles):

        for article in articles:

            if article.id is None: # None means the article doesn't exist in the DB.
                
                article.save()

                try:

                    newspaper_article = newspaper.Article(article.url,config=self.article_config)

                    newspaper_article.download()

                    newspaper_article.parse()

                    article.publish_date = newspaper_article.publish_date if article.publish_date is None else article.publish_date

                    content_type_headline = ContentType.get(type='headline')

                    content_type_body = ContentType.get(type='body')

                    for i in range(2):

                        newspaper_content = newspaper_article.title if i == 0 else newspaper_article.text

                        content = Content(text=newspaper_content,type=(content_type_headline.id if i == 0 else content_type_body.id))

                        content.save()

                        ArticleContent.create(article_id=article.id,content_id=content.id)

                        score = self.__score_content(newspaper_content)

                        score.save()

                        ContentScore.create(content_id=content.id,score_id=score.id)

                    # Don't want to overdo it.
                    time.sleep(5)

                except Exception as e:

                    self.logger.error(e)

    def __score_content(self,text):

        sentences = tokenize.sent_tokenize(text)

        total_compound_score = 0

        for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

        raw_score = total_compound_score / len(sentences)

        score = Score(value=raw_score)

        return score