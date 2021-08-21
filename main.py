# ------------- INFORMACION ------------- 

# info at https://github.com/binance-exchange/binance-official-api-docs
# https://mrjbq7.github.io/ta-lib/
# https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#klinecandlestick-streams

# --------------------------------------- 

# ------------- FUNCIONES -------------

# EMA 15
# real = EMA(close, timeperiod=30)
# apo 
# real = APO(close, fastperiod=10, slowperiod=20, matype=0)
# bbands 
# upperband, middleband, lowerband = BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)

# --------------------------------------

import config, websocket, json, numpy, talib, pprint

SOCKET = "wss://stream.binance.com:9443/ws/adausdt@kline_15m"    # <symbol>@kline<interval>
closes = []

# ------------- PARAMETROS -------------
 
EMA_period = 17*(60/2)
APO_slow = 20*(60/2) # 10 y 20 para velas de 15 minutos
APO_fast = 10*(60/2)
matype = 0

# --------------------------------------

def on_open(ws):
    print('opened conneciton')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes # lista de cierres de vela
    # print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    # is_candle_closed = candle['x']
    closes.append(candle['c'])
    
    if len(closes) > EMA_period:
        my_ema = talib.EMA(closes, EMA_period)

    if len(closes) > APO_slow:
        my_apo = talib.APO(closes, APO_fast, APO_slow, matype)
        if(my_apo >= matype):
            print("comprar!")
        else:
            print("vender!")

def on_error(ws,error):
    print(error)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()

# bbands 
# upperband, middleband, lowerband = BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
upperband, middleband, lowerband = talib.BBANDS(closes, ) 
# EMA 15
# real = EMA(close, timeperiod=30)
# apo 
# real = APO(close, fastperiod=10, slowperiod=20, matype=0)

