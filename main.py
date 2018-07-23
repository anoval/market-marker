from binance.client import Client
from marketScourer import *
from config import *

print('\n'*100)
client=Client(apikey,seckey)
symbols=getSymbols(client,'BTC')
print(symbols)
while True:
    checkSymbols(client,symbols)
