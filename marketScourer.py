from binance.client import Client
import statistics
from mpl_finance import candlestick2_ohlc
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def getSymbols(client,marketSymbol): # get symbols for certain market
    symbolList=[]
    for tick in client.get_all_tickers():
        if (tick['symbol'][-3:]==marketSymbol):
            symbolList.append(tick['symbol'])
    return symbolList

'''def plotCandlesticks(OHLC1,title1,OHLC2,title2):
    [fig,ax]=plt.subplots(2,sharex=True)
    candlestick2_ohlc(ax[0],OHLC1[0],OHLC1[1],OHLC1[2],OHLC1[3],width=.5)
    #ax[0].set_title(title1)
    candlestick2_ohlc(ax[1],OHLC2[0],OHLC2[1],OHLC2[2],OHLC2[3],width=.5)
    #ax[1].set_title(title2)
    plt.show(block=False)'''

def getIndices(client,symbol): # get indices for symbol
    opens=[]
    highs=[]
    lows=[] 
    closes=[]
    typicalPrices=[]
    haCandlesO=[]
    haCandlesH=[]
    haCandlesL=[]
    haCandlesC=[]
    posFlow=0.0
    negFlow=0.0
    ng=0.0
    nl=0.0
    g=0.0
    l=0.0
    sofar=0
    klines=client.get_historical_klines(symbol,'5m','1 hour 40 min ago UTC')
    for kline in klines:
        typicalPrices.append((float(kline[1])+float(kline[2])+float(kline[4]))/3.0)
        if sofar>5:
            if float(kline[4])>=float(kline[1]): # price up
                ng+=1.0
                g+=float(kline[4])-float(kline[1])
            else: # price down
                nl+=1.0
                l+=float(kline[1])-float(kline[4])
            if typicalPrices[-1]>=typicalPrices[-2]: # money flow up
                posFlow+=typicalPrices[-1]*float(kline[5])
            else: # money flow down
                negFlow+=typicalPrices[-1]*float(kline[5])
        sofar+=1
        closes.append(float(kline[4]))
        lows.append(float(kline[3]))
        highs.append(float(kline[2]))
        opens.append(float(kline[1]))
        if sofar>2:
            haCandlesO.append([(closes[-2]+opens[-2])/2.0][0])
            haCandlesH.append([max(float(kline[2]),opens[-1],closes[-1])][0])
            haCandlesL.append([min(float(kline[3]),opens[-1],closes[-1])][0])
            haCandlesC.append([(float(kline[3])+float(kline[2])+opens[-1]+closes[-1])/4.0][0])
    if nl and l:
        RSI=1.0-1.0/(1.0+(g/ng)/(l/nl))
    else:
        RSI=0.5
    if negFlow:
        MFI=1.0-1.0/(1.0+posFlow/negFlow)
    else:
        MFI=0.5
    haCandles=[haCandlesO,haCandlesH,haCandlesL,haCandlesC]
    OHLC=[opens,highs,lows,closes]
    mean=statistics.mean(closes)
    std=statistics.stdev(closes)
    Z=(closes[-1]-mean)/std
    if (haCandlesC[-1]>haCandlesO[-1]) and (closes[-2]<opens[-2]):
        haSwitch=1
    elif (haCandlesC[-1]<haCandlesO[-1]) and (closes[-2]>opens[-2]):
        haSwitch=-1
    else:
        haSwitch=0
    #plotCandlesticks(haCandles,'Heikin-Ashi Candles ('+symbol+')',OHLC,'Candles ('+symbol+')') 
    return [RSI,Z,MFI,haSwitch]

def printNicely(data,market):
    print(" SYMBOL\t\tRSI\t\tBOLL\t\tMFI\t\tHAS\n ----------------------------------------------")
    for dat in data:
        print(" "+str(dat[0]).replace(market,'')+"\t\t"+str(dat[1])[:5]+"\t\t"+str(dat[2])[:5]+"\t\t"+str(dat[3])[:5]+"\t\t"+str(dat[4]))
        
def printProgress(i,n):
    progress=int(10.0*float(i)/float(n))
    print("~~~NEXT UPDATE: ["+"1"*progress+"0"*(10-progress)+"]",end='~~~\r')

def checkSymbols(client,symbols,market):
    strongSell=[]
    sell=[]
    neutral=[]
    buy=[]
    strongBuy=[]
    track=0
    for symbol in symbols:
        [RSI,Z,MFI,haS]=getIndices(client,symbol)
        if (RSI>0.8 and Z>2.25): # strong sell
            strongSell.append([symbol,RSI,Z,MFI,haS])
        elif (RSI>0.6 and Z>1.75): # sell
            sell.append([symbol,RSI,Z,MFI,haS])
        elif (RSI<0.2 and Z<-2.25): # strong buy
            strongBuy.append([symbol,RSI,Z,MFI,haS]) 
        elif (RSI<0.4 and Z<-1.75): # buy
            buy.append([symbol,RSI,Z,MFI,haS])       
        else: # neutral
            neutral.append([symbol,RSI,Z,MFI,haS])
        track+=1
        printProgress(track,len(symbols))
    print('\n'*100)
    print("\n==============STRONG BUY==============")
    printNicely(strongBuy,market)
    print("\n==================BUY=================")
    printNicely(buy,market)
    print("\n=================SELL=================")
    printNicely(sell,market)
    print("\n==============STRONG SELL=============")
    printNicely(strongSell,market)
    print('\n')
