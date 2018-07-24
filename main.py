from binance.client import Client
from marketScourer import *
from config import *


market='BTC'
print('\n'*100)
client=Client(apikey,seckey)
symbols=getSymbols(client,market)
print(symbols)
while True:
    checkSymbols(client,symbols,market)
