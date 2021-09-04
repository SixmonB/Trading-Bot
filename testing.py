
import config, websockets, json, talib, math
import numpy as np
from binance.client import Client
from binance.enums import *
import matplotlib.pyplot as plt
import csv

SOCKET = "wss://stream.binance.com:9443/ws/maticusdt@kline_1m"    # <symbol>@kline<interval>
closes = []
closes_to_print = []
closesHace15 = []
trades = 0
# ------------- PARAMETROS -------------

tiempo_vela = 15 # Duracion de la vela pensada para la estrategia en min 
ajuste = tiempo_vela*60/60 # En el denominador indicar la duracion de la vela para operar en seg 
EMA_period = 9*ajuste
APO_slow = 20*ajuste
APO_fast = 10*ajuste
matype = 0
APO_delta=0.35
# 0.009
# 0.008
# 0.006
# 3 velas
# (0.009-0.006)/0.009
comision = 0
stop_loss = 0.98
bbands_period = 10*ajuste

nbdevup = 2.15
nbdevdn = 2.15
compra = 0 # valor de inicializacion de la variable de compra
money_anterior = 100
money_actual = 100
trades_wins = 0
trades_loss = 0
ada = 0
compras = list()
minutes_compra = list()
ventas1 = list()
ventas2 = list()
ventas3 = list()
minutes_venta1 = list()
minutes_venta2 = list()
minutes_venta3 = list()
closes = list() # lista de valores de cierre de velas
highs = list()
sell_condition_1 = 0
sell_condition_2 = 0
sell_condition_3 = 0
# --------------------------------------

# cliente con informacion de cada cuenta de binance
client = Client(config.apiKey, config.apiSecurity, tld='com')
symbolTicker = 'MATICUSDT' # token a tradear
# velas historicas de la moneda indicada obtenidas de la api
#candles_historical = client.get_historical_klines(symbolTicker, Client.KLINE_INTERVAL_1MINUTE, "15 hour ago UTC")


# funcion auxiliar para calcular promedio
def Average(lst):
    return sum(lst)/len(lst)


# los valores de las velas son strings, por lo que luego debemos castear esta variable a float
# para poder operar con talib
minute = 0


# print('received message')
with open ('historical.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        closes.append(float(row[4]))
        highs.append(row[2])
        closes_to_print.append(float(row[4]))
        line_count +=1
        # print(closes)
        if (len(closes) >= EMA_period):
            np_closes = np.array(closes)
            np_closes_to_print = np.array(closes_to_print)
            # las funciones de talib requieren un numpy array de floats, por lo que debemos convertir las listas a 
            # np.array
            my_ema = talib.EMA(np_closes, EMA_period)
            my_ema_to_print = talib.EMA(np_closes_to_print, EMA_period)
            #print(my_ema)
            #print("closes: {}", len(np_float_closes))
        # if not (math.isnan(my_ema[-1])): # verificamos que el valor de my_ema/my_apo sea un numero real
            if len(closes) >= APO_slow + ajuste:
                closes_actual = closes[int(ajuste-1):int(len(closes))]
                np_closes_actual = np.array(closes_actual)
                my_apo = talib.APO(np_closes_actual, APO_fast, APO_slow, matype)
                my_apo_to_print = talib.APO(np_closes_to_print, APO_fast, APO_slow, matype)
                upperband, middleband, lowerband = talib.BBANDS(np_closes, bbands_period, nbdevup, nbdevdn, matype)
                upperband_to_print, middleband_to_print, lowerband_to_print = talib.BBANDS(np_closes_to_print, bbands_period, nbdevup, nbdevdn, matype)
                # if not (math.isnan(my_apo[-1])):
                    # Condicion de compra 1: APO con valor positivo
                if(my_apo[-1] >= matype):
                    # print("buy condition 1!")
                    # Variación del my_apo - apo_Hace15 >= APO_delta
                    # Cambia la condición porque hay que tener las últimas 21 velas de 15 min, ya que no usamos la última de 15 min
                    closes_hace15 = closes[:int(len(closes)-ajuste)]
                    np_closes_hace15 = np.array(closes_hace15)
                    apo_hace15 = talib.APO(np_closes_hace15, APO_fast, APO_slow, matype)
                    # if not (math.isnan(apo_hace15[-1])):
                    variation = (apo_hace15[-1]-my_apo[-1])/apo_hace15[-1]
                    if(variation < APO_delta):        
                # print("buy condition 2!")
                # Precio de vela cruza con indicador EMA (buy condition 4)
                # Opcion 1: Precio vela (-5)< EMA < Precio vela (0)
                        if (closes[-2] < my_ema[-1] and my_ema[-1] < closes[-1]):
                            if (money_actual>0):
                                # print("buy condition 4!")
                                print("COMPRASTE")
                                compra = closes[-1]
                                compras.append(compra)
                                minutes_compra.append(minute)
                                ada = money_actual*(1-comision)/closes[-1]
                                money_actual = 0
                                print("Compraste en el minuto:", minute)
                                print("ADA:", ada)
                                print("USDT:", money_actual, "\n")
                        # if (variation < APO_delta*0.6):
                        #     if (closes[-2]>lowerband[-1] and closes[-1]<lowerband[-1]):
                        #         if (money_actual>0):
                        #             # print("buy condition 4!")
                        #             print("COMPRASTE")
                        #             compra = closes[-1]
                        #             compras.append(compra)
                        #             minutes_compra.append(minute)
                        #             ada = money_actual*(1-0.001)/closes[-1]
                        #             money_actual = 0
                        #             print("Compraste en el minuto: {}", minute)
                        #             print("ADA: ", ada)
                        #             print("USDT: ", money_actual)
                else:
                    if (ada>0):
                        print("sell condition 1!")
                        sell_condition_1 += 1
                        print("VENDISTE")
                        venta = closes[-1]
                        ventas1.append(venta)
                        minutes_venta1.append(minute)
                        money_actual = ada*closes[-1]*(1-comision)
                        if (money_actual > money_anterior):
                            trades_wins += 1
                        else:
                            trades_loss += 1
                        print("VARIACION:", (money_actual-money_anterior)*100/money_anterior)
                        print("Vendiste en el minuto:", minute)
                        money_anterior = money_actual
                        ada = 0
                        trades += 1
                        print("ADA:", ada)
                        print("USDT:", money_actual, "\n")
                    # Precio de vela cruza con indicador BBands (sell condition 1 - take profit - )
                    # Opcion 1: Precio vela (-5)< BBands < Precio vela (0)
                #if not (math.isnan(upperband[-1])):    
                if (closes[-2] < upperband[-1] and upperband[-1] < closes[-1]):
                    if (ada>0):
                        print("sell condition 2!")
                        sell_condition_2 += 1
                        print("VENDISTE")
                        venta = closes[-1]
                        ventas2.append(venta)
                        minutes_venta2.append(minute)
                        money_actual = ada*closes[-1]*(1-comision)
                        if (money_actual > money_anterior):
                            trades_wins += 1
                        else:
                            trades_loss += 1
                        print("VARIACION:", (money_actual-money_anterior)*100/money_anterior)
                        print("Vendiste en el minuto:", minute)
                        money_anterior = money_actual
                        ada = 0
                        trades += 1
                        print("ADA:", ada)
                        print("USDT:", money_actual, "\n")
                    # Stop loss -5% (sell condition 3)
                    # Precio de vela (0) < Precio de vela de compra * 0.95
                if (closes[-1] < compra*stop_loss):
                    if (ada>0):
                        print("sell condition 3!")
                        sell_condition_3 += 1
                        print("-------------------")
                        print("STOP LOSS")
                        print("-------------------")
                        print("VENDISTE")
                        venta = closes[-1]
                        ventas3.append(venta)
                        minutes_venta3.append(minute)
                        money_actual = ada*closes[-1]*(1-comision)
                        if (money_actual > money_anterior):
                            trades_wins += 1
                        else:
                            trades_loss += 1
                        print("VARIACION:", (money_actual-money_anterior)*100/money_anterior)
                        print("Vendiste en el minuto:", minute)
                        money_anterior = money_actual
                        ada = 0
                        trades += 1
                        print("ADA:", ada)
                        print("USDT:", money_actual, "\n")
                closes.pop(0)
        minute = minute+1

print("TRADES:", trades)
print("WINS:", trades_wins)
print("LOSS:", trades_loss)
print("SELL CONDITION 1:", sell_condition_1)
print("SELL CONDITION 2:", sell_condition_2)
print("SELL CONDITION 3:", sell_condition_3)

plt.figure(1)
plt.plot(my_ema_to_print, label='EMA')
plt.plot(upperband_to_print, label='upperband')
plt.plot(middleband_to_print, label='middleband')
plt.plot(lowerband_to_print, label='lowerband')
plt.plot(closes_to_print, label='Price', color='black')
plt.plot(minutes_compra, compras, 'o', color = 'green')
plt.plot(minutes_venta1, ventas1, 'x', color='red') # sell condition 1: apo negativo
plt.plot(minutes_venta2, ventas2, '^', color='red') # sell condition 2: toca upperband
plt.plot(minutes_venta3, ventas3, 'o', color='red') # sell condition 3: stop loss
plt.xlim([0, len(np_closes_to_print)])
plt.legend(loc='best')
plt.figure(2)
plt.plot(my_apo_to_print, label='APO')
plt.axhline(y=0, color='red')
plt.xlim([0, len(np_closes_to_print)])
plt.show()

