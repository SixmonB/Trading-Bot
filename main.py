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
closesHace15 = []
# ------------- PARAMETROS -------------

ajuste = 15*60/2
EMA_period = 18*ajuste
APO_slow = 20*ajuste # 10 y 20 para velas de 15 minutos
APO_fast = 10*ajuste
matype = 0
APO_delta=-0.0025 #Posibilidad de que varíe en función del precio (podría ser por rango de precio)
            #Precio   $(0.66-1) ; $(1-1.33) ; $(1.33-1.66) ; $(1.66-2)
         #APO_delta    -0.0012     -0.0014      -0.0025 
bbands_period = 10*ajuste
nbdevup = 1
nbdevdn = 1
compra = 0 # valor de inicializacion de la variable de compra

# --------------------------------------

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
    
    if len(closes) >= EMA_period:
        my_ema = talib.EMA(closes, EMA_period)

    if len(closes) >= APO_slow + ajuste:
        closes_actual = closes[ajuste-1:len(closes)]
        my_apo = talib.APO(closes_actual, APO_fast, APO_slow, matype)
            # Condicion de venta 1: APO con valor negativo
        if(my_apo >= matype):
            print("buy condition 1!")
            # Variación del my_apo - apo_Hace15 >= APO_delta
            # Cambia la condición porque hay que tener las últimas 21 velas de 15 min, ya que no usamos la última de 15 min
            closes_Hace15 = closes[:len(closes)-ajuste]
            apo_Hace15=talib.APO(closes_Hace15, APO_fast, APO_slow, matype)
            if(my_apo-apo_Hace15 > APO_delta):
                print("buy condition 2!")
        # Precio de vela creciente (buy condition 3)
        # Promedio velas(-600;-400) < Promedio velas(-400;-200) < Promedio velas(-200;0)
                velas_600_400 = closes[-601:-401]
                velas_400_200 = closes[-401:-201]
                velas_200_0 = closes[-201:-1]
                average600 = Average(velas_600_400)
                average400 = Average(velas_400_200)
                average200 = Average(velas_200_0)
                if (average600 < average400 and average400 < average200):
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
            upperband, middleband, lowerband = talib.BBANDS(closes, ) 
            if (closes[-6] < upperband and upperband < closes[-1]):
                print("sell condition 2!")
            # Stop loss -5% (sell condition 3)
            # Precio de vela (0) < Precio de vela de compra * 0.95
                if (closes[-1] < compra*0.95):
                    print("sell condition 3!")

        closes.pop()

    
  # Opcion 2: Precio vela (0)*0.998 < EMA < Precio vela (0)*1.002

  #Condiciones de venta______________________________

    
  # Opcion 2: Precio vela (0)*0.998 < BBands < Precio vela (0)*1.002

  #Evaluar la posibilidad de venta con BBands inferior (sell condition 4 - creo q no es necesaria- )
      
def on_error(ws,error):
    print(error)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()




