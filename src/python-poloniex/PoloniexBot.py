# -*- coding: utf-8 -*-
import poloniex
import sched
import json
import math
import datetime
import time
from datetime import datetime, timedelta
from time import gmtime, strftime
import logging
from decimal import *
#
###
MIN_BTC_LOT = 0.01
MIN_ALT_LOT = 0.001
MIN_USDC_LOT = 0.001
ALTCOIN_FIX_CLOSE_LIMIT_HOUR = 24
WAINTING_TIME = 5
CHANGE_PERCENT_RATE = 0.01
MIMIMUM_ORDER_SIZE = 0.001
KEEP_BTC = 0.01
import requests
import sys
#
global polopri
global polopub
global polotrd
#
#
global myInitBTC_Balance
global myInitUSDC_Balance
global myInitALT_Balance
global lasttimehour
#
global myBTC_Balance
global myUSDC_Balance
global myBTC_EOS_Balance
global myBCHSV_BTC_Balance
global myXMR_BTC_Balance
global myXEM_BTC_Balance
global myXRP_BTC_Balance
global myZEC_BTC_Balance
global myLSK_BTC_Balance
global myREP_BTC_Balance

#
global myHoldBTC_Balance
global myHoldUSDC_Balance
global myHoldBCHSV_BTC_Balance
global myHoldEOS_BTC_Balance
global myHoldXMR_BTC_Balance
global myHoldXEM_BTC_Balance
global myHoldXRP_BTC_Balance
global myHoldZEC_BTC_Balance
global myHoldLSK_BTC_Balance
global myHoldREP_BTC_Balance
#
global cr_BTC_Average
global cr_USDC_Average
global last_BTC_Average
global last_USDC_Average
#
global cr_PercentChangeUSDC
global cr_PercentChangeBCHSV
global cr_PercentChangeEOS
global cr_PercentChangeXMR
global cr_PercentChangeXEM
global cr_PercentChangeXRP
global cr_PercentChangeZEC
global cr_PercentChangeLSK
global cr_PercentChangeREP
#
global last_PercentChangeUSDC
global last_PercentChangeBCHSV
global last_PercentChangeEOS
global last_PercentChangeXMR
global last_PercentChangeXEM
global last_PercentChangeXRP
global last_PercentChangeZEC
global last_PercentChangeLSK
global last_PercentChangeREP
#
global cr_HighestUSDC
global cr_LowestUSDC
global cr_HighestBCHSV
global cr_LowestBCHSV
global cr_HighestEOS
global cr_LowestEOS
global cr_HighestXMR
global cr_LowestXMR
global cr_HighestXEM
global cr_LowestXEM
global cr_HighestXRP
global cr_LowestXRP
global cr_HighestZEC
global cr_LowestZEC
global cr_HighestLSK
global cr_LowestLSK
global cr_HighestREP
global cr_LowestREP
#
global cr_CloseUSDC
global cr_CloseBCHSV
global cr_CloseEOS
global cr_CloseXMR
global cr_CloseXEM
global cr_CloseXRP
global cr_CloseZEC
global cr_CloseLSK
global cr_CloseREP
#
global last_CloseUSDC
global last_CloseBCHSV
global last_CloseEOS
global last_CloseXMR
global last_CloseXEM
global last_CloseXRP
global last_CloseZEC
global last_CloseLSK
global last_CloseREP
#
global cr_OpenUSDC
global cr_OpenBCHSV
global cr_OpenEOS
global cr_OpenXMR
global cr_OpenXEM
global cr_OpenXRP
global cr_OpenZEC
global cr_OpenLSK
global cr_OpenREP
#
global last_OpenUSDC
global last_OpenBCHSV
global last_OpenEOS
global last_OpenXMR
global last_OpenXEM
global last_OpenXRP
global last_OpenZEC
global last_OpenLSK
global last_OpenREP
#
#
global cr_VolumeUSDC
global cr_VolumeBCHSV
global cr_VolumeEOS
global cr_VolumeXMR
global cr_VolumeXEM
global cr_VolumeXRP
global cr_VolumeZEC
global cr_VolumeLSK
global cr_VolumeREP
#
global last_VolumeUSDC
global last_VolumeBCHSV
global last_VolumeEOS
global last_VolumeXMR
global last_VolumeXEM
global last_VolumeXRP
global last_VolumeZEC
global last_VolumeLSK
global last_VolumeREP
#
global cr_WeightedAverageUSDC
global cr_WeightedAverageBCHSV
global cr_WeightedAverageEOS
global cr_WeightedAverageXMR
global cr_WeightedAverageXEM
global cr_WeightedAverageXRP
global cr_WeightedAverageZEC
global cr_WeightedAverageLSK
global cr_WeightedAverageREP
#
global last_WeightedAverageUSDC
global last_WeightedAverageBCHSV
global last_WeightedAverageEOS
global last_WeightedAverageXMR
global last_WeightedAverageXEM
global last_WeightedAverageXRP
global last_WeightedAverageZEC
global last_WeightedAverageLSK
global last_WeightedAverageREP
#
global lastPriceUSDCBTC
global lastPriceBCHSVBTC
global lastPriceEOSBTC
global lastPriceXMRBTC
global lastPriceXEMBTC
global lastPriceXRPBTC
global lastPriceZECBTC
global lastPriceLSKBTC
global lastPriceREPBTC
#
global pre_PriceUSDCBTC
global pre_PriceBCHSVBTC
global pre_PriceEOSBTC
global pre_PriceXMRBTC
global pre_PriceXEMBTC
global pre_PriceXRPBTC
global pre_PriceZECBTC
global pre_PriceLSKBTC
global pre_PriceREPBTC
global start_hour
global day_close_flag
global total_alt_btc
global exp_jpy_rate
#########################################
#
#####################
#####
# ログの出力名を設定（1）
logger = logging.getLogger('PoloniexBot')
# ログレベルの設定
logger.setLevel(10)
# ログのファイル出力先を設定
fh = logging.FileHandler('PoloniexBot_Trace.log')
logger.addHandler(fh)
# ログの出力形式の設定
formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
#####################
#
#####################
#####
#ラインに稼働状況を通知
line_notify_token = '******************************************'
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
        pass

#####################
#####
def decimal(number):
    return str(Decimal(str(number)))
#
#####
def check_order_size(order_size, order_price):
# If (order_size * order_price) < 0.0001(MIMIMUM_ORDER_SIZE)) Is Wrong Order Size
#  So Return Normal(>MIMIMUM_ORDER_SIZE) order size
    #logger.info("In check_order_size:ouder_size=" + str(order_size) + "@order_price=" + str(order_price))
    min_order_size = MIMIMUM_ORDER_SIZE
    start_order_size = round(float(order_size),4)
    order_price_min = round(float(order_price),8)
    temp_order_size = round(float(start_order_size) * float(order_price_min),4)
    if (temp_order_size < min_order_size):
        while ((start_order_size * order_price_min) < min_order_size):
            start_order_size = start_order_size + min_order_size * 0.1
    #ogger.info("Out check_order_size:order_size=" + str(start_order_size))
    return float(start_order_size)
#
######################
##########################################
#
def initAPI():
#
    global polopri
    global polopub
    global polotrd
#
    global myInitBTC_Balance
    global myInitUSDC_Balance
    global myInitALT_Balance
    global lasttimehour
    global myBTC_Balance
    global myUSDC_Balance
    global myBCHSV_BTC_Balance
    global myEOS_BTC_Balance
    global myXMR_BTC_Balance
    global myXEM_BTC_Balance
    global myXRP_BTC_Balance
    global myZEC_BTC_Balance
    global myLSK_BTC_Balance
    global myREP_BTC_Balance
    global myUSDCHoldBTC_Balance
    global myBCHSVHoldBTC_Balance
    global myEOSHoldBTC_Balance
    global myXMRHoldBTC_Balance
    global myXEMHoldBTC_Balance
    global myXRPHoldBTC_Balance
    global myZECHoldBTC_Balance
    global myLSKHoldBTC_Balance
    global myREPHoldBTC_Balance
    global cr_BTC_Average
    global cr_USDC_Average
    global last_BTC_Average
    global last_USDC_Average
    global cr_HighestUSDC
    global cr_LowestUSDC
    global cr_HighestBCHSV
    global cr_LowestBCHSV
    global cr_HighestEOS
    global cr_LowestEOS
    global cr_HighestXMR
    global cr_LowestXMR
    global cr_HighestXEM
    global cr_LowestXEM
    global cr_HighestXRP
    global cr_LowestXRP
    global cr_HighestZEC
    global cr_LowestZEC
    global cr_HighestLSK
    global cr_LowestLSK
    global cr_HighestREP
    global cr_LowestREP
    global cr_PercentChangeBTC
    global cr_PercentChangeUSDC
    global cr_PercentChangeBCHSV
    global cr_PercentChangeEOS
    global cr_PercentChangeXMR
    global cr_PercentChangeXEM
    global cr_PercentChangeXRP
    global cr_PercentChangeZEC
    global cr_PercentChangeREP
    global cr_PercentChangeUSDC_BTC
    global cr_PercentChangeBTC_BCHSV
    global cr_PercentChangeBTC_EOS
    global cr_PercentChangeBTC_XMR
    global cr_PercentChangeBTC_XEM
    global cr_PercentChangeBTC_XRP
    global cr_PercentChangeBTC_ZEC
    global cr_PercentChangeBTC_LSK
    global cr_PercentChangeBTC_REP
    global last_PercentChangeUSDC_BTC
    global last_PercentChangeBTC_BCHSV
    global last_PercentChangeBTC_EOS
    global last_PercentChangeBTC_XMR
    global last_PercentChangeBTC_XEM
    global last_PercentChangeBTC_XRP
    global last_PercentChangeBTC_ZEC
    global last_PercentChangeBTC_LSK
    global last_PercentChangeBTC_REP
    global last_PercentChangeBTC
    global last_PercentChangeUSDC
    global last_PercentChangeBCHSV
    global last_PercentChangeEOS
    global last_PercentChangeXMR
    global last_PercentChangeXEM
    global last_PercentChangeXRP
    global last_PercentChangeZEC
    global last_PercentChangeLSK
    global last_PercentChangeREP
    global lastPriceUSDCBTC
    global lastPriceBTCEOS
    global lastPriceBCHSVBTC
    global lastPriceXMRBTC
    global lastPriceXEMBTC
    global lastPriceXRPBTC
    global lastPriceZECBTC
    global lastPriceLSKBTC
    global lastPriceREPBTC
    global pre_PriceUSDCBTC
    global pre_PriceBTCBCHSV
    global pre_PriceBTCEOS
    global pre_lastPriceXMR
    global pre_PriceBTC_XEM
    global pre_PriceBTC_XRP
    global pre_PriceBTC_ZEC
    global pre_PriceBTC_LSK
    global pre_PriceBTC_REP
    global cr_CloseUSDC
    global cr_CloseBCHSV
    global cr_CloseEOS
    global cr_CloseXMR
    global cr_CloseXEM
    global cr_CloseXRP
    global cr_CloseZEC
    global cr_CloseLSK
    global cr_CloseREP
    global last_CloseUSDC
    global last_CloseBCHSV
    global last_CloseEOS
    global last_CloseXMR
    global last_CloseXEM
    global last_CloseXRP
    global last_CloseZEC
    global last_CloseLSK
    global last_CloseREP
    global cr_OpenUSDC
    global cr_OpenBCHSV
    global cr_OpenEOS
    global cr_OpenXMR
    global cr_OpenXEM
    global cr_OpenXRP
    global cr_OpenZEC
    global cr_OpenLSK
    global cr_OpenREP
    global last_OpenUSDC
    global last_OpenBCHSV
    global last_OpenEOS
    global last_OpenXMR
    global last_OpenXEM
    global last_OpenXRP
    global last_OpenZEC
    global last_OpenLSK
    global last_OpenREP
    global cr_VolumeUSDC
    global cr_VolumeBCHSV
    global cr_VolumeEOS
    global cr_VolumeXMR
    global cr_VolumeXEM
    global cr_VolumeXRP
    global cr_VolumeZEC
    global cr_VolumeLSK
    global cr_VolumeREP
    global last_VolumeUSDC
    global last_VolumeBCHSV
    global last_VolumeEOS
    global last_VolumeXMR
    global last_VolumeXEM
    global last_VolumeXRP
    global last_VolumeZEC
    global last_VolumeLSK
    global last_VolumeREP
    global cr_WeightedAverageUSDC
    global cr_WeightedAverageBCHSV
    global cr_WeightedAverageEOS
    global cr_WeightedAverageXMR
    global cr_WeightedAverageXEM
    global cr_WeightedAverageXRP
    global cr_WeightedAverageZEC
    global cr_WeightedAverageLSK
    global cr_WeightedAverageREP
    global last_WeightedAverageUSDC
    global last_WeightedAverageBCHSV
    global last_WeightedAverageEOS
    global last_WeightedAverageXMR
    global last_WeightedAverageXEM
    global last_WeightedAverageXRP
    global last_WeightedAverageZEC
    global last_WeightedAverageLSK
    global last_WeightedAverageREP
    global start_hour
    global day_close_flag
    global total_alt_btc
    global exp_jpy_rate
###########
#####
    polopub = poloniex.Poloniex()
    polopri = poloniex.Poloniex("***********************************","*******************************************************************************************************************************",timeout=60, coach=True)
    polotrd = poloniex.Poloniex("***********************************","*******************************************************************************************************************************",timeout=60, coach=True)
#####
###########
    polopub.timeout = 60
#
    day_close_flag = False
    cr_BTC_Average = 0.0
    cr_USDC_Average = 0.0
    last_BTC_Average = 0.0
    last_USDC_Average = 0.0
    myBTC_Balance = 0.0
    myUSDC_Balance = 0.0
    myBCHSV_BTC_Balance = 0.0
    myEOS_BTC_Balance = 0.0
    myXMR_BTC_Balance = 0.0
    myXEM_BTC_Balance = 0.0
    myXRP_BTC_Balance = 0.0
    myZEC_BTC_Balance = 0.0
    myLSK_BTC_Balance = 0.0
    myREP_BTC_Balance = 0.0
    myUSDCHoldBTC_Balance = 0.0
    myBCHSVHoldBTC_Balance = 0.0
    myEOSHoldBTC_Balance = 0.0
    myXMRHoldBTC_Balance = 0.0
    myXEMHoldBTC_Balance = 0.0
    myXRPHoldBTC_Balance = 0.0
    myZECHoldBTC_Balance = 0.0
    myLSKHoldBTC_Balance = 0.0
    myREPHoldBTC_Balance = 0.0
    cr_BTC_Average = 0.0
    cr_USDC_Average = 0.0
    last_BTC_Average = 0.0
    last_USDC_Average = 0.0
    cr_HighestUSDC = 0.0
    cr_LowestUSDC = 0.0
    cr_HighestBCHSV = 0.0
    cr_LowestBCHSV = 0.0
    cr_HighestEOS = 0.0
    cr_LowestEOS = 0.0
    cr_HighestXMR = 0.0
    cr_LowestXMR = 0.0
    cr_HighestXEM = 0.0
    cr_LowestXEM = 0.0
    cr_HighestXRP = 0.0
    cr_LowestXRP = 0.0
    cr_HighestZEC = 0.0
    cr_LowestZEC = 0.0
    cr_HighestLSK = 0.0
    cr_LowestLSK = 0.0
    cr_HighestREP = 0.0
    cr_LowestREP = 0.0
    cr_PercentChangeBTC = 0.0
    cr_PercentChangeUSDC = 0.0
    cr_PercentChangeBCHSV = 0.0
    cr_PercentChangeEOS = 0.0
    cr_PercentChangeXMR = 0.0
    cr_PercentChangeXEM = 0.0
    cr_PercentChangeXRP = 0.0
    cr_PercentChangeZEC = 0.0
    cr_PercentChangeREP = 0.0
    cr_PercentChangeUSDC_BTC = 0.0
    cr_PercentChangeBTC_BCHSV = 0.0
    cr_PercentChangeBTC_EOS = 0.0
    cr_PercentChangeBTC_XMR = 0.0
    cr_PercentChangeBTC_XEM = 0.0
    cr_PercentChangeBTC_XRP = 0.0
    cr_PercentChangeBTC_ZEC = 0.0
    cr_PercentChangeBTC_LSK = 0.0
    cr_PercentChangeBTC_REP = 0.0
    last_PercentChangeUSDC_BTC = 0.0
    last_PercentChangeBTC_BCHSV = 0.0
    last_PercentChangeBTC_EOS = 0.0
    last_PercentChangeBTC_XMR = 0.0
    last_PercentChangeBTC_XEM = 0.0
    last_PercentChangeBTC_XRP = 0.0
    last_PercentChangeBTC_ZEC = 0.0
    last_PercentChangeBTC_LSK = 0.0
    last_PercentChangeBTC_REP = 0.0
    last_PercentChangeBTC = 0.0
    last_PercentChangeUSDC = 0.0
    last_PercentChangeBCHSV = 0.0
    last_PercentChangeEOS = 0.0
    last_PercentChangeXMR = 0.0
    last_PercentChangeXEM = 0.0
    last_PercentChangeXRP = 0.0
    last_PercentChangeZEC = 0.0
    last_PercentChangeLSK = 0.0
    last_PercentChangeREP = 0.0
    lastPriceUSDCBTC = 0.0
    lastPriceBTCEOS = 0.0
    lastPriceBCHSVBTC = 0.0
    lastPriceXMRBTC = 0.0
    lastPriceXEMBTC = 0.0
    lastPriceXRPBTC = 0.0
    lastPriceZECBTC = 0.0
    lastPriceLSKBTC = 0.0
    lastPriceREPBTC = 0.0
    last_CloseUSDC = 0.0
    last_CloseBCHSV = 0.0
    last_CloseEOS = 0.0
    last_CloseXMR = 0.0
    last_CloseXEM = 0.0
    last_CloseXRP = 0.0
    last_CloseZEC = 0.0
    last_CloseLSK = 0.0
    last_CloseREP = 0.0
    cr_OpenUSDC = 0.0
    cr_OpenBCHSV = 0.0
    cr_OpenEOS = 0.0
    cr_OpenXMR = 0.0
    cr_OpenXEM = 0.0
    cr_OpenXRP = 0.0
    cr_OpenZEC = 0.0
    cr_OpenLSK = 0.0
    cr_OpenREP = 0.0
    last_OpenUSDC = 0.0
    last_OpenBCHSV = 0.0
    last_OpenEOS = 0.0
    last_OpenXMR = 0.0
    last_OpenXEM = 0.0
    last_OpenXRP = 0.0
    last_OpenZEC = 0.0
    last_OpenLSK = 0.0
    last_OpenREP = 0.0
    cr_VolumeUSDC = 0.0
    cr_VolumeBCHSV = 0.0
    cr_VolumeEOS = 0.0
    cr_VolumeXMR = 0.0
    cr_VolumeXEM = 0.0
    cr_VolumeXRP = 0.0
    cr_VolumeZEC = 0.0
    cr_VolumeLSK = 0.0
    cr_VolumeREP = 0.0
    last_VolumeUSDC = 0.0
    last_VolumeBCHSV = 0.0
    last_VolumeEOS = 0.0
    last_VolumeXMR = 0.0
    last_VolumeXEM = 0.0
    last_VolumeXRP = 0.0
    last_VolumeZEC = 0.0
    last_VolumeLSK = 0.0
    last_VolumeREP = 0.0
    cr_WeightedAverageUSDC = 0.0
    cr_WeightedAverageBCHSV = 0.0
    cr_WeightedAverageEOS = 0.0
    cr_WeightedAverageXMR = 0.0
    cr_WeightedAverageXEM = 0.0
    cr_WeightedAverageXRP = 0.0
    cr_WeightedAverageZEC = 0.0
    cr_WeightedAverageLSK = 0.0
    cr_WeightedAverageREP = 0.0
    last_WeightedAverageUSDC = 0.0
    last_WeightedAverageBCHSV = 0.0
    last_WeightedAverageEOS = 0.0
    last_WeightedAverageXMR = 0.0
    last_WeightedAverageXEM = 0.0
    last_WeightedAverageXRP = 0.0
    last_WeightedAverageZEC = 0.0
    last_WeightedAverageLSK = 0.0
    last_WeightedAverageREP = 0.0
    pre_PriceUSDCBTC = 0.0
    pre_PriceBTCBCHSV = 0.0
    pre_PriceBTCEOS = 0.0
    pre_PriceBTC_XMR = 0.0
    pre_PriceBTC_XEM = 0.0
    pre_PriceBTC_XRP = 0.0
    pre_PriceBTC_ZEC = 0.0
    pre_PriceBTC_LSK = 0.0
    pre_PriceBTC_REP = 0.0
    total_alt_btc = 0.0
#
    myInitBTC_Balance = getBTC_Balance()
    myInitUSDC_Balance = getUSDC_Balance()
    myInitALT_Balance = total_alt_btc
    gt = time.gmtime()
    lasttimehour = gt.tm_hour
    start_hour = ALTCOIN_FIX_CLOSE_LIMIT_HOUR - lasttimehour
    exp_jpy_rate = 0.0
#
#########################
### get My Balance
def dispAllMyBalance():
    global polopri
#
    global myHoldBTC_Balance
    global myHoldUSDC_Balance
    global myHoldBCHSV_BTC_Balance
    global myHoldEOS_BTC_Balance
    global myHoldXMR_BTC_Balance
    global myHoldXEM_BTC_Balance
    global myHoldXRP_BTC_Balance
    global myHoldZEC_BTC_Balance
    global myHoldLSK_BTC_Balance
    global myHoldREP_BTC_Balance
    global myInitBTC_Balance
    global myInitUSDC_Balance
    global myInitALT_Balance
    global lasttimehour
    global start_hour
    global day_close_flag
    global total_alt_btc
    global exp_jpy_rate
#
    day_close_flag = False
    CrBTC_Balance = getBTC_Balance()
    getBTCJPY_Price()
    CrUSDC_Balance = getUSDC_Balance()
    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
    gt = time.gmtime()
    current_timehour = gt.tm_hour
    if (current_timehour == 0):
        current_timehour = 24
    if (float(CrUSDC_Balance) > 0.0 and float(lastPriceUSDCBTC) > 0.0):
         total_btc = round((float(CrBTC_Balance) + float(CrUSDC_Balance / lastPriceUSDCBTC) + float(total_alt_btc)),4)
         Profit = round(float(total_btc) - (float(myInitBTC_Balance) + float(myInitUSDC_Balance / lastPriceUSDCBTC + float(myInitALT_Balance))),4)
    else:
         total_btc = round((float(CrBTC_Balance) + float(total_alt_btc)),4)
         Profit = round(float(total_btc) - (float(myInitBTC_Balance) + float(myInitALT_Balance)),4)    
    total_btc_to_jpy = round(float(total_btc) * float(exp_jpy_rate),0)
    if (current_timehour != lasttimehour):
        mes = "***  Poloniex Trading Bot(" + d + ") @Current Balance(Profit)=" + "{0:.8f}".format(Profit) + "BTC to rate JPY:" + "{:,}".format(total_btc_to_jpy) + "YEN ***"
        lineNotify(mes)
        lasttimehour = current_timehour
        if (start_hour + ALTCOIN_FIX_CLOSE_LIMIT_HOUR <= lasttimehour):
            day_close_flag = True
            start_hour = ALTCOIN_FIX_CLOSE_LIMIT_HOUR - lasttimehour
#
    balance = polopri.returnBalances()
    print("++++++++++++ Current My Balance Data +++++++++++++++")
#
    myHoldBTC_Balance = float(balance['BTC'])
    print('Current Balance of BTC      = {0:.8f}.'.format(myHoldBTC_Balance))
#
    myUSDC_Balance = float(format(balance['USDC']))
    print('Current Balance of USDC     = {0:.8f}.'.format(myUSDC_Balance))
#
    myHoldBCHSV_BTC_Balance = float(balance['BCHSV'])
    print('Current Balance of BCHSV    = {0:.8f}.'.format(myHoldBCHSV_BTC_Balance))
#
    myHoldEOS_BTC_Balance = float(balance['EOS'])
    print('Current Balance of EOS      = {0:.8f}.'.format(myHoldEOS_BTC_Balance))
#
    myHoldXMR_BTC_Balance = float(balance['XMR'])
    print('Current Balance of XMR      = {0:.8f}.'.format(myHoldXMR_BTC_Balance))
#
    myHoldXEM_BTC_Balance = float(balance['XEM'])
    print('Current Balance of XEM      = {0:.8f}.'.format(myHoldXEM_BTC_Balance))
#
    myHoldXRP_BTC_Balance = float(balance['XRP'])
    print('Current Balance of XRP      = {0:.8f}.'.format(myHoldXRP_BTC_Balance))
#
    myHoldZEC_BTC_Balance = float(balance['ZEC'])
    print('Current Balance of ZEC      = {0:.8f}.'.format(myHoldZEC_BTC_Balance))
#
    myHoldLSK_BTC_Balance = float(balance['LSK'])
    print('Current Balance of LSK      = {0:.8f}.'.format(myHoldZEC_BTC_Balance))
#
    myHoldREP_BTC_Balance = float(balance['REP'])
    print('Current Balance of REP      = {0:.8f}.'.format(myHoldREP_BTC_Balance))
    
    print("Holding Total BTC           = " + "{0:.4f}".format(total_btc))
    print("Current Profit BTC          = " + "{0:.4f}".format(Profit))
    print("Current TOTAL JPY(BTC RATE) = " + "{:,}".format(total_btc_to_jpy))
    logger.info("Holding Total BTC;" + "{0:.4f}".format(total_btc))
    logger.info("Current Profit BTC:" + "{0:.4f}".format(Profit))
    logger.info("Current TOTAL JPY(BTC RATE):" + "{:,}".format(total_btc_to_jpy))
    time.sleep(10)
#
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
######
def getBTCJPY_Price():
   global exp_jpy_rate
   jpy_price = 0.0
   try:
      price = json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc",params="300").text)["result"]
      #print(price)
      jpy_price = float("{}".format(price['300'][0][4]))
   except:
      pass
   exp_jpy_rate = jpy_price
#
#########
#
### get BTC Balance
def getBTC_Balance():
    global myBTC_Balance
    global polopri
#
    global myBTC_Balance
    try:
        balance = polopri.returnCompleteBalances()
        myBTC_Balance = float(format(balance['BTC']['available']))
    except:
        myBTC_Balance = 0.0
    print("My BTC Balance =" + str(myBTC_Balance))
    return(myBTC_Balance)
#
### get USDC_ Balance
def getUSDC_Balance():
    global myUSDC_Balance
    try:
        balance = polopri.returnCompleteBalances()
        myUSDC_Balance = float(format(balance['USDC']['available']))
    except:
        myUSDC_Balance = 0.0
    print("My USDC Balance =" + str(myUSDC_Balance))
    return(myBTC_Balance)
#
### get Balance of BTC(.....)
def getCoin_Balance_BTC():
    global polopri
#
    global myUSDCHoldBTC_Balance
    global myBCHSVHoldBTC_Balance
    global myEOSHoldBTC_Balance
    global myXMRHoldBTC_Balance
    global myXEMHoldBTC_Balance
    global myXRPHoldBTC_Balance
    global myZECHoldBTC_Balance
    global myLSKHoldBTC_Balance
    global myREPHoldBTC_Balance
    global total_alt_btc
#
    try:
        balance = polopri.returnCompleteBalances()
#
        myUSDCHoldBTC_Balance = float(format(balance['USDC']['btcValue']))
        myBCHSVHoldBTC_Balance = float(format(balance['BCHSV']['btcValue']))
        myEOSHoldBTC_Balance = float(format(balance['EOS']['btcValue']))
        myXMRHoldBTC_Balance = float(format(balance['XMR']['btcValue']))
        myXEMHoldBTC_Balance = float(format(balance['XEM']['btcValue']))
        myXRPHoldBTC_Balance = float(format(balance['XRP']['btcValue']))
        myZECHoldBTC_Balance = float(format(balance['ZEC']['btcValue']))
        myLSKHoldBTC_Balance = float(format(balance['LSK']['btcValue']))
        myREPHoldBTC_Balance = float(format(balance['REP']['btcValue']))
        total_alt_btc = myUSDCHoldBTC_Balance + myBCHSVHoldBTC_Balance + myEOSHoldBTC_Balance + myXMRHoldBTC_Balance\
         + myXEMHoldBTC_Balance + myXRPHoldBTC_Balance + myZECHoldBTC_Balance + myZECHoldBTC_Balance + myLSKHoldBTC_Balance + myREPHoldBTC_Balance
    except:
        myUSDCHoldBTC_Balance = 0.0
        myBCHSVHoldBTC_Balance = 0.0
        myEOSHoldBTC_Balance = 0.0
        myXMRHoldBTC_Balance = 0.0
        myXEMHoldBTC_Balance = 0.0
        myXRPHoldBTC_Balance = 0.0
        myZECHoldBTC_Balance = 0.0
        myLSKHoldBTC_Balance = 0.0
        myREPHoldBTC_Balance = 0.0
        total_alt_btc = 0.0
        pass
#
####################
def get_Coin_Holding_Balace():
    global myBTC_Balance
    global myUSDC_Balance
    global myBTC_EOS_Balance
    global myBCHSV_BTC_Balance
    global myXMR_BTC_Balance
    global myXEM_BTC_Balance
    global myXRP_BTC_Balance
    global myZEC_BTC_Balance
    global myLSK_BTC_Balance
    global myREP_BTC_Balance
#
    try:
        balance = polopri.returnBalances()
        myBTC_Balance = float(format(balance['BTC']))
        myUSDC_Balance = float(format(balance['USDC']))
        myBCHSV_BTC_Balance = float(format(balance['BCHSV']))
        myBTC_EOS_Balance = float(format(balance['EOS']))
        myXMR_BTC_Balance = float(format(balance['XMR']))
        myXEM_BTC_Balance = float(format(balance['XEM']))
        myXRP_BTC_Balance = float(format(balance['XRP']))
        myZEC_BTC_Balance = float(format(balance['ZEC']))
        myLSK_BTC_Balance = float(format(balance['LSK']))
        myREP_BTC_Balance = float(format(balance['REP']))
    except:
        myBTC_Balance = 0.0
        myUSDC_Balance= 0.0
        myBCHSV_BTC_Balance= 0.0
        myBTC_EOS_Balance= 0.0
        myXMR_BTC_Balance= 0.0
        myXEM_BTC_Balance= 0.0
        myXRP_BTC_Balance= 0.0
        myZEC_BTC_Balance= 0.0
        myLSK_BTC_Balance= 0.0
        myREP_BTC_Balance= 0.0
        pass
#
### get lastprice(for BTC.....)
def get_lastPrice():
#
    global lastPriceUSDCBTC
    global lastPriceBCHSVBTC
    global lastPriceEOSBTC
    global lastPriceXMRBTC
    global lastPriceXEMBTC
    global lastPriceXRPBTC
    global lastPriceZECBTC
    global lastPriceLSKBTC
    global lastPriceREPBTC
#
    try:
        tickData = polopub.returnTicker()
#
        lastPriceUSDCBTC = float(format(tickData['USDC_BTC']['last']))
#
        lastPriceBCHSVBTC = float(format(tickData['BTC_BCHSV']['last']))
        lastPriceEOSBTC = float(format(tickData['BTC_EOS']['last']))
        lastPriceXMRBTC = float(format(tickData['BTC_XMR']['last']))
        lastPriceXEMBTC = float(format(tickData['BTC_XEM']['last']))
        lastPriceXRPBTC = float(format(tickData['BTC_XRP']['last']))
        lastPriceZECBTC = float(format(tickData['BTC_ZEC']['last']))
        lastPriceLSKBTC = float(format(tickData['BTC_LSK']['last']))
        lastPriceREPBTC = float(format(tickData['BTC_REP']['last']))
    except:
        lastPriceUSDCBTC = 0.0
        lastPriceBCHSVBTC = 0.0
        lastPriceEOSBTC = 0.0
        lastPriceXMRBTC = 0.0
        lastPriceXEMBTC = 0.0
        lastPriceXRPBTC = 0.0
        lastPriceZECBTC = 0.0
        lastPriceLSKBTC = 0.0
        lastPriceREPBTC = 0.0
        pass

### get Ask is for Buy Order
def getUSDC_Ask():
    USDCAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        USDCAsk = format(tickData['USDC_BTC']['lowestAsk'])
    except:
        pass
    return(float(USDCAsk))
#
def getBCHSV_Ask():
    BCHSVAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        BCHSVAsk = format(tickData['BTC_BCHSV']['lowestAsk'])
    except:
        pass
    return(float(BCHSVAsk))
#
def getEOS_Ask():
    BTCAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        BTCAsk = format(tickData['BTC_EOS']['lowestAsk'])
    except:
        pass
    return(float(BTCAsk))
#
def getXMR_Ask():
    XMRAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        XMRAsk = format(tickData['BTC_XMR']['lowestAsk'])
    except:
        pass
    return(float(XMRAsk))
#
def getXEM_Ask():
    XEMAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        XEMAsk = format(tickData['BTC_XEM']['lowestAsk'])
    except:
        pass
    return(float(XEMAsk))
#
def getXRP_Ask():
    XRPAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        XRPAsk = format(tickData['BTC_XRP']['lowestAsk'])
    except:
        pass
    return(float(XRPAsk))
#
def getZEC_Ask():
    ZECAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        ZECAsk = format(tickData['BTC_ZEC']['lowestAsk'])
    except:
        pass
    return(float(ZECAsk))
#
def getLSK_Ask():
    LSKAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        LSKAsk = format(tickData['BTC_LSK']['lowestAsk'])
    except:
        pass
    return(float(LSKAsk))
#
def getREP_Ask():
    REPAsk = 0.0
    try:
        tickData = polopub.returnTicker()
        REPAsk = format(tickData['BTC_REP']['lowestAsk'])
    except:
        pass
    return(float(REPAsk))
#
#########
### get Bid is for Sell Order
def getUSDC_Bid():
    USDCBid = 0.0
    try:
        tickData = polopub.returnTicker()
        USDCBid = format(tickData['USDC_BTC']['highestBid'])
    except:
        pass
    return(float(USDCBid))
#
def getBCHSV_Bid():
    BCHSVBid = 0.0
    try:
        tickData = polopub.returnTicker()
        BCHSVBid = format(tickData['BTC_BCHSV']['highestBid'])
    except:
        pass
    return(float(BCHSVBid))
#
def getEOS_Bid():
    EOSBid = 0.0
    try:
        tickData = polopub.returnTicker()
        EOSBid = format(tickData['BTC_EOS']['highestBid'])
    except:
        pass
    return(float(EOSBid))
#
def getXMR_Bid():
    XMRBid = 0.0
    try:
        tickData = polopub.returnTicker()
        XMRBid = format(tickData['BTC_XMR']['highestBid'])
    except:
        pass
    return(float(XMRBid))
#
def getXEM_Bid():
    XEMBid = 0.0
    try:
        tickData = polopub.returnTicker()
        XEMBid = format(tickData['BTC_XEM']['highestBid'])
    except:
        pass
    return(float(XEMBid))
#
def getXRP_Bid():
    XRPBid = 0.0
    try:
        tickData = polopub.returnTicker()
        XRPBid = format(tickData['BTC_XRP']['highestBid'])
    except:
        pass
    return(float(XRPBid))
#
def getZEC_Bid():
    ZECBid = 0.0
    try:
        tickData = polopub.returnTicker()
        ZECBid = format(tickData['BTC_ZEC']['highestBid'])
    except:
        pass
    return(float(ZECBid))
#
def getLSK_Bid():
    LSKBid = 0.0
    try:
        tickData = polopub.returnTicker()
        LSKBid = format(tickData['BTC_LSK']['highestBid'])
    except:
        pass
    return(float(LSKBid))
#
def getREP_Bid():
    REPBid = 0.0
    try:
        tickData = polopub.returnTicker()
        REPBid = format(tickData['BTC_REP']['highestBid'])
    except:
        pass
    return(float(REPBid))
#
###############
### BTC Info price on today during days(USDC)
def getBTC_Info_Price():
    global cr_BTC_Average
    global last_BTC_Average
    global cr_HighestUSDC
    global cr_LowestUSDC
    global cr_OpenUSDC
    global cr_CloseUSDC
    global cr_VolumeUSDC
    global cr_OpenUSDC
    global last_OpenUSDC
    global last_CloseUSDC
    global last_VolumeUSDC
    global cr_WeightedAverageUSDC
    global last_WeightedAverageUSDC
#
    ret = False
    try:
        chartUSDC_BTC = polopub.returnChartData('USDC_BTC', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
        ret = True
    except:
        pass
    if (ret):
        cr_HighestUSDC = float(chartUSDC_BTC[-1]['high'])
        cr_LowestUSDC = float(chartUSDC_BTC[-1]['low'])
        #
        cr_OpenUSDC = float(chartUSDC_BTC[-1]['open'])
        cr_CloseUSDC = float(chartUSDC_BTC[-1]['close'])
        cr_VolumeUSDC = float(chartUSDC_BTC[-1]['volume'])
        cr_BTC_Average = chartUSDC_BTC[-1]['weightedAverage']
        cr_WeightedAverageUSDC = chartUSDC_BTC[-1]['weightedAverage']
        #
        last_OpenUSDC = float(chartUSDC_BTC[-2]['open'])
        last_CloseUSDC = float(chartUSDC_BTC[-2]['close'])
        last_VolumeUSDC = float(chartUSDC_BTC[-2]['volume'])
        last_BTC_Average = chartUSDC_BTC[-2]['weightedAverage']
        last_WeightedAverageUSDC = chartUSDC_BTC[-2]['weightedAverage']
    return ret
#
### BCHSV Info_price on today during days(BTC)
def getBCHSV_Info_Price():
    global cr_HighestBCHSV
    global cr_LowestBCHSV
    global cr_OpenBCHSV
    global cr_CloseBCHSV
    global cr_VolumeBCHSV
    global cr_OpenBCHSV
    global last_OpenBCHSV
    global last_CloseBCHSV
    global last_VolumeBCHSV
    global cr_WeightedAverageBCHSV
    global last_WeightedAverageBCHSV
#
    ret = False
    try:
        chartBCHSV_BTC = polopub.returnChartData('BTC_BCHSV', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
        ret = True
    except:
        pass
    if (ret):
        cr_HighestBCHSV = float(chartBCHSV_BTC[-1]['high'])
        cr_LowestBCHSV = float(chartBCHSV_BTC[-1]['low'])
        #
        cr_OpenBCHSV = float(chartBCHSV_BTC[-1]['open'])
        cr_CloseBCHSV = float(chartBCHSV_BTC[-1]['close'])
        cr_VolumeBCHSV = float(chartBCHSV_BTC[-1]['volume'])
        cr_WeightedAverageBCHSV = chartBCHSV_BTC[-1]['weightedAverage']
        #
        last_OpenBCHSV = float(chartBCHSV_BTC[-2]['open'])
        last_CloseBCHSV = float(chartBCHSV_BTC[-2]['close'])
        last_VolumeBCHSV = float(chartBCHSV_BTC[-2]['volume'])
        last_WeightedAverageBCHSV = chartBCHSV_BTC[-2]['weightedAverage']
    return ret
#
### EOS Info price on today during days
def getEOS_Info_Price():
#
    global cr_HighestEOS
    global cr_LowestEOS
    global cr_OpenEOS
    global cr_CloseEOS
    global cr_VolumeEOS
    global cr_OpenEOS
    global last_OpenEOS
    global last_CloseEOS
    global last_VolumeEOS
    global cr_WeightedAverageEOS
    global last_WeightedAverageEOS
#
    ret = False
    try:
        chartEOS_BTC = polopub.returnChartData('BTC_EOS', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestEOS = float(chartEOS_BTC[-1]['high'])
        cr_LowestEOS = float(chartEOS_BTC[-1]['low'])
        #
        cr_OpenEOS = float(chartEOS_BTC[-1]['open'])
        cr_CloseEOS = float(chartEOS_BTC[-1]['close'])
        cr_VolumeEOS = float(chartEOS_BTC[-1]['volume'])
        cr_WeightedAverageEOS = chartEOS_BTC[-1]['weightedAverage']
        #
        last_OpenEOS = float(chartEOS_BTC[-2]['open'])
        last_CloseEOS = float(chartEOS_BTC[-2]['close'])
        last_VolumeEOS = float(chartEOS_BTC[-2]['volume'])
        last_WeightedAverageEOS = chartEOS_BTC[-2]['weightedAverage']
    return ret
#
### XMR Info price on today during days
def getXMR_Info_Price():
#
    global cr_HighesXMR
    global cr_LowesXMR
    global cr_OpenUSDC
    global cr_CloseUSDC
    global cr_VolumeUSDC
    global cr_OpenUSDC
    global last_OpenUSDC
    global last_CloseUSDC
    global last_VolumeUSDC
    global cr_WeightedAverageUSDC
    global last_WeightedAverageUSDC
    ret = False
    try:
        chartXMR_BTC = polopub.returnChartData('BTC_XMR', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestXMR = float(chartXMR_BTC[-1]['high'])
        cr_LowestXMR = float(chartXMR_BTC[-1]['low'])
        #
        cr_OpenXMR = float(chartXMR_BTC[-1]['open'])
        cr_CloseXMR = float(chartXMR_BTC[-1]['close'])
        cr_VolumeXMR = float(chartXMR_BTC[-1]['volume'])
        cr_WeightedAverageXMR = chartXMR_BTC[-1]['weightedAverage']
        #
        last_OpenXMR = float(chartXMR_BTC[-2]['open'])
        last_CloseXMR = float(chartXMR_BTC[-2]['close'])
        last_VolumeXMR = float(chartXMR_BTC[-2]['volume'])
        last_WeightedAverageXMR = chartXMR_BTC[-2]['weightedAverage']
    return ret
#
### XEM Info price on today during days
def getXEM_Info_Price():
#
    global cr_HighestXEM
    global cr_LowestXEM
    global cr_OpenXEM
    global cr_CloseXEM
    global cr_VolumeXEM
    global cr_OpenXEM
    global last_OpenXEM
    global last_CloseXEM
    global last_VolumeXEM
    global cr_WeightedAverageXEM
    global last_WeightedAverageXEM
    ret = False
    try:
        chartXEM_BTC = polopub.returnChartData('BTC_XEM', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestXEM = float(chartXEM_BTC[-1]['high'])
        cr_LowestXEM = float(chartXEM_BTC[-1]['low'])
        #
        cr_OpenXEM = float(chartXEM_BTC[-1]['open'])
        cr_CloseXEM = float(chartXEM_BTC[-1]['close'])
        cr_VolumeXEM = float(chartXEM_BTC[-1]['volume'])
        cr_WeightedAverageXEM = chartXEM_BTC[-1]['weightedAverage']
        #
        last_OpenXEM = float(chartXEM_BTC[-2]['open'])
        last_CloseXEM = float(chartXEM_BTC[-2]['close'])
        last_VolumeXEM = float(chartXEM_BTC[-2]['volume'])
        last_WeightedAverageXEM = chartXEM_BTC[-2]['weightedAverage']
    return ret
#
### XRP Info price on today during days
def getXRP_Info_Price():
#
    global cr_HighestXRP
    global cr_LowestXRP
    global cr_OpenXRP
    global cr_CloseXRP
    global cr_VolumeXRP
    global cr_OpenXRP
    global last_OpenXRP
    global last_CloseXRP
    global last_VolumeXRP
    global cr_WeightedAverageXRP
    global last_WeightedAverageXRP
    ret = False
    try:
        chartXRP_BTC = polopub.returnChartData('BTC_XRP', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestXRP = float(chartXRP_BTC[-1]['high'])
        cr_LowestXRP = float(chartXRP_BTC[-1]['low'])
        #
        cr_OpenXRP = float(chartXRP_BTC[-1]['open'])
        cr_CloseXRP = float(chartXRP_BTC[-1]['close'])
        cr_VolumeXRP = float(chartXRP_BTC[-1]['volume'])
        cr_WeightedAverageXRP = chartXRP_BTC[-1]['weightedAverage']
        #
        last_OpenXRP = float(chartXRP_BTC[-2]['open'])
        last_CloseXRP = float(chartXRP_BTC[-2]['close'])
        last_VolumeXRP = float(chartXRP_BTC[-2]['volume'])
        last_WeightedAverageXRP = chartXRP_BTC[-2]['weightedAverage']
    return ret
#
### ZEC Info price on today during days
def getZEC_Info_Price():
#
    global cr_HighestZEC
    global cr_LowestZEC
    global cr_OpenZEC
    global cr_CloseZEC
    global cr_VolumeZEC
    global cr_OpenZEC
    global last_OpenZEC
    global last_CloseZEC
    global last_VolumeZEC
    global cr_WeightedAverageZEC
    global last_WeightedAverageZEC
    ret = False
    try:
        chartZEC_BTC = polopub.returnChartData('BTC_ZEC', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestZEC = float(chartZEC_BTC[-1]['high'])
        cr_LowestZEC = float(chartZEC_BTC[-1]['low'])
        #
        cr_OpenZEC = float(chartZEC_BTC[-1]['open'])
        cr_CloseZEC = float(chartZEC_BTC[-1]['close'])
        cr_VolumeZEC = float(chartZEC_BTC[-1]['volume'])
        cr_WeightedAverageZEC = chartZEC_BTC[-1]['weightedAverage']
        #
        last_OpenZEC = float(chartZEC_BTC[-2]['open'])
        last_CloseZEC = float(chartZEC_BTC[-2]['close'])
        last_VolumeZEC = float(chartZEC_BTC[-2]['volume'])
        last_WeightedAverageZEC = chartZEC_BTC[-2]['weightedAverage']
    return ret
#
### LSK Info price on today during days
def getLSK_Info_Price():
#
    global cr_HighestLSK
    global cr_LowestLSK
    global cr_OpenLSK
    global cr_CloseLSK
    global cr_VolumeLSK
    global cr_OpenLSK
    global last_OpenLSK
    global last_CloseLSK
    global last_VolumeLSK
    global cr_WeightedAverageLSK
    global last_WeightedAverageLSK
    ret = False
    try:
        chartLSK_BTC = polopub.returnChartData('BTC_LSK', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestLSK = float(chartLSK_BTC[-1]['high'])
        cr_LowestLSK = float(chartLSK_BTC[-1]['low'])
        #
        cr_OpenLSK = float(chartLSK_BTC[-1]['open'])
        cr_CloseLSK = float(chartLSK_BTC[-1]['close'])
        cr_VolumeLSK = float(chartLSK_BTC[-1]['volume'])
        cr_WeightedAverageLSK = chartLSK_BTC[-1]['weightedAverage']
        #
        last_OpenLSK = float(chartLSK_BTC[-2]['open'])
        last_CloseLSK = float(chartLSK_BTC[-2]['close'])
        last_VolumeLSK = float(chartLSK_BTC[-2]['volume'])
        last_WeightedAverageLSK = chartLSK_BTC[-2]['weightedAverage']
    return ret
#
### REP Info price on today during days
def getREP_Info_Price():
#
    global cr_HighestREP
    global cr_LowestREP
    global cr_OpenREP
    global cr_CloseREP
    global cr_VolumeREP
    global cr_OpenREP
    global last_OpenREP
    global last_CloseREP
    global last_VolumeREP
    global cr_WeightedAverageREP
    global last_WeightedAverageREP
    ret = False
    try:
        chartREP_BTC = polopub.returnChartData('BTC_REP', period=300, start=time.time()-polopub.DAY, end=time.time())
        time.sleep(5)
    except:
        pass
    if (ret):
        cr_HighestREP = float(chartREP_BTC[-1]['high'])
        cr_LowestREP = float(chartREP_BTC[-1]['low'])
        #
        cr_OpenREP = float(chartREP_BTC[-1]['open'])
        cr_CloseREP = float(chartREP_BTC[-1]['close'])
        cr_VolumeREP = float(chartREP_BTC[-1]['volume'])
        cr_WeightedAverageREP = chartREP_BTC[-1]['weightedAverage']
        #
        last_OpenREP = float(chartREP_BTC[-2]['open'])
        last_CloseREP = float(chartREP_BTC[-2]['close'])
        last_VolumeREP = float(chartREP_BTC[-2]['volume'])
        last_WeightedAverageREP = chartREP_BTC[-2]['weightedAverage']
    return ret
#
####################
#
def getPercentChangeCoin():
    global cr_PercentChangeUSDC
    global cr_PercentChangeEOS
    global cr_PercentChangeBCHSV
    global cr_PercentChangeXMR
    global cr_PercentChangeXEM
    global cr_PercentChangeXRP
    global cr_PercentChangeZEC
    global cr_PercentChangeLSK
    global cr_PercentChangeREP
#
    tickData = polopub.returnTicker()
#
    ### BTC percentChange
    cr_PercentChangeUSDC = float(format(tickData['USDC_BTC']['percentChange']))
##For BTC
    ### BCHSV percentChange
    cr_PercentChangeBCHSV = float(format(tickData['BTC_BCHSV']['percentChange']))
    ### EOS percentChange
    cr_PercentChangeEOS = float(format(tickData['BTC_EOS']['percentChange']))
    ### XMR percentChange
    cr_PercentChangeXMR = float(format(tickData['BTC_XMR']['percentChange']))
    ### XEM percentChange
    cr_PercentChangeXEM = float(format(tickData['BTC_XEM']['percentChange']))
    ### XRP percentChange
    cr_PercentChangeXRP = float(format(tickData['BTC_XRP']['percentChange']))
    ### ZEC percentChange
    cr_PercentChangeZEC = float(format(tickData['BTC_ZEC']['percentChange']))
    ### LSK percentChange
    cr_PercentChangeLSK = float(format(tickData['BTC_LSK']['percentChange']))
    ### REP percentChange
    cr_PercentChangeREP = float(format(tickData['BTC_REP']['percentChange']))
#######################################################################################
#######################################################################################
#                              MAIN LOGIC                                             #
#######################################################################################
def order_logic():
#
    global myBTC_Balance
    global myUSDC_Balance
    global myBTC_USDC_Balance
    global myBTC_EOS_Balance
    global myBCHSV_BTC_Balance
    global myXMR_BTC_Balance
    global myXEM_BTC_Balance
    global myXRP_BTC_Balance
    global myZEC_BTC_Balance
    global myBTC_USDC_Balance
    global myBCHSV_BTC_Balance
    global myXMR_BTC_Balance
    global myXEM_BTC_Balance
    global myXRP_BTC_Balance
    global myZEC_BTC_Balance
    global myHoldBTC_EOS_Balance
    global myHoldBCHSV_BTC_Balance
    global myHoldXMR_BTC_Balance
    global myHoldXEM_BTC_Balance
    global myHoldXRP_BTC_Balance
    global myHoldZEC_BTC_Balance
    global myHoldBCHSV_BTC_Balance
    global myHoldXMR_BTC_Balance
    global myHoldXEM_BTC_Balance
    global myHoldXRP_BTC_Balance
    global myHoldZEC_BTC_Balance
    global cr_BTC_Average
    global cr_USDC_Average
    global last_BTC_Average
    global last_USDC_Average
    global cr_PercentChangeBTC
    global cr_PercentChangeUSDC
    global cr_PercentChangeBCHSV
    global cr_PercentChangeEOS
    global cr_PercentChangeXMR
    global cr_PercentChangeXEM
    global cr_PercentChangeXRP
    global cr_PercentChangeZEC
    global cr_PercentChangeLSK
    global cr_PercentChangeREP
    global last_PercentChangeBTC
    global last_PercentChangeUSDC
    global last_PercentChangeBCHSV
    global last_PercentChangeEOS
    global last_PercentChangeXMR
    global last_PercentChangeXEM
    global last_PercentChangeXRP
    global last_PercentChangeZEC
    global last_PercentChangeLSK
    global last_PercentChangeREP
    global cr_HighestUSDC
    global cr_LowestUSDC
    global cr_HighestBCHSV
    global cr_LowestBCHSV
    global cr_HighestEOS
    global cr_LowestEOS
    global cr_HighestXMR
    global cr_LowestXMR
    global cr_HighestXEM
    global cr_LowestXEM
    global cr_HighestXRP
    global cr_LowestXRP
    global cr_HighestZEC
    global cr_LowestZEC
    global cr_HighestLSK
    global cr_LowestLSK
    global cr_HighestREP
    global cr_LowestREP
    global lastPriceUSDCBTC
    global lastPriceBCHSVBTC
    global lastPriceEOSBTC
    global lastPriceXMRBTC
    global lastPriceXEMBTC
    global lastPriceXRPBTC
    global lastPriceZECBTC
    global lastPriceLSKBTC
    global lastPriceREPBTC
    global pre_PriceUSDCBTC
    global pre_PriceBCHSVBTC
    global pre_PriceEOSBTC
    global pre_PriceXMRBTC
    global pre_PriceXEMBTC
    global pre_PriceXRPBTC
    global pre_PriceZECBTC
    global pre_PriceLSKBTC
    global pre_PriceREPBTC
    global cr_CloseUSDC
    global cr_CloseBCHSV
    global cr_CloseEOS
    global cr_CloseXMR
    global cr_CloseXEM
    global cr_CloseXRP
    global cr_CloseZEC
    global cr_CloseLSK
    global cr_CloseREP
    global last_CloseUSDC
    global last_CloseBCHSV
    global last_CloseEOS
    global last_CloseXMR
    global last_CloseXEM
    global last_CloseXRP
    global last_CloseZEC
    global last_CloseLSK
    global last_CloseREP
    global cr_OpenUSDC
    global cr_OpenBCHSV
    global cr_OpenEOS
    global cr_OpenXMR
    global cr_OpenXEM
    global cr_OpenXRP
    global cr_OpenZEC
    global cr_OpenLSK
    global cr_OpenREP
    global last_OpenUSDC
    global last_OpenBCHSV
    global last_OpenEOS
    global last_OpenXMR
    global last_OpenXEM
    global last_OpenXRP
    global last_OpenZEC
    global last_OpenLSK
    global last_OpenREP
    global cr_VolumeUSDC
    global cr_VolumeBCHSV
    global cr_VolumeEOS
    global cr_VolumeXMR
    global cr_VolumeXEM
    global cr_VolumeXRP
    global cr_VolumeZEC
    global cr_VolumeLSK
    global cr_VolumeREP
    global last_VolumeUSDC
    global last_VolumeBCHSV
    global last_VolumeEOS
    global last_VolumeXMR
    global last_VolumeXEM
    global last_VolumeXRP
    global last_VolumeZEC
    global last_VolumeLSK
    global last_VolumeREP
    global cr_WeightedAverageUSDC
    global cr_WeightedAverageBCHSV
    global cr_WeightedAverageEOS
    global cr_WeightedAverageXMR
    global cr_WeightedAverageXEM
    global cr_WeightedAverageXRP
    global cr_WeightedAverageZEC
    global cr_WeightedAverageLSK
    global cr_WeightedAverageREP
    global last_WeightedAverageUSDC
    global last_WeightedAverageBCHSV
    global last_WeightedAverageEOS
    global last_WeightedAverageXMR
    global last_WeightedAverageXEM
    global last_WeightedAverageXRP
    global last_WeightedAverageZEC
    global last_WeightedAverageLSK
    global last_WeightedAverageREP
    global day_close_flag
#
    dispAllMyBalance()
#
    print("********* order_logic *********")
#####
# BTC,USDC,BCHSV,XMR,XEM,ZEC,LSK,REP Balance of BTC
    getCoin_Balance_BTC()
    get_Coin_Holding_Balace()
#####
# BTC(USDC),USDC(BTC),BCHSV(BTC),EOS(BTC),XMR(BTC),XEM(BTC),ZEC(BTC),LSK(BTC),REP(BTC) LastPrice
    get_lastPrice()
#
######
# BTC(USDC),BCHSV(BTC),XMR(BTC),XEM(BTC),XRP(BTC),ZEC(BTC), LSK(BTC), REP(BTC) PercentChange
    getPercentChangeCoin()
#####
    USDC_order="NONE"
    BCHSV_order = "NONE"
    EOS_order = "NONE"
    XMR_order="NONE"
    XEM_order="NONE"
    XRP_order = "NONE"
    ZEC_order="NONE"
    LSK_order="NONE"
    REP_order="NONE"
#
    # BTC_USDC Balance
    time.sleep(1.0)
    BTC_Balance = getBTC_Balance()
    time.sleep(1.0)
    USDC_Balance = getUSDC_Balance()
    ###
### Dummy Not Used BTC_order_sell_amount(USDC_order_buy_amount USDC_BTC BUY Means BTC BUY)
    if(float(USDC_Balance)>0.0):
        BTC_order_sell_amount = round(float(USDC_Balance / lastPriceUSDCBTC * 0.95),4)
        USDC_order_buy_amount = round(float(USDC_Balance * 0.75),4)
        #if (BTC_Balance - USDC_order_sell_amount * lastPriceUSDCBTC < KEEP_BTC):
        #   while (BTC_Balance - USDC_order_sell_amount * lastPriceUSDCBTC < KEEP_BTC):
        #       USDC_order_sell_amount = USDC_order_sell_amount - KEEP_BTC
    else:
        BTC_order_buy_amount = 0.0
        USDC_order_buy_amount = 0.0
    #
### Dummy Not Used BTC_order_buy_amount(USDC_order_sell_amount USDC_BTC SELL Means BTC SELL)
    if(float(BTC_Balance)>0.0):
        BTC_order_buy_amount = round(float(BTC_Balance / lastPriceUSDCBTC * 0.95),4)
        USDC_order_sell_amount = round(float(BTC_Balance * 0.75) ,4)
        if (BTC_Balance - USDC_order_sell_amount * lastPriceUSDCBTC < KEEP_BTC):
            while (BTC_Balance - USDC_order_sell_amount * lastPriceUSDCBTC < KEEP_BTC):
                USDC_order_sell_amount = USDC_order_sell_amount - KEEP_BTC
    else:
        USDC_order_sell_amount = 0.0
        BTC_order_sell_amount = 0.0
    #
    print("----------------------------------------")
    print("BTC_Balance            =" + str(BTC_Balance))
    print("USDC_Balance           =" + str(USDC_Balance))
    print("BTC_order_buy_amount   =" + str(USDC_order_buy_amount))
    #print("USDC_order_buy_amount  =" + str(USDC_order_buy_amount))
    print("BTC_order_sell_amount  =" + str(USDC_order_sell_amount))
    #print("USDC_order_sell_amount=" + str(USDC_order_sell_amount))
    print("----------------------------------------")
#
#
    if(day_close_flag):
        BCHSV_order_sell_amount = round(float(myBCHSVHoldBTC_Balance * 0.95),4)
    else:
        BCHSV_order_buy_amount = round(float((BTC_Balance -KEEP_BTC) / lastPriceBCHSVBTC),4)
        BCHSV_order_sell_amount = round(float(myBCHSVHoldBTC_Balance * 0.75),4)
    print("BCHSV_BTC_order_buy_amount=" + str(BCHSV_order_buy_amount))
    print("BCHSV_BTC_order_sell_amount=" + str(BCHSV_order_sell_amount))
    
#
    if(day_close_flag):
        EOS_order_sell_amount = round(float(myEOSHoldBTC_Balance * 0.95), 4)
    else:
        EOS_order_buy_amount = round(float((BTC_Balance -KEEP_BTC) / lastPriceEOSBTC),4)
        EOS_order_sell_amount = round(float(myEOSHoldBTC_Balance * 0.75),4)
    print("EOS_BTC_order_buy_amount=" + str(EOS_order_buy_amount))
    print("EOS_BTC_order_sell_amount=" + str(EOS_order_sell_amount))
#
    if(day_close_flag):
        XMR_order_sell_amount = round(float(myXMRHoldBTC_Balance * 0.95) ,4)
    else:
        XMR_order_buy_amount = round(float((BTC_Balance -KEEP_BTC) / lastPriceXMRBTC),4)
        XMR_order_sell_amount = round(float(myXMRHoldBTC_Balance * 0.75),4)
    print("XMR_BTC_order_buy_amount=" + str(XMR_order_buy_amount))
    print("XMR_BTC_order_sell_amount=" + str(XMR_order_sell_amount))
#
    if(day_close_flag):
        XEM_order_sell_amount = round(float(myXEMHoldBTC_Balance * 0.95) ,4)
    else:
        XEM_order_buy_amount = round(float((BTC_Balance -KEEP_BTC) / lastPriceXEMBTC),4)
        XEM_order_sell_amount = round(float(myXEMHoldBTC_Balance * 0.75),4)
    print("XEM_BTC_order_buy_amount=" + str(XEM_order_buy_amount))
    print("XEM_BTC_order_sell_amount=" + str(XEM_order_sell_amount))
#
    if(day_close_flag):
        XRP_order_sell_amount = round(float(myXRPHoldBTC_Balance * 0.95), 4)
    else:
        XRP_order_buy_amount = round(float((BTC_Balance - KEEP_BTC) / lastPriceXRPBTC),4)
        XRP_order_sell_amount = round(float(myXRPHoldBTC_Balance * 0.75),4)
    print("XRP_BTC_order_buy_amount=" + str(XRP_order_buy_amount))
    print("XRP_BTC_order_sell_amount=" + str(XRP_order_sell_amount))
#
    if(day_close_flag):
        ZEC_order_sell_amount = round(float(myZECHoldBTC_Balance * 0.95) ,4)
    else:
        ZEC_order_buy_amount = round(float((BTC_Balance - KEEP_BTC) / lastPriceZECBTC),4)
        ZEC_order_sell_amount = round(float(myZECHoldBTC_Balance + 0.75),4)
    print("ZEC_BTC_order_buy_amount=" + str(ZEC_order_buy_amount))
    print("ZEC_BTC_order_sell_amount=" + str(ZEC_order_sell_amount))
#
    if(day_close_flag):
        LSK_order_sell_amount = round(float(myLSKHoldBTC_Balance * 0.75) ,4)
    else:
        LSK_order_buy_amount = round(float((BTC_Balance -KEEP_BTC) / lastPriceLSKBTC),4)
        LSK_order_sell_amount = round(float(myLSKHoldBTC_Balance  * 0.75),4)
    print("LSK_BTC_order_buy_amount=" + str(LSK_order_buy_amount))
    print("LSK_BTC_order_sell_amount=" + str(LSK_order_sell_amount))
##
    if(day_close_flag):
        REP_order_sell_amount = round(float(myREPHoldBTC_Balance * 0.95) ,4)
    else:
        REP_order_buy_amount = round(float((BTC_Balance - KEEP_BTC) / lastPriceREPBTC),4)
        REP_order_sell_amount = round(float(myREPHoldBTC_Balance  * 0.75),4)
    print("REP_BTC_order_buy_amount=" + str(REP_order_buy_amount))
    print("REP_BTC_order_sell_amount=" + str(REP_order_sell_amount))
#
    print("----------------------------------------")
##########################################
########## check USDC BUY/SELL ###########
    print("*** Checking USDC/BTC Order Signal ***")
    if(getBTC_Info_Price()):
        if(USDC_order == "NONE"):
            ## print("**** USDC Buy Checking 1 ****")
            if((cr_LowestUSDC > lastPriceUSDCBTC)\
            or (cr_WeightedAverageUSDC > last_WeightedAverageUSDC and last_CloseUSDC < cr_WeightedAverageUSDC and cr_CloseUSDC > last_OpenUSDC)\
            and (cr_VolumeUSDC > last_VolumeUSDC * 1.25)\
            and (pre_PriceUSDCBTC < lastPriceUSDCBTC)\
            and ((cr_PercentChangeUSDC - last_PercentChangeUSDC) > CHANGE_PERCENT_RATE)):
                if(USDC_order_buy_amount > MIN_USDC_LOT and BTC_order_sell_amount > MIN_BTC_LOT):
                    USDC_order = "BUY"
                    print("USDC_BTC_BUY" + "@AMOUNT=" + str(USDC_order_buy_amount))
        if(USDC_order == "NONE"):
            ## print("**** USDC Sell Checking 1 ****")
            if((cr_HighestUSDC <  lastPriceUSDCBTC)\
            or (cr_WeightedAverageUSDC < last_WeightedAverageUSDC and last_CloseUSDC > cr_WeightedAverageUSDC and cr_CloseUSDC < last_OpenUSDC)\
            and (cr_VolumeUSDC < last_VolumeUSDC)\
            and (pre_PriceUSDCBTC > lastPriceUSDCBTC)\
            and ((last_PercentChangeUSDC - cr_PercentChangeUSDC) > CHANGE_PERCENT_RATE)):
                if(USDC_order_sell_amount > MIN_USDC_LOT and BTC_order_buy_amount > MIN_BTC_LOT):
                    USDC_order = "SELL"
                    print("USDC_BTC_SELL" + "@AMOUNT=" + str(USDC_order_sell_amount))
#
######################################### ALTCOIN ..............
########### check BCHSV BUY/SELL
    print("*** Checking BCHSV/BTC Order Signal ***")
    if(getBCHSV_Info_Price()):
        if(BCHSV_order == "NONE" and USDC_order == "NONE"):
        ## print("**** BCHSV Buy Checking 1 ****")
            if((cr_LowestBCHSV > lastPriceBCHSVBTC)\
            or (cr_WeightedAverageBCHSV > last_WeightedAverageBCHSV and last_CloseBCHSV < cr_WeightedAverageBCHSV and cr_CloseBCHSV > last_OpenBCHSV)\
            and (cr_VolumeBCHSV > last_VolumeBCHSV * 1.25)\
            and (pre_PriceBCHSVBTC < lastPriceBCHSVBTC)\
            and ((cr_PercentChangeBCHSV - last_PercentChangeBCHSV) > CHANGE_PERCENT_RATE)):
                if(BCHSV_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    BCHSV_order = "BUY"
                    print("BCHSV_BTC_BUY" + "@AMOUNT=" + str(BCHSV_order_buy_amount))
            if(BCHSV_order == "NONE"):
            ## print("**** BCHSV Sell Checking 1 ****")
                if((cr_HighestBCHSV <  lastPriceBCHSVBTC)\
                or (cr_WeightedAverageBCHSV < last_WeightedAverageBCHSV and last_CloseBCHSV > cr_WeightedAverageBCHSV and cr_CloseBCHSV < last_OpenBCHSV)\
                and (cr_VolumeBCHSV < last_VolumeBCHSV)\
                and (pre_PriceBCHSVBTC > lastPriceBCHSVBTC)\
                and ((last_PercentChangeBCHSV - cr_PercentChangeBCHSV) > CHANGE_PERCENT_RATE)):
                    if(BCHSV_order_sell_amount > MIN_ALT_LOT):
                        BCHSV_order = "SELL"
                        print("BCHSV_BTC_SELL" + "@AMOUNT=" + str(BCHSV_order_sell_amount))
########### chack EOS BUY/SELL
    print("*** Checking EOS/BTC Order Signal ***")
    if(getEOS_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and USDC_order == "NONE"):
        ## print("**** EOS Buy Checking 1 ****")
            if((cr_LowestEOS  >  lastPriceEOSBTC)\
            or (cr_WeightedAverageEOS > last_WeightedAverageEOS and last_CloseEOS < cr_WeightedAverageEOS and cr_CloseEOS > last_OpenEOS)\
            and (cr_VolumeEOS > last_VolumeEOS * 1.25)\
            and (pre_PriceEOSBTC < lastPriceEOSBTC)\
            and ((cr_PercentChangeEOS - last_PercentChangeEOS) > CHANGE_PERCENT_RATE)):
                if(EOS_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    EOS_order = "BUY"
                    print("EOS_BTC_BUY" + "@AMOUNT=" + str(EOS_order_buy_amount))
            if(EOS_order == "NONE"):
            ## print("**** EOS Sell Checking 1 ****")
                if((cr_HighestEOS <  lastPriceEOSBTC)\
                or (cr_WeightedAverageEOS < last_WeightedAverageEOS and last_CloseEOS > cr_WeightedAverageEOS and cr_CloseEOS < last_OpenEOS)\
                and (cr_VolumeEOS < last_VolumeEOS)\
                and (pre_PriceEOSBTC > lastPriceEOSBTC)\
                and ((last_PercentChangeEOS - cr_PercentChangeEOS) > CHANGE_PERCENT_RATE)):
                    if(EOS_order_sell_amount > MIN_ALT_LOT):
                        EOS_order = "SELL"
                        print("EOS_BTC_SELL" + "@AMOUNT=" + str(EOS_order_sell_amount))
########### chack XMR BUY/SELL
    print("*** Checking XMR/BTC Order Signal ***")
    if(getXMR_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and USDC_order == "NONE"):
        ## print("**** XMR Buy Checking 1 ****")
            if((cr_LowestXMR > lastPriceXMRBTC)\
            or (cr_WeightedAverageXMR > last_WeightedAverageXMR and last_CloseXMR < cr_WeightedAverageXMR and cr_CloseXMR > last_OpenXMR)\
            and (cr_VolumeXMR > last_VolumeXMR * 1.25)\
            and (pre_PriceXMRBTC < lastPriceXMRBTC)\
            and ((cr_PercentChangeXMR - last_PercentChangeXMR) > CHANGE_PERCENT_RATE)):
                if(XMR_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    XMR_order = "BUY"
                    print("XMR_BTC_BUY" + "@AMOUNT=" + str(XMR_order_buy_amount))
            if(XMR_order == "NONE"):
            ## print("**** XMR Sell Checking 1 ****")
                if((cr_HighestXMR < lastPriceXMRBTC)\
                or (cr_WeightedAverageXMR < last_WeightedAverageXMR and last_CloseXMR > cr_WeightedAverageXMR and cr_CloseXMR < last_OpenXMR)\
                and (cr_VolumeXMR < last_VolumeXMR)\
                and (pre_PriceXMRBTC > lastPriceXMRBTC)\
                and ((last_PercentChangeXMR - cr_PercentChangeXMR) > CHANGE_PERCENT_RATE)):
                    if(XMR_order_sell_amount > MIN_ALT_LOT):
                        XMR_order = "SELL"
                        print("XMR_BTC_SELL" + "@AMOUNT=" + str(XMR_order_sell_amount))
########### chack XEM BUY/SELL
    print("*** Checking XEM/BTC Order Signal ***")
    if(getXEM_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and XEM_order == "NONE" and USDC_order == "NONE"):
        ## print("**** XEM Buy Checking 1 ****")
            if((cr_LowestXEM > lastPriceXEMBTC)\
            or (cr_WeightedAverageXEM > last_WeightedAverageXEM and last_CloseXEM < cr_WeightedAverageXEM and cr_CloseXEM > last_OpenXEM)\
            and (cr_VolumeXEM > last_VolumeXEM * 1.25)\
            and (pre_PriceXEMBTC < lastPriceXEMBTC)\
            and ((cr_PercentChangeXEM - last_PercentChangeXEM) > CHANGE_PERCENT_RATE)):
                if(XEM_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    XEM_order = "BUY"
                    print("XEM_BTC_BUY" + "@AMOUNT=" + str(XEM_order_buy_amount))
            if(XEM_order == "NONE"):
                ## print("**** XEM Sell Checking 1 ****")
                if((cr_HighestXEM < lastPriceXEMBTC)\
                or (cr_WeightedAverageXEM < last_WeightedAverageXEM and last_CloseXEM > cr_WeightedAverageXEM and cr_CloseXEM < last_OpenXEM)\
                and (cr_CloseXEM < last_VolumeXEM)\
                and (pre_PriceXEMBTC > lastPriceXEMBTC)\
                and ((last_PercentChangeXEM - cr_PercentChangeXEM) > CHANGE_PERCENT_RATE)):
                    if(XEM_order_sell_amount > MIN_ALT_LOT):
                        XEM_order = "SELL"
                        print("XEM_BTC_SELL" + "@AMOUNT=" + str(XEM_order_sell_amount))
########### chack XRP BUY/SELL
    print("*** Checking XRP/BTC Order Signal ***")
    if(getXRP_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and XEM_order == "NONE" and XRP_order == "NONE" and USDC_order == "NONE"):
        ## print("**** XRP Buy Checking 1 ****")
            if((cr_LowestXRP > lastPriceXRPBTC)\
            or (cr_WeightedAverageXRP > last_WeightedAverageXRP and last_CloseXRP < cr_WeightedAverageXRP and cr_CloseXRP > last_OpenXRP)\
            and (cr_VolumeXRP > last_VolumeXRP * 1.25)\
            and (pre_PriceXRPBTC < lastPriceXRPBTC)\
            and ((cr_PercentChangeXRP - last_PercentChangeXRP) > CHANGE_PERCENT_RATE)):
                if(XRP_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    XRP_order = "BUY"
                    print("XRP_BTC_BUY" + "@AMOUNT=" + str(XRP_order_buy_amount))
            if(XRP_order == "NONE"):
                ## print("**** XRP Sell Checking 1 ****")
                if((cr_HighestXRP < lastPriceXRPBTC)\
                or (cr_WeightedAverageXRP < last_WeightedAverageXRP and last_CloseXRP > cr_WeightedAverageXRP and cr_CloseXRP < last_OpenXRP)\
                and (cr_VolumeXRP > last_VolumeXRP)\
                and (pre_PriceXRPBTC > lastPriceXRPBTC)\
                and ((last_PercentChangeXRP - cr_PercentChangeXRP) > CHANGE_PERCENT_RATE)):
                    if(XRP_order_sell_amount > MIN_ALT_LOT):
                        XRP_order = "SELL"
                        print("XRP_BTC_SELL" + "@AMOUNT=" + str(XRP_order_sell_amount))
########### chack ZEC BUY/SELL
    print("*** Checking ZEC/BTC Order Signal ***")
    if(getZEC_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and XEM_order == "NONE" and XRP_order == "NONE" and ZEC_order == "NONE" and USDC_order == "NONE"):
        ## print("**** ZEC Buy Checking 1 ****")
            if((cr_LowestZEC > lastPriceZECBTC)\
            or (cr_WeightedAverageZEC > last_WeightedAverageZEC and last_CloseZEC < cr_WeightedAverageZEC and cr_CloseZEC > last_OpenZEC)\
            and (cr_VolumeZEC > last_VolumeZEC * 1.25)\
            and (pre_PriceZECBTC < lastPriceZECBTC)\
            and ((cr_PercentChangeZEC - last_PercentChangeZEC) > CHANGE_PERCENT_RATE)):
                if(ZEC_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    ZEC_order = "BUY"
                    print("ZEC_BTC_BUY" + "@AMOUNT=" + str(ZEC_order_buy_amount))
            if(ZEC_order == "NONE"):
            ## print("**** ZEC Sell Checking 1 ****")
                if((cr_HighestZEC < lastPriceZECBTC)\
                or (cr_WeightedAverageZEC < last_WeightedAverageZEC and last_CloseZEC > cr_WeightedAverageZEC and cr_CloseZEC < last_OpenZEC)\
                and (cr_VolumeZEC < last_VolumeZEC)\
                and (pre_PriceZECBTC > lastPriceZECBTC)\
                and ((last_PercentChangeZEC - cr_PercentChangeZEC) > CHANGE_PERCENT_RATE)):
                    if(ZEC_order_sell_amount > MIN_ALT_LOT):
                        ZEC_order = "SELL"
                        print("ZEC_BTC_SELL" + "@AMOUNT=" + str(ZEC_order_sell_amount))
########### chack LSK BUY/SELL
    print("*** Checking LSK/BTC Order Signal ***")
    if(getLSK_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and XEM_order == "NONE" and XRP_order == "NONE" and ZEC_order == "NONE" and LSK_order == "NONE" and USDC_order == "NONE"):
        ## print("**** LSK Buy Checking 1 ****")
            if((CR_LowestLSK > lastPriceLSKBTC)\
            or (cr_WeightedAverageLSK > last_WeightedAverageLSK and last_CloseLSK < cr_WeightedAverageLSK and cr_CloseLSK > last_OpenLSK)\
            and (cr_VolumeLSK < last_VolumeLSK * 1.25)\
            and (pre_PriceLSKBTC < lastPriceLSKBTC)\
            and ((cr_PercentChangeLSK - last_PercentChangeLSK) > CHANGE_PERCENT_RATE)):
                if(LSK_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    LSK_order = "BUY"
                    print("LSK_BTC_BUY" + "@AMOUNT=" + str(LSK_order_buy_amount))
            if(LSK_order == "NONE"):
            ## print("**** LSK Sell Checking 1 ****")
                if((LSK_Today_HighPrice < lastPriceLSKBTC)\
                or (cr_WeightedAverageLSK < last_WeightedAverageLSK and last_CloseLSK > cr_WeightedAverageLSK and cr_CloseLSK < last_OpenLSK)\
                and (cr_CloseLSK < last_VolumeLSK)\
                and (pre_PriceLSKBTC > lastPriceLSKBTC)\
                and ((last_PercentChangeLSK - cr_PercentChangeLSK) > CHANGE_PERCENT_RATE)):
                    if(LSK_order_sell_amount > MIN_ALT_LOT):
                        LSK_order = "SELL"
                        print("LSK_BTC_SELL" + "@AMOUNT=" + str(LSK_order_sell_amount))
########### chack REP BUY/SELL
    print("*** Checking REP/BTC Order Signal ***")
    if(getREP_Info_Price()):
        if(BCHSV_order == "NONE" and EOS_order == "NONE" and XMR_order == "NONE" and XEM_order == "NONE" and XRP_order == "NONE" and ZEC_order == "NONE" and LSK_order == "NONE" and REP_order == "NONE" and USDC_order == "NONE"):
        ## print("**** REP Buy Checking 1 ****")
            if((cr_LowestREP > lastPriceREPBTC)\
            or (cr_WeightedAverageREP > last_WeightedAverageREP and last_CloseREP < cr_WeightedAverageREP and cr_CloseREP > last_OpenREP)\
            and (cr_VolumeREP > last_VolumeREP * 1.25)\
            and (pre_PriceREPBTC < lastPriceREPBTC)\
            and ((cr_PercentChangeREP - last_PercentChangeREP) > CHANGE_PERCENT_RATE)):
                if(REP_order_buy_amount > MIN_ALT_LOT and BTC_Balance > MIN_BTC_LOT):
                    REP_order = "BUY"
                    print("REP_BTC_BUY" + "@AMOUNT=" + str(REP_order_buy_amount))
            if(REP_order == "NONE"):
            ## print("**** REP Sell Checking 1 ****")
                if((cr_HighestREP < lastPriceREPBTC)\
                or (cr_WeightedAverageREP < last_WeightedAverageREP and last_CloseREP > cr_WeightedAverageREP and cr_CloseREP < last_OpenREP)\
                and (cr_VolumeREP < last_VolumeREP)\
                and (pre_PriceREPBTC > lastPriceREPBTC)\
                and ((last_PercentChangeREP - cr_PercentChangeREP) > CHANGE_PERCENT_RATE)):
                    if(REP_order_sell_amount > MIN_ALT_LOT):
                        REP_order = "SELL"
                        print("REP_BTC_SELL" + "@AMOUNT=" + str(REP_order_sell_amount))
##########
    if (day_close_flag):
        if (BCHSV_order_sell_amount > MIN_ALT_LOT):
            BCHSV_order = "SELL"
        if (EOS_order_sell_amount > MIN_ALT_LOT):
            EOS_order = "SELL"
        if (XMR_order_sell_amount > MIN_ALT_LOT):
            XMR_order = "SELL"
        if (XEM_order_sell_amount > MIN_ALT_LOT):
            XEM_order = "SELL"
        if (XRP_order_sell_amount > MIN_ALT_LOT):
            XRP_order = "SELL"
        if (ZEC_order_sell_amount > MIN_ALT_LOT):
            ZEC_order = "SELL"
        if (LSK_order_sell_amount > MIN_ALT_LOT):
            LSK_order = "SELL"
        if (REP_order_sell_amount > MIN_ALT_LOT):
            REP_order = "SELL"
###
###############################
### SEND ORDER TO Poloniex  ###
###############################
#
    if(USDC_order == "BUY"):
        USDCBUY_Ask = getUSDC_Ask()
        err = True
        if (USDCBUY_Ask > 0):
            logger.debug("USDC_order_buy_amount=" + str(USDC_order_buy_amount))
            order_size = check_order_size(USDC_order_buy_amount, USDCBUY_Ask)
            print("************ USDC/BTC BUY ***************")
            print("BUY(USDC_BTC)" + " OrderPrice=" + "{0:.4f}".format(USDCBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(USDC_BTC)" + " OrderPrice=" + "{0:.4f}".format(USDCBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("USDC_BTC", USDCBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(USDC_BTC)_BUY: " + d + "\r\n" + str(lastPriceUSDCBTC) + "@orderPrice=" + str(USDCBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            USDC_order = "NONE"
    if(USDC_order == "SELL"):
        USDCSELL_Bid = getUSDC_Bid()
        err = True
        if(USDCSELL_Bid > 0):
            logger.debug("USDC_order_sell_amount=" + str(USDC_order_sell_amount))
            order_size = check_order_size(USDC_order_sell_amount, USDCSELL_Bid)
            print("************ USDC/BTC SELL ***************")
            print("SELL(USDC_BTC)" + " OrderPrice=" + "{0:.4f}".format(USDCSELL_Bid) + "@Amount=" + str(order_size))
            logger.info("SELL(USDC_BTC)" + " OrderPrice=" + "{0:.4f}".format(USDCSELL_Bid) + "@Amount=" + str(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("USDC_BTC", USDCSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(USDC_BTC)_SELL:" + d + "\r\n" + str(lastPriceUSDCBTC) + "@orderPrice=" + str(USDCSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        USDC_order = "NONE"
####
########################
    if(BCHSV_order == "BUY"):
        BCHSVBUY_Ask = getBCHSV_Ask()
        err = True
        if (BCHSVBUY_Ask > 0):
            logger.debug("BCHSV_order_buy_amount=" + str(BCHSV_order_buy_amount))
            order_size = check_order_size(BCHSV_order_buy_amount, BCHSVBUY_Ask)
            print("************ BCHSV/BTC BUY ***************")
            print("BUY(BCHSV_BTC)" + " OrderPrice=" + "{0:.4f}".format(BCHSVBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(BCHSV_BTC)" + " OrderPrice=" + "{0:.4f}".format(BCHSVBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_BCHSV", BCHSVBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(BCHSV_BTC)_BUY: " + d + "\r\n" + str(lastPriceBCHSVBTC) + "@orderPrice=" + str(BCHSVBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            BCHSV_order = "NONE"
    if(BCHSV_order == "SELL"):
        BCHSVSELL_Bid = getBCHSV_Bid()
        err = True
        if(BCHSVSELL_Bid > 0):
            logger.debug("BCHSV_order_sell_amount=" + str(BCHSV_order_sell_amount))
            order_size = check_order_size(BCHSV_order_sell_amount, BCHSVSELL_Bid)
            print("************ BCHSV/BTC SELL ***************")
            print("SELL(BCHSV_BTC)" + " OrderPrice=" + "{0:.4f}".format(BCHSVSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(BCHSV_BTC)" + " OrderPrice=" + "{0:.4f}".format(BCHSVSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_BCHSV", BCHSVSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(BCHSV_BTC)_SELL:" + d + "\r\n" + str(lastPriceBCHSVBTC) + "@orderPrice=" + str(BCHSVSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass

        BCHSV_order = "NONE"
####
######################## ALTCOIN
    if(EOS_order == "BUY"):
        EOSBUY_Ask = getEOS_Ask()
        err = True
        if (EOSBUY_Ask > 0):
            logger.debug("EOS_order_buy_amount=" + str(EOS_order_buy_amount))
            order_size = check_order_size(EOS_order_buy_amount, EOSBUY_Ask)
            print("************ EOS/BTC BUY ***************")
            print("BUY(EOS_BTC)" + " OrderPrice=" + "{0:.4f}".format(EOSBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(EOS_BTC)" + " OrderPrice=" + "{0:.4f}".format(EOSBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_EOS", EOSBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(EOS_BTC)_BUY: " + d + "\r\n" + str(lastPriceEOSBTC) + "@orderPrice=" + str(EOSBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            EOS_order = "NONE"
    if(EOS_order == "SELL"):
        EOSSELL_Bid = getEOS_Bid()
        err = True
        if(EOSSELL_Bid > 0):
            logger.debug("EOS_order_sell_amount=" + str(EOS_order_sell_amount))
            order_size = check_order_size(EOS_order_sell_amount, EOSSELL_Bid)
            print("************ EOS/BTC SELL ***************")
            print("SELL(BTC_EOS)" + "OrderPrice=" + "{0:.4f}".format(EOSSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(BTC_EOS)" + "OrderPrice=" + "{0:.4f}".format(EOSSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_EOS", EOSSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(EOS_BTC)_SELL:" + d + "\r\n" + str(lastPriceEOSBTC) + "@orderPrice=" + str(EOSSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        EOS_order = "NONE"
####
    if(XMR_order == "BUY"):
        XMRBUY_Ask = getXMR_Ask()
        err = True
        if (XMRBUY_Ask > 0):
            logger.debug("XMR_order_buy_amount=" + str(XMR_order_buy_amount))
            order_size = check_order_size(XMR_order_buy_amount, XMRBUY_Ask)
            print("************ XMR/BTC BUY ***************")
            print("BUY(XMR_BTC)" + " OrderPrice=" + "{0:.4f}".format(XMRBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(XMR_BTC)" + " OrderPrice=" + "{0:.4f}".format(XMRBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_XMR", XMRBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XMR_BTC)_BUY: " + d + "\r\n" + str(lastPriceXMRBTC) + "@orderPrice=" + str(XMRBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            XMR_order = "NONE"
    if(XMR_order == "SELL"):
        XMRSELL_Bid = getXMR_Bid()
        err = True
        if(XMRSELL_Bid > 0):
            logger.debug("XMR_order_sell_amount=" + str(XMR_order_sell_amount))
            order_size = check_order_size(XMR_order_sell_amount, XMRSELL_Bid)
            print("************ XMR/BTC SELL ***************")
            print("SELL(XMR_BTC)" + " OrderPrice=" + "{0:.4f}".format(XMRSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(XMR_BTC)" + " OrderPrice=" + "{0:.4f}".format(XMRSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_XMR", XMRSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XMR_BTC)_SELL:" + d + "\r\n" + str(lastPriceXMRBTC) + "@orderPrice=" + str(XMRSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        XMR_order = "NONE"
####
    if(XEM_order == "BUY"):
        XEMBUY_Ask = getXEM_Ask()
        err = True
        if (XEMBUY_Ask > 0):
            logger.debug("XEM_order_buy_amount=" + str(XEM_order_buy_amount))
            order_size = check_order_size(XEM_order_buy_amount, XEMBUY_Ask)
            print("************ XEM/BTC BUY ***************")
            print("BUY(XEM_BTC)" + " OrderPrice=" + "{0:.4f}".format(XEMBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(XEM_BTC)" + " OrderPrice=" + "{0:.4f}".format(XEMBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_XEM", XEMBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XEM_BTC)_BUY: " + d + "\r\n" + str(lastPriceXEMBTC) + "@orderPrice=" + str(XEMBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            XEM_order = "NONE"
    if(XEM_order == "SELL"):
        XEMSELL_Bid = getXEM_Bid()
        err = True
        if(XEMSELL_Bid > 0):
            logger.debug("XEM_order_sell_amount=" + str(XEM_order_sell_amount))
            order_size = check_order_size(XEM_order_sell_amount, XEMSELL_Bid)
            print("************ XEM/BTC SELL ***************")
            print("SELL(XEM_BTC)" + " OrderPrice=" + "{0:.4f}".format(XEMSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(XEM_BTC)" + " OrderPrice=" + "{0:.4f}".format(XEMSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_XEM", XEMSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XEM_BTC)_SELL:" + d + "\r\n" + str(lastPriceXEMBTC) + "@orderPrice=" + str(XEMSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        XEM_order = "NONE"
####
    if(XRP_order == "BUY"):
        XRPBUY_Ask = getXRP_Ask()
        err = True
        if (XRPBUY_Ask > 0):
            logger.debug("XRP_order_buy_amount=" + str(XRP_order_buy_amount))
            order_size = check_order_size(XRP_order_buy_amount, XRPBUY_Ask)
            print("************ XRP/BTC BUY ***************")
            print("BUY(XRP_BTC)" + " OrderPrice=" + "{0:.4f}".format(XRPBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(XRP_BTC)" + " OrderPrice=" + "{0:.4f}".format(XRPBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_XRP", XRPBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XRP_BTC)_BUY: " + d + "\r\n" + str(lastPriceXRPBTC) + "@orderPrice=" + str(XRPBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            XRP_order = "NONE"
    if(XRP_order == "SELL"):
        XRPSELL_Bid = getXRP_Bid()
        err = True
        if(XRPSELL_Bid > 0):
            logger.debug("XRP_order_sell_amount=" + str(XRP_order_sell_amount))
            order_size = check_order_size(XRP_order_sell_amount, XRPSELL_Bid)
            print("************ XRP/BTC SELL ***************")
            print("SELL(XRP_BTC)" + " OrderPrice=" + "{0:.4f}".format(XRPSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(XRP_BTC)" + " OrderPrice=" + "{0:.4f}".format(XRPSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_XRP", XRPSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(XRP_BTC)_SELL:" + d + "\r\n" + str(lastPriceXRPBTC) + "@orderPrice=" + str(XRPSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        XRP_order = "NONE"
####
    if(ZEC_order == "BUY"):
        ZECBUY_Ask = getZEC_Ask()
        err = True
        if (ZECBUY_Ask > 0):
            logger.debug("ZEC_order_buy_amount=" + str(ZEC_order_buy_amount))
            order_size = check_order_size(ZEC_order_buy_amount, ZECBUY_Ask)
            print("************ ZEC/BTC BUY ***************")
            print("BUY(ZEC_BTC)" + " OrderPrice=" + "{0:.4f}".format(ZECBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(ZEC_BTC)" + " OrderPrice=" + "{0:.4f}".format(ZECBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_ZEC", ZECBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(ZEC_BTC)_BUY: " + d + "\r\n" + str(lastPriceZECBTC) + "@orderPrice=" + str(ZECBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            ZEC_order = "NONE"
    if(ZEC_order == "SELL"):
        ZECSELL_Bid = getZEC_Bid()
        err = True
        if(ZECSELL_Bid > 0):
            logger.debug("ZEC_order_sell_amount=" + str(ZEC_order_sell_amount))
            order_size = check_order_size(ZEC_order_sell_amount, ZECSELL_Bid)
            print("************ ZEC/BTC SELL ***************")
            print("SELL(ZEC_BTC)" + " OrderPrice=" + "{0:.4f}".format(ZECSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(ZEC_BTC)" + " OrderPrice=" + "{0:.4f}".format(ZECSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_ZEC", ZECSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(ZEC_BTC)_SELL:" + d + "\r\n" + str(lastPriceZECBTC) + "@orderPrice=" + str(ZECSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        ZEC_order = "NONE"
####
    if(LSK_order == "BUY"):
        LSKBUY_Ask = getLSK_Ask()
        err = True
        if (LSKBUY_Ask > 0):
            logger.debug("LSK_order_buy_amount=" + str(LSK_order_buy_amount))
            order_size = check_order_size(LSK_order_buy_amount, LSKBUY_Ask)
            print("************ LSK/BTC BUY ***************")
            print("BUY(LSK_BTC)" + " OrderPrice=" + "{0:.4f}".format(LSKBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(LSK_BTC)" + " OrderPrice=" + "{0:.4f}".format(LSKBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_LSK", LSKBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(LSK_BTC)_BUY: " + d + "\r\n" + str(lastPriceLSKBTC) + "@orderPrice=" + str(LSKBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            LSK_order = "NONE"
    if(LSK_order == "SELL"):
        LSKSELL_Bid = getLSK_Bid()
        err = True
        if(LSKSELL_Bid > 0):
            logger.debug("LSK_order_sell_amount=" + str(LSK_order_sell_amount))
            order_size = check_order_size(LSK_order_sell_amount, LSKSELL_Bid)
            print("************ LSK/BTC SELL ***************")
            print("SELL(LSK_BTC)" + " OrderPrice=" + "{0:.4f}".format(LSKSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(LSK_BTC)" + " OrderPrice=" + "{0:.4f}".format(LSKSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_LSK", LSKSELL_Bid, decimal(LSK_order_sell_amount))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(LSK_BTC)_SELL:" + d + "\r\n" + str(lastPriceLSKBTC) + "@orderPrice=" + str(LSKSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        LSK_order = "NONE"
####
    if(REP_order == "BUY"):
        REPBUY_Ask = getREP_Ask()
        err = True
        if (REPBUY_Ask > 0):
            logger.debug("REP_order_buy_amount=" + str(REP_order_buy_amount))
            order_size = check_order_size(REP_order_buy_amount, REPBUY_Ask)
            print("************ REP/BTC BUY ***************")
            print("BUY(REP_BTC)" + " OrderPrice=" + "{0:.4f}".format(REPBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("BUY(REP_BTC)" + " OrderPrice=" + "{0:.4f}".format(REPBUY_Ask) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.buy("BTC_REP", REPBUY_Ask, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(REP_BTC)_BUY: " + d + "\r\n" + str(lastPriceREPBTC) + "@orderPrice=" + str(REPBUY_Ask) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Buy Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
            REP_order = "NONE"
    if(REP_order == "SELL"):
        REPSELL_Bid = getREP_Bid()
        err = True
        if(REPSELL_Bid > 0):
            logger.debug("REP_order_sell_amount=" + str(REP_order_sell_amount))
            order_size = check_order_size(REP_order_sell_amount, REPSELL_Bid)
            print("************ REP/BTC SELL ***************")
            print("SELL(REP_BTC)" + " OrderPrice=" + "{0:.4f}".format(REPSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            logger.info("SELL(REP_BTC)" + " OrderPrice=" + "{0:.4f}".format(REPSELL_Bid) + "@Amount=" + "{0:.4f}".format(order_size))
            tryd = 0
            while (err):
                try:
                    polotrd.sell("BTC_REP", REPSELL_Bid, decimal(order_size))
                    d = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
                    mes = "(Poloniex Trading Bot(REP_BTC)_SELL:" + d + "\r\n" + str(lastPriceREPBTC) + "@orderPrice=" + str(REPSELL_Bid) + "@Amount=" + str(order_size)
                    linemes = mes
                    lineNotify(linemes)
                    logger.info(mes)
                    err = False
                    print("*** Order OK ***")
                except Exception as e:
                    print ("Market Sell Order Error@" + str(e.args))
                    logger.error(str(e.args))
                    time.sleep(10)
                    tryd = tryd + 1
                    if(tryd > 3):
                        err = False
                    pass
        REP_order = "NONE"
#####
    last_PercentChangeEOS = cr_PercentChangeEOS
    last_PercentChangeBCHSV = cr_PercentChangeBCHSV
    last_PercentChangeXMR = cr_PercentChangeXMR
    last_PercentChangeXEM = cr_PercentChangeXEM
    last_PercentChangeXRP = cr_PercentChangeXRP
    last_PercentChangeZEC = cr_PercentChangeZEC
    last_PercentChangeLSK = cr_PercentChangeLSK
    last_PercentChangeREP = cr_PercentChangeREP
    last_PercentChangeUSDC = cr_PercentChangeUSDC
#
    pre_PriceUSDCBTC = lastPriceUSDCBTC
    pre_PriceEOSBTC = lastPriceEOSBTC
    pre_PriceBCHSVBTC = lastPriceBCHSVBTC
    pre_PriceXMRBTC = lastPriceXMRBTC
    pre_PriceXEMBTC = lastPriceXEMBTC
    pre_PriceXRPBTC = lastPriceXRPBTC
    pre_PriceZECBTC = lastPriceZECBTC
    pre_PriceLSKBTC = lastPriceLSKBTC
    pre_PriceREPBTC = lastPriceREPBTC
###
    print("***** Wainting " + str(WAINTING_TIME) + " Minutes For Signal USDC(BTC)/EOS/BCHSV/XMR/XEM/XRP/ZEC/LSK/REP ******")
#
if __name__ == '__main__':
  print ('START:'+ time.ctime())
  initAPI()
  print ("**************** STRAT Poloniex Bot******************")
  s = sched.scheduler(time.time, time.sleep)
  while 1 == 1:
    try:
      s.enter(60*WAINTING_TIME, 1, order_logic, ())
    except Exception:
      pass
    s.run()
##################

