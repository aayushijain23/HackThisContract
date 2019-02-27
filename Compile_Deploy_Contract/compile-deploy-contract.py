# from solc import install_solc
# install_solc('v0.4.25')
import argparse
import web3
from web3 import Web3, HTTPProvider
from solc import compile_source

contract = '''
pragma solidity >=0.4.22 <0.6.0;

contract MyToken {
	uint8 public decimals = 18;
	uint256 public totalSupply;

	// This creates an array with all balances
	mapping (address => uint256) public balanceOf;
	mapping (address => mapping (address => uint256)) public allowance;

	// This generates a public event on the blockchain that will notify clients
	event Transfer(address indexed from, address indexed to, uint256 value);
	
	// This generates a public event on the blockchain that will notify clients
	event Approval(address indexed _owner, address indexed _spender, uint256 _value);

	/**
	 * Constructor function
	 *
	 * Initializes contract with initial supply tokens to the creator of the contract
	 */
	constructor() public {
		totalSupply = 1 * 10 ** uint256(decimals);  // Update total supply with the decimal amount
		balanceOf[msg.sender] = totalSupply;        // Give the creator all initial tokens
	}

	/**
	 * Internal transfer, only can be called by this contract
	 */
	function _transfer(address _from, address _to, uint _value) internal {
		require(_to != address(0x0));							// Prevent transfer to 0x0 address. Use burn() instead
		require(balanceOf[_from] >= _value);					// Check for overflows        
		require(balanceOf[_to] + _value >= balanceOf[_to]); 	// Save this for an assertion in the future
		uint previousBalances = balanceOf[_from] + balanceOf[_to];
		balanceOf[_from] -= _value;
		balanceOf[_to] += _value;
		emit Transfer(_from, _to, _value);
		assert(balanceOf[_from] + balanceOf[_to] == previousBalances);  // Asserts are used to use static analysis to find bugs in your code. They should never fail
	}

	/**
	 * Transfer tokens
	 *
	 * Send `_value` tokens to `_to` from your account
	 *
	 * @param _to The address of the recipient
	 * @param _value the amount to send
	 */
	function transfer(address _to, uint256 _value) public returns (bool success) {
		_transfer(msg.sender, _to, _value);
		return true;
	}

	/**
	 * Transfer tokens from other address
	 *
	 * Send `_value` tokens to `_to` on behalf of `_from`
	 *
	 * @param _from The address of the sender
	 * @param _to The address of the recipient
	 * @param _value the amount to send
	 */
	function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
		require(_value <= allowance[_from][msg.sender]);     // Check allowance
		allowance[_from][msg.sender] -= _value;
		_transfer(_from, _to, _value);
		return true;
	}

	/**
	 * Set allowance for other address
	 *
	 * Allows `_spender` to spend no more than `_value` tokens on your behalf
	 *
	 * @param _spender The address authorized to spend
	 * @param _value the max amount they can spend
	 */
	function approve(address _spender, uint256 _value) public returns (bool success) {
		allowance[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}
}
'''

def compile_contract():
	compiled_contract = compile_source(contract)
	contract_interface = compiled_contract['<stdin>:MyToken']
	print(contract_interface)
	return contract_interface

def deploy_contract(args, contract_interface):
	# Connecting to the Infura node server
	w3 = Web3(HTTPProvider('https://rinkeby.infura.io/' + args.p))
	# Set pre-funded account as sender
	w3.eth.defaultAccount = args.a
	# Instantiate and deploy contract
	MyToken = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
	# Submit the transaction that deploys the contract
	deploy_tx = MyToken.constructor().buildTransaction({
		'nonce': 0
		})
	signed = w3.eth.account.signTransaction(deploy_tx, args.s)
	tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
	# Wait for the transaction to be mined, and get the transaction receipt
	print('Waiting for transaction to be mined')
	tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
	print(tx_receipt)
	return tx_receipt.contractAddress

if (__name__== "__main__"):
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("-p", help="Infura key for Rinkeby.")
	arg_parser.add_argument("-s", help="Private key of the wallet.")
	arg_parser.add_argument("-a", help="Wallet address.")
	args = arg_parser.parse_args()
	contract_interface = compile_contract()
	deploy_contract(args, contract_interface)
