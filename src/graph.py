from common import *

d997 = Decimal(997)
d1000 = Decimal(1000)

def toInt(n):
    return Decimal(int(n))

def getEaEb(tokenIn, pairs):
    Ea = None
    Eb = None
    idx = 0
    tokenOut = tokenIn.copy()
    for pair in pairs:
        if idx == 0:
            if tokenIn['address'] == pair['tokenA']['address']:
                tokenOut = pair['tokenB']
            else:
                tokenOut = pair['tokenA']
        if idx == 1:
            Ra = pairs[0]['reserveA']
            Rb = pairs[0]['reserveB']
            if tokenIn['address'] == pairs[0]['tokenB']['address']:
                temp = Ra
                Ra = Rb
                Rb = temp
            Rb1 = pair['reserveA']
            Rc = pair['reserveB']
            if tokenOut['address'] == pair['tokenB']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['tokenA']
            else:
                tokenOut = pair['tokenB']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        if idx > 1:
            Ra = Ea
            Rb = Eb
            Rb1 = pair['reserveA']
            Rc = pair['reserveB']
            if tokenOut['address'] == pair['tokenB']['address']:
                temp = Rb1
                Rb1 = Rc
                Rc = temp
                tokenOut = pair['tokenA']
            else:
                tokenOut = pair['tokenB']
            Ea = toInt(d1000*Ra*Rb1/(d1000*Rb1+d997*Rb))
            Eb = toInt(d997*Rb*Rc/(d1000*Rb1+d997*Rb))
        idx += 1
    return Ea, Eb

def sortTrades(trades, newTrade):
    trades.append(newTrade)
    return sorted(trades, key = lambda x: x['profit'])

def findTrades(pairs, tokenIn, tokenOut, amountIn, maxHops, currentPairs, path, bestTrades, count=4):
    for i in range(len(pairs)):
        newPath = path.copy()
        pair = pairs[i]
        if not pair['tokenA']['address'] == tokenIn['address'] and not pair['tokenB']['address'] == tokenIn['address']:
            continue
        if pair['reserveA'] / pow(10, pair['tokenA']['decimal']) < 1 or pair['reserveB']/pow(10, pair['tokenB']['decimal']) < 1:
            continue
        if tokenIn['address'] == pair['tokenA']['address']:
            tempOut = pair['tokenB']
        else:
            tempOut = pair['tokenA']
        newPath.append(tempOut)
        if tempOut['address'] == tokenOut['address'] and len(path) >2:
            # get virtual reserves through path           
            Ea, Eb = getEaEb(tokenOut, currentPairs + [pair])
            newTrade = {'route': currentPairs + [pair], 'path': newPath, 'Ea': Ea, 'Eb': Eb}
            if Ea and Eb and Ea < Eb:
                ## add amount optimization here
                newTrade['amountOut'] = getAmountOut(amountIn, Ea, Eb)
                newTrade['profit'] = newTrade['amountOut'] - amountIn
                newTrade['p'] = int(newTrade['profit'])/pow(10, tokenOut['decimal'])
                bestTrades = sortTrades(bestTrades, newTrade)
                bestTrades.reverse()
                bestTrades = bestTrades[:count]
        elif maxHops > 1 and len(pairs) > 1:
            pairsExcludingThisPair = pairs[:i] + pairs[i+1:]
            bestTrades = findTrades(pairsExcludingThisPair, tempOut, tokenOut, amountIn, maxHops-1, currentPairs + [pair], newPath, bestTrades, count)
    return bestTrades

def updateReserves(pairs):
    for pair in range(len(pairs)):
        reserves = getReserves(FACTORY_ADDRESS, pairs[pair]['tokenA']['address'], pairs[pair]['tokenB']['address'])
        pairs[pair]['reserveA'], pairs[pair]['reserveB'] = reserves

def buildGraph(tokens):
    pairs = {}

    for tokenA in tokens:
        for tokenB in tokens:
            if tokens[tokenA]['address'] == tokens[tokenB]['address']:
                continue
            else:
                pair_address = factory.functions.getPair(
                    Web3.toChecksumAddress(tokens[tokenA]['address']), Web3.toChecksumAddress(tokens[tokenB]['address'])
                ).call()
                if int(pair_address, 0) != (0):
                    pair = {
                        'address': pair_address, 'tokenA': tokens[tokenA], 'tokenB': tokens[tokenB], 'reserveA': 0, 'reserveB': 0
                    }
                    pairs[pair_address] = pair
    pairs_list = []

    for pair in pairs:
        pairs_list.append(pairs[pair])
    
    return pairs_list