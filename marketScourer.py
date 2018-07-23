from binance.client import Client
import statistics

def getSymbols(client,marketSymbol): # get symbols for certain market
    symbolList=[]
    for tick in client.get_all_tickers():
        if (tick['symbol'][-3:]==marketSymbol):
            symbolList.append(tick['symbol'])
    return symbolList

def getRSI_BOLL(client,symbol): # get indices for symbol
    closes=[]
    typicalPrices=[]
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
    if nl and l:
        RSI=1.0-1.0/(1.0+(g/ng)/(l/nl))
    else:
        RSI=0.5
    if negFlow:
        MFI=1.0-1.0/(1.0+posFlow/negFlow)
    else:
        MFI=0.5
    mean=statistics.mean(closes)
    std=statistics.stdev(closes)
    Z=(closes[-1]-mean)/std
    return [RSI,Z,MFI]

def printNicely(data):
    print(" SYMBOL\t\tRSI\t\tBOLL\t\tMFI\n ------------------------------------")
    for dat in data:
        print(" "+str(dat[0]).replace('BTC','')+"\t\t"+str(dat[1])[:5]+"\t\t"+str(dat[2])[:5]+"\t\t"+str(dat[3])[:5])
        
def printProgress(i,n):
    progress=int(10.0*float(i)/float(n))
    print("~~~NEXT UPDATE: ["+"1"*progress+"0"*(10-progress)+"]",end='~~~\r')

def checkSymbols(client,symbols):
    strongSell=[]
    sell=[]
    neutral=[]
    buy=[]
    strongBuy=[]
    track=0
    for symbol in symbols:
        [RSI,Z,MFI]=getRSI_BOLL(client,symbol)
        if (RSI>0.8 and Z>2.25): # strong sell
            strongSell.append([symbol,RSI,Z,MFI])
        elif (RSI>0.6 and Z>1.75): # sell
            sell.append([symbol,RSI,Z,MFI])
        elif (RSI<0.2 and Z<-2.25): # strong buy
            strongBuy.append([symbol,RSI,Z,MFI]) 
        elif (RSI<0.4 and Z<-1.75): # buy
            buy.append([symbol,RSI,Z,MFI])       
        else: # neutral
            neutral.append([symbol,RSI,Z,MFI])
        track+=1
        printProgress(track,len(symbols))
    print('\n'*100)
    print("\n==============STRONG BUY==============")
    printNicely(strongBuy)
    print("\n==================BUY=================")
    printNicely(buy)
    print("\n=================SELL=================")
    printNicely(sell)
    print("\n==============STRONG SELL=============")
    printNicely(strongSell)
    print('\n')
