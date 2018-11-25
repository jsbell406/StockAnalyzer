import logging
import re
import threading
import newspaper
import time
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.models import StockArticle

class StockNewsRater(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.analyzer = SentimentIntensityAnalyzer()

        self.article_config = newspaper.configuration.Configuration()

        self.article_config.browser_user_agent = 'My User Agent 1.0'

        self.article_config.headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        self.logger.info('StockNewsRater Loaded')

    def rate_stock_news(self,stock_articles):

        self.logger.info('Reviewing {} articles.'.format(len(stock_articles)))

        host_articles_map = {}

        for stock_article in stock_articles:

            host = re.findall(r':\/\/(.+?)\/',stock_article.url)[0].replace('www.','').replace('.com','').split('.')[-1]

            if host not in host_articles_map.keys(): host_articles_map[host] = []

            host_articles_map[host].append(stock_article)

        threads = []

        for host in host_articles_map.keys(): 
            
            thread = threading.Thread(target=self.score_articles, args=(host_articles_map[host],))

            thread.daemon = True

            threads.append(thread)

            thread.start()

        for thread in threads: thread.join()

        # https://www.ploggingdev.com/2017/01/multiprocessing-and-multithreading-in-python-3/
        # with Pool(len(host_articles_map.keys())) as process_pool:

        #     for host in host_articles_map.keys(): process_pool.map(self.score_articles, host_articles_map[host])

    def score_articles(self,stock_articles):

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

                except Exception as e:

                    self.logger.error(e)

            else: stock_article = existing_stock_article

    def __score_text(self,text):

        sentences = tokenize.sent_tokenize(text)

        total_compound_score = 0

        for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

        return total_compound_score / len(sentences)