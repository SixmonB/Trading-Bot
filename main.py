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

import config, websocket, json, talib, pprint
import numpy as np
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/adausdt@kline_1m"    # <symbol>@kline<interval>
closes = []
closesHace15 = []
# ------------- PARAMETROS -------------

tiempo_vela = 15 #Duracion de la vela pensada para la estrategia en min 
ajuste = tiempo_vela*60/2 #En el denominador indicar la duracion de la vela para operar en seg 
EMA_period = 18*ajuste
APO_slow = 20*ajuste 
APO_fast = 10*ajuste
correction = 300
matype = 0
APO_delta=-0.0025 #Posibilidad de que varíe en función del precio (podría ser por rango de precio)
            #Precio       $(0.66-1) ; $(1-1.33) ; $(1.33-1.66) ; $(1.66-2)
            #APO_delta    -0.0012     -0.0014      -0.0025 
bbands_period = 10*ajuste
nbdevup = 2.15
nbdevdn = 2.15
compra = 0 # valor de inicializacion de la variable de compra

# --------------------------------------

client = Client(config.apiKey, config.apiSecurity, tld='com')
symbolTicker = 'ADAUSDT'
quantityOrders = 1
candles_historical = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "5 hour ago UTC")

def on_open(ws):
    print('opened conneciton')

def on_close(ws):
    print('closed connection')

def Average(lst):
    return sum(lst)/len(lst)

def on_message(ws, message):
    global closes # lista de cierres de vela
    global compra
    # print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']
    # is_candle_closed = candle['x']
    closes.append(candle['c'])
    
    if (len(closes) >= EMA_period+correction):
        float_closes = [float(x) for x in closes]
        np_float_closes = np.array(float_closes)
        my_ema = talib.EMA(np_float_closes, EMA_period)
        print(".")
    if len(closes) >= APO_slow + ajuste:
        closes_actual = closes[int(ajuste-1):int(len(closes))]
        float_closes_actual = [float(x) for x in closes_actual]
        np_float_closes_actual = np.array(float_closes_actual)
        my_apo = talib.APO(np_float_closes_actual, APO_fast, APO_slow, matype)
            # Condicion de venta 1: APO con valor negativo
        if(my_apo >= matype):
            print("buy condition 1!")
            # Variación del my_apo - apo_Hace15 >= APO_delta
            # Cambia la condición porque hay que tener las últimas 21 velas de 15 min, ya que no usamos la última de 15 min
            closes_hace15 = closes[:len(closes)-ajuste]
            float_closes_hace15 = [float(x) for x in closes_hace15]
            np_float_closes_hace15 = np.array(float_closes_hace15)
            apo_Hace15=talib.APO(np_float_closes_hace15, APO_fast, APO_slow, matype)
            if(my_apo-apo_Hace15 > APO_delta):
                print("buy condition 2!")
        # Precio de vela creciente (buy condition 3)
        # Promedio velas(-600;-400) < Promedio velas(-400;-200) < Promedio velas(-200;0)
                velas_150_100 = closes[-ajuste*1.5-1:-ajuste-1]
                velas_100_50 = closes[-ajuste-1:-ajuste*0.5-1]
                velas_50_0 = closes[-ajuste*0.5-1:-1]
                average_150 = Average(velas_150_100)
                average_100 = Average(velas_100_50)
                average_50 = Average(velas_50_0)
                if (average_150 < average_100 and average_100 < average_50):
                    print("buy condition 3!")
        # Precio de vela cruza con indicador EMA (buy condition 4)
        # Opcion 1: Precio vela (-5)< EMA < Precio vela (0)
                    if (closes[-6] < my_ema and my_ema < closes[-1] ):
                        print("buy condition 4!")
                        compra = closes[-1]
        else:
            print("sell condition 1!")
            # Precio de vela cruza con indicador BBands (sell condition 1 - take profit - )
            # Opcion 1: Precio vela (-5)< BBands < Precio vela (0)
            upperband, middleband, lowerband = talib.BBANDS(closes, bbands_period, nbdevup, nbdevdn, matype) 
            if (closes[-6] < upperband and upperband < closes[-1]):
                print("sell condition 2!")
            # Stop loss -5% (sell condition 3)
            # Precio de vela (0) < Precio de vela de compra * 0.95
                if (closes[-1] < compra*0.95):
                    print("sell condition 3!")

        closes.pop(0)

    
  # Opcion 2: Precio vela (0)*0.998 < EMA < Precio vela (0)*1.002

  #Condiciones de venta______________________________

    
  # Opcion 2: Precio vela (0)*0.998 < BBands < Precio vela (0)*1.002

  #Evaluar la posibilidad de venta con BBands inferior (sell condition 4 - creo q no es necesaria- )
      
def on_error(ws,error):
    print(error)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()




