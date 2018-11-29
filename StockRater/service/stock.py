from service.rating import Rating

class Stock(object):

    def __init__(self,grade,ticker,market,price,two_wk_price_change):

        self.grade = grade

        self.ticker = ticker

        self.market = market

        self.price = price

        self.two_wk_price_change = two_wk_price_change

        self.ratings = []

    def __str__(self):

        info = '{} : {}\nPrice: {}\n2wk Price Change: {}\n\tRatings\n\tInitial Grade: {}\n\t'.format(self.market,self.ticker,self.price,self.two_wk_price_change,self.grade)

        for rating in self.ratings: info += '\n\t{}'.format(rating)

        return info