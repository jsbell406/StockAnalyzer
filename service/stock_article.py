class StockArticle(object):

    def __init__(self,stock_ticker,url,stock_article_id=None):

        self.stock_article_id = stock_article_id

        self.stock_ticker = stock_ticker

        self.url = url

        self.publish_date = None

        self.article_score = -1