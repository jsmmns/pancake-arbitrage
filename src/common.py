import json
from decimal import Decimal
from web3 import Web3

config = json.load(open('config.json'))
address = Web3.toChecksumAddress(config['address'])
privkey = config['privatekey']

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org:443'))

factoryABI = json.load(open('abi/IUniswapV2Factory.json'))['abi']
pairABI = json.load(open('abi/IUniswapV2Pair.json'))['abi']
routerABI = json.load(open('abi/IUniswapV2Router02.json'))['abi']
erc20abi = json.load(open('./abi/erc20.abi'))

#Pancake Swap Contracts
ROUTER_ADDRESS = Web3.toChecksumAddress('0x05fF2B0DB69458A0750badebc4f9e13aDd608C7F')
FACTORY_ADDRESS = Web3.toChecksumAddress('0xBCfCcbde45cE874adCB698cC183deBcF17952812')
router = w3.eth.contract(
    address=ROUTER_ADDRESS, abi=routerABI
)
factory = w3.eth.contract(
    address=FACTORY_ADDRESS, abi=factoryABI
)

def approve(tokenAddress, contractAddress, amount):
    bep20Token = w3.eth.contract(address=tokenAddress, abi=erc20abi)
    approved_amount = bep20Token.functions.allowance(address, contractAddress).call()
    if approved_amount >= amount:
        return True
    try:
        tx = bep20Token.functions.approve(contractAddress, 2**256-1).buildTransaction({
            'from': address,
            'value': 0,
            'gasPrice': int(20e9),
            'gas': 1500000,
            "nonce": w3.eth.getTransactionCount(address),
            })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=privkey)
        txhash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        print('approving... ', txhash.hex())
        w3.eth.waitForTransactionReceipt(txhash.hex(), timeout=6000)
    except Exception as e:
        print('exception:', e)
        return False
    return True

def sortTokens(addressA, addressB):
    if (addressA < addressB):
        return (addressA, addressB)
    else:
        return (addressB, addressA)

def getReserves(factoryAddress, aAddress, bAddress):
    token0address = sortTokens(aAddress, bAddress)[0]
    reserves = (0,0)
    uni_pair_address = factory.functions.getPair(
        Web3.toChecksumAddress(aAddress), 
        Web3.toChecksumAddress(bAddress)).call()
    uni_pair = w3.eth.contract(
        address=Web3.toChecksumAddress(uni_pair_address), abi=pairABI)
    reserves = uni_pair.functions.getReserves().call()
    if token0address == aAddress:
        return (reserves[0], reserves[1])
    else:
        return (reserves[1], reserves[0])

def getAmountOut(amountIn, reserveIn, reserveOut):
    amountInWithFee = Decimal(amountIn) * Decimal(997) 
    numerator = amountInWithFee * reserveOut
    demominator = (reserveIn * Decimal(1000) + amountInWithFee)
    amountOut = numerator / demominator
    return float(amountOut) 

