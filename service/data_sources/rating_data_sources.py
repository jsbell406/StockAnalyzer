from service.data_sources.data_sources import RatingDataSource

class Zacks(RatingDataSource):
    '''Zacks.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RatingDataSource {RatingDataSource} -- The RatingDataSource class, which extends DataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://www.zacks.com/stock/quote/{}',r'<div class="zr_rankbox">[\s\S]+?<p class="rank_view">([^<]+?)<')

class TheStreet(RatingDataSource):
    '''TheStreet.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RatingDataSource {RatingDataSource} -- The RatingDataSource class, which extends DataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://www.thestreet.com/quote/{}',r'<span class="quote-nav-rating-qr-rating.+?\((.+?)\)')

class StockHelpIsland(RatingDataSource):
    '''StockHelpIsland.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RatingDataSource {RatingDataSource} -- The RatingDataSource class, which extends DataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('http://stock.helpisland.com/quote.php?symbol={}',r'<font color="black" size="2"><FONT SIZE=10 color=.+?><p align=center style=\'margin-top: 2; margin-bottom: 0\'>.+?<')

    def parse_rating(self,raw_rating):
        '''Parses raw rating data, returning eithet a 1 for Buy, 0 for Hold, or -1 for Sell. Overrides the same method in RatingDataSource.
        
        Arguments:
            raw_rating {str} -- The raw rating data from the StockHelpIsland webpage html.
        
        Returns:
            int -- The rating (1/0/-1) equivalent of the raw rating data.
        '''
        if 'COLOR=GREEN' in raw_rating: return 1

        elif 'COLOR=RED' in raw_rating: return -1

        elif raw_rating.count('*') == 1: return 0

        else: return None

class SuperStockScreener(RatingDataSource):
    '''SuperStockScreener.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RatingDataSource {RatingDataSource} -- The RatingDataSource class, which extends DataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://www.superstockscreener.com/company/{}',r'<td class=\'rank\'>(.+?)<')

class MarketBeat(RatingDataSource):
    '''MarketBeat.com used as a DataSource via regex applied to the webpage's html.
    
    Arguments:
        RatingDataSource {RatingDataSource} -- The RatingDataSource class, which extends DataSource.
    '''

    def __init__(self):
        '''Constructor'''

        super().__init__('https://www.marketbeat.com/stocks/NASDAQ/{}/price-target/',r'Wall Street analysts have issued ratings and price targets.+?resulting in a consensus rating of "(.+?)\."')