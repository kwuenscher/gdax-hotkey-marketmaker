from pprint import pformat
from decimal import Decimal

import requests
from authentification_client import AuthenticatedClient

class OpenOrders(object):

    def __init__(self, auth_client):

        self.accounts = {}

        self.auth_client = auth_client

        self.open_bid_order_id = None
        self.open_bid_price = None
        self.open_bid_status = None
        self.open_bid_cancelled = False
        self.open_bid_rejections = Decimal('0.0')

        self.open_ask_order_id = None
        self.open_ask_price = None
        self.open_ask_status = None
        self.open_ask_cancelled = False
        self.open_ask_rejections = Decimal('0.0')

    def cancel_all(self):
        self.auth_client.cancel_all(product = self.auth_client.product_id)

    def cancel(self, side):
        if side == 'bid':
            order_id = self.open_bid_order_id
            price = self.open_bid_price
            self.open_bid_cancelled = True
        elif side == 'ask':
            order_id = self.open_ask_order_id
            price = self.open_ask_price
            self.open_ask_cancelled = True
        else:
            return False

        response = self.auth_client.cancel_order(order_id)

        #if response.status_code == 200:
        #    file_logger.info('canceled {0} {1} @ {2}'.format(side, order_id, price))
        #elif 'message' in response and response['message'] == 'order not found':
        #    file_logger.info('{0} already canceled: {1} @ {2}'.format(side, order_id, price))
        #elif 'message' in response and response['message'] == 'Order already done':
        #    file_logger.info('{0} already filled: {1} @ {2}'.format(side, order_id, price))
        #else:
        #    file_logger.error('Unhandled response: {0}'.format((pformat(response))))

    def get_open_orders(self):

        open_orders = self.auth_client.get_orders()

        print('Number of open orders: {}'.format(len(open_orders[0])))

        try:
            self.open_bid_order_id = [order['id'] for order in open_orders[0] if order['side'] == 'buy'][0]
            self.open_bid_price = [Decimal(order['price']) for order in open_orders[0] if order['side'] == 'buy'][0]
        except IndexError:
            self.open_bid_order_id = None
            self.open_bid_price = None
            self.open_bid_status = None
            self.open_bid_cancelled = False
            self.open_bid_rejections = Decimal('0.0')
            #print('not working')

        try:
            self.open_ask_order_id = [order['id'] for order in open_orders[0] if order['side'] == 'sell'][0]
            self.open_ask_price = [Decimal(order['price']) for order in open_orders[0] if order['side'] == 'sell'][0]
        except IndexError:
            self.open_ask_order_id = None
            self.open_ask_price = None
            self.open_ask_status = None
            self.open_ask_cancelled = False
            self.open_ask_rejections = Decimal('0.0')


    def get_balances(self):
        accounts_query = self.auth_client.get_accounts()
        #print(accounts_query)
        for account in accounts_query:
            self.accounts[account['currency']] = account

    @property
    def decimal_open_bid_price(self):
        if self.open_bid_price:
            return self.open_bid_price
        else:
            return Decimal('0.0')

    @property
    def decimal_open_ask_price(self):
        if self.open_ask_price:
            return self.open_bid_price
        else:
            return Decimal('0.0')
