class StockRater(object):

    def __init__(self):

        self.sources = [Zacks(),TheStreet(),StockHelpIsland(),SuperStockScreener()]