import asyncio
from datetime import datetime
from decimal import Decimal
import argparse

import functools
import pytz

import numpy

#try:
#    import ujson as json
#except ImportError:
    #import json

import json
import logging
from pprint import pformat
import random
from socket import gaierror
import time

from dateutil.tz import tzlocal
from websockets import connect

from open_orders import OpenOrders
from spreads import Spreads
from bets import Bets
from order_book import Book
from controller import gameController
from authentification_client import AuthenticatedClient
from websocket_client import WebsocketClient
import config


import logging
from logging.handlers import RotatingFileHandler

file_handler = RotatingFileHandler('trading_log.csv', 'a', 10 * 1024 * 1024, 100)
file_handler.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s, %(message)s'))
file_handler.setLevel(logging.INFO)

trading_file_logger = logging.getLogger('trading_file_log')
trading_file_logger.addHandler(file_handler)
trading_file_logger.setLevel(logging.INFO)



ARGS = argparse.ArgumentParser(description='Coinbase Exchange bot.')
ARGS.add_argument('--c', action='store_true', dest='command_line', default=False, help='Command line output')
ARGS.add_argument('--t', action='store_true', dest='trading', default=False, help='Trade')

args = ARGS.parse_args()

master_switch = False

if master_switch == True:
    print('Danger Zone!')
    network ='https://api.gdax.com'
    conf_key = config.key_real
    conf_b64 = config.b64secret_real
    conf_pass = config.passphrase_real
else:
    network = "https://api-public.sandbox.gdax.com"
    conf_key = config.key
    conf_b64 = config.b64secret
    conf_pass = config.passphrase

product_id = 'ETH-EUR'

order_book = Book(product_id = product_id)

auth_client = AuthenticatedClient(conf_key, conf_b64 , conf_pass, api_url = network, product_id=product_id)

open_orders = OpenOrders(auth_client)
# Make sure that the accounts are initialised.
#open_orders.get_balances()

#open_orders.cancel_all()

spreads = Spreads()
bets = Bets()


@asyncio.coroutine
def websocket_to_order_book():

    try:
        coinbase_websocket = yield from connect("wss://ws-feed.gdax.com") #wss://ws-feed.gdax.com
    except gaierror:
        print('something went wrong')
        order_book_file_logger.error('socket.gaierror - had a problem connecting to Coinbase feed')
        return

    sub_params = {'type': 'subscribe', 'product_ids': [product_id]}
    yield from coinbase_websocket.send(json.dumps(sub_params))

    messages = []
    while True:
        message = yield from coinbase_websocket.recv()
        message = json.loads(message)
        messages += [message]
        if len(messages) > 50:
            break

    order_book.get_level3()

    [order_book.process_message(message) for message in messages if message['sequence'] > order_book.level3_sequence]

    messages = []

    while True:

        message = yield from coinbase_websocket.recv()

        if message is None:
            order_book_file_logger.error('Websocket message is None.')
            return False
        try:
            message = json.loads(message)
        except TypeError:
            order_book_file_logger.error('JSON did not load, see ' + str(message))
            return False

        if not order_book.process_message(message):
            print(pformat(message))
            return False


        if args.trading:

            if 'order_id' in message and message['order_id'] == open_orders.open_ask_order_id:
                if message['type'] == 'done':
                    open_orders.open_ask_order_id = None
                    open_orders.open_ask_price = None
                    open_orders.open_ask_status = None
                    open_orders.open_ask_rejections = Decimal('0.0')
                    open_orders.open_ask_cancelled = False
                else:
                    open_orders.open_ask_status = message['type']

            elif 'order_id' in message and message['order_id'] == open_orders.open_bid_order_id:
                if message['type'] == 'done':
                    open_orders.open_bid_order_id = None
                    open_orders.open_bid_price = None
                    open_orders.open_bid_status = None
                    open_orders.open_bid_rejections = Decimal('0.0')
                    open_orders.open_bid_cancelled = False
                else:
                    open_orders.open_bid_status = message['type']


def update_orders():
    time.sleep(5)
    open_orders.cancel_all()

    while True:
        open_orders.get_open_orders()
        time.sleep(20)


def monitor():
    time.sleep(5)
    while True:
        time.sleep(0.001)
        print('Last message: {0:.6f} secs, '
              'Min ask: {1:.2f}, Max bid: {2:.2f}, Spread: {3:.2f}, '
              'Your ask: {4:.2f}, Your bid: {5:.2f}, Your spread: {6:.2f} '
              'Avg: {7:.10f} Min: {8:.10f} Max: {9:.10f}'.format(
            ((datetime.now(tzlocal()) - order_book.last_time).microseconds * 1e-6),
            order_book.asks.price_tree.min_key(), order_book.bids.price_tree.max_key(),
            order_book.asks.price_tree.min_key() - order_book.bids.price_tree.max_key(),
            open_orders.decimal_open_ask_price, open_orders.decimal_open_bid_price,
            open_orders.decimal_open_ask_price - open_orders.decimal_open_bid_price,
            order_book.average_rate*1e-6, order_book.fastest_rate*1e-6, order_book.slowest_rate*1e-6), end='\r')


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    loop.run_in_executor(None, functools.partial(gameController, open_orders, order_book, spreads, bets, auth_client, product_id))
    #loop.run_in_executor(None, update_balances)
    loop.run_in_executor(None, update_orders)
    #loop.run_in_executor(None, update_pl)

    n = 0

    while True:
        start_time = loop.time()
        loop.run_until_complete(websocket_to_order_book())
        end_time = loop.time()
        seconds = end_time - start_time
        if seconds < 2:
            n += 1
            sleep_time = (2 ** n) + (random.randint(0, 1000) / 1000)
            order_book_file_logger.error('Websocket connectivity problem, going to sleep for {0}'.format(sleep_time))
            time.sleep(sleep_time)
            if n > 6:
                n = 0
