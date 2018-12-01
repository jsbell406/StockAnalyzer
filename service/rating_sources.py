from service.data_sources import RatingSource

class Zacks(RatingSource):

    def __init__(self):

        super().__init__('https://www.zacks.com/stock/quote/{}',r'<div class="zr_rankbox">[\s\S]+?<p class="rank_view">([^<]+?)<')

class TheStreet(RatingSource):

    def __init__(self):

        super().__init__('https://www.thestreet.com/quote/{}',r'<span class="quote-nav-rating-qr-rating.+?\((.+?)\)')

class StockHelpIsland(RatingSource):

    def __init__(self):

        super().__init__('http://stock.helpisland.com/quote.php?symbol={}',r'<font color="black" size="2"><FONT SIZE=10 color=.+?><p align=center style=\'margin-top: 2; margin-bottom: 0\'>.+?<')

    def parse_rating(self,raw_rating):

        if 'color=green' in raw_rating: return 1

        elif 'color=red' in raw_rating: return -1

        elif raw_rating.count('*') == 1: return 0

        else: None

class SuperStockScreener(RatingSource):

    def __init__(self):

        super().__init__('https://www.superstockscreener.com/company/{}',r'<td class=\'rank\'>(.+?)<')