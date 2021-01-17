#_*_ coding: utf-8 _*_
### Modified BitcForex bitcforex@gmail.com from 2020/06/07
### https://bitcforex.com
import sys,os
import pybitflyer
import ccxt
#import py_bitflyer_jsonrpc
import json
import requests
import logging
import csv
import math
from decimal import *
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import time
import datetime
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
# from tornado import gen
import threading
from collections import deque
#####################
# ログの出力名を設定（1）
logger = logging.getLogger('bitFlyer_BTC-FXJPY_bot')
# ログレベルの設定
logger.setLevel(10)
# ログのファイル出力先を設定
fh = logging.FileHandler('bitFlyer_BTC-FXJPY_Trace.log')
logger.addHandler(fh)
# ログの出力形式の設定
formatter = logging.Formatter('%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
fh.setFormatter(formatter)
#####################

class ChannelBreakOut:
    def __init__(self):
        #pubnubから取得した約定履歴を保存するリスト（基本的に不要．）
        self._executions = deque(maxlen=300)
        self._lot = 0.01
        self._margin = 4
        self._product_code = "FX_BTC_JPY"
        #各パラメタ．
        self._entryTerm = 30
        self._closeTerm = 30
        self._rangeTerm = 15
        self._rangeTh = 5000
        self._waitTerm = 5
        self._waitTh = 1000
        self._candleTerm = "5T"
        #現在のポジション．1ならロング．-1ならショート．0ならポジションなし．
        self._pos = 0
        #注文執行コスト．遅延などでこの値幅を最初から取られていると仮定する
        self._cost = 0.01
        self._risk = 0.3
        self._max_orders = 5 # Max=5
        self.order = Order()
        self.api = pybitflyer.API('GSj5CHLLvHNwpZcwZnAjTj', 'JLP1drD5LkLgd4AbyKHy0rB3zJDZynwpcYS2FyIFFk0=')
        self.bitflyer = ccxt.bitflyer()
        self.bitflyer.apiKey = 'GSj5CHLLvHNwpZcwZnAjTj'
        self.bitflyer.secret = 'JLP1drD5LkLgd4AbyKHy0rB3zJDZynwpcYS2FyIFFk0='
#
        #ラインに稼働状況を通知
        self.line_notify_token = 'm5zT4mquJDVU2zK5GtqWOw0hBokC9hqPZQOI3xadDrx'
        self.line_notify_api = 'https://notify-api.line.me/api/notify'

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost = value

    @property
    def risk(self):
        return self._risk

    @risk.setter
    def risk(self, value):
        self._risk = value

    @property
    def max_orders(self):
        return self._max_orders

    @max_orders.setter
    def max_orders(self, value):
        self._max_orders = value

    @property
    def candleTerm(self):
        return self._candleTerm

    @candleTerm.setter
    def candleTerm(self, val):
        """
        valは"5T"，"1H"などのString
        """
        self._candleTerm = val

    @property
    def waitTh(self):
        return self._waitTh

    @waitTh.setter
    def waitTh(self, val):
        self._waitTh = val

    @property
    def waitTerm(self):
        return self._waitTerm

    @waitTerm.setter
    def waitTerm(self, val):
        self._waitTerm = val

    @property
    def rangeTh(self):
        return self._rangeTh

    @rangeTh.setter
    def rangeTh(self,val):
        self._rangeTh = val

    @property
    def rangeTerm(self):
        return self._rangeTerm

    @rangeTerm.setter
    def rangeTerm(self,val):
        self._rangeTerm = val

    @property
    def executions(self):
        return self._executions

    @executions.setter
    def executions(self, val):
        self._executions = val

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, val):
        self._pos = int(val)

    @property
    def lot(self):
        return self._lot

    @lot.setter
    def lot(self, val):
        self._lot = round(val,3)

    @property
    def product_code(self):
        return self._product_code

    @product_code.setter
    def product_code(self, val):
        self._product_code = val

    @property
    def entryTerm(self):
        return self._entryTerm

    @entryTerm.setter
    def entryTerm(self, val):
        self._entryTerm = int(val)

    @property
    def closeTerm(self):
        return self._closeTerm

    @closeTerm.setter
    def closeTerm(self, val):
        self._closeTerm = int(val)
# 口座残高を取得する関数
    def bitflyer_collateral(self):
	    while True:
		    try:
			    collateral = self.bitflyer.private_get_getcollateral()
			    #print("現在のアカウント残高(BTC--->JPY)は{}円です".format( int(collateral["collateral"]) ))
			    return int( collateral["collateral"] ), float( collateral["keep_rate"] ), float( collateral["open_position_pnl"] )
		    except ccxt.BaseError as e:
			    print("BitflyerのAPIでの口座残高取得に失敗しました ： ", e)
			    print("20秒待機してやり直します")
			    time.sleep(20)

    # 注文ロットを計算する関数
    def calculate_lot(self, df_candleStick, margin, risk, term):
        data = 0
        lot = 0
        able_lot = 0.00
        loscut = 0.8
        balance , keep_rate , position = self.bitflyer_collateral()
        #if(keep_rate < loscut):
        #    print("証拠金:Not Enough Money")
        #    return -1,0
        for i in range(len(df_candleStick.index)):
            try:
                data = np.mean([price for price in df_candleStick["close"][i-term:i]])
            except:
                pass
        #print("data=", data)
        able_lot = float((balance/data)*self.margin*self.risk)
        # able_lot = float((balance*(data*10)*margin*risk)/10*10*10*10*10)
        lot = round(able_lot,3)        #print("許容リスクから購入できる枚数は最大{}BTCまでです".format(calc_lot))
        #print("証拠金から購入できる枚数は最大{}BTCまでです".format(lot))
        return lot,position
#
    def calculateLot(self, margin):
        """
        証拠金からロットを計算する関数．
        """
        lot = math.floor(margin*10**(-4))*10**(-2)*self.cost
        return round(lot,4)
#####
    def check_bf_positions(self):
	    while True:
		    try:
			    size = []
			    price = []
			    positions = self.bitflyer.private_get_getpositions( params = { "product_code" : "FX_BTC_JPY" })
			    if not positions:
				    #print("現在ポジションは存在しません")
				    return 0,0,None
			    for pos in positions:
				    size.append( pos["size"] )
				    price.append( pos["price"] )
				    side = pos["side"]
			
			    # 平均建値を計算する
			    average_price = round(sum( price[i] * size[i] for i in range(len(price)) ) / sum(size))
			    sum_size = round(sum(size),3)
			    #print("保有中の建玉：合計{}つ\n平均建値：{}円\n合計サイズ：{}BTC\n方向：{}".format(len(price),average_price,sum_size,side))
			
			    # 価格・サイズ・方向を返す
			    return average_price,sum_size,side
				
		    except ccxt.BaseError as e:
			    #print("BitflyerのAPIで問題発生 : ",e)
			    #print("20秒待機してやり直します")
			    time.sleep(20)
#####
    def calculateLines(self, df_candleStick, term, flag):
    #def calculateLines(self, df_candleStick, flag):
        """
        Flag=0:Open, Flag=1:Close
        期間高値・安値を計算する．
        candleStickはcryptowatchのローソク足．termは安値，高値を計算する期間．（5ならローソク足5本文の安値，高値．)
        """
        lowLine = []
        highLine = []

        for i in range(len(df_candleStick.index)):
            if i < term:
                if(flag==0):
                    if(i>0):
                        if(lowLine[i-1] > df_candleStick["open"][i]):
                            lowLine.append(lowLine[i-1])
                            lowLine[i-1] = df_candleStick["open"][i]
                        else:
                            lowLine.append(df_candleStick["open"][i])
                        if(highLine[i-1] < df_candleStick["open"][i]):
                            highLine.append(highLine[i-1])
                            highLine[i-1]=df_candleStick["open"][i]
                        else:
                            highLine.append(df_candleStick["open"][i])
                    else:
                        lowLine.append(df_candleStick["open"][i])
                        highLine.append(df_candleStick["open"][i])           
                else:
                    if(i>0):
                        if(lowLine[i-1] > df_candleStick["close"][i]):
                            lowLine.append(lowLine[i-1])
                            lowLine[i-1]=df_candleStick["close"][i]
                        else:
                            lowLine.append(df_candleStick["close"][i])
                        if(highLine[i-1] < df_candleStick["close"][i]):
                            highLine.append(highLine[i-1])
                            highLine[i-1]=df_candleStick["close"][i]
                        else:
                            highLine.append(df_candleStick["close"][i])
                    else:
                        lowLine.append(df_candleStick["close"][i])
                        highLine.append(df_candleStick["close"][i]) 
            else:
                if(flag==0):
                    low = min([price for price in df_candleStick["open"][i-term:i]])
                    high = max([price for price in df_candleStick["open"][i-term:i]])
                    lowLine.append(low)
                    highLine.append(high)
                else:
                    low = min([price for price in df_candleStick["close"][i-term:i]])
                    high = max([price for price in df_candleStick["close"][i-term:i]])
                    lowLine.append(low)
                    highLine.append(high)

        return (lowLine, highLine)

    def calculatePriceRange(self, df_candleStick, term):
        """
        termの期間の値幅を計算．
        """
        low = [min([df_candleStick["close"][i-term+1:i].min(),df_candleStick["open"][i-term+1:i].min()]) for i in range(len(df_candleStick.index))]
        high = [max([df_candleStick["close"][i-term+1:i].max(), df_candleStick["open"][i-term+1:i].max()]) for i in range(len(df_candleStick.index))]
        low = pd.Series(low)
        high = pd.Series(high)
        priceRange = [high.iloc[i]-low.iloc[i] for i in range(len(df_candleStick.index))]
        return priceRange

    def isRange(self,df_candleStick ,term, th):
        """
        レンジ相場かどうかをTrue,Falseの配列で返す．termは期間高値・安値の計算期間．thはレンジ判定閾値．
        """
        #値幅での判定．
        if th != None:
            priceRange = self.calculatePriceRange(df_candleStick, term)
            isRange = [th > i for i in priceRange]
        #終値の標準偏差の差分が正か負かでの判定．
        elif th == None and term != None:
            df_candleStick["std"] = [df_candleStick["close"][i-term+1:i].std() for i in range(len(df_candleStick.index))]
            df_candleStick["std_slope"] = [df_candleStick["std"][i]-df_candleStick["std"][i-1] for i in range(len(df_candleStick.index))]
            isRange = [i > 0 for i in df_candleStick["std_slope"]]
        else:
            isRange = [False for i in df_candleStick.index]
        return isRange

    #def judge(self, df_candleStick, entryHighLine, entryLowLine, closeHighLine, closeLowLine, entryTerm):
    def judge(self, df_candleStick, entryHighLine, entryLowLine, closeHighLine, closeLowLine, entryTerm, closeTerm, BarLineTerm):
        """
        売り買い判断．ローソク足の高値が期間高値を上抜けたら買いエントリー．（2）ローソク足の安値が期間安値を下抜けたら売りエントリー．judgementリストは[買いエントリー，売りエントリー，買いクローズ（売り），売りクローズ（買い）]のリストになっている．（二次元リスト）リスト内リストはの要素は，0（シグナルなし）,価格（シグナル点灯）を取る．
        """
        judgement = [[0,0,0,0] for i in range(len(df_candleStick.index))]
        ret_judgement = [0,0,0,0] 
        ai = 0
        bi = 0
        ci = 0
        di = 0
        for i in range(len(df_candleStick.index)):
            #下抜けでエントリー
            #print("df_candleStick[low][-i]", df_candleStick["low"][-i])
            #print("df_candleStick[low][i]", df_candleStick["low"][i])
            #print("entryLowLine[-i]", entryLowLine[-i])
            #print("entryLowLine[i]", entryLowLine[i])
            if df_candleStick["low"][i] < entryLowLine[i] and i > entryTerm:
                judgement[i][0] = entryLowLine[i]
                ai = i
            elif df_candleStick["low"][i] > entryLowLine[i] and i > entryTerm:
                if judgement[ai][0] == 0:
                    judgement[ai][0] = entryLowLine[i]
                    ai = i
                elif judgement[ai][0] > entryLowLine[i] and ai < i:
                    ret_judgement[0] = 1
                    break
            #上抜けでエントリー
            if df_candleStick["high"][i] > entryHighLine[i] and i > entryTerm:
                judgement[i][1] = entryHighLine[i]
                bi = i
            elif df_candleStick["high"][i] < entryHighLine[i] and i > entryTerm:
                if judgement[bi][1] == 0:
                    judgement[bi][1] = entryHighLine[i]
                    bi = i
                elif judgement[bi][1] <= entryHighLine[i] and bi < i:
                    ret_judgement[1] = 1
                    break
#
           #上抜けでクローズ
            if df_candleStick["high"][i] > closeHighLine[i] and i > closeTerm:
                judgement[i][2] = closeHighLine[i]  
                ci = i
            elif df_candleStick["high"][i] < closeHighLine[i] and i > closeTerm:
                if judgement[ci][2] == 0:
                    judgement[ci][1] = closeHighLine[i]
                    ci = i
                elif judgement[ci][2] < closeHighLine[i] and ci < i:
                    ret_judgement[2] = 1
                    break
            #下抜けでクローズ
            if df_candleStick["low"][i] < closeLowLine[i] and i > closeTerm:
                judgement[i][3] = closeLowLine[i]
                di = i
            elif df_candleStick["low"][i] > closeLowLine[i] and i > closeTerm:
                if judgement[di][3] == 0:
                    judgement[di][3] = closeLowLine[i]
                    di = i
                elif judgement[di][3] > closeLowLine[i] and di < i:
                    ret_judgement[3] = 1
                    break
#
            #else:
            #    pass
        return ret_judgement

    def judgeForLoop(self, high, low, entryHighLine, entryLowLine, closeHighLine, closeLowLine):
        """
        売り買い判断．入力した価格が期間高値より高ければ買いエントリー，期間安値を下抜けたら売りエントリー．judgementリストは[買いエントリー，売りエントリー，買いクローズ（売り），売りクローズ（買い）]のリストになっている．（値は0or1）
        ローソク足は1分ごとに取得するのでインデックスが-1のもの（現在より1本前）をつかう．
        """
        judgement = [0,0,0,0]
        #上抜けでエントリー
        if high > entryHighLine[-1]:
            judgement[0] = 1
        #下抜けでエントリー
        if low < entryLowLine[-1]:
            judgement[1] = 1
        #下抜けでクローズ
        if low < closeLowLine[-1]:
            judgement[2] = 1
        #上抜けでクローズ
        if high > closeHighLine[-1]:
            judgement[3] = 1
        return judgement

    def getCandlestick(self, number, period):
        """
        number:ローソク足の数．period:ローソク足の期間（文字列で秒数を指定，Ex:1分足なら"60"）．cryptowatchはときどきおかしなデータ（price=0）が含まれるのでそれを除く．
        """
        #ローソク足の時間を指定
        periods = [period]
        #クエリパラメータを指定
        query = {"periods":','.join(periods)}
        #ローソク足取得
        res = \
            json.loads(requests.get("https://api.cryptowat.ch/markets/bitflyer/btcfxjpy/ohlc", params=query).text)[
                "result"]
        # ローソク足のデータを入れる配列．
        data = []
        for i in periods:
            row = res[i]
            length = len(row)
            for column in row[:length - (number + 1):-1]:
                # dataへローソク足データを追加．
                if column[4] != 0:
                    column = column[0:6]
                    data.append(column)
        return data[::-1]


    def fromListToDF(self, candleStick):
        """
        Listのローソク足をpandasデータフレームへ．
        """
        #print("In candleStick=",candleStick)
        date = [price[0] for price in candleStick]
        #c = [int(price[1]) for price in candleStick]
        priceOpen = [float(price[1]) for price in candleStick]
        priceHigh = [float(price[2]) for price in candleStick]
        priceLow = [float(price[3]) for price in candleStick]
        priceClose = [float(price[4]) for price in candleStick]
        date_datetime = map(datetime.datetime.fromtimestamp, date)
        dti = pd.DatetimeIndex(date_datetime)
        df_candleStick = pd.DataFrame({"open" : priceOpen, "high" : priceHigh, "low": priceLow, "close" : priceClose}, index=dti)
        return df_candleStick

    def processCandleStick(self, candleStick, timeScale):
        """
        1分足データから各時間軸のデータを作成.timeScaleには5T（5分），H（1時間）などの文字列を入れる
        """
        df_candleStick = self.fromListToDF(candleStick)
        processed_candleStick = df_candleStick.resample(timeScale).agg({'open': 'first','high':'max','low': 'min','close': 'last'})
        processed_candleStick = processed_candleStick.dropna()
        return processed_candleStick

    def lineNotify(self, message, fileName=None):
        payload = {'message': message}
        headers = {'Authorization': 'Bearer ' + self.line_notify_token}
        if fileName == None:
            try:
                requests.post(self.line_notify_api, data=payload, headers=headers)
            except:
                pass
        else:
            try:
                files = {"imageFile": open(fileName, "rb")}
                requests.post(self.line_notify_api, data=payload, headers=headers, files = files)
            except:
                pass

    def my_round(self, x, d):
        strtakeRange = "{0:.7f}".format(x)
        point = '.1'
        if (d==2):
            point = '.01'
        elif (d==3):
            point = '.001'
        elif (d==4):
            point = '.0001'
        elif (d==5):
            point = '.00001'
        takeRange = Decimal(strtakeRange).quantize(Decimal(point), rounding=ROUND_UP)
        ftakeRange = float(takeRange)
        return ftakeRange

    def describePLForNotification(self, pl, df_candleStick):
        #import matplotlib
        matplotlib.use('Agg')
        #import matplotlib.pyplot as plt
        close = df_candleStick["close"]
        index = range(len(pl))
        # figure
        fig = plt.figure(figsize=(20,12))
        #for price
        ax = fig.add_subplot(2, 1, 1)
        ax.plot(df_candleStick.index, close)
        ax.set_xlabel('Time')
        # y axis
        ax.set_ylabel('The price[JPY]')
        #for PLcurve
        ax = fig.add_subplot(2, 1, 2)
        # plot
        ax.plot(index, pl, color='b', label='The PL curve')
        ax.plot(index, [0]*len(pl), color='b',)
        # x axis
        ax.set_xlabel('The number of Trade')
        # y axis
        ax.set_ylabel('The estimated Profit/Loss(JPY)')
        # legend and title
        ax.legend(loc='best')
        ax.set_title('The PL curve(Time span:{})'.format(self.candleTerm))
        # save as png
        today = datetime.datetime.now().strftime('%Y%m%d')
        number = "_" + str(len(pl))
        fileName = today + number + ".png"
        plt.savefig(fileName)
        plt.close()
        return fileName
######################
##### MAIN LOGIC #####
######################
    def loop(self,entryTerm, closeTerm, rangeTh, rangeTerm,originalWaitTerm, waitTh,candleTerm):
        recheck_flg = 0
        """
        注文の実行ループを回す関数
        """
        BarLineTerm = 5
        entryLowLine = []
        entryHighLine = []
        closeLowLine = []
        closeHighLine = []
        profitPos = 0.0
        getProfit = 5000
        lossCut = 1500
        okOrder = False
        pos = 0
        pl = []
        pl.append(0)
        lastPositionAsk = 9999999.99
        lastPositionBid = 0.00
        Longposition = 0.00
        Shortposition = 0.00
        counter = 0
        term = 0
        long_order_count = 0
        short_order_count = 0
        long_order_lots = 0.00
        short_order_lots = 0.00
        waitTerm = 0
        onLoop = False
        pre_balance = 0.00
        crt_balance = 0.00
        keep_rate = 0.00
        repFlag = True
        postion = 0
        pre_position = 0.0
        stp = 0
        pre_bid = 0.0
        pre_ask = 0.0
        side = None
        order_flg = 0
 
        try:
           candleStick = self.getCandlestick(120, "60")
        except:
            print("Unknown error happend when you requested candleStick")
        if candleTerm == None:
            df_candleStick = self.fromListToDF(candleStick)
        else:
            df_candleStick = self.processCandleStick(candleStick, candleTerm)
        #entryLowLine, entryHighLine = self.calculateLines(df_candleStick,0)
        #closeLowLine, closeHighLine = self.calculateLines(df_candleStick,1)
        #lot = self.calculate_lot(df_candleStick, self.margin, entryTerm)
#
        pre_balance , keep_rate, position = self.bitflyer_collateral()
#
        while True:
            #5分ごとに基準ラインを更新
            if datetime.datetime.now().minute % 5 == 0 and recheck_flg == 0:
                print("Renewing candleSticks(" + str(counter) + ")")
                recheck_flg = 1
                counter += 1
                side = None              
#
                try:
                    candleStick = self.getCandlestick(120, "60")
                except:
                    print("Unknown error happend when you requested candleStick")
                if candleTerm == None:
                    df_candleStick = self.fromListToDF(candleStick)
                    #print("df_candleStick_01=",df_candleStick)
                else:
                    df_candleStick = self.processCandleStick(candleStick, candleTerm)
                    #print("df_candleStick_02=",df_candleStick)#
#
            else:
                recheck_flg = 0
                #if (stp > 0): time.sleep(20)
                price,size,side = self.check_bf_positions()
                if (side != None):
                    #print("Side : {} Lots : {} Price : {}".format(side, size, price))
                    if (size == 0.0):
                        size,position = self.calculate_lot(df_candleStick, self.margin, self.risk, entryTerm)
                    if (size == -1):
                        size = self.lot
                    if (side == "BUY"):
                        pos = 1
                        long_order_count = 1
                        long_order_lots = size
                        Longposition = price
                        lastPositionBid = price
                        if (stp == 0):
                            tp = int(1/size*20)
                            sl = -(int(1/size*20))
                    else:
                        pos = -1
                        short_order_count = 1
                        short_order_lots = size
                        Shortposition = price
                        lastPositionAsk = price
                        if (stp == 0):
                            tp = int(1/size*20)
                            sl = -(int(1/size*20))

                else:
                    pos = 0
                    stp = 0
                    long_order_count = 0
                    short_order_count = 0
                    tp = 0
                    sl = 0
#####
                if (side != None):
                    ### ロングクローズ()
                    if (long_order_count > 0 and onLoop == True):
                        # ロングクローズ
                        price,size,side = self.check_bf_positions()
                        if (side != None):
                            if (side == "BUY"):
                                Longposition = price
                                long_order_lots = size
                                crt_balance , keep_rate, position = self.bitflyer_collateral()
                                print("Position(Long)={:,.0f}".format(position))
                                doOrder = False
                                if (pos > 0):
                                    print("counter:{},stp:{},tp:{:,.1f},sl:{:,.1f}".format(counter,stp,tp,sl))
                                    if (position > tp and position != 0):
                                        doOrder = True
                                        order_flg = 0
                                    #if (counter > 12):
                                    if (position < sl and position != 0):
                                        doOrder = True
                                        order_flg = -1
                                    #if (doOrder == False and pre_position < 0 and position < 0 and (pre_position - 300)  > position):
                                    #    doOrder = True
                                    #if (doOrder == False and pre_position < 0 and position < 0 and counter > 12):
                                    #    doOrder = True
                                    #    order_flg = -1
                                    #elif (doOrder == False and counter > 12):
                                    #    order_flg = 0
                                pre_position = position
                                if (doOrder):
                                    counter = 0
                                    profitPos = int(position)
                                    okOrder = False
                                    print(datetime.datetime.now())
                                    print("market SELL(Long Close) order Lot=",long_order_lots)
                                    self.order.market(size=long_order_lots,side="SELL")
                                    okOrder = True
                                    pos = 0
                                    position = 0
                                    stp = 0
                                    long_order_count = 0
                                    mes = None
                                    if (profitPos>0): mes = " +Profit"
                                    else: mes = " -Loss"
                                    message = "bitFlyer_Bot(BTCJPY) Long Position Close Lot:{}, Price:{}, pl:{:,.0f}, Result:{}".format(long_order_lots, best_ask, profitPos, mes)
                                    ### comment because od file sizr bigger fileName = self.describePLForNotification(pl, df_candleStick)
                                    ### comment because od file sizr bigger self.lineNotify(message,fileName)
                                    self.lineNotify(message)
                                    logger.info(message)
                                    long_order_lots = 0.00
                                    lastSide = -1
                                    lastPositionAsk = best_ask
                                    lastPositionBid = best_bid
                                    onLoop = False
                                else:
                                    if (counter < 12):
                                        if (position > 0):
                                            tp = int((1/size*10 + ((12-counter)*10)))
                                            sl = -(int(((1/size*5 + ((12-counter)*5)))))
                                        else:
                                            tp = int((1/size*5 + ((12-counter)*5)))
                                            sl = -(int(((1/size*5 + ((12-counter)*10)))))
                                    else:
                                        tp = int(1/size*10)
                                        sl = -(int(1/size*10))
                    #### ショートクローズ
                    if (short_order_count > 0 and onLoop == True):
                        price,size,side = self.check_bf_positions()
                        if (side != None):
                            if (side == "SELL"):
                                Shortposition = price
                                short_order_lots = size
                                crt_balance , keep_rate, position = self.bitflyer_collateral()
                                print("Position(Short)={:,.0f}".format(position))
                                doOrder = False
                                if (pos < 0):
                                    print("counter:{},stp:{},tp:{:,.1f},sl:{:,.1f}".format(counter,stp,tp,sl))
                                    if (position > tp and position != 0):
                                        doOrder = True
                                        order_flg = 0
                                    #if (counter > 12):
                                    if (position < sl and position != 0):
                                        doOrder = True
                                        order_flg = 1
                                    #if (doOrder == False and pre_position < 0 and position < 0 and (pre_position - 300)  > position):
                                    #    doOrder = True
                                    #if (doOrder == False and pre_position < 0 and position < 0 and counter > 12):
                                    #    doOrder = True
                                    #    order_flg = 1
                                    #elif (doOrder == False and counter > 12):
                                    #    order_flg = 0
                                pre_position = position
                                if (doOrder):
                                    counter = 0
                                    profitPos = int(position)
                                    okOrder = False
                                    print(datetime.datetime.now())
                                    print("market BUY(Short Close) order Lot=",short_order_lots)
                                    self.order.market(size=short_order_lots, side="BUY")
                                    okOrder = True
                                    pos = 0
                                    position = 0
                                    stp = 0
                                    short_order_count = 0
                                    mes = None
                                    if (profitPos>0): mes = " +Profit"
                                    else: mes = " -Loss"
                                    message = "bitFlyer_Bot(BTCJPY) Short Position Close Lot:{}, Price:{}, pl:{:,.0f}, Result:{}".format(short_order_lots, best_bid, profitPos, mes)
                                    ### comment because od file sizr bigger fileName = self.describePLForNotification(pl, df_candleStick)
                                    ### comment because od file sizr bigger self.lineNotify(message,fileName)
                                    self.lineNotify(message)
                                    logger.info(message)
                                    short_order_lots = 0.00
                                    lastSide = 1
                                    lastPositionAsk = best_ask
                                    lastPositionBid = best_bid
                                    onLoop = False
                                else:
                                    if (counter < 12):
                                        if (position > 0):
                                            tp = int((1/size*10 + ((12-counter)*10)))
                                            sl = -(int(((1/size*5 + ((12-counter)*5)))))
                                        else:
                                            tp = int((1/size*5 + ((12-counter)*5)))
                                            sl = -(int(((1/size*5 +  ((12-counter)*10)))))
                                    else:
                                        tp = int(1/size*10)
                                        sl = -(int(1/size*10))
                if (stp > 0):
                    if (position > 0):
                        time.sleep(10)
                    elif (position < 0):
                        time.sleep(20)
                stp += 1
#####
            if(recheck_flg==1):
                entryLowLine, entryHighLine = self.calculateLines(df_candleStick, BarLineTerm,0)
                closeLowLine, closeHighLine = self.calculateLines(df_candleStick, BarLineTerm,1)
                #entryLowLine, entryHighLine = self.calculateLines(df_candleStick, 0)
                #closeLowLine, closeHighLine = self.calculateLines(df_candleStick, 1)
###                lot = self.calculateLot(self.margin)
###                if (lot < self.lot):
###                    lot = self.lot
####
                #直近約定件数30件の高値と安値
                #high = max([candleStick[-1-i][4] for i in range(30)])
                #low = min([candleStick[-1-i][4] for i in range(30)])
                #judgement = self.judgeForLoop(high, low, entryHighLine, entryLowLine, closeHighLine, closeLowLine)
#
                #print("df_candleStick=",df_candleStick)
                judgement = self.judge(df_candleStick, entryHighLine, entryLowLine, closeHighLine, closeLowLine, entryTerm, closeTerm, BarLineTerm)
#
                #現在レンジ相場かどうか． 
                isRange = self.isRange(df_candleStick, rangeTerm, rangeTh)
                #if(judgement[0]): logger.info("********** Buy signal ******Range+pos:" + str(isRange[-1]) +"-pos-" + str(pos))
                #if(judgement[1]): logger.info("********** Sell signal ******Range+pos:" + str(isRange[-1]) + "-pos-" + str(pos))
                #if(judgement[2]): logger.info("********** Sell(Long Close) signal ******Range+pos:" + str(isRange[-1]) + "-pos-" + str(pos))
                #if(judgement[3]): logger.info("********** Buy(Short Close) signal ******Range+pos:" + str(isRange[-1]) + "-pos-"+ str(pos))
                try :
                    ### print("get ticker!!!!!!!!!!!!!!!!!!!")
                    ticker = self.api.ticker(product_code=self.product_code)
                    best_ask = ticker["best_ask"]
                    best_bid = ticker["best_bid"]
                except:
                    print("Unknown error happend when you requested ticker.")
                    time.sleep(60)
                finally:
                    pass

                time.sleep(10)
                price,size,side = self.check_bf_positions()
                print("Side : {} Lots : {} Price : {}".format(side, size, price))
#
                crt_balance , keep_rate, position = self.bitflyer_collateral()
                pre_position = position
                getProfit = 5000
                getProfit = int(best_ask - best_bid)
                if (counter < 12 and getProfit < 3000):
                    getProfit = 3000
                elif (counter < 24 and getProfit < 2000):
                    getProfit = 2000
                elif (counter > 48 and getProfit < 1000):
                    getProfit = 1000

                #print("getProfit = " , getProfit)
                #print("takeprofit = " , takeprofit)
                #print("lossCut   = " , lossCut)
#
                #ここからエントリー，クローズ処理
                onLoop = True
                doOrder = False
                ClosedFlg = False
                #if pos == 0 and not isRange[-1]:
                #if (isRange[-1]): 
                print("judgement[0]:Buy Entry= ",judgement[0])
                print("judgement[1]:Sell Entry= ",judgement[1])
                print("judgement[2]:Buy Close(Sell)= ",judgement[2])
                print("judgement[3]:Sell Close(Buy)= ",judgement[3])
                print("isRange[-1]= ",isRange[-1])
                print("long_order_count= ",long_order_count)
                print("short_order_count= ",short_order_count)
                #ショートエントリー 
                if ((judgement[1]==1 and isRange[-1]==False) or (order_flg == -1)) and short_order_count < self.max_orders and pos == 0 and onLoop == True and side == None:
                    stp = 0
                    order_flg = 0
                    counter = 0
                    long_order_count = 0
                    short_order_count = 1
                    pos = -1
#
                    lot,position = self.calculate_lot(df_candleStick, self.margin, self.risk, entryTerm)
                    if (lot == -1):
                        continue 
                    short_order_lots = lot
                    long_order_lots = 0.00
#
                    print(datetime.datetime.now())
                    print("market SELL order Lot=",lot)
                    self.order.market(size=lot,side="SELL")
                    message = "bitFlyer_Bot(BTCJPY) Short entry Lot=" + "{:.3f}".format(lot) + "@price={}".format(best_bid)
                    self.lineNotify(message)
                    logger.info(message)
                    if (lastPositionAsk == 9999999.99 or lastPositionAsk < best_ask):
                        lastPositionAsk = best_ask
                    if (lastPositionBid == 0.00 or lastPositionBid > best_bid):
                        lastPositionBid = best_bid
                    Shortposition = lastPositionAsk
                    onLoop = False
                    pre_position = position
                    #time.sleep(5)
                #ロングエントリー
                if ((judgement[0]==1 and isRange[-1]==False) or (order_flg == 1)) and long_order_count < self.max_orders and pos == 0 and onLoop == True and side == None:
                    stp = 0
                    order_flg = 0
                    counter = 0
                    long_order_count = 1
                    short_order_count = 0
                    pos = 1
#
                    lot,position = self.calculate_lot(df_candleStick, self.margin, self.risk, entryTerm)
                    if (lot == -1):
                        continue 
                    long_order_lots = lot
                    short_order_lots = 0.00
#                       
                    print(datetime.datetime.now())
                    print("market BUY order Lot=",lot)
                    self.order.market(size=lot, side="BUY")
                    message = "bitFlyer_Bot(BTCJPY) Long entry Lot=" + "{:.3f}".format(lot) + "@price={}".format(best_ask)
                    self.lineNotify(message)
                    logger.info(message)
                    if (lastPositionAsk == 9999999.99 or lastPositionAsk < best_ask):
                        lastPositionAsk = best_ask
                    if (lastPositionBid == 0.00 or lastPositionBid > best_bid):
                        lastPositionBid = best_bid
                    Longposition = lastPositionBid
                    onLoop = False
                    pre_position = position
                    #time.sleep(5)
#
                if judgement[2] and long_order_count > 0 and onLoop == True and self.my_round((best_bid - Longposition),2) > getProfit:
                    #ロングクローズ
                    stp = 0
                    counter = 0
                    profitPos = int(position)
                    okOrder = False
                    print(datetime.datetime.now())
                    print("market SELL(Long Close) order Lot=",long_order_lots)
                    self.order.market(size=long_order_lots,side="SELL")
                    okOrder = True
                    doOrder = False
                    stp = 0
                    pos = 0
                    long_order_count = 0
                    mes = None
                    if (profitPos>0): mes = " +Profit"
                    else: mes = " -Loss"
                    message = "bitFlyer_Bot(BTCJPY) Long Close Lot:{}, Price:{}, pl:{:,.0f}, Result:{}".format(long_order_lots, best_ask, profitPos, mes)
                    ### comment because od file sizr bigger fileName = self.describePLForNotification(pl, df_candleStick)
                    ### comment because od file sizr bigger self.lineNotify(message,fileName)
                    self.lineNotify(message)
                    logger.info(message)
                    long_order_lots = 0.0000
                    lastSide = -1
                    if (lastPositionAsk < best_ask):
                        lastPositionAsk = best_ask
                    if (lastPositionBid > best_bid):
                        lastPositionBid = best_bid
                    onLoop = False
                    #time.sleep(5)
                if judgement[3] and short_order_count > 0 and onLoop == True and self.my_round((Shortposition - best_ask),2) > getProfit:
                    #ショートクローズ
                    stp = 0
                    counter = 0
                    profitPos = int(position)
                    okOrder = False
                    doOrder = False
                    stp = 0
                    print(datetime.datetime.now())
                    print("market BUY(Short Close) order Lot=",short_order_lots)
                    self.order.market(size=short_order_lots, side="BUY")
                    okOrder = True
                    pos = 0
                    short_order_count = 0
                    mes = None
                    if (profitPos>0): mes = " +Profit"
                    else: mes = " -Loss"
                    message = "bitFlyer_Bot(BTCJPY) Short Close Lot:{}, Price:{}, pl:{:,.0f}, Result:{}".format(short_order_lots, best_bid, profitPos, mes)
                    ### comment because od file sizr bigger fileName = self.describePLForNotification(pl, df_candleStick)
                    ### comment because od file sizr bigger self.lineNotify(message,fileName)
                    logger.info(message)
                    self.lineNotify(message)
                    short_order_lots = 0.00
                    lastSide = 1
                    if (lastPositionAsk < best_ask):
                        lastPositionAsk = best_ask
                    if (lastPositionBid > best_bid):
                        lastPositionBid = best_bid
                    onLoop = False
                    pre_position = position
                    #time.sleep(5)
######
                pre_ask = best_ask
                pre_bid = best_bid
                ### クローズ(Timeout)
                
                if (counter > 12*24 and onLoop == True):
                    pos = 0
                    counter = 0
                    order_flg = 0
                    okOrder = True
                    if (long_order_count >= self.max_orders):
                        long_order_count = 0
                        ##long_order_lots = 0.00
                    if (short_order_count >= self.max_orders):
                        short_order_count = 0
                        ##short_order_lots = 0.00
                    lastPositionAsk = 9999999.99
                    lastPositionBid = 0.00
                    mes = None
                    time.sleep(10)
#####
            if(position ==0): time.sleep(10)
            message = "Waiting for channelbreaking."
            if (datetime.datetime.now().minute % 60 == 0):
                if (repFlag):
                    crt_balance , keep_rate, position = self.bitflyer_collateral()
                    profit = crt_balance - pre_balance
                    if (profit == 0):
                        mes = "...Drawing"
                    elif (profit > 0):
                        mes = "...Winning"
                    else:
                        mes = "...Lossing"
                    message = "bitFlyer_Bot(BTCJPY) Current Profit Balance:{:,},  Pre_Balance:{:,},  Profit:{:,}, Position{:,.0f},  Risk{:.2%},  Result:{}".format(crt_balance, pre_balance, profit, position, keep_rate, mes)
                    print(message)
                    if (pre_balance < crt_balance):
                        pre_balance = crt_balance
                    repFlag = False
                if(message != "Waiting for channelbreaking."):
                	self.lineNotify(message)
                	logger.info(message)
            else:
                repFlag = True
#注文処理をまとめている
class Order:
    def __init__(self):
        self.product_code = "FX_BTC_JPY"
        self.key = '652Sn8QoMLj8ibEmhu3ero'
        self.secret = 'hPFOfgiEcSuO8cn6RhTOLGeAsHD/1f5QLWieACuEZDQ='
        self.api = pybitflyer.API(self.key, self.secret)

    def market(self, side, size, minute_to_expire= None):
        print("Order: Market. Side : {} Lots : {}".format(side, size))
        #return False
        response = {"status": "internalError in order.py"}
        try:
            response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
        except:
            pass
        i=0
        while "status" in response:
            try:
                response = self.api.sendchildorder(product_code=self.product_code, child_order_type="MARKET", side=side, size=size, minute_to_expire = minute_to_expire)
            except:
                pass
            time.sleep(3)
            i=i+1
            if(i>10):
            	break;
        return response

if __name__ == '__main__':
    #とりあえず5分足，5期間安値・高値でエントリー，クローズする設定
    channelBreakOut = ChannelBreakOut()
    channelBreakOut.entryTerm = 15
    channelBreakOut.closeTerm = 15
    channelBreakOut.rangeTh = 5000
    channelBreakOut.rangeTerm = 15
    channelBreakOut.waitTerm = 60
    channelBreakOut.waitTh = 1000
    channelBreakOut.candleTerm = "5T"
    channelBreakOut.cost = 0.01
    channelBreakOut.risk = 0.3
    channelBreakOut.max_orders = 1
    channelBreakOut.margin = 4

    #実働
    channelBreakOut.loop(channelBreakOut.entryTerm, channelBreakOut.closeTerm, channelBreakOut.rangeTh, channelBreakOut.rangeTerm, channelBreakOut.waitTerm, channelBreakOut.waitTh,channelBreakOut.candleTerm)
    
