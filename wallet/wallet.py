# Import dependencies
import subprocess
import json
import os
from dotenv import load_dotenv
from bit import wif_to_key
from web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
from web3.middleware import geth_poa_middleware
from eth_account import Account

# Load and set environment variables
load_dotenv()
mnemonic = os.getenv("mnemonic")


# Import constants.py and necessary functions from bit and web3
from constants import *


# Create a function called `derive_wallets`
def derive_wallets(coin):
    command = f'php derive -g --mnemonic=mnemonic --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --numderive=3 --coin={coin} --format=json' #f at start so we can add variables in string
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate()
    p_status = p.wait()
    return json.loads(output)


# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {BTCTEST: derive_wallets(BTCTEST), ETH: derive_wallets(ETH)}

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin==ETH:
        return Account.privateKeyToAccount(priv_key)
    elif coin==BTCTEST:
        return PrivateKeyTestnet(priv_key)


# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, recipient, amount):
    
    gasEstimate = w3.eth.estimateGas({"from":account.address,"to":recipient,"value":amount})

    if coin==ETH:
        return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
        "chainId": w3.eth.chain_id,
        }
    elif coin==BTCTEST:
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])


# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, recipient, amount):
    if coin == ETH:
        tx = create_tx(coin, account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == BTC:
        tx = create_tx(coin, account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = NetworkAPI.broadcast_tx_testnet(signed)
    return result.hex()


