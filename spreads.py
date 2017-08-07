from decimal import Decimal

# Spread needs to adjust according to volatility estimatsions.
# Propriatary intentions. Predicting whether price goes up or down.
    # - if the price goes up make ask price more competitive.
    # - if the price goes down make the bid price more competitive.
# risk of assymetric information. i.e. earnings reporsts.


class Spreads(object):
    def __init__(self):
        # amount over the highest bid that you are willing to buy btc for
        self.bid_spread = Decimal('0.01')

        # amount below the lowest ask that you are willing to sell btc for
        self.ask_spread = Decimal('0.01')

    # spread at which your ask is cancelled
    @property
    def ask_too_far_adjustment_spread(self):
        return Decimal(self.ask_spread) + Decimal('0.03')

    @property
    def ask_too_close_adjustment_spread(self):
        return Decimal(self.ask_spread) - Decimal('0.08')

    # spread at which your bid is cancelled
    @property
    def bid_too_far_adjustment_spread(self):
        return Decimal(self.bid_spread) + Decimal('0.05')

    @property
    def bid_too_close_adjustment_spread(self):
        return Decimal(self.bid_spread) - Decimal('0.03')
