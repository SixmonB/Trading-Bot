import config, websockets, json, talib, math
import numpy as np
from binance.client import Client
from binance.enums import *


SOCKET = "wss://stream.binance.com:9443/ws/adausdt@kline_1m"    # <symbol>@kline<interval>
closes = []
closesHace15 = []
# ------------- PARAMETROS -------------

tiempo_vela = 15 #Duracion de la vela pensada para la estrategia en min 
ajuste = tiempo_vela*60/60 #En el denominador indicar la duracion de la vela para operar en seg 
EMA_period = ajuste/3
APO_slow = 20*ajuste 
APO_fast = 10*ajuste
matype = 0
APO_delta=-0.0025 #Posibilidad de que varíe en función del precio (podría ser por rango de precio)
            #Precio       $(0.66-1) ; $(1-1.33) ; $(1.33-1.66) ; $(1.66-2)
            #APO_delta    -0.0012     -0.0014      -0.0025 
bbands_period = 10*ajuste
nbdevup = 2.15
nbdevdn = 2.15
compra = 0 # valor de inicializacion de la variable de compra
money = 100
ada = 0

# --------------------------------------

# cliente con informacion de cada cuenta de binance
client = Client(config.apiKey, config.apiSecurity, tld='com')
symbolTicker = 'ADAUSDT' # token a tradear
# velas historicas de la moneda indicada obtenidas de la api
candles_historical = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "15 hour ago UTC")

# funcion auxiliar para calcular promedio
def Average(lst):
    return sum(lst)/len(lst)

closes = list() # lista de valores de cierre de velas
# los valores de las velas son strings, por lo que luego debemos castear esta variable a float
# para poder operar con talib

# print('received message')
for i in range(len(candles_historical)):
    closes.append(float(candles_historical[i][4]))
    # print(closes)
    if (len(closes) >= EMA_period):
        float_closes = [float(x) for x in closes]
        np_float_closes = np.array(float_closes)
        # las funciones de talib requieren un numpy array de floats, por lo que debemos convertir las listas a 
        # np.array
        my_ema = talib.EMA(np_float_closes, EMA_period)
        print(my_ema)
        