'''The equivalent of a Java .properties file.
There's only one DataSource that needs an api key- news_sources.NewsApi.
The api key isn't included by default b/c only 1000 queries are allowed/key/day.
If you don't include one it won't break anything.
If you want your own go here: https://newsapi.org/register

Then replace the value for news_api_key with your NewsApi api key.
'''

no_news_api_key = '<< YOUR API KEY HERE >>'

news_api_key = '<< YOUR API KEY HERE >>'