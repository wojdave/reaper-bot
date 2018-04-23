import datetime
import logging

logging.basicConfig(filename='/var/log/reaper.log',level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')

#logging.debug('set level=logging.DEBUG')
#logging.info('set level=logging.INFO')
#logging.warning('set level=logging.WARNING')

import asyncio
import json
import threading
import urllib
import urllib.request
from collections import OrderedDict

import websockets

GET_TICKERS_URL = 'https://poloniex.com/public?command=returnTicker'
API_LINK = 'wss://api2.poloniex.com'
SUBSCRIBE_COMMAND = '{"command":"subscribe","channel":$}'
TICKER_SUBSCRIBE = 1002
#TICKER_OUTPUT = 'TICKER UPDATE {}={}(last),{}(lowestAsk),{}(highestBid),{}(percentChange),{}(baseVolume),{}(quoteVolume),{}(isFrozen),{}(high24hr),{}(low24hr)'
#TRADE_OUTPUT = 'TRADE {}={}(tradeId),{}(bookSide),{}(price),{}(size),{}(timestamp)'

TICKER_OUTPUT = "INSERT INTO ticker (currencyPair,last,lowestAsk,highestBid,baseVolume,quoteVolume,isFrozen) VALUES ('{}',{},{},{},{},{},{});"
TRADE_OUTPUT =  "INSERT INTO market (currencyPair,tradeID,type,rate,total,timestamp) VALUES ('{}',{},'{}',{},{},{});"
ORDER_OUTPUT ="INSERT INTO orderBook (currencyPair,type,rate) VALUES ('{}','{}',{}) ON DUPLICATE KEY UPDATE amount=amount+{};"
                                #print(ORDER_OUTPUT.format(ticker_id, side, price, size))

                                #print('Add or change {},side={},price={},size={}'.format(ticker_id, side, price, size))
                                #print ("INSERT INTO orderBook (currencyPair,type,rate,amount) VALUES ('{}','{}',{},{});".format(ticker_id, side, price, size))

                                #print('Remove {},side={},price={}'.format(ticker_id, side, price))
                                #print("DELETE FROM orderBook WHERE currencyPair = '{}' AND type = '{}' AND rate = '{}';".format(ticker_id, side, price))

class PoloniexSubscriber(object):

    def __init__(self):
        tickers_data = self._get_all_tickers()
        self._tickers_list = []
        self._tickers_id = {}  # map to tranlate id (integer) to ticker name
        for ticker, data in tickers_data.items():
            self._tickers_id[data['id']] = ticker
            self._tickers_list.append(ticker)
        self._sub_thread = None
        self._event_loop = None
        self._last_seq_dic = {}

    def get_tickers(self):
        return self._tickers_list

    @staticmethod
    def _get_all_tickers():
        req = urllib.request.Request(GET_TICKERS_URL)
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
        data = the_page.decode('utf8')
        data = json.loads(data)
        return data

    def start_subscribe(self):
        self._sub_thread = threading.Thread(target=self._start_subscriber)
        self._sub_thread.daemon = True
        self._sub_thread.start()

    def _start_subscriber(self):
        self._event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._event_loop)
        self._event_loop.run_until_complete(self._subscribe())

    async def _subscribe(self):
        async with websockets.connect(API_LINK) as websocket:
            # first subscribe to ticker channel and all tickers update channels
            await websocket.send(SUBSCRIBE_COMMAND.replace(
                '$', str(TICKER_SUBSCRIBE)))
            for ticker in self._tickers_list:
                req = SUBSCRIBE_COMMAND.replace(
                    '$', '\"' + ticker + '\"')
                await websocket.send(req)

            # now parse received data
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message, object_pairs_hook=OrderedDict)
                except websocket.ConnectionClosed:
                    logging.error('connection closed message={}'.format(message))
                    pass
                if 'error' in data:
                    logging.error('error arrived message={}'.format(message))
                    raise Exception('error arrived message={}'.format(message))

                if data[0] == 1010:
                    logging.info('heartbeat ')
                    continue
                if len(data) < 2:
                    logging.warning('Short message arrived message={} ')
                    raise Exception(
                        'Short message arrived message={}'.format(message))
                if data[1] == 1:
                    logging.info('subscription successful')
                    continue
                if data[1] == 0:
                    logging.info('subscription failed message={} '.format(message))
                    raise Exception(
                        'subscription failed message={}'.format(message))
                if data[0] == TICKER_SUBSCRIBE:
                    #logging.info('subscribed to ticker')
                    values = data[2]
                    ticker_id_int = values[0]
                    #last = values[1]
                    #lowestAsk = values[2]
                    #highestBid = values[3]
                    #percentChange = values[4]
                    #baseVolume = values[5]
                    #quoteVolume = values[6]
                    #isFrozen = values[7]
                    #high24hr = values[8]
                    #low24hr = values[9]
                    ticker_id = self._tickers_id[ticker_id_int]
                    out_list = [ticker_id] + values[1:]
                    #print(TICKER_OUTPUT.format(*out_list))
                    print(TICKER_OUTPUT.format(ticker_id,values[1],values[2],values[3],values[5],values[6],values[7]))

                    # this mean my sql inserts
                    #print ("INSERT INTO ticker (currencyPair,last,lowestAsk,highestBid,baseVolume,quoteVolume,isFrozen)", 
                    #       "VALUES ('"+ticker_id+"',"+values[1]+","+values[2]+","+values[3]+","+values[5]+","+values[6]+",{});".format(values[7]) )

                else:
                    ticker_id = self._tickers_id[data[0]]

                    seq = data[1]

                    for update in data[2]:
                        # this mean this is snapshot
                        if update[0] == 'i':
                            # UPDATE[1]['currencyPair'] is the ticker name
                            self._last_seq_dic[ticker_id] = seq
                            asks = []

                            for price, size in update[1]['orderBook'][0].items():
                                asks.append([price, size])

                            bids = []
                            for price, size in update[1]['orderBook'][1].items():
                                bids.append([price, size])
                            # printing just 5 levels(this book can be 3000 levels)
                            '''
                            print('{} book:'.format(ticker_id))
                            print('asks((price,size)):')
                            for level in asks[0:5]:
                                print('({},{})'.format(level[0], level[1]))
                            print('bids((price,size)):')
                            for level in bids[0:5]:
                                print('({},{})'.format(level[0], level[1]))
                            '''
                        # this mean add or change or remove
                        elif update[0] == 'o':
                            if self._last_seq_dic[ticker_id] + 1 != seq:
                                raise Exception('Problem with seq number prev_seq={},message={}'.format(
                                    self._last_seq_dic[ticker_id], message))

                            price = update[2]
                            side = 'bid' if update[1] == 1 else 'ask'
                            size = update[3]
                            # this mean remove
                            if size == '0.00000000':
                                #print('Remove {},side={},price={}'.format(ticker_id, side, price))
                                print("DELETE FROM orderBook WHERE currencyPair = '{}' AND type = '{}' AND rate = '{}';".format(ticker_id, side, price))
                                #continue
                            # this mean add or change
                            else:
                                print(ORDER_OUTPUT.format(ticker_id, side, price, size))
                                #print('Add or change {},side={},price={},size={}'.format(ticker_id, side, price, size))
                                #print ("INSERT INTO orderBook (currencyPair,type,rate,amount) VALUES ('{}','{}',{},{});".format(ticker_id, side, price, size))
                        # this mean trade
                        elif update[0] == 't':
                            if self._last_seq_dic[ticker_id] + 1 != seq:
                                raise Exception('Problem with seq number prev_seq={},message={}'.format(
                                    self._last_seq_dic[ticker_id], message))

                            trade_id = update[1]
                            book_side = 'bid' if update[2] == 1 else 'ask'
                            price = update[3]
                            size = update[4]
                            timestamp = update[5]
                            out_list = [ticker_id, trade_id,
                                        book_side, price, size, timestamp]
                            print(TRADE_OUTPUT.format(*out_list))

                    self._last_seq_dic[ticker_id] = seq


if __name__ == '__main__':
    logging.info('starting reaper')
    sub = PoloniexSubscriber()
    sub.start_subscribe()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        # quit
        pass
    logging.info('ending reaper')

