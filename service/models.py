from peewee import *

database = SqliteDatabase('service/StockNews.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class AggScore(BaseModel):
    avg_score = FloatField(null=True)
    max_score = FloatField(null=True)
    min_score = FloatField(null=True)
    score_date = TextField(null=True)
    stock_ticker = TextField()

    class Meta:
        table_name = 'agg_score'

class AggScoreStockArticleXref(BaseModel):
    agg_score = IntegerField(null=True)
    score_date = TextField(null=True)
    stock_article = IntegerField(null=True)

    class Meta:
        table_name = 'agg_score_stock_article_xref'

class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

class StockArticle(BaseModel):
    article_score = FloatField(null=True)
    publish_date = TextField(null=True)
    save_date = TextField(null=True)
    stock_ticker = TextField()
    url = TextField()

    class Meta:
        table_name = 'stock_article'

class StockTickerNameXref(BaseModel):
    stock_name = TextField(null=True)
    stock_ticker = TextField(null=True)

    class Meta:
        table_name = 'stock_ticker_name_xref'
        primary_key = False

