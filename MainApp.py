# import sys
# import os
# from service.histogram_generator import HistogramGenerator
# from service.stock_news_analyzer import StockNewsAnalyzer
# from service.models import Stock
# from service.stock_recommender import StockRecommender
# from service.histogram_generator import HistogramGenerator

# if __name__ == '__main__':

#     # if os.path.exists('service/StockNews.db') == False:

#     #     os.system('sqlite3 service/StockNews.db < CREATE_DB.sql')

#     # Analyze one stock of your choice

#     # stock_ticker = sys.argv[1]

#     stock_ticker = 'NVDA'
    
#     # Testing
#     report = StockNewsAnalyzer().analyze_stock(stock_ticker=stock_ticker)

#     print(report)


#     # Recommend stocks

#     # recommended_stocks = StockRecommender().recommend_stocks()


#     # Generate Histogram for stock

#     HistogramGenerator().generate_histogram_for_stock(stock_ticker) # Also takes a stock object

import requests

if __name__ == "__main__":

    # headers = {'Accept': 'application/json'}
    
    response = requests.get('https://marketdata.websol.barchart.com/getNews.json?apikey=769916ee01d11c2065d9980464e8b030&sources=AP%2CIF&symbols=AMZN%2CGOOG%2CAAPL&category=stocks&subCategory=tech&series=MORNCALL&keyword=tablet&maxRecords=10&startDate=2018-12-03T10%3A47%3A39&displayType=preview&images=true&storyId=259220&rss=false&fields=publishDateHost:%20ondemand.websol.barchart.comPOSTPOST%20https://ondemand.websol.barchart.com/getNews.jsonHost:%20ondemand.websol.barchart.comContent-Type:%20application/x-www-form-urlencodedContent-Length:%20lengthapikey=YOUR_API_KEY&sources=AP%2CIF&symbols=AMZN%2CGOOG%2CAAPL&category=stocks&subCategory=tech&series=MORNCALL&keyword=tablet&maxRecords=10&startDate=2018-12-03T10%3A47%3A39&displayType=preview&images=true&storyId=259220&rss=false&fields=publishDateResponse{%22status%22:%20{%22code%22:%20200,%22message%22:%20%22Success.%22},%22results%22:%20[{%22newsID%22:%20null,%22timestamp%22:%20null,%22source%22:%20null,%22categories%22:%20[],%22subCategories%22:%20[],%22headline%22:%20null,%22isExternal%22:%20null,%22publishDate%22:%20null,%22imageURL%22:%20null,%22imageCaption%22:%20null,%22imageHeight%22:%20null,%22imageWidth%22:%20null,%22preview%22:%20null,%22headlineURL%22:%20null,%22pdfURL%22:%20null}]}') # , headers=headers

    code = response.status_code

    text = response.text

    print(code)

    print(text)