from decimal import Decimal

try:
    import ujson as json
except ImportError:
    import json

from pprint import pformat
import time

import requests

from authentification_client import AuthenticatedClient

from pynput import keyboard


def gameController(open_orders, order_book, spreads, bets, auth_client, product_id):
    print('initialising strategy')
    time.sleep(10)
    open_orders.get_open_orders()
    #open_orders.cancel_all()
    print('initialising strategy')

    def on_press(key):
        try:
            if key.char == "b":
                open_bid_price = order_book.asks.price_tree.min_key() - spreads.bid_spread - open_orders.open_bid_rejections
                response = auth_client.buy(size = bets, price = str(open_bid_price), side = 'buy', product_id =product_id)
                if 'status' in response and response['status'] == 'pending':
                    #print('pending')
                    open_orders.open_bid_order_id = response['id']
                    open_orders.open_bid_price = open_bid_price
                    open_orders.open_bid_rejections = Decimal('0.0')
                    print('New Bid @ {}'.format(open_bid_price))
                elif 'status' in response and response['status'] == 'rejected':
                    #print('rejected')
                    open_orders.open_bid_order_id = None
                    open_orders.open_bid_price = None
                    open_orders.open_bid_rejections += Decimal('0.04')

                elif 'message' in response and response['message'] == 'Insufficient funds':
                    #print('insufficient funds')
                    open_orders.open_bid_order_id = None
                    open_orders.open_bid_price = None
                else:
                    None
                print("Buy")
            elif key.char == "s":# and 0.01 < float(open_orders.accounts['ETH']['available']):
                open_ask_price = order_book.bids.price_tree.max_key() + spreads.ask_spread + open_orders.open_ask_rejections
                response = auth_client.sell(size = bets, price = str(open_ask_price), side = 'sell', product_id =product_id)
                if 'status' in response and response['status'] == 'pending':
                    open_orders.open_ask_order_id = response['id']
                    open_orders.open_ask_price = open_ask_price
                    print('New ask @ {}'.format(open_ask_price))
                    open_orders.open_ask_rejections = Decimal('0.0')
                elif 'status' in response and response['status'] == 'rejected':
                    open_orders.open_ask_order_id = None
                    open_orders.open_ask_price = None
                    open_orders.open_ask_rejections += Decimal('0.04')
                elif 'message' in response and response['message'] == 'Insufficient funds':
                    open_orders.open_ask_order_id = None
                    open_orders.open_ask_price = None
                else:
                    None
                print("Sell")
            elif key.char == "c":
                open_orders.cancel_all()
                print("canceled all")
            else:
                print('{0} released'.format(
                    key))

        except:
            if key == keyboard.Key.up:
                spreads.ask_spread += Decimal("0.01")
                spreads.bid_spread += Decimal("0.01")
                print("Increased Spread to: ",spreads.ask_spread)

            elif key == keyboard.Key.down:

                if spreads.ask_spread > Decimal("0.01"):
                    spreads.ask_spread -= Decimal("0.01")
                    spreads.bid_spread -= Decimal("0.01")
                    print("Decrease Spread to: ", spreads.ask_spread)

            elif key == keyboard.Key.right:
                print("some")
                bets.size += 0.01
                print("Increased Size to: ", bets.size)

            elif key == keyboard.Key.left:

                if bets.size > 0.01:
                    bets.size -= 0.01
                    print("Decrease Size to: ", bets.size)

            else:
                None

    def on_release(key):
        None

    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
