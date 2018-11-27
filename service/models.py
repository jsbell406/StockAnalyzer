from peewee import *

database = SqliteDatabase('service/StockNews.db', **{})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Article(BaseModel):
    publish_date = TextField(null=True)
    save_date = TextField(null=True)
    url = TextField()

    class Meta:
        table_name = 'Article'

class Content(BaseModel):
    content_type = IntegerField()
    text = TextField()

    class Meta:
        table_name = 'Content'

class ArticleContent(BaseModel):
    article = ForeignKeyField(column_name='article', field='id', model=Article)
    content = ForeignKeyField(column_name='content', field='id', model=Content)

    class Meta:
        table_name = 'Article_Content'

class Score(BaseModel):
    value = FloatField(null=True)

    class Meta:
        table_name = 'Score'

class ContentScore(BaseModel):
    content = ForeignKeyField(column_name='content_id', field='id', model=Content)
    score = ForeignKeyField(column_name='score_id', field='id', model=Score)

    class Meta:
        table_name = 'Content_Score'

class ContentType(BaseModel):
    type = TextField()

    class Meta:
        table_name = 'Content_Type'

class Stock(BaseModel):
    name = TextField(null=True)
    ticker = TextField(primary_key=True)

    class Meta:
        table_name = 'Stock'

class StockArticle(BaseModel):
    article = ForeignKeyField(column_name='article_id', field='id', model=Article)
    stock_ticker = ForeignKeyField(column_name='stock_ticker', field='ticker', model=Stock)

    class Meta:
        table_name = 'Stock_Article'

class SqliteSequence(BaseModel):
    name = UnknownField(null=True)  # 
    seq = UnknownField(null=True)  # 

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False

