import web3
import contract_abi
import requests
import argparse
from web3 import Web3, HTTPProvider
from decimal import Decimal

def get_balance(args):
	# Connecting to the Infura node server
	w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/' + args.p))

	# Fetching the balance of Ether
	conversion_rate = w3.toWei('1', 'ether')
	ether_balance = w3.eth.getBalance(args.a[0]) / Decimal(conversion_rate)
	print(ether_balance)

	# Fetching the balance of OmiseGo ERC20 Token
	contract = w3.eth.contract(address = args.a[1], abi = contract_abi.abi)
	omg_balance = contract.functions.balanceOf(args.a[0]).call()
	decimal = contract.functions.decimals().call()
	omg_balance = omg_balance / Decimal(10 ** decimal)
	print(omg_balance)

	# Fetching the USD conversion rate
	response = requests.get(url = 'https://bittrex.com/api/v1.1/public/getmarketsummaries')
	if (response.status_code == 200):
		results = response.json()['result']
		usdt_eth = list(filter(lambda x: (x['MarketName'] == 'USDT-ETH'), list(results)))[0]['Last']
		usdt_omg = list(filter(lambda x: (x['MarketName'] == 'USDT-OMG'), list(results)))[0]['Last']

	# Converting Ether and OmiseGo balance in USD
	eth_bal_usd = round(ether_balance * Decimal(usdt_eth), 2)
	omg_bal_usd = round(omg_balance * Decimal(usdt_omg), 2)
	print(eth_bal_usd)
	print(omg_bal_usd)

if (__name__== "__main__"):
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("-a", nargs='+', help="Address of the account owner, followed by smart contract's address.")
	arg_parser.add_argument("-p", help="Infura key.")
	args = arg_parser.parse_args()
	get_balance(args)



