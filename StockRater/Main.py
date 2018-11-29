from service.stock_provider import StockProvider
from service.rater import Rater
from service.stock import Stock

if __name__ == '__main__':

    # Checking Multiple stocks
    stocks = StockProvider().provide_stocks()

    Rater().rate_stocks(stocks)
    
    for stock in stocks: print(stock)

    # Checking single stock
    # ticker = 'NVDA'

    # market = StockProvider().get_market_for_ticker(ticker)

    # stock = Stock(None,ticker,market,0,0)

    # Rater().rate_stock(stock)

    # print(stock)

#### Testing

# import requests
# import re
# from service.stock import Stock
# from service.source import *

# sources = [TheStreet()]

# stocks = []

# stocks.append(Stock(None,'CCC','NASDAQ',0,0))

# stocks.append(Stock(None,'BVNSC','NYSE',0,0))

# stocks.append(Stock(None,'NIHD','NYSE',0,0))

# stocks.append(Stock(None,'NNA','NASDAQ',0,0))

# stocks.append(Stock(None,'BEDU','NASDAQ',0,0))

# stocks.append(Stock(None,'AMRN','NYSE',0,0))

# stocks.append(Stock(None,'TRVG','NYSE',0,0))

# stocks.append(Stock(None,'JTPY','NYSE',0,0))

# stocks.append(Stock(None,'NAP','NASDAQ',0,0))

# stocks.append(Stock(None,'SEED','NYSE',0,0))

# stocks.append(Stock(None,'BHVN','NASDAQ',0,0))

# stocks.append(Stock(None,'KBH','NASDAQ',0,0))

# for stock in stocks:

#     for source in sources: 

#         headers = {'User-Agent': 'My User Agent 1.0'}

#         url = source.construct_url(stock)

#         response = requests.get(url,allow_redirects=True,headers=headers)

#         text = response.text

#         print(response.status_code)

#         print(response.url)

#         raw_rating = re.findall(source.regex_string,text)[0].strip()

#         print(raw_rating)

#         break

#     break