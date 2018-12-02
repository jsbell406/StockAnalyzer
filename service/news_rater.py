import logging
import re
import threading
import newspaper
import time
from datetime import datetime, date, timedelta
from nltk import tokenize
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from service.models import Article, Content, Score, ArticleContent, ContentScore, ContentType, Stock, StockArticle

class NewsRater(object):

    def __init__(self):

        self.logger = logging.getLogger()

        self.analyzer = SentimentIntensityAnalyzer()

        self.article_config = newspaper.configuration.Configuration()

        self.article_config.browser_user_agent = 'My User Agent 1.0'

        self.article_config.headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.com'}

        self.logger.info('StockNewsRater Loaded.')

    def rate_news(self,articles,stock):

        self.logger.info('Reviewing {} articles.'.format(len(articles)))

        host_articles_map = self.map_articles_to_hosts(articles)

        threads = []

        for host in host_articles_map.keys(): 
            
            thread = threading.Thread(target=self.score_articles, args=(host_articles_map[host],stock))

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

    def score_articles(self,articles,stock):

        self.logger.info('Scoring articles.')

        articles_to_remove = []

        for article in articles:

            self.logger.info('Scoring ' + article.url)

            if article.id is None: # None means the article doesn't exist in the DB.

                content_type_headline = ContentType.get(type='headline')

                content_type_body = ContentType.get(type='body')

                try:

                    newspaper_article = newspaper.Article(article.url,config=self.article_config)

                    newspaper_article.download()

                    newspaper_article.parse()

                    article.publish_date = newspaper_article.publish_date if article.publish_date is None else article.publish_date

                    title_score = self.__score_content(newspaper_article.title)

                    text_score = self.__score_content(newspaper_article.text)

                    if self.__publish_date_valid(article) and self.__stock_mentioned_in_article(stock,newspaper_article.title, newspaper_article.text) and (title_score != 0 or text_score != 0):

                        article.save()

                        if title_score != 0: self.__save_content(newspaper_article.title, title_score, content_type_headline, article)

                        if text_score != 0: self.__save_content(newspaper_article.text, text_score, content_type_body, article)

                        stock_article = StockArticle.create(stock_ticker=stock,article=article)

                        stock_article.save()

                    else: articles_to_remove.append(article)

                    # Don't want to overdo it.
                    time.sleep(5)

                except Exception as e:

                    self.logger.error(e)

    def __score_content(self,content_text):

        raw_score = 0

        sentences = tokenize.sent_tokenize(content_text)

        if len(sentences) > 0:

            total_compound_score = 0

            for sentence in sentences: total_compound_score += self.analyzer.polarity_scores(sentence)['compound']

            raw_score = total_compound_score / len(sentences)

        return raw_score

    def __save_content(self, content_text, content_score, content_type, article):

        content = Content.create(text=content_text,content_type=content_type)

        content.save()

        article_content = ArticleContent.create(article_id=article,content_id=content)

        article_content.save()

        score = Score.create(value=content_score)

        score.save()

        content_score = ContentScore.create(content_id=content,score_id=score)

        content_score.save()

    def __publish_date_valid(self,article):

        publish_date_valid = False

        try:

            pub_date = None

            if isinstance(article.publish_date, str):

                pub_date = article.publish_date if 'T' not in article.publish_date else article.publish_date.split('T')[0]

                pub_date = datetime.strptime(pub_date,'%Y-%m-%d').date()

            elif isinstance(article.publish_date, datetime):

                pub_date = article.publish_date.date()

            publish_date_valid = pub_date >= (date.today() - timedelta(days = 7))

        except Exception as e:

            self.logger.error(e)

        return publish_date_valid

    def __stock_mentioned_in_article(self,stock,title,text):

        stock_mentioned_in_article = False

        if title is not None:

            stock_mentioned_in_article = stock.ticker in title or stock.name in title

        if text is not None and stock_mentioned_in_article == False:

            stock_mentioned_in_article = stock.ticker in text or stock.name in text

        return stock_mentioned_in_article