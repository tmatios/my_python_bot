#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import request
import poloniex
import sched
import time
from time import gmtime, strftime
import logging
import json
import datetime
import math
from predictionprice.derivedpoloniex import MarginTradePoloniex
global polopri
global polopub
global polotrd
#
global myETH_BTC_Balance
global myXEM_BTC_Balance
global myXRP_BTC_Balance
#
global myBTC_Balance
global myBTC_order_amount
global myETH_order_amount
global myXEM_order_amount
global myXRP_order_amount
#
global myMargin
global crWeekday
global save_count
global max_save_count
##
global cr_PercentChangeBTC
global cr_PercentChangeETH
global cr_PercentChangeXEM
global cr_PercentChangeXRP
#
global last_PercentChangeBTC
global last_PercentChangeETH
global last_PercentChangeXEM
global last_PercentChangeXRP
#
global last_PriceETHBTC
global last_PriceXEMBTC
global last_PriceXRPBTC
#
global pre_PriceETHBTC
global pre_PriceXEMBTC
global pre_PriceXRPBTC
###
global BTC_ETH_Pos_Amount
global BTC_ETH_Pos_Type
global BTC_ETH_Pos_Profit
global BTC_LTC_Pos_Amount
global BTC_LTC_Pos_Type
global BTC_LTC_Pos_Profit
global BTC_XEM_Pos_Amount
global BTC_XEM_Pos_Type
global BTC_XEM_Pos_Profit
global BTC_XRP_Pos_Amount
global BTC_XRP_Pos_Type
global BTC_XRP_Pos_Profit
#
global Ordered
global myStopLoss
global myTakeProfit
global myStopLossLisk
global myTakeProfitLisk
global totalPosBalance
global lastDay

##############################
myGmailAddress = "Your Gmail Address"
myGmailAddressPassword = "Your Gmail Password"
myAPIKey = "Your API Key"
mySecret = "Your API Secret Key"
coins = ["ETH", "XEM", "XRP"]
basicCoin = "BTC"
tradeSigns = ["none", "none", "none"]
workingDirPath = os.path.dirname(os.path.abspath(__file__))
##########################
#########################################
#
WAIT_MIN = 5
MV_RANGE = 60
CHANEL_PERIOD = 22
###JPNAPI ="https://api.bitflyer.jp/v1/ticker"
#####################
#####
# 
logger = logging.getLogger('PoloniexBot')
# 
logger.setLevel(10)
# 
fh = logging.FileHandler('MyPoloniexMarginBot_Trace.log')
logger.addHandler(fh)
# 
formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
#####################
#####
#
line_notify_token = 'y3B2qB6G4uV1nnxrFEa0nBIqsj9dNTJGs2XNquyU24H'
line_notify_api = 'https://notify-api.line.me/api/notify'
#
#####################
#####
def lineNotify(message):
    payload = {'message': message}
    headers = {'Authorization': 'Bearer ' + line_notify_token}
    try:
        requests.post(line_notify_api, data=payload, headers=headers)
    except:
        #logger.info("line_notify_api error")
        pass

#####################
#
def initAPI():
  global myETH_BTC_Balance
  global myLTC_BTC_Balance
  global myXEM_BTC_Balance
  global myXRP_BTC_Balance
#
  global myHoldETH_BTC_Balance
  global myHoldXEM_BTC_Balance
  global myHoldXRP_BTC_Balance
###
#
  global last_PriceETHBTC
  global last_PriceXEMBTC
  global last_PriceXRPBTC
#
  global pre_PriceETHBTC
  global pre_PriceXEMBTC
  global pre_PriceXRPBTC
  global Ordered
  global crWeekday
  global save_count
  global max_save_count
  global lastDay
#
  global myStopLossLisk
  global myTakeProfitLisk
  global totalPosBalance
#
  global init_btc_balance
  global exp_jpy_rate
  global init_jpy_reta
  global lasttimehour
  global start_hour
#
  global myBTC_Balance
#
  global polopri
  global polopub
  global polotrd
#
  Ordered = 0
  save_count = 0
  lastDay = 0
  max_save_count = 22
  now = datetime.datetime.now()
  crWeekday = now.weekday()
#  logging.basicConfig(level=logging.INFO)
  polopub = poloniex.Poloniex()
  polopub.timeout = 60
  polopri = poloniex.Poloniex("Your API Kry","Your API Secret Key")
  polotrd = MarginTradePoloniex(Key=myAPIKey, Secret=mySecret, workingDirPath=workingDirPath,
                              gmailAddress=myGmailAddress, gmailAddressPassword=myGmailAddressPassword,
                              coins=coins, tradeSigns=tradeSigns)
  ###polotrd.savePoloniexMarginAccountBalanceToCsv()
  #polotrd.sendMailBalance(polotrd.getSummary())
  ###polotrd.savePoloniexMarginAccountBalanceToCsv()

# Set Up Tradeing StopLoss and TakeProfit on BTC
  myStopLossLisk =  -0.00003
  myTakeProfitLisk = 0.00005
  totalPosBalance = 0.0
#
  last_PriceETHBTC = 0
  last_PriceLTCBTC = 0
  last_PriceXEMBTC = 0
  last_PriceXRPBTC = 0
#
  pre_PriceETHBTC = 0
  pre_PriceLTCBTC = 0
  pre_PriceXEMBTC = 0
  pre_PriceXRPBTC = 0
#
  myBTC_Balance = getBTC_Balance()
#
  gt = time.gmtime()
  lasttimehour = gt.tm_hour
  getCoin_Balance_BTC()
  init_btc_balance = myBTC_Balance
  ##getBTCJPY_Price()
  ##init_jpy_reta = exp_jpy_rate
  ###exp_jpy_rate = 0
#
#
######
###def getBTCJPY_Price():
###   global exp_jpy_rate
###   jpy_price = 400000
###   try:
###     res = requests.get(JPNAPI)
###     json = res.json() 
###     jpy_price = int(json["best_bid"])
###   except:
###      #logger.error("GET JPY RATE ERROR")
###      pass
###   exp_jpy_rate = jpy_price
#
#########
##############################
### get BTC Balance of USD
def getBTC_Balance():
  global polotrd
  global myMargin
  global myBTC_Balance
  global myStopLossLisk
  global myTakeProfitLisk
  global myStopLoss
  global myTakeProfit
#
  ret=""
  try:
    ret = polotrd.returnSummary()
    ## ret = polopri.returnMarginAccountSummary()
  except:
    logger.error("getBTC_Balance ERROR")
    pass
  if(len(ret) > 0):
    myBTC_Balance = float(format(ret['summary']['totalValue']))
    myMargin = int(round(float(format(ret['summary']['currentMargin'])),4)*100)
    myStopLoss = round(float(myBTC_Balance * myStopLossLisk * float(myMargin)),8) 
    myTakeProfit = round(float(myBTC_Balance * myTakeProfitLisk * float(myMargin)),8) 
    return myBTC_Balance
#
### get Balance of BTC(BTC,ETH,LTC,XEM,XRP)
def getCoin_Balance_BTC():
#
  global propri
  global save_count
  global myBTC_order_amount
  global myETH_order_amount
  global myXEM_order_amount
  global myXRP_order_amount
#
  myBTC_Balance = getBTC_Balance()
  BTC_Balance = myBTC_Balance
  err=-1
  try:
    balance = polopri.returnTradableBalances()
    err=0
  except:
    logger.error("getCoin_Balance_BTC ERROR")
    pass
  if(err == 0):
    if (save_count == 0):
      print("returnMarginAccountSummary=" + json.dumps(balance))
    myBTC_order_amount = float(format(balance['BTC_ETH']['BTC']))
    print("MY BTC Order Amount=" + str(myBTC_order_amount))
    myETH_order_amount = float(format(balance['BTC_ETH']['ETH']))
    myETH_order_amount = round(myETH_order_amount * BTC_Balance ,4)                        
    print("MY ETH Order Amount=" + str(myETH_order_amount))
    myXEM_order_amount = float(format(balance['BTC_XEM']['XEM']))
    myXEM_order_amount = round(myXEM_order_amount * BTC_Balance ,4)
    print("MY XEM Order Amount=" + str(myXEM_order_amount))
    myXRP_order_amount = float(format(balance['BTC_XRP']['XRP']))
    myXRP_order_amount = round(myXRP_order_amount * BTC_Balance ,4)
    print("MY XRP Order Amount=" + str(myXRP_order_amount))
  return err
#
####################
def getMarginBalance():
###
  global BTC_ETH_Pos_Amount
  global BTC_ETH_Pos_Type
  global BTC_ETH_Pos_Profit
  global BTC_XEM_Pos_Amount
  global BTC_XEM_Pos_Type
  global BTC_XEM_Pos_Profit
  global BTC_XRP_Pos_Amount
  global BTC_XRP_Pos_Type
  global BTC_XRP_Pos_Profit
  global polopri
  global polotrd
  global totalPosBalance

#
  err = -1
  try:
    ret = polopri.getMarginPosition()
    err = 0
  except:
    logger.error("getMarginBalance ERROR")
    pass
  if (err == 0):
    BTC_ETH_Pos_Amount = float(format(ret['BTC_ETH']['amount']))
    BTC_ETH_Pos_Type = format(ret['BTC_ETH']['type'])
    BTC_ETH_Pos_Profit = format(ret['BTC_ETH']['pl'])
    polotrd.tradeSigns[0] = str(BTC_ETH_Pos_Type) 
    print("BTC_ETH_Pos_Amount=" + str(BTC_ETH_Pos_Amount) + "@type=" + BTC_ETH_Pos_Type + "@profit=" + str(BTC_ETH_Pos_Profit))
#
    BTC_XEM_Pos_Amount = float(format(ret['BTC_XEM']['amount']))
    BTC_XEM_Pos_Type = format(ret['BTC_XEM']['type'])
    BTC_XEM_Pos_Profit = format(ret['BTC_XEM']['pl'])
    polotrd.tradeSigns[2] = str(BTC_XEM_Pos_Type) 
    print("BTC_XEM_Pos_Amount=" + str(BTC_XEM_Pos_Amount) + "@type=" + BTC_XEM_Pos_Type + "@profit=" + str(BTC_XEM_Pos_Profit))
#
    BTC_XRP_Pos_Amount = float(format(ret['BTC_XRP']['amount']))
    BTC_XRP_Pos_Type = format(ret['BTC_XRP']['type'])
    BTC_XRP_Pos_Profit = format(ret['BTC_XRP']['pl'])
    polotrd.tradeSigns[3] = str(BTC_XRP_Pos_Type)
    print("BTC_XRP_Pos_Amount=" + str(BTC_XRP_Pos_Amount) + "@type=" + BTC_XRP_Pos_Type + "@profit=" + str(BTC_XRP_Pos_Profit))
#
    totalPosBalance = float(BTC_ETH_Pos_Profit) + float(BTC_LTC_Pos_Profit) + float(BTC_XEM_Pos_Profit) + float(BTC_XRP_Pos_Profit)
    ## print("totalPosBalance = " + str(totalPosBalance))  
  return err
#
### get lastprice(BTC_ETH,LTC,XEM,BTS,XRP,BTS)
def get_lastPrice():
  global last_PriceETHBTC
  global last_PriceXEMBTC
  global last_PriceXRPBTC
#
  err = -1
  try:
    tickData = polopub.returnTicker()
    err = 0
  except:
    logger.error("get_lastprice ERROR")
    pass
  if (err == 0):
    last_PriceETHBTC = float(format(tickData['BTC_ETH']['last']))
#   print("ETH_BTC_lastprice=" + str(lastPriceETHBTC))
    last_PriceXEMBTC = float(format(tickData['BTC_XEM']['last']))
#   print("XEM_BTC_lastprice=" + str(lastPriceXEMBTC))
    last_PriceXRPBTC = float(format(tickData['BTC_XRP']['last']))
#   print("XRP_BTC_lastprice=" + str(lastPriceXRPBTC))
  return err
####################
def getBTC_ETH_MV_Cross():
#
#
  global last_PriceETHBTC
  global pre_PriceETHBTC
#
  ret = 0
  #print("In getBTC_ETH_MV_Cross")
  chartBTC_ETH = polopub.returnChartData('BTC_ETH', period=300, start=time.time() - polopub.DAY, end=time.time())
#
  clen = len(chartBTC_ETH)
  if (clen == 0 or clen < MV_RANGE + 2):
    logger.error("getBTC_ETH_MV_Cross Error")
    return ret
#
  total_price = 0.0
  lowp = 99999999.9999
  higp = 0.0000
  #print("chartBTC_ETH LEN =" + str(clen)
#  for i in range(clen-1):  print("chartBTC_ETH[" + str(i) + "]['weightedAverage']=" + str(float(chartBTC_ETH[i]['weightedAverage'])))
  i=2
  for i in range(MV_RANGE+i):
    total_price = total_price + float(chartBTC_ETH[i]['weightedAverage'])
    if (float(chartBTC_ETH[i]['low']) < lowp):
      lowp = float(chartBTC_ETH[i]['low'])
    if (float(chartBTC_ETH[i]['high']) > higp):
      higp = float(chartBTC_ETH[i]['high'])
  ave_price = float(total_price / (MV_RANGE+1))
  closp = float(chartBTC_ETH[-1]['close'])
  openp = float(chartBTC_ETH[-2]['open'])
  #print("ETH ave_price         =" + str(ave_price))
  #print("ETH lowp              =" + str(lowp))
  #print("ETH higp              =" + str(higp))
  #print("last_PriceETHBTC      =" + str(last_PriceETHBTC))
  #print("pre_PriceETHBTC       =" + str(pre_PriceETHBTC))
  #print("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #print("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  #logger.info("ETH ave_price         =" + str(ave_price))
  #logger.info("ETH lowp              =" + str(lowp))
  #logger.info("ETH higp              =" + str(higp))
  #logger.info("last_PriceETHBTC      =" + str(last_PriceETHBTC))
  #logger.info("pre_PriceETHBTC       =" + str(pre_PriceETHBTC))
  #logger.info("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #logger.info("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  if ((last_PriceETHBTC < ave_price and last_PriceETHBTC > pre_PriceETHBTC and openp < closp)\
   and (last_PriceETHBTC < float((ave_price + lowp)/2.05))):
    print("BTC_EHT Low Line Cross to Buy")
    logger.info("BTC_EHT Low Line Cross to Buy")
    ret = 1   # Up Signal
#
  elif ((last_PriceETHBTC > ave_price and last_PriceETHBTC < pre_PriceETHBTC and openp > closp)\
   and (last_PriceETHBTC > float((ave_price + higp)/1.95))):
#
    print("BTC_ETH High Line Cross to Sell")
    logger.info("BTC_ETH High Line Cross to Sell")
    ret = -1   # Down Signal
  return(ret)
####################
def getBTC_XEM_MV_Cross():
#
  global last_PriceXEMBTC
  global pre_PriceXEMBTC
# 
  ret = 0
  #print("In getBTC_XEM_MV_Cross")
  chartBTC_XEM = polopub.returnChartData('BTC_XEM', period=300, start=time.time() - polopub.DAY, end=time.time())
#
  clen = len(chartBTC_XEM)
  if (clen == 0 or clen < MV_RANGE + 2):
    logger.error("getBTC_XEM_MV_Cross Error")
    return ret
#
  total_price = 0.0
  lowp = 99999999.9999
  higp = 0.0000
  #print("chartBTC_XEM LEN =" + str(clen)
#  for i in range(clen-1):  print("chartBTC_XEM[" + str(i) + "]['weightedAverage']=" + str(float(chartBTC_XEM[i]['weightedAverage'])))
  i=2
  for i in range(MV_RANGE+i):
    total_price = total_price + float(chartBTC_XEM[i]['weightedAverage'])
    if (float(chartBTC_XEM[i]['low']) < lowp):
      lowp = float(chartBTC_XEM[i]['low'])
    if (float(chartBTC_XEM[i]['high']) > higp):
      higp = float(chartBTC_XEM[i]['high'])
  ave_price = float(total_price / (MV_RANGE+1))
  closp = float(chartBTC_XEM[-1]['close'])
  openp = float(chartBTC_XEM[-2]['open'])
  #print("XEM ave_price         =" + str(ave_price))
  #print("XEM lowp              =" + str(lowp))
  #print("XEM higp              =" + str(higp))
  #print("last_PriceXEMBTC      =" + str(last_PriceXEMBTC))
  #print("pre_PriceXEMBTC       =" + str(pre_PriceXEMBTC))
  #print("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #print("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  #logger.info("XEM ave_price         =" + str(ave_price))
  #logger.info("XEM lowp              =" + str(lowp))
  #logger.info("XEM higp              =" + str(higp))
  #logger.info("last_PriceXEMBTC      =" + str(last_PriceXEMBTC))
  #logger.info("pre_PriceXEMBTC       =" + str(pre_PriceXEMBTC))
  #logger.info("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #logger.info("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  if ((last_PriceXEMBTC < ave_price and last_PriceXEMBTC > pre_PriceXEMBTC and openp < closp)\
   and (last_PriceXEMBTC < float((ave_price + lowp)/2.05))):
    print("BTC_EHT Low Line Cross to Buy")
    logger.info("BTC_XEM Low Line Cross to Buy")
    ret = 1   # Up Signal
#
  elif ((last_PriceXEMBTC > ave_price and last_PriceXEMBTC < pre_PriceXEMBTC and openp > closp)\
   and (last_PriceXEMBTC > float((ave_price + higp)/1.95))):
#
    print("BTC_EHT High Line Cross to Sell")
    logger.info("BTC_XEM High Line Cross to Sell")
    ret = -1   # Down Signal
  return(ret)
####################
def getBTC_XRP_MV_Cross():
#
  global last_PriceXRPBTC
  global pre_PriceXRPBTC
# 
  ret = 0
  #print("In getBTC_XRP_MV_Cross")
  chartBTC_XRP = polopub.returnChartData('BTC_XRP', period=300, start=time.time() - polopub.DAY, end=time.time())
#
  clen = len(chartBTC_XRP)
  if (clen == 0 or clen < MV_RANGE + 2):
    logger.error("getBTC_XRP_MV_Cross Error")
    return ret
#
  total_price = 0.0
  lowp = 99999999.9999
  higp = 0.0000
  #print("chartBTC_XRP LEN =" + str(clen)
#  for i in range(clen-1):  print("chartBTC_XRP[" + str(i) + "]['weightedAverage']=" + str(float(chartBTC_XRP[i]['weightedAverage'])))
  i=2
  for i in range(MV_RANGE+i):
    total_price = total_price + float(chartBTC_XRP[i]['weightedAverage'])
    if (float(chartBTC_XRP[i]['low']) < lowp):
      lowp = float(chartBTC_XRP[i]['low'])
    if (float(chartBTC_XRP[i]['high']) > higp):
      higp = float(chartBTC_XRP[i]['high'])
  ave_price = float(total_price / (MV_RANGE+1))
  closp = float(chartBTC_XRP[-1]['close'])
  openp = float(chartBTC_XRP[-2]['open'])
  #print("XRP ave_price         =" + str(ave_price))
  #print("XRP lowp              =" + str(lowp))
  #print("XRP higp              =" + str(higp))
  #print("last_PriceXRPBTC      =" + str(last_PriceXRPBTC))
  #print("pre_PriceXRPBTC       =" + str(pre_PriceXRPBTC))
  #print("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #print("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  #logger.info("XRP ave_price         =" + str(ave_price))
  #logger.info("XRP lowp              =" + str(lowp))
  #logger.info("XRP higp              =" + str(higp))
  #logger.info("last_PriceXRPBTC      =" + str(last_PriceXRPBTC))
  #logger.info("pre_PriceXRPBTC       =" + str(pre_PriceXRPBTC))
  #logger.info("ave_price + higp)/2   =" + str(float((ave_price + higp)/2)))
  #logger.info("ave_price + lowp)/2   =" + str(float((ave_price + lowp)/2)))
#
  if ((last_PriceXRPBTC < ave_price and last_PriceXRPBTC > pre_PriceXRPBTC and openp < closp)\
   and (last_PriceXRPBTC < float((ave_price + lowp)/2.05))):
    print("BTC_EHT Low Line Cross to Buy")
    logger.info("BTC_XRP Low Line Cross to Buy")
    ret = 1   # Up Signal
#
  elif ((last_PriceXRPBTC > ave_price and last_PriceXRPBTC < pre_PriceXRPBTC and openp > closp)\
   and (last_PriceXRPBTC > float((ave_price + higp)/1.95))):
#
    print("BTC_EHT High Line Cross to Sell")
    logger.info("BTC_XRP High Line Cross to Sell")
    ret = -1   # Down Signal
  return(ret)
####################
##############################################################
#           MAIM LOGIC                                       #
##############################################################
def order_logic():
  global myETH_BTC_Balance
  global myXEM_BTC_Balance
  global myXRP_BTC_Balance
#
  global myBTC_order_amount
  global myETH_order_amount
  global myXEM_order_amount
  global myXRP_order_amount
#
  global myStopLoss
  global myTakeProfit
#
#
  global init_btc_balance
  global lasttimehour
  global start_hour
#
  global myMargin
  global myBTC_Balance
  global crWeekday
  global Ordered
  global lastDay
  global save_count
  global max_save_count
  global poropri
  global polotrd
#
  global last_PriceETHBTC
  global last_PriceXEMBTC
  global last_PriceXRPBTC
#
  global pre_PriceETHBTC
  global pre_PriceXEMBTC
  global pre_PriceXRPBTC
#
  global BTC_ETH_Pos_Amount
  global BTC_ETH_Pos_Type
  global BTC_ETH_Pos_Profit
  global BTC_XEM_Pos_Amount
  global BTC_XEM_Pos_Type
  global BTC_XEM_Pos_Profit
  global BTC_XRP_Pos_Amount
  global BTC_XRP_Pos_Type
  global BTC_XRP_Pos_Profit
#
  global totalPosBalance
###
  print("********* order_logic *********")
#
  go = getCoin_Balance_BTC()
  if(go == -1):
    return
  if(save_count < max_save_count):
    save_count = save_count + 1
#
  ret = getMarginBalance()
  if (ret == -1):
    return
  ret = getBTC_Balance()
  if (ret == -1):
    return
  BTC_Balance = myBTC_Balance
  print("BTC_Balance=" + str(myBTC_Balance))
  print(u'Current StopLoss BTC = %.8f'%(myStopLoss))
  print(u'Current TakeProfit BTC = %.8f'%(myTakeProfit))
  print(u'Current Total Position Balance BTC = %.8f'%(totalPosBalance))
  print("Current Margin(Margin Call bellow 20%) = " + str(myMargin) + "%")
##  time.sleep(10.0)
#####
  ret = get_lastPrice()
  if (ret == -1):
    return
#####
  Ordered = 0
  ETH_order="NONE"
  XEM_order="NONE"
  XRP_order = "NONE"
#
  time.sleep(5.0)
  closeFlag = 0
#######################
  now = datetime.datetime.now()
  if(crWeekday != now.weekday()):
    print("++++++++++ Day Trade is Closed " + now.strftime("%Y/%m/%d %H:%M:%S") + " ++++++++++")
    logger.info("++++++++++ Day Trade is Closed " + now.strftime("%Y/%m/%d %H:%M:%S") + " ++++++++++")
    crWeekday = now.weekday()
    lastDay = 1
    closeFlag = 1
    ### Next Day Position is All Close
  elif(myMargin < 21):
    ### StopMargin
    print("***** Margin Call cna't more oder *****")
    closeFlag = 1
# Check StopLoss
  if(closeFlag == 0):
    if(myStopLoss > totalPosBalance):
      closeFlag = 1
      print("***** StopLoss ALl Position Closing *****")
    elif(myTakeProfit < totalPosBalance):
        closeFlag = 1
        print("***** TakeProfit ALl Position Closing *****")
#
  if(closeFlag == 1):
    for coinIndex in range(len(coins)):
      if(polotrd.tradeSigns[coinIndex] != "none"):
        try:
          polopri.closeMarginPosition(basicCoin + "_" + coins[coinIndex])
        except:
          pass
    polotrd.savePoloniexMarginAccountBalanceToCsv()
    #####
#
  if(closeFlag == 1):
    print("********* None Trade ************")
    return
#######################
#
  print("----------------------------------------")
  ###
  ##### chack ETH BUY/SELL
#####
  if(ETH_order == "NONE"):
    ## print("**** StopLoss(-Profit) Checking ****")
    if(polotrd.tradeSigns[0] != "none"):
      if(float(BTC_ETH_Pos_Profit) < 0.0 and float(BTC_ETH_Pos_Profit) < float(myStopLoss)):
        print(u'ETH StopLoss BTC < %.8f'%(myStopLoss))
        logger.info(u'ETH StopLoss BTC < %.8f'%(myStopLoss))
        closeFlag = 1
        polotrd.tradeSigns[0] = "close"
        linemes = "Poloniex_Margin_Bot ETC_BTC StopLoss(-Profit) Close=" + u'ETH StopLoss BTC < %.8f'%(myStopLoss)
        lineNotify(linemes)
        ETH_order = "CLOSE"
      elif(float(BTC_ETH_Pos_Profit) > 0.0 and float(BTC_ETH_Pos_Profit) > float(myTakeProfit)):
        print(u'ETH TakeProfit BTC > %.8f'%(myTakeProfit))
        logger.info(u'ETH TakeProfit BTC > %.8f'%(myTakeProfit))
        closeFlag = 1
        polotrd.tradeSigns[0] = "close"
        linemes = "Poloniex_Margin_Bot ETC_BTC TakeProfit(+Profit) Close=" + u'ETH TakeProfit BTC > %.8f'%(myTakeProfit)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
        ETH_order = "CLOSE"
#####
  if(ETH_order == "NONE" and pre_PriceETHBTC > 0.0):
    ret = getBTC_ETH_MV_Cross()
    if(ret == 1):
      if(myETH_order_amount > 0.001 and BTC_Balance > 0.0001):
        ETH_order = "BUY"
        Ordered = 1
        if(polotrd.tradeSigns[0]=="long"):
          polotrd.tradeSigns[0] = "hold"
        elif(tradeSigns[0]=="short"):
          polotrd.tradeSigns[0] = "close_long"
        else:
          polotrd.tradeSigns[0] = "long"
        print("*** Low Line Cross ETH_BTC_BUY" + "@AMOUNT=" + str(myETH_order_amount))
        logger.info("*** Low Line Cross ETH_BTC_BUY" + "@AMOUNT=" + str(myETH_order_amount))
        linemes = "Poloniex_Margin_Bot Poloniex_Margin_Bot *** Low Line Cross ETH_BTC_BUY" + "@Price=" + str(last_PriceETHBTC) + "@Amount=" + str(myETH_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
    if(ret == -1):
      if(myETH_order_amount > 0.001 and save_count == max_save_count):
        ETH_order = "SELL"
        Ordered = 1
        if(polotrd.tradeSigns[0]=="short"):
          polotrd.tradeSigns[0] = "hold"
        elif(polotrd.tradeSigns[0]=="long"):
          polotrd.tradeSigns[0] = "close_short"
        else:
          polotrd.tradeSigns[0] = "short"
        print("Poloniex_Margib_Bot *** High Line Cross ETH_BTC_SELL" + "@AMOUNT=" + str(myETH_order_amount))
        logger.info("*** Low Line Cross ETH_BTC_SELL" + "@AMOUNT=" + str(myETH_order_amount))
        linemes = "Poloniex_Margin_Bot *** High Line Cross ETH_BTC_SELL" + "@Price=" + str(last_PriceETHBTC) + "@Amount=" + str(myETH_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
#    if (polotrd.tradeSigns[0]=="hold"):
#      Ordered = 2
###
  ##### check XEM BUY/SELL
#####
  if(XEM_order == "NONE"):
    ## print("**** StopLoss(-Profit) Checking ****")
    if(polotrd.tradeSigns[2] != "none"):
      if(float(BTC_XEM_Pos_Amount) < 0.0 and float(BTC_XEM_Pos_Profit) < float(myStopLoss)):
        print(u'XEM StopLoss BTC < %.8f'%(myStopLoss))
        logger.info(u'XEM StopLoss BTC < %.8f'%(myStopLoss))
        linemes = "Poloniex_Margin_Bot XEM_BTC StopLoss(-Profit) Close=" + u'XEM StopLoss BTC < %.8f'%(myStopLoss)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
        closeFlag = 1
        polotrd.tradeSigns[2] = "close"
        XEM_order = "CLOSE"
      elif(float(BTC_XEM_Pos_Profit) > 0.0 and float(BTC_XEM_Pos_Profit) > float(myTakeProfit)):
        print(u'XEM TakeProfit BTC > %.8f'%(myTakeProfit))
        logger.info(u'XEM TakeProfit BTC > %.8f'%(myTakeProfit))
        linemes = "Poloniex_Margin_Bot XEM_BTC TakeProfit(+Profit) Close=" + u'XEM TakeProfit BTC < %.8f'%(myTakeProfit)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
        closeFlag = 1
        polotrd.tradeSigns[2] = "close"
        XEM_order = "CLOSE"
#####
  if(XEM_order == "NONE" and pre_PriceXEMBTC > 0.0):
    ret = getBTC_XEM_MV_Cross()
    if(ret == 1):
      if(myXEM_order_amount > 0.001 and BTC_Balance > 0.0001):
        XEM_order = "BUY"
        Ordered = 1
        if(polotrd.tradeSigns[2]=="long"):
          polotrd.tradeSigns[2] = "hold"
        elif(polotrd.tradeSigns[2]=="short"):
          polotrd.tradeSigns[2] = "close_long"
        else:
          polotrd.tradeSigns[2] = "long"
        print("*** Low Line Cross XEM_BTC_BUY" + "@AMOUNT=" + str(myXEM_order_amount))
        logger.info("*** Low Line Cross XEM_BTC_BUY" + "@AMOUNT=" + str(myXEM_order_amount))
        linemes = "Poloniex_Margin_Bot *** Low Line Cross XEM_BTC_BUY" + "@Price=" + str(last_PriceXEMBTC) + "@Amount=" + str(myXEM_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
    if(ret == -1):
      if(myXEM_order_amount > 0.001 and save_count == max_save_count):
        XEM_order = "SELL"
        Ordered = 1
        if(polotrd.tradeSigns[2]=="short"):
          polotrd.tradeSigns[2] = "hold"
        elif(polotrd.tradeSigns[2]=="long"):
          polotrd.tradeSigns[2] = "close_short"
        else:
          polotrd.tradeSigns[2] = "short"
        print("*** High Line Cross XEM_BTC_SELL" + "@AMOUNT=" + str(myXEM_order_amount))
        logger.info("*** High Line Cross XEM_BTC_SELL" + "@AMOUNT=" + str(myXEM_order_amount))
        linemes = "Poloniex_Margin_Bot *** High Line Cross XEM_BTC_SELL" + "@Price=" + str(last_PriceXEMBTC) + "@Amount=" + str(myXEM_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
#    if (polotrd.tradeSigns[2]=="hold"):
#      Ordered = 2
###
  ##### check XRP BUY/SELL
#####
  if(XRP_order == "NONE"):
    ## print("**** StopLoss(-Profit) Checking ****")
    if(polotrd.tradeSigns[3] != "none"):
      if(float(BTC_XRP_Pos_Amount) < 0.0 and float(BTC_XRP_Pos_Profit) < float(myStopLoss)):
        print(u'XRP StopLoss BTC < %.8f'%(myStopLoss))
        logger.info(u'XRP StopLoss BTC < %.8f'%(myStopLoss))
        linemes = "Poloniex_Margin_Bot XRP_BTC StopLoss(-Profit) Close=" + u'XRP StopLoss BTC < %.8f'%(myStopLoss)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
        closeFlag = 1
        polotrd.tradeSigns[3] = "close"
        XRP_order = "CLOSE"
      elif(float(BTC_XRP_Pos_Profit) > 0.0 and float(BTC_XRP_Pos_Profit) > float(myTakeProfit)):
        print(u'XRP TakeProfit BTC > %.8f'%(myTakeProfit))
        logger.info(u'XRP TakeProfit BTC > %.8f'%(myTakeProfit))
        linemes = "Poloniex_Margin_Bot XRP_BTC TakeProfit(+Profit) Close=" + u'XRP TakeProfit BTC < %.8f'%(myTakeProfit)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
        closeFlag = 1
        polotrd.tradeSigns[3] = "close"
        XRP_order = "CLOSE"
#####
  if(XRP_order == "NONE" and pre_PriceXRPBTC > 0.0):
    ret = getBTC_XRP_MV_Cross()
    if(ret == 1):
      if(myXRP_order_amount > 0.001 and BTC_Balance > 0.0001):
        XRP_order = "BUY"
        Ordered = 1
        if(polotrd.tradeSigns[3]=="long"):
          polotrd.tradeSigns[3] = "hold"
        elif(polotrd.tradeSigns[3]=="short"):
          polotrd.tradeSigns[3] = "close_long"
        else:
          tradeSigns[3] = "long"
        print("*** Low Line Cross XRP_BTC_BUY" + "@AMOUNT=" + str(myXRP_order_amount))
        logger.info("*** Low Line Cross XRP_BTC_BUY" + "@AMOUNT=" + str(myXRP_order_amount))
        linemes = "Poloniex_Margin_Bot ***GoldenCross XRP_BTC_BUY" + "@Price=" + str(last_PriceXRPBTC) + "@Amount=" + str(myXRP_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
    if(ret == -1):
      if(myXRP_order_amount > 0.001 and save_count == max_save_count):
        XRP_order = "SELL"
        Ordered = 1
        if(polotrd.tradeSigns[3]=="short"):
          polotrd.tradeSigns[3] = "hold"
        elif(polotrd.tradeSigns[3]=="long"):
          polotrd.tradeSigns[3] = "close_short"
        else:
          polotrd.tradeSigns[3] = "short"
        print("*** High Line Crosss XRP_BTC_SELL" + "@AMOUNT=" + str(myXRP_order_amount))
        logger.info("*** High Line Crosss XRP_BTC_SELL" + "@AMOUNT=" + str(myXRP_order_amount))
        linemes = "Poloniex_Margin_Bot *** High Line Cross XEM_BTC_SELL" + "@Price=" + str(last_PriceXEMBTC) + "@Amount=" + str(myXEM_order_amount)
        lineNotify(linemes)
        #polotrd.sendMail(linemes)
#    if (polotrd.tradeSigns[3]=="hold"):
#      Ordered = 1
###
####### Close Margin Trade ##############
  if(closeFlag == 1):
    for coinIndex in range(len(coins)):
      if(polotrd.tradeSigns[coinIndex] == "close"):
        print("Closing Margion Order(BTC_" + coins[coinIndex] + ")")
        logger.info("Closing Margion Order(BTC_" + coins[coinIndex] + ")")
        try:
          polopri.closeMarginPosition(basicCoin + "_" + coins[coinIndex])
          polotrd.tradeSigns[coinIndex] == "none"
        except:
          pass
###
####### Open Margin Trade ##############
  if(Ordered == 1):
    print("Order Signal on BTC/" + coins[0] + ":" + tradeSigns[0] + " | " + coins[1] + ":" + tradeSigns[1] + " | " + coins[2] + ":" + tradeSigns[2])
    logger.info("Order Signal on BTC/" + coins[0] + ":" + tradeSigns[0] + " | " + coins[1] + ":" + tradeSigns[1] + " | " + coins[2] + ":" + tradeSigns[2] )
#####
    try:
      polotrd.fitBalance()
    except:
      pass
#####
  d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
  gt = time.gmtime()
  current_timehour = gt.tm_hour
  ###getBTCJPY_Price()
  ###HoldingJPY = int(round(float(myBTC_Balance) * float(exp_jpy_rate),0))
  ###PROFITBTC = round(float(myBTC_Balance) - float(init_btc_balance),8)
  ###PROFITJPY = int(round(float(PROFITBTC)*float(exp_jpy_rate),0))
  mes = "Poloniex Margin_Trading Bot(" + d + ")Current Balance(BTC)=" + "{0:.8f}".format(myBTC_Balance)
  if (current_timehour != lasttimehour):
    #polotrd.sendMail(mes)
    lasttimehour = current_timehour
    linemes = polotrd.getSummary()
    #polotrd.sendMail(linemes)
    polotrd.sendMailBalance(polotrd.getSummary())
    ###polotrd.savePoloniexMarginAccountBalanceToCsv()
    lineNotify(linemes)
  else:
    print(mes)
#
###################################    
  time.sleep(1.0)  # sleep
#####
#
  pre_PriceETHBTC = last_PriceETHBTC
  pre_PriceXEMBTC = last_PriceXEMBTC
  pre_PriceXRPBTC = last_PriceXRPBTC
#
  print("******** Wainting " + str(WAIT_MIN) + " Minutes Margin Trade Signal BTC_/ETH/XEM/XRP ************")
##########################################
##  print(tickData)
#  time.sleep(10.0)  # sleep

if __name__ == '__main__':
  print ('START:'+ time.ctime())
  now = datetime.datetime.now() # => datetime.datetime(2017, 7, 1, 23, 15, 34, 309309)
  initAPI()
  print ("**************** STRAT Poloniex Margin Trade Bot******************")
  s = sched.scheduler(time.time, time.sleep)
  while 1 == 1:
    try:
      if(save_count < max_save_count):
        s.enter(60, 1, order_logic, ())
      else:
        s.enter(60*WAIT_MIN, 1, order_logic, ())
    except Exception:
      pass
    s.run()
##################

