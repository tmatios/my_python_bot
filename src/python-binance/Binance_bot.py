# -*- coding: utf-8 -*-

import datetime
import time
from datetime import datetime, timedelta
import os, json
import logging
from binance.client import Client
from binance.enums import *
import _pydecimal
import math
import ccxt
from pyti.bollinger_bands import upper_bollinger_band as bb_up
from pyti.bollinger_bands import middle_bollinger_band as bb_mid
from pyti.bollinger_bands import lower_bollinger_band as bb_low
#####
import requests
import sys
#####
import pybitflyer
#####################
#####################
#####################
#####################
# ログの出力名を設定（1）
logger = logging.getLogger('Binance_bot')
# ログレベルの設定
logger.setLevel(10)
# ログのファイル出力先を設定
fh = logging.FileHandler('Binance_bot_Trace.log')
logger.addHandler(fh)
# ログの出力形式の設定
formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
#####################
#
#ラインに稼働状況を通知
line_notify_token = '********************************************'
line_notify_api = 'https://notify-api.line.me/api/notify'
###
BINC_API_KEY = "**************************************************************"
BINC_API_SECRET = "****************************************************************"

BTCUSDT_Pair = 'BTCUSDT'
#
USDCBTC_Pair = 'USDCBTC'
ZENBTC_Pair  = 'ZENBTC'
XRPBTC_Pair  = 'XRPBTC'
BNBBTC_Pair  = 'BNBBTC'
#
### 有効桁数(round)
BTCUSDT_DECIMAL = 4
USDCBTC_DECIMAL = 0
ZENBTC_DECIMAL  = 3
XRPBTC_DECIMAL  = 0
BNBBTC_DECIMAL  = 2
#
LOTOF_BTCUSDT = 1.0
LOTOF_USDCBTC = 0.000001
LOTOF_ZENBTC  = 0.0001
LOTOF_XRPBTC  = 0.00001
LOTOF_BNBBTC  = 0.0001
PERIOD = 22
PROFIT = 125     # (0.25*500=100)
ALT_PROFIT = 100 # (0.25*500=50)
UpRange = 2.25
DwRange = 1.75
FEE = 0.1
ORDER_LIMIT = 0.3
BNBFEE = 0.05
KEEP_BTC = 0.01
###
MAX_BTC = 0.5000
MIN_BTC = 0.0010
MAX_ALT = 100.000
MIN_ALT = 0.1000
MAX_BNB = 5.0
MIN_BNB = 3.0
BTC_LOT = 0.01
ALT_LOT = 0.1
DEC_LOT = 1
LOT_CHECK_COUNT = 20
MARKET_ORDER_TRY = 3
#
SYMBOL_BTCUSDT = 'BTC/USDT'
#
SYMBOL_USDCBTC = 'USDC/BTC'
SYMBOL_ZENBTC  = 'ZEN/BTC'
SYMBOL_XRPBTC  = 'XRP/BTC'
SYMBOL_BNBBTC  = 'BNB/BTC'
WAITING_TIME = 5
TIMEFRAME = '5m'
SELL = 'sell'
BUY = 'buy'
NONE = 'None'
#
global init
global init_values
global BTCJPY_price
global BTCUSDT_Amount
#
global USDCBTC_Amount
global ZENBTC_Amount
global XRPBTC_Amount
global BNBBTC_Amount
#
ENTRY_MEAN = 75
STOP_LOSS_MEAN = 100
TAKE_PROFIT_MEAN = 80
global BincRateBuy,BincRateSell,BincRateNow
global BalanceUSDT,BalanceBTC
global BuyPrice,SellPrice
global Binp
global Binc
global stop_order_price
global take_order_price
global entry_order_BTCUSDT_ask
global entry_order_BTCUSDT_bid
global ORDER_SIDE_BTCUSDT
global last_hour
global last_high_mid_Bollinger_Range
global last_mid_low_Bollinger_Range
global last_high_low_Bollinger_Range
global last_b_up
global last_b_low
global long_side_position
global short_side_position
###
global BalanceUSDC
global USDCRateBuy,USDCRateSell,USDCRateNow
global entry_order_USDCBTC_ask
global entry_order_USDCBTC_bid
global ORDER_SIDE_USDCBTC
global last_USDCBTC_high_mid_Bollinger_Range
global last_USDCBTC_mid_low_Bollinger_Range
global last_USDCBTC_high_low_Bollinger_Range
global last_USDCBTC_b_up
global last_USDCBTC_b_low
global long_side_USDCBTC_position
global short_side_USDCBTC_position
###
global BalanceZEN
global ZENRateBuy,ZENRateSell,ZENRateNow
global entry_order_ZENBTC_ask
global entry_order_ZENBTC_bid
global ORDER_SIDE_ZENBTC
global last_ZENBTC_high_mid_Bollinger_Range
global last_ZENBTC_mid_low_Bollinger_Range
global last_ZENBTC_high_low_Bollinger_Range
global last_ZENBTC_b_up
global last_ZENBTC_b_low
###
global BalanceXRP
global XRPRateBuy,XRPRateSell,XRPRateNow
global entry_order_XRPBTC_ask
global entry_order_XRPBTC_bid
global ORDER_SIDE_XRPBTC
global last_XRPBTC_high_mid_Bollinger_Range
global last_XRPBTC_mid_low_Bollinger_Range
global last_XRPBTC_high_low_Bollinger_Range
global last_XRPBTC_b_up
global last_XRPBTC_b_low
###
global BalanceBNB
global BNBRateBuy,BNBRateSell,BNBRateNow
global entry_order_BNBBTC_ask
global entry_order_BNBBTC_bid
global ORDER_SIDE_BNBBTC
global last_BNBBTC_high_mid_Bollinger_Range
global last_BNBBTC_mid_low_Bollinger_Range
global last_BNBBTC_high_low_Bollinger_Range
global last_BNBBTC_b_up
global last_BNBBTC_b_low
#
global ORDER_SIDE_BTCUSDT
global ORDER_SIDE_USDCBTC
global ORDER_SIDE_ZENBTC
global ORDER_SIDE_XRPBTC
global ORDER_SIDE_BNBBTC
#
global min_lot_BTCUSDT
global min_lot_USDCBTC
global min_lot_ZENBTC
global min_lot_XRPBTC
global min_lot_BNBBTC
###################
# 実際の価格を取得(BTC--JPY)
def getBTCJPY_Price():
        jpy_price = 0.0
        try:
            price = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params="300").text)["result"]
            #print(price)
            jpy_price = float("{}".format(price['300'][0][4]))
        except:
            pass
        return jpy_price
#########
###################
# 最小取引ロット数返す(BTC基礎通貨)
def getMinLotSizeBTC(Pair_Symbol):
        #print("getMinLotSizeBTC=" + Pair_Symbol)
        min_lot = 0.001
        if (Pair_Symbol == "BTCUSDT"):
            min_lot = MIN_BTC
        else:
            min_lot = MIN_ALT
        pairs_lot_min = None
        market_info = ""
        try:
            #market_info =  Binp.fetch_markets()
            #print(json.dumps(market_info, indent=True))
            if (Pair_Symbol == "BTCUSDT"):
               pairs_lot_min = 0.0010
            elif(Pair_Symbol == "USDCBTC"):
               pairs_lot_min = 1
            elif(Pair_Symbol == "ZENBTC"):
               pairs_lot_min = 0.100
            elif(Pair_Symbol == "XRPBTC"):
               pairs_lot_min = 1
            elif(Pair_Symbol == "BNBBTC"):
               pairs_lot_min = 1.00
        except Exception as e :
            msg = "ERROR("+str(e.message)+")\n"
            print (msg)
        #if (pairs_lot_min!=None): print("pairs_lot_min=" + str(pairs_lot_min))
        if (pairs_lot_min != None):
            min_lot = float(pairs_lot_min)
        return min_lot
#
#########
def lineNotify(message):
        payload = {'message': message}
        headers = {'Authorization': 'Bearer ' + line_notify_token}
        try:
            requests.post(line_notify_api, data=payload, headers=headers)
        except:
            pass
###
def get_chart_data(TARGET_SYMBOL):
        global Binp
        ohlcv = ""
        ohlcv = Binp.fetch_ohlcv(TARGET_SYMBOL,TIMEFRAME)
        return(ohlcv)
###
def get_bollinger_band(data):
        bb_ups = 0.0
        bb_mids = 0.0
        bb_lows = 0.0
        bb_ups = bb_up(data,PERIOD)
        bb_mids = bb_mid(data,PERIOD)
        bb_lows = bb_low(data,PERIOD)
        return {'bb_up':bb_ups, 'bb_mid':bb_mids, 'bb_low':bb_lows}
###
def decimal(number):
    return str(_pydecimal.Decimal(str(number)))
#
def GetRateA(repeat, Target_Pair) :
   global Buy_price
   global Sell_price
   # Binance
   rateNow = 0.0
   rateBuy = 0.0
   rateSell = 0.0
   for i in range(repeat) :
       # Rate
       rate = Binc.get_ticker(symbol=Target_Pair)
       rateNow += (float(rate["bidPrice"]) + float(rate["askPrice"])) / 2.0
       rateBuy += float(rate["askPrice"])
       rateSell += float(rate["bidPrice"])
       time.sleep(1)
   rateNow /= repeat
   rateBuy /= repeat
   rateSell /= repeat
   Buy_price = rateBuy
   Sell_price = rateSell
   return rateNow,rateBuy,rateSell
#
def GetBalanceA() :

   # Binance
   try:
      balance = Binc.get_asset_balance(asset='USDT')
      balanceUSDT = balance["free"]
      print("balanceUSDT =" + str(balanceUSDT))
      balance = Binc.get_asset_balance(asset='BTC')
      balanceBTC = balance["free"]
      print("balanceBTC =" + str(balanceBTC))
#
      balance = Binc.get_asset_balance(asset='USDC')
      balanceUSDC = balance["free"]
      print("balanceUSDC =" + str(balanceUSDC))
      balance = Binc.get_asset_balance(asset='ZEN')
      balanceZEN = balance["free"]
      print("balanceZEN =" + str(balanceZEN))
      balance = Binc.get_asset_balance(asset='XRP')
      balanceXRP = balance["free"]
      print("balanceXRP =" + str(balanceXRP))
      balance = Binc.get_asset_balance(asset='BNB')
      balanceBNB = balance["free"]
      print("balanceBNB =" +str(balanceBNB))
   except Exception as e :    
       msg = "保有資産の取得ができませんでした。("+str(e.message)+")\n"
       print (msg)
       logger.error(msg)
       pass
   return balanceUSDT,balanceBTC,balanceUSDC,balanceZEN,balanceXRP,balanceBNB
###################
def check_order_size(side, symbol, amount, price):
#
   #logger.info("In check_order_size:" + "@side=" + side + "@symbol=" + symbol + "@amount=" + str(amount) + "@price=" + "{0:.8f}".format(price))
   #print("In check_order_size:" + "@side=" + side + "@symbol=" + symbol + "@amount=" + str(amount) + "@price=" + "{0:.8f}".format(price))
   OK = False
   try_count = 0
   camount = amount
   setlot = 0.0001
   try_max = LOT_CHECK_COUNT
   if (symbol == BTCUSDT_Pair):
      camount = round(float(amount),BTCUSDT_DECIMAL)
      setlot = BTC_LOT
   elif (symbol == USDCBTC_Pair):
      camount = round(float(amount),USDCBTC_DECIMAL)
      setlot = DEC_LOT
   elif (symbol == ZENBTC_Pair):
      camount = round(float(amount),ZENBTC_DECIMAL)
      setlot = ALT_LOT
   elif (symbol == XRPBTC_Pair):
      camount = round(float(amount),XRPBTC_DECIMAL)
      setlot = DEC_LOT
   elif (symbol == BNBBTC_Pair):
      camount = round(float(amount),BNBBTC_DECIMAL)
      setlot = ALT_LOT
#
   if (symbol == BTCUSDT_Pair):
      if (float(camount) < MIN_BTC):
         return {'OK':OK, 'OrderSize':float(camount)}
   if (symbol == USDCBTC_Pair):
      if (float(camount) < DEC_LOT):
         return {'OK':OK, 'OrderSize':float(camount)}
   else:
      if (float(amount) < MIN_ALT):
         return {'OK':OK, 'OrderSize':float(camount)}
#
   #logger.info("In check_order_size:" + str(camount))
   err_mes = ""
   while(OK==False):
      try:
         order_size = decimal(camount)
         order = Binc.create_test_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=order_size)
         OK = True
         #print(order)
         #logger.info("In check_order_size is OK:" + order_size)
      except Exception as e:
         try_count = try_count + 1
         if (try_count > try_max):
            break
         tb = sys.exc_info()[2]
         err_mes = "message:{0}".format(e.with_traceback(tb))
         #logger.error(err_mes)
         ### Filter failure: LOT_SIZE
         lot_size_err = "Filter failure: LOT_SIZE"
         ### Account has insufficient balance for requested action
         not_enogh_err = "Account has insufficient balance for requested action"
         ### Invalid quantity
         Invalid_err = "Invalid quantity"
         ### Invalid quantity
         Min_notional_err = "Filter failure: NIN_NOTIONAL"
         if (lot_size_err in err_mes):
            camount = camount + setlot
            #logger.debug(lot_size_err)
            time.sleep(2)
            err_mes = ""
            continue
         elif (not_enogh_err in err_mes):
            camount = camount - setlot
            #logger.debug("check_order_size:" + not_enogh_err)
            time.sleep(2)
            err_mes = ""
            continue
         elif (Min_notional_err in err_mes):
            camount = camount + setlot
            #logger.debug("check_order_size:" + Min_notional_err)
            time.sleep(2)
            err_mes = ""
            continue         
         elif (Invalid_err in err_mes):
            #print("Quantity Error Message = " + err_mes)
            #logger.debug("check_order_size:" + Invalid_err)
            break
         else:
            #print("None Error Message = " + err_mes)
            #logger.error("check_order_size:" + err_mes)
            break
         #print("message:{0}".format(e.with_traceback(tb)))
         pass
   return {'OK':OK, 'OrderSize':float(camount)}
###
###################
def BuyMarket(amount, Symbol, Pairs, RateBuy) :
   # Binance
   global BincRateBuy
   global BalanceBough
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
#
   if (Pairs == BTCUSDT_Pair):
      amount = round(float(amount),BTCUSDT_DECIMAL)
   elif (Pairs == USDCBTC_Pair):
      amount = round(float(amount),USDCBTC_DECIMAL)
   elif (Pairs == ZENBTC_Pair):
      amount = round(float(amount),ZENBTC_DECIMAL)
   elif (Pairs == XRPBTC_Pair):
      amount = round(float(amount),XRPBTC_DECIMAL)
   elif (Pairs == BNBBTC_Pair):
      amount = round(float(amount),BNBBTC_DECIMAL)
#
   order_size = decimal(amount)
   print("BuyMarket:" + Pairs + "@amount=" + str(amount))
#   
   linemes = "Binance_Bot@BUY:" + Symbol + "(買い指値注文)" + " :価格=" + "{0:.4f}".format(RateBuy) + " :ロット数=" + order_size
   OK = False
   cont = 0
   while (OK == False):
      try:
         Binc.order_market_buy(symbol=Pairs, quantity=order_size)
         OK = True
      except Exception as e : 
         if(cont > MARKET_ORDER_TRY):
            msg = "買い指値注文に失敗しました。("+str(e.message)+")\n"
            print (d+" "+msg)
            break
         logger.error(str(e.message))
         cont = cont + 1
         time.sleep(5)
         pass
   if (OK == True):
         print(linemes)
         lineNotify(linemes)
         logger.info(linemes)
   return OK
#
def SellMarket(amount, Symbol, Pairs, RateSell) :
   # Binance
   global BincRateSell
   global BalanceBought
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
#
   if (Pairs == BTCUSDT_Pair):
      amount = round(float(abs(amount)),BTCUSDT_DECIMAL)
   elif (Pairs == USDCBTC_Pair):
      amount = round(float(abs(amount)),USDCBTC_DECIMAL)
   elif (Pairs == ZENBTC_Pair):
      amount = round(float(abs(amount)),ZENBTC_DECIMAL)
   elif (Pairs == XRPBTC_Pair):
      amount = round(float(abs(amount)),XRPBTC_DECIMAL)
   elif (Pairs == BNBBTC_Pair):
      amount = round(float(abs(amount)),BNBBTC_DECIMAL)
#
   order_size = decimal(amount)
#
   print("SellMarket:" + Pairs + "@amount=" + str(amount))
   order_size = decimal(abs(amount))
   linemes = "Binance_Bot@SELL:" + Symbol + "(売り指値注文)" + " :価格=" + "{0:.4f}".format(RateSell) + " :ロット数=" + order_size
   OK = False
   cont = 0
   while (OK == False):
      try:
         Binc.order_market_sell(symbol=Pairs, quantity=order_size)
         OK = True
      except Exception as e :
         if(cont > MARKET_ORDER_TRY):
            msg = "売り指値注文に失敗しました。("+str(e.message)+")\n"
            print (d+" "+msg)
            break
         logger.error(str(e.message))
         cont = cont + 1
         time.sleep(5)
         pass
   if (OK == True):
       print(linemes)
       lineNotify(linemes)
       logger.info(linemes)
   return OK
#
# Binance から情報を取得する
# 戻り値：TRUE 成功
#         FALSE 失敗 
def GetBinance() :
   global BincRateNow,BincRateBuy,BincRateSell,BalanceUSDT,BalanceBTC
#
   global BTCJPY_price
   global BalanceUSDC,BalanceZEN,BalanceXRP,BalanceBNB
   global USDCRateBuy,USDCRateSell,USDCRateNow
   global ZENRateBuy,ZENRateSell,ZENRateNow
   global XRPRateBuy,XRPRateSell,XRPRateNow
   global BNBRateBuy,BNBRateSell,BNBRateNow
#
   global F_Buy,F_Sell,F_Non
   global BalanceBought
   global last_hour
   notify = False
   global init
   global init_values
#
   global min_lot_BTCUSDT
   global min_lot_USDCBTC
   global min_lot_ZENBTC
   global min_lot_XRPBTC
   global min_lot_BNBBTC
#

   # タイムスタンプ
   now = datetime.today();
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ret = True
### 各対象ペアの最小取引量MINIMUM_LOT
   min_lot_BTCUSDT = getMinLotSizeBTC(BTCUSDT_Pair)
   min_lot_USDCBTC = getMinLotSizeBTC(USDCBTC_Pair)
   min_lot_ZENBTC = getMinLotSizeBTC(ZENBTC_Pair)
   min_lot_XRPBTC = getMinLotSizeBTC(XRPBTC_Pair)
   min_lot_BNBBTC = getMinLotSizeBTC(BNBBTC_Pair)
###
   try :
       # Rate
       BincRateNow,BincRateBuy,BincRateSell = GetRateA(1, BTCUSDT_Pair)
       USDCRateNow,USDCRateBuy,USDCRateSell = GetRateA(1, USDCBTC_Pair)
       ZENRateNow,ZENRateBuy,ZENRateSell = GetRateA(1, ZENBTC_Pair)
       XRPRateNow,XRPRateBuy,XRPRateSell = GetRateA(1, XRPBTC_Pair)
       BNBRateNow,BNBRateBuy,BNBRateSell = GetRateA(1, BNBBTC_Pair)
   except Exception as e :
       ret = False
   BalanceUSDT = 0.0
   BalanceBTC = 0.0
   BalanceUSDC = 0.0
   BalanceZEN = 0.0
   BalanceXRP = 0.0
   BalanceBNB = 0.0
   try :    
       # Balance
        BalanceUSDT,BalanceBTC,BalanceUSDC,BalanceZEN,BalanceXRP,BalanceBNB = GetBalanceA()
   except Exception as e :
       ret =  False
   # ログ
   if (F_Buy == True) :
       msg = "RateBuy:"+"{0:.8f}".format(BincRateBuy)+"(USDT) BalanceUSDT:" \
              +str(BalanceUSDT)+"(USDT) BalanceBTC:"+str(BalanceBTC)+"(BTC) BalanceAll:" \
              +"{0:.8f}".format(float(BalanceUSDT) + float(BalanceBTC) * float(BincRateBuy))+"(USDT)"
   elif (F_Sell == True) :
       msg = "RateSell:"+"{0:.8f}".format(BincRateSell)+"(USDT) BalanceUSDT:" \
              +str(BalanceUSDT)+"(USDT) BalanceBTC:"+str(BalanceBTC)+"(BTC) BalanceAll:" \
              +"{0:.8f}".format(float(BalanceUSDT) + float(BalanceBTC) * float(BincRateSell))+"(USDT)"
###
   # profits は厳密に計算しない。参考程度に
   BTCJPY_price = getBTCJPY_Price()
   print("***** Current BTC/JPY Rate = " +"{:,}".format(BTCJPY_price))
   profitsBit = round(float(
       float(BalanceUSDT) / float(BincRateNow)\
       + float(BalanceBTC)\
       + float(BalanceUSDC) * float(USDCRateNow)\
       + float(BalanceZEN) * float(ZENRateNow)\
       + float(BalanceXRP) * float(XRPRateNow)\
       + float(BalanceBNB) * float(BNBRateNow)\
       - float(BalanceBought)),4)
   print("***** Current Holding(BTC) = " + "{0:.4f}".format(profitsBit))
   #logger.info("Current Holding(BTC) = " + "{0:.4f}".format(profitsBit))
   profitsJPY = round(profitsBit * BTCJPY_price)

   if (init):
       init_values = profitsJPY
       init = False

   Current_Profit = profitsJPY - init_values
   
   msg2 = "***** Current Holding ON JPY:" + "{:,}".format(profitsJPY) + "(JPY) *****\r\n"
   msg3 = "***** Current Profit        :" + "{:,}".format(Current_Profit) + "(JPY) *****"
   #print(d+" "+msg2)
   if (last_hour != datetime.now().hour):
        notify = True
        last_hour = datetime.now().hour
#
   if (notify) :
        linemes = d + ": Binance_Trading_Bot" + "\r\n" + msg2 + msg3
        lineNotify(linemes)
        logger.info(linemes)
        notify = False
   else :
        totalUSDT = float(float(BalanceUSDT) + float(BalanceBTC) * float(BincRateBuy))
        msg = "RateMean(BTCUSDT Rate):" + str(BincRateNow) + "\r\n"\
            + "BalanceUSDT(USDT):" + str(BalanceUSDT) + "\r\n"\
            + "BalanceBTC(BTC):" + str(BalanceBTC) + "\r\n"\
            + "BalanceAll(USDT):" + str(totalUSDT)
        print (d+" "+msg + "\r\n" + msg2 + msg3)
        logger.info(msg + msg2 + msg3)
   return ret
####################
def Calcurate() :
   global ORDER_SIDE_BTCUSDT
   global ORDER_SIDE_USDCBTC
   global ORDER_SIDE_ZENBTC
   global ORDER_SIDE_XRPBTC
   global ORDER_SIDE_BNBBTC
#
   global BTCUSDT_Amount
#
   global USDCBTC_Amount
   global ZENBTC_Amount
   global XRPBTC_Amount
   global XRPBTC_Amount
   global BNBBTC_Amount
#
   global min_lot_BTCUSDT
   global min_lot_USDCBTC
   global min_lot_XRPBTC
   global min_lot_BNBBTC
#
   global BincRateBuy,BincRateSell,BincRateNow
   global BalanceUSDT,BalanceBTC
   global stop_order_price
   global take_order_price
   global last_high_mid_Bollinger_Range
   global last_mid_low_Bollinger_Range
   global last_high_low_Bollinger_Range
   global last_b_up
   global last_b_low
   global long_side_position
   global short_side_position
##
   global BalanceUSDC
   global USDCRateBuy,USDCRateSell,USDCRateNow
   global last_USDCBTC_high_mid_Bollinger_Range
   global last_USDCBTC_mid_low_Bollinger_Range
   global last_USDCBTC_high_low_Bollinger_Range
   global last_USDCBTC_b_up
   global last_USDCBTC_b_low
##
   global BalanceZEN
   global ZENRateBuy,ZENRateSell,ZENRateNow
   global last_ZENBTC_high_mid_Bollinger_Range
   global last_ZENBTC_mid_low_Bollinger_Range
   global last_ZENBTC_high_low_Bollinger_Range
   global last_ZENBTC_b_up
   global last_ZENBTC_b_low
##
   global BalanceXRP
   global XRPRateBuy,XRPRateSell,XRPRateNow
   global last_XRPBTC_high_mid_Bollinger_Range
   global last_XRPBTC_mid_low_Bollinger_Range
   global last_XRPBTC_high_low_Bollinger_Range
   global last_XRPBTC_b_up
   global last_XRPBTC_b_low
##
   global BalanceBNB
   global BNBRateBuy,BNBRateSell,BNBRateNow
   global last_BNBBTC_high_mid_Bollinger_Range
   global last_BNBBTC_mid_low_Bollinger_Range
   global last_BNBBTC_high_low_Bollinger_Range
   global last_BNBBTC_b_up
   global last_BNBBTC_b_low
#
   global entry_order_BTCUSDT_ask
   global entry_order_BTCUSDT_bid
   global entry_order_USDCBTC_ask
   global entry_order_USDCBTC_bid
   global entry_order_ZENBTC_ask
   global entry_order_ZENBTC_bid
   global entry_order_XRPBTC_ask
   global entry_order_XRPBTC_bid
   global entry_order_BNBBTC_ask
   global entry_order_BNBBTC_bid
#
###
################################
########## ***** MAIN TARGET BTCUSDT ***** ##########
   print("Calcurate BTCUSDT Chart for Execute Market Order on Signal Checking ***")
###
   BTCUSDT_Amount == 0.0000
   ups = False
   dws = False
   lots = False
###
   # ボリンンジャーバンド取得(CLOSE値の1分足)
   b_up = 99999999.9999
   b_low = 0.00000
   b_mid = 0.00000
   # 1分足チヤートデータ取得
   chart = get_chart_data(SYMBOL_BTCUSDT)
   time.sleep(5)
   index = 4  ## INDEX(4):CLOSE値
   if (len(chart)>0):
      # get the ohlCv (closing price, index == 4)
      closes = [x[index] for x in chart]
      bret = get_bollinger_band(closes)
      time.sleep(5)
      b_up = bret['bb_up'][-1]
      b_mid = bret['bb_mid'][-1]
      b_low = bret['bb_low'][-1]
#
   # 最安値
   clow = 99999999.99999999 
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp < clow) :
         clow = clp
#
   # 最高値
   chigh = 00000000.00000000
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp > chigh) :
         chigh = clp
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
   ask= float(ticker['askPrice']) 
   bid =float(ticker['bidPrice'])
   last=float(ticker['lastPrice'])
   if (last_high_mid_Bollinger_Range == 0.0000):
      last_high_mid_Bollinger_Range = (b_up - b_mid)
      last_mid_low_Bollinger_Range = (b_mid - b_low)
      last_high_low_Bollinger_Range = (b_up - b_low)
   else:
      if ((b_up - b_low) > last_high_low_Bollinger_Range) :
         if (last_high_mid_Bollinger_Range < b_up - b_mid) :
            if (last < b_mid) :
               ups = True
         if (last_mid_low_Bollinger_Range < (b_mid - b_low)):
            if (last > b_mid) :
               dws = True
      else:
         if (last < b_mid and last < b_mid - ENTRY_MEAN*LOTOF_BTCUSDT):
            if (closes[-2] > closes[-1] and (last - last_b_low) > (last - b_low) and last < (b_mid + b_low)/UpRange) :
               ups = True
            if (last > b_mid and last > b_mid + ENTRY_MEAN*LOTOF_BTCUSDT):
               if (closes[-2] < closes[-1] and (last_b_up - last) > (b_up - last) and last > (b_up + b_mid)/DwRange) :
                  dws = True
      last_high_mid_Bollinger_Range = (b_up - b_mid)
      last_mid_low_Bollinger_Range = (b_mid - b_low)
      last_high_low_Bollinger_Range = (b_up - b_low)
      last_b_up = b_up
      last_b_low = b_low
#
### BTCUSDT のみSTOPLOSS TAKEPROFIT判定があるので省略
#   if (ups):
#      if (ORDER_SIDE_BTCUSDT == SELL):
#        if ( bid > entry_order_BTCUSDT_bid):
#            ups = False
#   if (dws):
#      if ORDER_SIDE_BTCUSDT == BUY):
#        if ( ask  < entry_order_BTCUSDT_bid):
#            ups = False
#
#
   print(BTCUSDT_Pair + " Upper signal = " + str(ups))
   print(BTCUSDT_Pair + " Downd signal = " + str(dws))
####################
   #print("************* Checking Order Signal *******************")
   # 買い条件を決めているところ
   # 買い注文
   if(ups):
      BTCUSDT_Amount = round(float((float(BalanceUSDT) / float(BincRateBuy)) * 0.95), 4)
      ### ここで買い再度取引収計算
      lots = False
      if(BTCUSDT_Amount >= min_lot_BTCUSDT):
         lots = True
         ret = check_order_size(BUY, BTCUSDT_Pair, BTCUSDT_Amount, ask)
         if (ret['OK']):
            if (float(ret['OrderSize']) > float(round(float((float(BalanceUSDT) / float(BincRateBuy)) * 0.95), 4))):
                lots = False
            else:
                BTCUSDT_Amount = float(ret['OrderSize'])
         else:
            lots = False
      if (lots):
         stop_order_price = bid - STOP_LOSS_MEAN * LOTOF_BTCUSDT
         take_order_price = ask + TAKE_PROFIT_MEAN * LOTOF_BTCUSDT
#
         logger.info("Buy stop_order_price(BTCUSDT)=" + "{0:.8f}".format(stop_order_price))
         logger.info("Buy take_order_price(BTCUSDT)=" + "{0:.8f}".format(take_order_price))
         logger.info("Buy ask_price(BTCUSDT)=" + "{0:.8f}".format(ask))
         logger.info("Buy bid_price(BTCUSDT)=" + "{0:.8f}".format(bid))
#
         if (BTCUSDT_Amount > MAX_BTC) :
            BTCUSDT_Amount = MAX_BTC
         msg = "Calcurate BTCUSDT_Amount(Buy):"+str(BTCUSDT_Amount)
         print (d+" "+msg)
      else:
         BTCUSDT_Amount = 0.0000
######
   # 売り条件を決めているところ
   # 売り注文
   if (dws) :
      BTCUSDT_Amount = -round(float(BalanceBTC) - float(KEEP_BTC), 4)
      ### ここで売り再度取引収計算
      lots = False
      if(abs(BTCUSDT_Amount) >= min_lot_BTCUSDT):
         lots = True
      ret = check_order_size(SELL, BTCUSDT_Pair, abs(BTCUSDT_Amount), bid)
      if (ret['OK']):
         if (float(ret['OrderSize']) > float(round(abs(float(BTCUSDT_Amount)*0.75),4))):
            lots = False
         else:
            BTCUSDT_Amount = -float(ret['OrderSize'])
      else:
         lots = False
#
      if(lots):
         stop_order_price = ask + STOP_LOSS_MEAN * LOTOF_BTCUSDT
         take_order_price = bid - TAKE_PROFIT_MEAN * LOTOF_BTCUSDT
#
         print("Sell stop_order_price(BTCUSDT)=" + "{0:.8f}".format(stop_order_price))
         print("Sell take_order_price(BTCUSDT)=" + "{0:.8f}".format(take_order_price))
         logger.info("Sell ask_price(BTCUSDT)=" + "{0:.8f}".format(ask))
         logger.info("Sell bid_price(BTCUSDT)=" + "{0:.8f}".format(bid))
#
         if (abs(BTCUSDT_Amount) > MAX_BTC) : # 最低限必要な量（要確認）
            BTCUSDT_Amount = - MAX_BTC
         msg = "Calcurate BTCUSDT_Amount(Sell):"+str(BTCUSDT_Amount)
         print (d+" "+msg)
      else:
         BTCUSDT_Amount = 0.0000
###
      #print("BTCUSDT_Amount=" + str(BTCUSDT_Amount))
      # 何もしない
   if (BTCUSDT_Amount == 0.0000) :
      if (ORDER_SIDE == BUY and entry_order_ask > 0.0 and long_side_position > 0.0) :
         msg = "Long Position BTCUSDT_Amount = " + "{0:.8f}".format(long_side_position)
      elif (ORDER_SIDE == SELL and entry_order_bid > 0.0 and short_side_position > 0.0) :
         msg = "Short Posision BTCUSDT_Amount = " + "{0:.8f}".format(short_side_position)
      else :
         msg = "Calcurate BTCUSDT_Amount(None Position) = " + "{0:.8f}".format(BTCUSDT_Amount)
      print (d+" "+msg)
####################
########## ***** SUB TARGET USDCBTC ***** ##########
   print("Calcurate USDCBTC Chart for Execute Market Order on Signal Checking ***")
#
   USDCBTC_Amount = 0.0000
   ups = False
   dws = False
   lots = False
#
   # ボリンンジャーバンド取得(CLOSE値の1分足)
   b_up = 99999999.9999
   b_low = 0.00000
   b_mid = 0.00000
   # 1分足チヤートデータ取得
   chart = get_chart_data(SYMBOL_USDCBTC)
   time.sleep(5)
   index = 4  ## INDEX(4):CLOSE値
   if (len(chart)>0):
      # get the ohlCv (closing price, index == 4)
      closes = [x[index] for x in chart]
      bret = get_bollinger_band(closes)
      time.sleep(5)
      b_up = bret['bb_up'][-1]
      b_mid = bret['bb_mid'][-1]
      b_low = bret['bb_low'][-1]
#
   # 最安値
   clow = 99999999.99999999 
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp < clow) :
         clow = clp
#
   # 最高値
   chigh = 00000000.00000000
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp > chigh) :
         chigh = clp
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ticker = Binc.get_ticker(symbol=USDCBTC_Pair)
   ask= float(ticker['askPrice']) 
   bid =float(ticker['bidPrice'])
   last=float(ticker['lastPrice'])
   if (last_USDCBTC_high_mid_Bollinger_Range == 0.0000):
      last_USDCBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_USDCBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_USDCBTC_high_low_Bollinger_Range = (b_up - b_low)
   else:
      if ((b_up - b_low) > last_USDCBTC_high_low_Bollinger_Range) :
         if (last_USDCBTC_high_mid_Bollinger_Range < b_up - b_mid) :
            if (last < b_mid) :
               ups = True
         if (last_USDCBTC_mid_low_Bollinger_Range < (b_mid - b_low)):
            if (last > b_mid) :
               dws = True
      else:
         if (last < b_mid and last < b_mid - ENTRY_MEAN*LOTOF_USDCBTC):
            if (closes[-2] > closes[-1] and (last - last_b_low) > (last - b_low) and last < (b_mid + b_low)/UpRange) :
               ups = True
            if (last > b_mid and last > b_mid + ENTRY_MEAN*LOTOF_USDCBTC):
               if (closes[-2] < closes[-1] and (last_b_up - last) > (b_up - last) and last > (b_up + b_mid)/DwRange) :
                  dws = True
      last_USDCBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_USDCBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_USDCBTC_high_low_Bollinger_Range = (b_up - b_low)
      last_USDCBTC_b_up = b_up
      last_USDCBTC_b_low = b_low
#
   if (ups):
      if (ORDER_SIDE_USDCBTC == SELL):
        if ( ask > entry_order_USDCBTC_ask + STOP_LOSS_MEAN * LOTOF_USDCBTC):
            ups = False
   if (dws):
      if (ORDER_SIDE_USDCBTC == BUY):
        if ( bid < entry_order_USDCBTC_bid - STOP_LOSS_MEAN * LOTOF_USDCBTC):
            ups = False
   elif (ups == False and dws == False):
      if (ORDER_SIDE_USDCBTC == BUY):
        if ( bid > entry_order_USDCBTC_bid + TAKE_PROFIT_MEAN * LOTOF_USDCBTC):
            ups = True
        elif (ORDER_SIDE_USDCBTC == SELL):
            if ( ask < entry_order_USDCBTC_ask - TAKE_PROFIT_MEAN * LOTOF_USDCBTC):
                dws = True
#
   print(USDCBTC_Pair + " Upper signal = " + str(ups))
   print(USDCBTC_Pair + " Downd signal = " + str(dws))
####################
   #print("************* Checking Order Signal *******************")
   # 買い条件を決めているところ
   # 買い注文
   if(ups):
      USDCBTC_Amount = round(float((float(BalanceBTC) - float(KEEP_BTC)) / float(USDCRateBuy) * 0.75), 4)
      #print("Buy USDCBTC_Amount=" + str(USDCBTC_Amount))
      ### ここで買い再度取引収計算
      lots = False
      if(USDCBTC_Amount >= min_lot_USDCBTC):
         lots = True
         ret = check_order_size(BUY, USDCBTC_Pair, USDCBTC_Amount, ask)
         if (ret['OK']):
            USDCBTC_Amount = float(ret['OrderSize'])
         else:
            lots = False
      if (lots):
         if (USDCBTC_Amount > MAX_ALT) :
            USDCBTC_Amount = MAX_ALT
         msg = "Calcurate USDCBTC_Amount(Buy):"+str(USDCBTC_Amount)
         print (d+" "+msg)
      else:
         USDCBTC_Amount = 0.0000
#
#   USDCBTC_Amount = 0.0000
   # 売り条件を決めているところ
   # 売り注文
   if (dws) :
      USDCBTC_Amount = -round(float(BalanceUSDC) - 0.005, 4)
      ### ここで売り再度取引収計算
      lots = False
      if(abs(USDCBTC_Amount) >= min_lot_USDCBTC):
         lots = True
      ret = check_order_size(SELL, USDCBTC_Pair, abs(USDCBTC_Amount), bid)
      if (ret['OK']):
         USDCBTC_Amount = -float(ret['OrderSize'])
      else:
         lots = False
######
   if (lots):
       if (abs(USDCBTC_Amount) > MAX_ALT) : # 最低限必要な量（要確認）
           USDCBTC_Amount = - MAX_ALT
       msg = "Calcurate USDCBTC_Amount(Sell):"+str(USDCBTC_Amount)
       print (d+" "+msg)
   else:
       USDCBTC_Amount = 0.0000
#
   print("USDCBTC_Amount=" + str(USDCBTC_Amount))
####################
########## ***** SUB TARGET ZENBTC ***** ##########
   print("Calcurate ZENBTC Chart for Execute Market Order on Signal Checking ***")
#
   ZENBTC_Amount = 0.0000
   ups = False
   dws = False
   lots = False
#
   # ボリンンジャーバンド取得(CLOSE値の1分足)
   b_up = 99999999.9999
   b_low = 0.00000
   b_mid = 0.00000
   # 1分足チヤートデータ取得
   chart = get_chart_data(SYMBOL_ZENBTC)
   time.sleep(5)
   index = 4  ## INDEX(4):CLOSE値
   if (len(chart)>0):
      # get the ohlCv (closing price, index == 4)
      closes = [x[index] for x in chart]
      bret = get_bollinger_band(closes)
      time.sleep(5)
      b_up = bret['bb_up'][-1]
      b_mid = bret['bb_mid'][-1]
      b_low = bret['bb_low'][-1]
#
   # 最安値
   clow = 99999999.99999999 
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp < clow) :
         clow = clp
#
   # 最高値
   chigh = 00000000.00000000
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp > chigh) :
         chigh = clp
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ticker = Binc.get_ticker(symbol=ZENBTC_Pair)
   ask= float(ticker['askPrice']) 
   bid =float(ticker['bidPrice'])
   last=float(ticker['lastPrice'])
   if (last_ZENBTC_high_mid_Bollinger_Range == 0.0000):
      last_ZENBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_ZENBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_ZENBTC_high_low_Bollinger_Range = (b_up - b_low)
   else:
      if ((b_up - b_low) > last_ZENBTC_high_low_Bollinger_Range) :
         if (last_ZENBTC_high_mid_Bollinger_Range < b_up - b_mid) :
            if (last < b_mid) :
               ups = True
         if (last_ZENBTC_mid_low_Bollinger_Range < (b_mid - b_low)):
            if (last > b_mid) :
               dws = True
      else :
         if (last < b_mid and last < b_mid - ENTRY_MEAN*LOTOF_ZENBTC) :
            if (closes[-2] > closes[-1] and (last - last_ZENBTC_b_low) > (last - b_low) and last < (b_mid + b_low)/UpRange) :
               ups = True
         if (last > b_mid and last > b_mid + ENTRY_MEAN*LOTOF_ZENBTC):
            if (closes[-2] < closes[-1] and (last_ZENBTC_b_up - last) > (b_up - last) and last > (b_up + b_mid)/DwRange) :
               dws = True
      last_ZENBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_ZENBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_ZENBTC_high_low_Bollinger_Range = (b_up - b_low)
      last_ZENBTC_b_up = b_up
      last_ZENBTC_b_low = b_low
#
   if (ups):
      if (ORDER_SIDE_ZENBTC == SELL):
        if ( ask > entry_order_ZENBTC_ask + STOP_LOSS_MEAN * LOTOF_ZENBTC):
            ups = False
   if (dws):
      if (ORDER_SIDE_ZENBTC == BUY):
        if ( bid < entry_order_ZENBTC_bid - STOP_LOSS_MEAN * LOTOF_ZENBTC):
            ups = False
   elif (ups == False and dws == False):
      if (ORDER_SIDE_ZENBTC == BUY):
        if ( bid > entry_order_ZENBTC_bid + TAKE_PROFIT_MEAN * LOTOF_ZENBTC):
            ups = True
        elif (ORDER_SIDE_ZENBTC == SELL):
            if ( ask < entry_order_ZENBTC_ask - TAKE_PROFIT_MEAN * LOTOF_ZENBTC):
                dws = True
#
   print(ZENBTC_Pair + " Upper signal = " + str(ups))
   print(ZENBTC_Pair + " Downd signal = " + str(dws))
####################
   #print("************* Checking Order Signal *******************")
   # 買い条件を決めているところ
   # 買い注文
   if(ups):
      ZENBTC_Amount = round(float((float(BalanceBTC) - float(KEEP_BTC)) / float(ZENRateBuy) * 0.75), 4)
      #print("Buy ZENBTC_Amount=" + str(ZENBTC_Amount))
      ### ここで買い再度取引収計算
      lots = False
      if(ZENBTC_Amount >= min_lot_ZENBTC):
         lots = True
         ret = check_order_size(BUY, ZENBTC_Pair, ZENBTC_Amount, ask)
         if (ret['OK']):
            ZENBTC_Amount = float(ret['OrderSize'])
         else:
            lots = False
      if (lots):
         if (ZENBTC_Amount > MAX_ALT) :
            ZENBTC_Amount = MAX_ALT
         msg = "Calcurate ZENBTC_Amount(Buy):"+str(ZENBTC_Amount)
         print (d+" "+msg)
      else:
         ZENBTC_Amount = 0.0000
########
   # 売り条件を決めているところ
   # 売り注文
   if(dws):
      ZENBTC_Amount = -round(float(BalanceZEN) - 0.005, 4)
      lots = False
      if(abs(ZENBTC_Amount) >= min_lot_ZENBTC):
         lots = True
      ret = check_order_size(SELL, ZENBTC_Pair, abs(ZENBTC_Amount), bid)
      if (ret['OK']):
         ZENBTC_Amount = -float(ret['OrderSize'])
      else:
         lots = False
      if (lots) :
         if (abs(ZENBTC_Amount) > MAX_ALT) : # 最低限必要な量（要確認）
            ZENBTC_Amount = - MAX_ALT
            msg = "Calcurate ZENBTC_Amount(Sell):"+str(ZENBTC_Amount)
            print (d+" "+msg)
      else:
         ZENBTC_Amount = 0.0000
#
#
   print("ZENBTC_Amount=" + str(ZENBTC_Amount))
####################
########## ***** SUB TARGET XRPBTC ***** ##########
   print("Calcurate XRPBTC Chart for Execute Market Order on Signal Checking ***")
#
   XRPBTC_Amount = 0.0000
   ups = False
   dws = False
   lots = False
#
   # ボリンンジャーバンド取得(CLOSE値の1分足)
   b_up = 99999999.9999
   b_low = 0.00000
   b_mid = 0.00000
   # 1分足チヤートデータ取得
   chart = get_chart_data(SYMBOL_XRPBTC)
   time.sleep(5)
   index = 4  ## INDEX(4):CLOSE値
   if (len(chart)>0):
      # get the ohlCv (closing price, index == 4)
      closes = [x[index] for x in chart]
      bret = get_bollinger_band(closes)
      time.sleep(5)
      b_up = bret['bb_up'][-1]
      b_mid = bret['bb_mid'][-1]
      b_low = bret['bb_low'][-1]
#
   # 最安値
   clow = 99999999.99999999 
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp < clow) :
         clow = clp
#
   # 最高値
   chigh = 00000000.00000000
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp > chigh) :
         chigh = clp
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ticker = Binc.get_ticker(symbol=XRPBTC_Pair)
   ask= float(ticker['askPrice']) 
   bid =float(ticker['bidPrice'])
   last=float(ticker['lastPrice'])
   if (last_XRPBTC_high_mid_Bollinger_Range == 0.0000):
      last_XRPBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_XRPBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_XRPBTC_high_low_Bollinger_Range = (b_up - b_low)
   else:
      if ((b_up - b_low) > last_XRPBTC_high_low_Bollinger_Range) :
         if (last_XRPBTC_high_mid_Bollinger_Range < b_up - b_mid) :
            if (last < b_mid) :
               ups = True
         if (last_XRPBTC_mid_low_Bollinger_Range < (b_mid - b_low)):
            if (last > b_mid) :
               dws = True
      else :
         if (last < b_mid and last < b_mid - ENTRY_MEAN*LOTOF_XRPBTC) :
            if (closes[-2] > closes[-1] and (last - last_XRPBTC_b_low) > (last - b_low) and last < (b_mid + b_low)/UpRange) :
               ups = True
         if (last > b_mid and last > b_mid + ENTRY_MEAN*LOTOF_XRPBTC):
            if (closes[-2] < closes[-1] and (last_XRPBTC_b_up - last) > (b_up - last) and last > (b_up + b_mid)/DwRange) :
               dws = True
      last_XRPBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_XRPBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_XRPBTC_high_low_Bollinger_Range = (b_up - b_low)
      last_XRPBTC_b_up = b_up
      last_XRPBTC_b_low = b_low
#
   if (ups):
      if (ORDER_SIDE_XRPBTC == SELL):
        if ( ask > entry_order_XRPBTC_ask + STOP_LOSS_MEAN * LOTOF_XRPBTC):
            ups = False
   if (dws):
      if (ORDER_SIDE_XRPBTC == BUY):
        if ( bid < entry_order_XRPBTC_bid - STOP_LOSS_MEAN * LOTOF_XRPBTC):
            ups = False
   elif (ups == False and dws == False):
      if (ORDER_SIDE_XRPBTC == BUY):
        if ( bid > entry_order_XRPBTC_bid + TAKE_PROFIT_MEAN * LOTOF_XRPBTC):
            ups = True
        elif (ORDER_SIDE_XRPBTC == SELL):
            if ( ask < entry_order_XRPBTCT_ask - TAKE_PROFIT_MEAN * LOTOF_XRPBTC):
                dws = True
#
   print(XRPBTC_Pair + " Upper signal = " + str(ups))
   print(XRPBTC_Pair + " Downd signal = " + str(dws))
####################
   #print("************* Checking Order Signal *******************")
   # 買い条件を決めているところ
   # 買い注文
   if(ups):
      XRPBTC_Amount = round(float((float(BalanceBTC) - float(KEEP_BTC)) / float(XRPRateBuy) * 0.75), 4)
      #print("Buy XRPBTC_Amount=" + str(XRPBTC_Amount))
      ### ここで買い再度取引収計算
      lots = False
      if(XRPBTC_Amount >= min_lot_XRPBTC):
         lots = True
         ret = check_order_size(BUY, XRPBTC_Pair, XRPBTC_Amount, ask)
         if (ret['OK']):
            XRPBTC_Amount = float(ret['OrderSize'])
         else:
            lots = False
      if(lots):
         if (XRPBTC_Amount > MAX_ALT) :
            XRPBTC_Amount = MAX_ALT
         msg = "Calcurate XRPBTC_Amount(Buy):"+str(XRPBTC_Amount)
         print (d+" "+msg)
      else:
         XRPBTC_Amount = 0.0000
########
   # 売り条件を決めているところ
   # 売り注文
   if (dws) :
      XRPBTC_Amount = -round(float(BalanceXRP) - 0.005, 4)
      ### ここで売り再度取引収計算
      lots = False
      if(abs(XRPBTC_Amount) >= min_lot_XRPBTC):
         lots = True
      ret = check_order_size(SELL, XRPBTC_Pair, abs(XRPBTC_Amount), bid)
      if (ret['OK']):
         XRPBTC_Amount = -float(ret['OrderSize'])
      else:
         lots = False
   if(lots) :
       if (abs(XRPBTC_Amount) > MAX_ALT) : # 最低限必要な量（要確認）
           XRPBTC_Amount = - MAX_ALT
       msg = "Calcurate XRPBTC_Amount(Sell):"+str(XRPBTC_Amount)
       print (d+" "+msg)
   else:
       XRPBTC_Amount = 0.0000
#
#
   print("XRPBTC_Amount=" + str(XRPBTC_Amount))
###################
########## ***** SUB TARGET BNBBTC ***** ##########
   print("Calcurate BNBBTC Chart for Execute Market Order on Signal Checking ***")
#
   BNBBTC_Amount = 0.0000
   ups = False
   dws = False
   lots = False
#
   # ボリンンジャーバンド取得(CLOSE値の1分足)
   b_up = 99999999.9999
   b_low = 0.00000
   b_mid = 0.00000
   # 1分足チヤートデータ取得
   chart = get_chart_data(SYMBOL_BNBBTC)
   time.sleep(5)
   index = 4  ## INDEX(4):CLOSE値
   if (len(chart)>0):
      # get the ohlCv (closing price, index == 4)
      closes = [x[index] for x in chart]
      bret = get_bollinger_band(closes)
      time.sleep(5)
      b_up = bret['bb_up'][-1]
      b_mid = bret['bb_mid'][-1]
      b_low = bret['bb_low'][-1]
#
   # 最安値
   clow = 99999999.99999999 
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp < clow) :
         clow = clp
#
   # 最高値
   chigh = 00000000.00000000
   for i in range(PERIOD-2) :
      clp = closes[-i]
      if (clp > chigh) :
         chigh = clp
#
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   ticker = Binc.get_ticker(symbol=BNBBTC_Pair)
   ask= float(ticker['askPrice']) 
   bid =float(ticker['bidPrice'])
   last=float(ticker['lastPrice'])
   if (last_BNBBTC_high_mid_Bollinger_Range == 0.0000):
      last_BNBBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_BNBBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_BNBBTC_high_low_Bollinger_Range = (b_up - b_low)
   else:
      if ((b_up - b_low) > last_BNBBTC_high_low_Bollinger_Range) :
         if (last_BNBBTC_high_mid_Bollinger_Range < b_up - b_mid) :
            if (last < b_mid) :
               ups = True
         if (last_BNBBTC_mid_low_Bollinger_Range < (b_mid - b_low)):
            if (last > b_mid) :
               dws = True
      else :
         if (last < b_mid and last < b_mid - ENTRY_MEAN*LOTOF_BNBBTC):
            if (closes[-2] > closes[-1] and (last - last_BNBBTC_b_low) > (last - b_low) and last < (b_mid + b_low)/UpRange) :
               ups = True
         if (last > b_mid and last > b_mid + ENTRY_MEAN*LOTOF_BNBBTC):
            if (closes[-2] < closes[-1] and (last_BNBBTC_b_up - last) > (b_up - last) and last > (b_up + b_mid)/DwRange) :
               dws = True
      last_BNBBTC_high_mid_Bollinger_Range = (b_up - b_mid)
      last_BNBBTC_mid_low_Bollinger_Range = (b_mid - b_low)
      last_BNBBTC_high_low_Bollinger_Range = (b_up - b_low)
      last_BNBBTC_b_up = b_up
      last_BNBBTC_b_low = b_low
#
   if (ups):
      if (ORDER_SIDE_BNBBTC == SELL):
        if ( ask > entry_order_BNBBTC_ask + STOP_LOSS_MEAN * LOTOF_BNBBTC):
            ups = False
   if (dws):
      if (ORDER_SIDE_BNBBTC == BUY):
        if ( bid < entry_order_BNBBTC_bid - STOP_LOSS_MEAN * LOTOF_BNBBTC):
            ups = False
   elif (ups == False and dws == False):
      if (ORDER_SIDE_BNBBTC == BUY):
        if ( bid > entry_order_BNBBTC_bid + TAKE_PROFIT_MEAN * LOTOF_BNBBTC):
            ups = True
        elif (ORDER_SIDE_BNBBTC == SELL):
            if ( ask < entry_order_BNBBTC_ask - TAKE_PROFIT_MEAN * LOTOF_BNBBTC):
                dws = True
#
   print(BNBBTC_Pair + " Upper signal = " + str(ups))
   print(BNBBTC_Pair + " Downd signal = " + str(dws))
####################
   #print("************* Checking Order Signal *******************")
   # 買い条件を決めているところ
   # 買い注文
   if(ups):
      BNBBTC_Amount = round(float((float(BalanceBTC) - float(KEEP_BTC) / float(BNBRateBuy)) * 0.5), 4)
      #print("Buy BNBBTC_Amount=" + str(BNBBTC_Amount))
      ### ここで買い再度取引収計算
      lots = False
      if(BNBBTC_Amount >= min_lot_BNBBTC):
         lots = True
         ret = check_order_size(BUY, BNBBTC_Pair, abs(BNBBTC_Amount), ask)
         if (ret['OK']):
            BNBBTC_Amount = float(ret['OrderSize'])
         else:
            lots = False
      if (lots):
         if (BNBBTC_Amount > MAX_ALT) :
            BNBBTC_Amount = MAX_ALT
         msg = "Calcurate BNBBTC_Amount(Buy):"+str(BNBBTC_Amount)
         print (d+" "+msg)
      else:
         BNBBTC_Amount = 0.0000
#####
   # 売り条件を決めているところ
   # 売り注文
   if (dws) :
      BNBBTC_Amount = -round(float(BalanceBNB) - MIN_BNB, 4)
      lots = False
      if(abs(BNBBTC_Amount) >= min_lot_BNBBTC):
         lots = True
      ret = check_order_size(SELL, BNBBTC_Pair, abs(BNBBTC_Amount), bid)
      if (ret['OK']):
         BNBBTC_Amount = -float(ret['OrderSize'])
      else:
         lots = False
######
   if (lots) :
       if (abs(BNBBTC_Amount) > MAX_ALT) : # 最低限必要な量（要確認）
           BNBBTC_Amount = - MAX_ALT
       msg = "Calcurate BNBBTC_Amount(Sell):"+str(BNBBTC_Amount)
       print (d+" "+msg)
   else:
       BNBBTC_Amount = 0.0000
#
   print("BNBBTC_Amount=" + str(BNBBTC_Amount))
#
   if (BNBBTC_Amount < MIN_BNB) :
      if (float(BalanceBNB) < float(MIN_BNB)) :
           BNBBTC_Amount = MIN_BNB
           if (BNBBTC_Amount > round(float((float(BalanceBTC) / float(BNBRateBuy)) * 0.9), 4)):
               BNBBTC_Amount = 0.0000
#
########################################################################
########################################################################
#
def PutBinance() :
   global BTCUSDT_Amount,BincRateBuy,BincRateSell,Rate,BincRateNow
   global BalanceUSDT,BalanaceBTC,BalanceBought
   global F_Buy,F_Sell,F_Non,F_Cancel,RateNow
   global BuyPrice,SellPrice
   global ORDER_SIDE
#
   global USDCRateBuy,USDCRateSell,USDCRateNow
   global ZENRateBuy,ZENRateSell,ZENRateNow
   global XRPRateBuy,XRPRateSell,XRPRateNow
   global BNBRateBuy,BNBRateSell,BNBRateNow
#
   global ORDER_SIDE_USDCBTC
   global ORDER_SIDE_ZENBTC
   global ORDER_SIDE_XRPBTC
   global ORDER_SIDE_BNBBTC

   global BTCUSDT_Amount
   global USDCBTC_Amount
   global ZENBTC_Amount
   global XRPBTC_Amount
   global BNBBTC_Amount
#
   global entry_ask_price
   global entry_bid_price
   global take_order_price
   global stop_order_price
   global entry_order_ask
   global entry_order_bid
   global long_side_position
   global short_side_position
#
   global entry_order_ask
   global entry_order_bid
#
   global ORDER_SIDE_BTCUSDT
   global ORDER_SIDE_USDCBTC
   global ORDER_SIDE_ZENBTC
   global ORDER_SIDE_XRPBTC
   global ORDER_SIDE_BNBBTC
#
   global entry_order_USDCBTC_ask
   global entry_order_USDCBTC_bid
   global entry_order_ZENBTC_ask
   global entry_order_ZENBTC_bid
   global entry_order_XRPBTC_ask
   global entry_order_XRPBTC_bid
   global entry_order_BNBBTC_ask
   global entry_order_BNBBTC_bid
#
   temp_profit = 0.0#
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
###
   F_Buy = False
   F_Sell = False
   F_Cancel = False
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   print("********** Starting PutBinance Buy Sell Order Process **********")
   msg = "\r\n@BTCUSDT_Amount=" + str(BTCUSDT_Amount) + "\r\n@USDCBTC_Amount=" + str(USDCBTC_Amount) +"\r\n@ZENBTC_Amount=" + str(ZENBTC_Amount) + "\r\n@XRPBTC_Amount=" + str(XRPBTC_Amount) + "\r\n@BNBBTC_Amount=" + str(BNBBTC_Amount)
   print (d + msg)
   #logger.info(msg)
#######################################################
########## Main Target BTCUSDT Order Logic ############
#
   if (BTCUSDT_Amount > 0.0000) :
       try :
           # 買い注文
           BuyPrice = BincRateBuy
           SellPrice = BincRateSell
           ### MarketでBuy注文 
           ret = BuyMarket(BTCUSDT_Amount, SYMBOL_BTCUSDT, BTCUSDT_Pair, BuyPrice)
           if (ret == False):
               ret = check_order_size(BUY, BTCUSDT_Pair, BTCUSDT_Amount, entry_order_ask)
               if (ret['OK']):
                  if (ret['OrderSize'] != BTCUSDT_Amount):
                     BTCUSDT_Amount = float(ret['OrderSize'])
                  ret = BuyMarket(BTCUSDT_Amount, SYMBOL_BTCUSDT, BTCUSDT_Pair, BuyPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_BTCUSDT = BUY
               long_side_position = float(BTCUSDT_Amount)
               ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
               entry_order_BTCUSDT_ask= float(ticker['askPrice']) 
               entry_order_BTCUSDT_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float(BTCUSDT_Amount * 0.1)
               # 約定待ち （必要に応じて修正、単位は秒）
               F_Buy = True
               time.sleep(20)
       except Exception as e :
           msg = "注文（買い）に失敗しました。@" + SYMBOL_BTCUSDT + "@" + str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
###
   elif (BTCUSDT_Amount < 0.0000) :
       try : 
           # 売り注文
           BuyPrice = BincRateBuy
           SellPrice = BincRateSell
           ### MarketでSell注文 
           ret = SellMarket(BTCUSDT_Amount, SYMBOL_BTCUSDT, BTCUSDT_Pair, SellPrice)
           if (ret == False):
               ret = check_order_size(SELL, BTCUSDT_Pair, abs(BTCUSDT_Amount), entry_order_bid)
               if (ret['OK']):
                  if (ret['OrderSize'] != abs(BTCUSDT_Amount)):
                     BTCUSDT_Amount = - float(ret['OrderSize'])
                  ret = SellMarket(BTCUSDT_Amount, SYMBOL_BTCUSDT, BTCUSDT_Pair, SellPrice)
               else:
                  ret = False
           if (ret):
               ORDER_SIDE_BTCUSDT = SELL
               short_side_position = -float(BTCUSDT_Amount)
               ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
               entry_order_BTCUSDT_ask= float(ticker['askPrice']) 
               entry_order_BTCUSDT_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float(BTCUSDT_Amount * 0.05)
               # 約定待ち （必要に応じて修正、単位は秒）
               F_Sell = True
               time.sleep(20)
       except Exception as e :
           msg = "注文（売り）に失敗しました。@"+ SYMBOL_BTCUSDT + "@" + +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
#
   elif (BTCUSDT_Amount == 0.0000) :   # No Signal Chacking TakeProfit & Stoploass
#
       ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
       current_ask = float(ticker['askPrice']) 
       current_bid =float(ticker['bidPrice'])
       order_mark = 0
#####
       if(ORDER_SIDE == BUY and entry_order_BTCUSDT_ask > 0.0 and long_side_position > 0.0):
           if(entry_order_BTCUSDT_ask > current_ask):
                if(current_ask > take_order_price) :
                    order_mark = 1
#
           if(entry_order_BTCUSDT_ask < current_ask):
                if(current_bid < stop_order_price - MIN_BTC) :
                    order_mark = 2
#
           if(order_mark>0 and long_side_position > MIN_BTC):
                try : 
                    # 売り注文
                    SellPrice = BincRateSell
                    ret = SellMarket(-long_side_position, SYMBOL_BTCUSDT, BTCUSDT_Pair, SellPrice)
                    if (ret == False):
                        ret = check_order_size(SELL, BTCUSDT_Pair, long_side_position, current_bid)
                        if (ret['OK']):
                            if (ret['OrderSize'] != long_side_position):
                                long_side_position = - float(ret['OrderSize'])
                            ret = SellMarket(long_side_position, SYMBOL_BTCUSDT, BTCUSDT_Pair, SellPrice)
                        else:
                            ret = False
                    if(ret):
                        temp_profit = float(entry_order_bid - current_bid)
                        if(order_mark == 1):
                            msg = "利益確定：注文（売り）を出しました。: " + SYMBOL_BTCUSDT + " :Long Position Change Entry Sell Position (TakeProfit)= " + "{0:.8f}".format(temp_profit)
                        if(order_mark == 2):
                            msg = "損失確定：注文（売り）を出しました。: " + SYMBOL_BTCUSDT + " :Long Position Change Entry Sell Position (StopLoss)  = " + "{0:.8f}".format(temp_profit)
                        print (d+" "+msg)
                        linemes= d+"\r\n"+msg
                        lineNotify(linemes)
                        logger.info(msg)
                        ORDER_SIDE_BTCUSDT = SELL
                        short_side_position = float(BTCUSDT_Amount)
                        ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
                        entry_order_BTCUSDT_ask= float(ticker['askPrice']) 
                        entry_order_BTCUSDT_bid =float(ticker['bidPrice'])
                        BalanceBought = BalanceBought + float(BTCUSDT_Amount * 0.1)
                        # 約定待ち （必要に応じて修正、単位は秒）
                        time.sleep(20)
                        F_Sell = True
                except Exception as e :
                    msg = "注文（売り）に失敗しました。@" + SYMBOL_BTCUSDT + "@" + str(e.message)
                    print (d+" "+msg)
                    logger.error(msg)
                    pass
#
######
       if(ORDER_SIDE == SELL and entry_order_BTCUSDT_bid > 0.0 and short_side_position > 0.0):
           if(entry_order_BTCUSDT_bid > current_bid):
                if(current_bid < take_order_price) :
                    order_mark = 1
#
           if(entry_order_BTCUSDT_bid < current_bid):
                if(current_ask > stop_order_price + MIN_BTC) :
                    order_mark = 2
#
           if(order_mark>0 and short_side_position > MIN_BTC):
                try : 
                    #買い注文
                    BuyPrice = BincRateBuy
                    ret = BuyMarket(short_side_position, SYMBOL_BTCUSDT, BTCUSDT_Pair, BuyPrice)
                    if (ret == False):
                        ret = check_order_size(BUY, BTCUSDT_Pair, short_side_position, current_ask)
                        if (ret['OK']):
                            if (ret['OrderSize'] != short_side_position):
                                short_side_position = float(ret['OrderSize'])
                            ret = BuyMarket(short_side_position, SYMBOL_BTCUSDT, BTCUSDT_Pair, BuyPrice)
                        else:
                            ret = False
                    if(ret):
                        temp_profit = float(current_ask - entry_order_ask)
                        if(order_mark == 1):
                            msg = "利益確定注文（買い）を出しました。: " + SYMBOL_BTCUSDT + " :Short Position Change Entry Buy Position (TakeProfit)= " + "{0:.8f}".format(temp_profit)
                        if(order_mark == 2):
                            msg = "損失確定注文（買い）を出しました。: " + SYMBOL_BTCUSDT + " :Short Position Change Entry Buy Position (StopLoss)  = " + "{0:.8f}".format(temp_profit)
                        print (d+" "+msg)
                        linemes= d+"\r\n"+msg
                        lineNotify(linemes)
                        logger.info(msg)
                        ORDER_SIDE_BTCUSDT = BUY
                        long_side_position = float(BTCUSDT_Amount)
                        ticker = Binc.get_ticker(symbol=BTCUSDT_Pair)
                        entry_order_BTCUSDT_ask= float(ticker['askPrice']) 
                        entry_order_BTCUSDT_bid =float(ticker['bidPrice'])
                        nceBought = BalanceBought + float(short_side_position * 0.1)
                        # 約定待ち （必要に応じて修正、単位は秒）
                        time.sleep(20)
                        F_Sell = True
                except Exception as e :
                    msg = "注文（売り）に失敗しました。@" + SYMBOL_BTCUSDT + "@" + str(e.message)
                    print (d+" "+msg)
                    logger.error(msg)
#####################################
#######################################################
########## SUb Target USDCBTC Order Logic ############
#
   if (USDCBTC_Amount > 0.0000) :
       try :
           # 買い注文
           BuyPrice = USDCRateBuy
           SellPrice = USDCRateSell
           ### MarketでBuy注文 
           ret = BuyMarket(USDCBTC_Amount, SYMBOL_USDCBTC, USDCBTC_Pair, BuyPrice)
           if (ret == False):
               ret = check_order_size(BUY, USDCBTC_Pair, USDCBTC_Amount, BuyPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != USDCBTC_Amount):
                     USDCBTC_Amount = float(ret['OrderSize'])
                  ret = BuyMarket(USDCBTC_Amount, SYMBOL_USDCBTC, USDCBTC_Pair, BuyPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_USDCBTC = BUY
               ticker = Binc.get_ticker(symbol=USDCBTC_Pair)
               entry_order_USDCBTC_ask= float(ticker['askPrice']) 
               entry_order_USDCBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(USDCBTC_Amount) * float(USDCRateNow)) * 0.1)
               time.sleep(20)
       except Exception as e :
           msg = "注文（買い）に失敗しました。@" + SYMBOL_USDCBTC + "@" + str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
###
   elif (USDCBTC_Amount < 0.0000) :
       try : 
           # 売り注文
           BuyPrice = USDCRateBuy
           SellPrice = USDCRateSell
           ### MarketでSell注文 
           ret = SellMarket(USDCBTC_Amount, SYMBOL_USDCBTC, USDCBTC_Pair, SellPrice)
           if (ret == False):
               ret = check_order_size(SELL, USDCBTC_Pair, abs(USDCBTC_Amount), SellPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != abs(USDCBTC_Amount)):
                     USDCBTC_Amount = - float(ret['OrderSize'])
                  ret = SellMarket(USDCBTC_Amount, SYMBOL_USDCBTC, USDCBTC_Pair, SellPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_USDCBTC = SELL
               ticker = Binc.get_ticker(symbol=USDCBTC_Pair)
               entry_order_USDCBTC_ask= float(ticker['askPrice']) 
               entry_order_USDCBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(USDCBTC_Amount) * float(USDCRateNow)) * 0.05)
               time.sleep(20)
       except Exception as e :
           msg = "注文（売り）に失敗しました。@" + SYMBOL_USDCBTC + "@" + str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
#######################################################
########## SUb Target ZENBTC Order Logic ############
#
   if (ZENBTC_Amount > 0.0000) :
       try :
           # 買い注文
           BuyPrice = ZENRateBuy
           SellPrice = ZENRateSell
           ### MarketでBuy注文 
           ret = BuyMarket(ZENBTC_Amount, SYMBOL_ZENBTC, ZENBTC_Pair, BuyPrice)
           if (ret == False):
               ret = check_order_size(BUY, ZENBTC_Pair, ZENBTC_Amount, BuyPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != ZENBTC_Amount):
                     ZENBTC_Amount = float(ret['OrderSize'])
                  ret = BuyMarket(ZENBTC_Amount, SYMBOL_ZENBTC, ZENBTC_Pair, BuyPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_ZENBTC = BUY
               ticker = Binc.get_ticker(symbol=ZENBTC_Pair)
               entry_order_ZENBTC_ask= float(ticker['askPrice']) 
               entry_order_ZENBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(ZENBTC_Amount) * float(ZENRateNow)) * 0.1)
               time.sleep(20)
       except Exception as e :
           msg = "注文（買い）に失敗しました。@" + SYMBOL_ZENBTC + "@" +str(e.message)
           logger.error(msg)
           print (d+" "+msg)
           pass
###
   elif (ZENBTC_Amount < 0.0000) :
       try : 
           # 売り注文
           BuyPrice = ZENRateBuy
           SellPrice = ZENRateSell
           ### MarketでSell注文 
           ret = SellMarket(ZENBTC_Amount, SYMBOL_ZENBTC, ZENBTC_Pair, SellPrice)
           if (ret == False):
               ret = check_order_size(SELL, ZENBTC_Pair, abs(ZENBTC_Amount), SellPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != abs(ZENBTC_Amount)):
                     ZENBTC_Amount = - float(ret['OrderSize'])
                  ret = SellMarket(ZENBTC_Amount, SYMBOL_ZENBTC, ZENBTC_Pair, SellPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_ZENBTC = SELL
               entry_order_ZENBTC_ask= float(ticker['askPrice']) 
               entry_order_ZENBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(ZENBTC_Amount) * float(ZENRateNow)) * 0.05)
               time.sleep(20)
       except Exception as e :
           msg = "注文（売り）に失敗しました。@" + SYMBOL_ZENBTC + "@" +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
#######################################################
########## SUb Target XRPBTC Order Logic ############
#
   if (XRPBTC_Amount > 0.0000) :
       try :
           # 買い注文
           BuyPrice = XRPRateBuy
           SellPrice = XRPRateSell
           ### MarketでBuy注文 
           ret = BuyMarket(XRPBTC_Amount, SYMBOL_XRPBTC, XRPBTC_Pair, BuyPrice)
           if (ret == False):
               ret = check_order_size(BUY, XRPBTC_Pair, XRPBTC_Amount, BuyPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != XRPBTC_Amount):
                     XRPBTC_Amount = float(ret['OrderSize'])
                  ret = BuyMarket(XRPBTC_Amount, SYMBOL_XRPBTC, XRPBTC_Pair, BuyPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_XRPBTC = BUY
               ticker = Binc.get_ticker(symbol=XRPBTC_Pair)
               entry_order_XRPBTC_ask= float(ticker['askPrice']) 
               entry_order_XRPBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(XRPBTC_Amount) * float(XRPRateNow)) * 0.1)
               time.sleep(20)
       except Exception as e :
           msg = "注文（買い）に失敗しました。@" + SYMBOL_XRPBTC + "@" +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
###
   elif (XRPBTC_Amount < 0.0000) :
       try : 
           # 売り注文
           BuyPrice = XRPRateBuy
           SellPrice = XRPRateSell
           ### MarketでSell注文 
           ret = SellMarket(XRPBTC_Amount, SYMBOL_XRPBTC, XRPBTC_Pair, SellPrice)
           if (ret == False):
               ret = check_order_size(SELL, XRPBTC_Pair, abs(XRPBTC_Amount), SellPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != abs(XRPBTC_Amount)):
                     XRPBTC_Amount = - float(ret['OrderSize'])
                  ret = SellMarket(XRPBTC_Amount, SYMBOL_XRPBTC, XRPBTC_Pair, SellPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_XRPBTC = SELL
               ticker = Binc.get_ticker(symbol=XRPBTC_Pair)
               entry_order_XRPBTC_ask= float(ticker['askPrice']) 
               entry_order_XRPBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(XRPBTC_Amount) * float(XRPRateNow)) * 0.05)
               time.sleep(20)
       except Exception as e :
           msg = "注文（売り）に失敗しました。@" + SYMBOL_XRPBTC + "@" +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
#######################################################
########## SUb Target BNBBTC Order Logic ############
#
   if (BNBBTC_Amount > 0.0000) :
       try :
           # 買い注文
           BuyPrice = BNBRateBuy
           SellPrice = BNBRateSell
           ### MarketでBuy注文 
           ret = BuyMarket(BNBBTC_Amount, SYMBOL_BNBBTC, BNBBTC_Pair, BuyPrice)
           if (ret == False):
               ret = check_order_size(BUY, BNBBTC_Pair, BNBBTC_Amount, BuyPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != BNBBTC_Amount):
                     BNBBTC_Amount = float(ret['OrderSize'])
                  ret = BuyMarket(BNBBTC_Amount, SYMBOL_BNBBTC, BNBBTC_Pair, BuyPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_BNBBTC = BUY
               ticker = Binc.get_ticker(symbol=BNBBTC_Pair)
               entry_order_BNBBTC_ask= float(ticker['askPrice']) 
               entry_order_BNBBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought + float((float(BNBBTC_Amount) * float(BNBRateNow)) * 0.05)
               time.sleep(20)
       except Exception as e :
           msg = "注文（買い）に失敗しました。@" + SYMBOL_BNBBTC + "@" +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
   elif (BNBBTC_Amount < 0.0000) :
       try : 
           # 売り注文
           BuyPrice = BNBRateBuy
           SellPrice = BNBRateSell
           ### MarketでSell注文 
           ret = SellMarket(BNBBTC_Amount, SYMBOL_BNBBTC, BNBBTC_Pair, SellPrice)
           if (ret == False):
               ret = check_order_size(SELL, BNBBTC_Pair, abs(BNBBTC_Amount), SellPrice)
               if (ret['OK']):
                  if (ret['OrderSize'] != abs(BNBBTC_Amount)):
                     BNBBTC_Amount = - float(ret['OrderSize'])
                  ret = SellMarket(BNBBTC_Amount, SYMBOL_BNBBTC, BNBBTC_Pair, SellPrice)
               else:
                  ret = False
           if(ret):
               ORDER_SIDE_BNBBTC = SELL
               ticker = Binc.get_ticker(symbol=BNBBTC_Pair)
               entry_order_BNBBTC_ask= float(ticker['askPrice']) 
               entry_order_BNBBTC_bid =float(ticker['bidPrice'])
               BalanceBought = BalanceBought - float((float(BNBBTC_Amount) * float(BNBRateNow)) * 0.05)
               time.sleep(20)
       except Exception as e :
           msg = "注文（売り）に失敗しました。@" + SYMBOL_BNBBTC + "@" +str(e.message)
           print (d+" "+msg)
           logger.error(msg)
           pass
#####
   # タイムスタンプ
   now = datetime.today()
   d = now.strftime("%Y/%m/%d %H:%M:%S")
   print("********** PutBinance Buy Sell Order Process End **********")
   msg = "\r\n@ORDER_SIDE_BTCUSDT:"+ ORDER_SIDE_BTCUSDT + "\r\n@ORDER_SIDE_USDCBTC:" + ORDER_SIDE_USDCBTC + "\r\n@ORDER_SIDE_ZENBTC:" + ORDER_SIDE_ZENBTC + "\r\n@ORDER_SIDE_XRPBTC:" + ORDER_SIDE_XRPBTC + "\r\n@ORDER_SIDE_BNBBTC:" + ORDER_SIDE_BNBBTC
   print (d + msg)
   #logger.info(msg)

#####################################
### None Order Signal and NonTouched StopLoass or Takeprofit of Current Holding Coin Position
   F_Non = True
   return True
###
def main() :
   global BTCUSDT_Amount
   global BalanceUSDT,BalanceBTC
   global BTCJPY_price
   global BalanceBought,F_Buy,F_Sell,F_Non,F_Cancel
   global Binc
   global Binp
   global BuyPrice,SellPrice
   global last_high_mid_Bollinger_Range
   global last_mid_low_Bollinger_Range
   global last_high_low_Bollinger_Range
#
   global last_USDCBTC_high_mid_Bollinger_Range
   global last_USDCBTC_mid_low_Bollinger_Range
   global last_USDCBTC_high_low_Bollinger_Range
   global last_ZENBTC_high_mid_Bollinger_Range
   global last_ZENBTC_mid_low_Bollinger_Range
   global last_ZENBTC_high_low_Bollinger_Range
   global last_XRPBTC_high_mid_Bollinger_Range
   global last_XRPBTC_mid_low_Bollinger_Range
   global last_XRPBTC_high_low_Bollinger_Range
   global last_BNBBTC_high_mid_Bollinger_Range
   global last_BNBBTC_mid_low_Bollinger_Range
   global last_BNBBTC_high_low_Bollinger_Range
#
   global BTCUSDT_Amount
   global USDCBTC_Amount
   global ZENBTC_Amount
   global XRPBTC_Amount
   global BNBBTC_Amount
#
   global last_b_up
   global last_b_low
   global stop_order_price
   global take_order_price
   global long_side_position
   global short_side_position
   global last_USDCBTC_b_up
   global last_USDCBTC_b_low
   global last_ZENBTC_b_up
   global last_ZENBTC_b_low
   global last_XRPBTC_b_up
   global last_XRPBTC_b_low
   global last_BNBBTC_b_up
   global last_BNBBTC_b_low
#
   global ORDER_SIDE_BTCUSDT
   global ORDER_SIDE_USDCBTC
   global ORDER_SIDE_ZENBTC
   global ORDER_SIDE_XRPBTC
   global ORDER_SIDE_BNBBTC
#
   global entry_order_BTCUSDT_ask
   global entry_order_BTCUSDT_bid
   global entry_order_USDCBTC_ask
   global entry_order_USDCBTC_bid
   global entry_order_ZENBTC_ask
   global entry_order_ZENBTC_bid
   global entry_order_XRPBTC_ask
   global entry_order_XRPBTC_bid
   global entry_order_BNBBTC_ask
   global entry_order_BNBBTC_bid
#
   global last_hour
   global init
   global init_values
#
   global min_lot_BTCUSDT
   global min_lot_USDCBTC
   global min_lot_ZENBTC
   global min_lot_XRPBTC
   global min_lot_BNBBTC
#
   BTCUSDT_Amount = 0.0
#
   USDCBTC_Amount = 0.0
   ZENBTC_Amount = 0.0
   XRPBTC_Amount = 0.0
   BNBBTC_Amount = 0.0
#
   min_lot_BTCUSDT = MIN_BTC
   min_lot_USDCBTC = MIN_ALT
   min_lot_ZENBTC = MIN_ALT
   min_lot_XRPBTC = MIN_ALT
   min_lot_BNBBTC = MIN_ALT
#
   last_b_up = 0.0
   last_b_low = 0.0
   stop_order_price = 0.0
   take_order_price = 0.0
   entry_order_ask = 0.0
   entry_order_bid = 0.0
   long_side_position = 0.0
   short_side_position = 0.0
   last_USDCBTC_b_up = 0.0
   last_USDCBTC_b_low = 0.0
   last_ZENBTC_b_up = 0.0
   last_ZENBTC_b_low = 0.0
   last_XRPBTC_b_up = 0.0
   last_XRPBTC_b_low = 0.0
   last_BNBBTC_b_up = 0.0
   last_BNBBTC_b_low = 0.0
   BuyPrice = 0.00000000
   SellPrice = 99999999.99999999
   stop_order_price = 0.0000
   take_order_price = 0.0000
   entry_order_ask = 0.0000
   entry_order_bid = 0.0000
   last_high_mid_Bollinger_Range = 0.0000
   last_mid_low_Bollinger_Range = 0.0000
   last_high_low_Bollinger_Range = 0.0000
   last_USDCBTC_high_mid_Bollinger_Range = 0.0000
   last_USDCBTC_mid_low_Bollinger_Range = 0.0000
   last_USDCBTC_high_low_Bollinger_Range = 0.0000
   last_ZENBTC_high_mid_Bollinger_Range = 0.0000
   last_ZENBTC_mid_low_Bollinger_Range = 0.0000
   last_ZENBTC_high_low_Bollinger_Range = 0.0000
   last_XRPBTC_high_mid_Bollinger_Range = 0.0000
   last_XRPBTC_mid_low_Bollinger_Range = 0.0000
   last_XRPBTC_high_low_Bollinger_Range = 0.0000
   last_BNBBTC_high_mid_Bollinger_Range = 0.0000
   last_BNBBTC_mid_low_Bollinger_Range = 0.0000
   last_BNBBTC_high_low_Bollinger_Range = 0.0000
#
   ORDER_SIDE_BTCUSDT = NONE
   ORDER_SIDE_USDCBTC = NONE
   ORDER_SIDE_ZENBTC = NONE
   ORDER_SIDE_XRPBTC = NONE
   ORDER_SIDE_BNBBTC = NONE
#
   entry_order_BTCUSDT_ask = 0.0
   entry_order_BTCUSDT_bid = 0.0
   entry_order_USDCBTC_ask = 0.0
   entry_order_USDCBTC_bid = 0.0
   entry_order_ZENBTC_ask = 0.0
   entry_order_ZENBTC_bid = 0.0
   entry_order_XRPBTC_ask = 0.0
   entry_order_XRPBTC_bid = 0.0
   entry_order_BNBBTC_ask = 0.0
   entry_order_BNBBTC_bid = 0.0
#
#   Binp.fetch_balance({'recvWindow': 10000000})
#   Binp = ccxt.binance({'verbose': True})
   Binp = ccxt.binance({'options': {'adjustForTimeDifference': True}})
#   Binp =  ccxt.binance()
   Binc = Client(BINC_API_KEY,BINC_API_SECRET,)
   int(time.time() * 1000) - Binc.get_server_time()['serverTime']
   BTCJPY_price = getBTCJPY_Price()
   #print("BTC_JPY Price = " + "{0:.4f}".format(BTCJPY_price))
#
   last_hour = datetime.now().hour
#
   init = True
   init_values = 0.0
   BalanceBought = 0.0
   
   while True :
#
       F_Buy = False
       F_Sell = False
       F_Non = False
      
       # Binance から Rate や Balance を取得する
       GetBinance()
#
       # 売買条件が成立しているか判断する
       Calcurate()
       PutBinance()
       F_Buy = False
       F_Sell = False
       F_Cancel = False
#
       print("Waiting " + str(WAITING_TIME) + " Minutes.....")
       # WAITING_TIME(5?)分のウエイト
       time.sleep(60*WAITING_TIME)

if __name__ == "__main__":
   ORDER_SIDE = NONE
   BTCUSDT_Amount = 0.0
   USDCBTC_Amount = 0.0
   ZENBTC_Amount = 0.0
   XRPBTC_Amount = 0.0
   BNBBTC_Amount = 0.0
#
   main()

   
