from __future__ import print_function
import json
from threading import Thread
from websockets import connect
import asyncio


class WebsocketClient(object):

    def __init__(self, url=None, products=["BTC-USD"], type=None):
        if url is None:
            url = "wss://ws-feed.gdax.com"

        self.url = url
        self.products = products
        self.type = "subscribe" #type or "subscribe"
        self.stop = False
        self.ws = None
        self.thread = None

    def start(self):
        #def _go():
            #self._connect()
            #self._listen()
        while True:
            asyncio.get_event_loop().run_until_complete(self._connect())

        #self.thread = Thread(target=_go)
        #self.thread.start()

    @asyncio.coroutine
    def _connect(self):

        self.onOpen()
        try:
            self.ws = yield from connect(self.url)
        except:
            print('something is fucked')

        if self.products is None:
            self.products = ["BTC-USD"]
        elif not isinstance(self.products, list):
            self.products = [self.products]

        if self.url[-1] == "/":
            self.url = self.url[:-1]

        self.stop = False
        sub_params = {'type': 'subscribe', 'product_ids': self.products}
        yield from self.ws.send(json.dumps(sub_params))
        if self.type == "heartbeat":
            sub_params = {"type": "heartbeat", "on": True}
            yield from self.ws.send(json.dumps(sub_params))

        while not self.stop:
            try:
                msg = yield from self.ws.recv()
            except Exception as e:
                self.onError(e)
                self.close()
            else:
                self.onMessage(json.loads(msg))


    def close(self):
        if not self.stop:
            if self.type == "heartbeat":
                self.ws.send(json.dumps({"type": "heartbeat", "on": False}))
            self.onClose()
            self.stop = True
            #self.thread = None
            #self.thread.join()
            #self.ws.close()

    def onOpen(self):
        print("-- Subscribed! --\n")

    def onClose(self):
        print("\n-- Socket Closed --")

    def onMessage(self, msg):
        pass
        #print(msg)

    def onError(self, e):
        SystemError(e)


if __name__ == "__main__":

    import time

    class myWebsocketClient(WebsocketClient):

        def onOpen(self):
            self.url = "wss://ws-feed.gdax.com/"
            self.products = ["ETH-EUR"]


        def onMessage(self, msg):

            if 'price' in msg and 'type' in msg and 'side' in msg:
                if msg['side'] == 'buy'and msg['type'] == 'open':
                    print(msg)
                else:
                    print(msg)

        def onClose(self):
            print ("-- Goodbye! --")

    mycl = myWebsocketClient()
    mycl.start()
    time.sleep(4)
    mycl.close()
