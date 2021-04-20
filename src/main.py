import time
from common import *
from graph import *

tokens = json.load(open('tokens.json'))
tokenIn = tokens['token0'] #BNB
tokenOut = tokenIn
amountIn = int(1e17) #.01 BNB
maxHops = 6
currentPairs = []
path = [tokenIn]
bestTrades = []

def takeTrade(trade):
    route = [Web3.toChecksumAddress(t['address']) for t in trade['path']]
    to = Web3.toChecksumAddress(config['address'])
    deadline = int(time.time() + 500)
    tx = router.functions.swapExactTokensForTokens(
        amountIn,
        amountIn,
        route,
        to,
        deadline
    ).buildTransaction({
        'from': address,
        'value': 0,
        'gasPrice': int(10e9),
        'gas': 1500000,
        'nonce': w3.eth.getTransactionCount(address)
    })
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
    try:
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return txhash.hex()
    except:
        return None

def main(pairs):
    try:
        updateReserves(pairs)
    except  Exception as e:
        print('error updating reserves')
        return
    trades = findTrades(pairs, tokenIn, tokenOut, amountIn, maxHops, currentPairs, path, bestTrades)
    if len(trades) == 0:
        return
    trade = trades[0] 
    print('Maximum Profit:', trade['profit']/pow(10, 18))
    print([x['symbol'] for x in trade['path']])
    if trade['profit'] > 0:
        tx = takeTrade(trade)
        print('tx:', tx)
        time.sleep(500)

if __name__ == "__main__":
    pairs = buildGraph(tokens)
    while(1):
        try:
            main(pairs)
        except Exception as e:
            print('exception:', e)
            raise
