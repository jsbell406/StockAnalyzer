class AggScore(object):

    def __init__(self, stock_ticker, stock_articles,agg_score_id = None):

        self.stock_ticker = stock_ticker

        self.agg_score_id = agg_score_id

        self.stock_articles = stock_articles

        self.avg_score = 0

        self.max_score = 0

        self.min_score = 0

    def __str__(self):

        return '{}\nNum Articles: {}\nAvg: {}\nMax: {}\nMin: {}'.format(self.stock_ticker,len(self.stock_articles),self.avg_score,self.max_score,self.min_score)