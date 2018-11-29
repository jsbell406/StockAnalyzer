import re
from service.rating import Rating

class Source(object):

    def __init__(self,base_url,regex_string):

        self.base_url = base_url

        self.regex_string = regex_string

    def construct_url(self,stock):

        return self.base_url.format(stock.ticker)

    def parse_rating(self,raw_rating):

        if 'Buy' in raw_rating: return Rating.BUY

        elif 'Hold' in raw_rating or 'Neutral' in raw_rating: return Rating.HOLD

        elif 'Sell' in raw_rating: return Rating.SELL

        else: return Rating.NONE

    def __str__(self):

        return re.findall(r'\/\/(.+?)\/',self.base_url)[0]
    

# Implementations =========================================


class Zacks(Source):

    def __init__(self):

        super().__init__('https://www.zacks.com/stock/quote/{}',r'<div class="zr_rankbox">[\s\S]+?<p class="rank_view">([^<]+?)<')

class TheStreet(Source):

    def __init__(self):

        super().__init__('https://www.thestreet.com/quote/{}',r'<span class="quote-nav-rating-qr-rating.+?\((.+?)\)')

class StockHelpIsland(Source):

    def __init__(self):

        super().__init__('http://stock.helpisland.com/quote.php?symbol={}',r'<font color="black" size="2"><FONT SIZE=10 color=.+?><p align=center style=\'margin-top: 2; margin-bottom: 0\'>.+?<')

    def parse_rating(self,raw_rating):

        if 'color=green' in raw_rating: return Rating.BUY

        elif 'color=red' in raw_rating: return Rating.SELL

        elif raw_rating.count('*') == 1: return Rating.HOLD

        else: return Rating.NONE

class SuperStockScreener(Source):

    def __init__(self):

        super().__init__('https://www.superstockscreener.com/company/{}',r'<td class=\'rank\'>(.+?)<')


