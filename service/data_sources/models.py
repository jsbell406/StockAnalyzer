import os
from peewee import *

current_dir = os.path.dirname(os.path.realpath(__file__))

db_path = current_dir + '/StockNews.db'

database = SqliteDatabase(db_path, **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Article(BaseModel):
    publish_date = TextField(null=True)
    save_date = TextField(null=True)
    summary = TextField(null=True)
    title = TextField(null=True)
    url = TextField()

    class Meta:
        table_name = 'Article'

class ArticleScore(BaseModel):
    article = ForeignKeyField(column_name='article_id', field='id', model=Article)
    score = FloatField()
    scored_content = TextField()

    class Meta:
        table_name = 'Article_Score'

class Rating(BaseModel):
    rating_date = TextField(null=True)
    source = TextField(null=True)
    value = IntegerField()

    class Meta:
        table_name = 'Rating'

class Stock(BaseModel):
    market = TextField(null=True)
    name = TextField(null=True)
    ticker = TextField(primary_key=True)

    class Meta:
        table_name = 'Stock'

class StockArticle(BaseModel):
    article = ForeignKeyField(column_name='article_id', field='id', model=Article)
    stock_ticker = ForeignKeyField(column_name='stock_ticker', field='ticker', model=Stock)

    class Meta:
        table_name = 'Stock_Article'

class StockRating(BaseModel):
    rating = ForeignKeyField(column_name='rating_id', field='id', model=Rating)
    stock_ticker = ForeignKeyField(column_name='stock_ticker', field='ticker', model=Stock)

    class Meta:
        table_name = 'Stock_Rating'

class StockRecommendation(BaseModel):
    recommendation_date = TextField(null=True)
    stock_ticker = ForeignKeyField(column_name='stock_ticker', field='ticker', model=Stock, null=True)

    class Meta:
        table_name = 'Stock_Recommendation'

class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

