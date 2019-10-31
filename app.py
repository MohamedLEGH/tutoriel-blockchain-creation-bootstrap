import time
import atexit
import requests
import json
import os

# flask imports
from flask import Flask, request, jsonify, render_template

#  files imports
from block import Block
from chain import Blockchain
from transaction import Transaction
from key import BitcoinAccount

# wallet generation

wallet = BitcoinAccount()
address = wallet.to_address()
file_name = "wallets/" + address + ".json"
wallet.to_file(file_name)

# blockchain data

difficulty = 4
blockchain = None

node = Flask(__name__)

# config data

portServer = 5000
hostIP = '0.0.0.0'


# set of ip address of the participating members of the network
peers = set()


@node.template_filter('timestamp_to_utc')
def timestamp_to_utc(timestamp):
    return time.asctime(time.gmtime(timestamp))


@node.route('/', methods=['GET'])
def hello():
    global blockchain
    chain = []
    lastblock = None
    myaccount = 0
    allaccounts = {}
    pending_tx = []
    if blockchain:
        chain = blockchain.to_dict()
        lastblock = chain[-1]
        pending_tx = blockchain.tx_pool

    return render_template('interface.html',
                           address=address,
                           chain=chain,
                           lastblock=lastblock,
                           allaccounts=allaccounts,
                           myaccount=myaccount,
                           peers=peers,
                           pending_tx=pending_tx)

# time.asctime(time.gmtime())


@node.route('/chain', methods=['GET'])
def get_chain():
    global blockchain
    if blockchain:
        chain = blockchain.to_dict()
        print("chain is")
        print(chain)
        return jsonify({"length": len(chain), "chain": chain}), 200
    else:
        return jsonify({"length": 0, "chain": []}), 404


@node.route('/lastblock', methods=['GET'])
def lastblock():
    global blockchain
    if request.method == 'GET':
        last_block = blockchain.blocks_list[-1].to_dict()
        return jsonify(last_block), 200


@node.route('/lastblock/transactions', methods=['GET'])
def transactions_lastblock():
    global blockchain
    if request.method == 'GET':
        transactions = blockchain.blocks_list[-1].transactions
        return jsonify(transactions), 200


@node.route('/lastblock/transactions/<int:id>', methods=['GET'])
def transaction_lastblock_by_id(id):
    global blockchain
    if request.method == 'GET':
        transaction = blockchain.blocks_list[-1].transactions[id]
        return jsonify(transaction), 200


@node.route('/block/<int:id>', methods=['GET'])
def block(id):
    global blockchain
    if request.method == 'GET':
        block = blockchain.get_block(id).to_dict()
        return jsonify(block), 200


@node.route('/block/<int:id>/transactions', methods=['GET'])
def block_transactions(id):
    global blockchain
    if request.method == 'GET':
        transactions = blockchain.get_block(id).get_transactions()
        return jsonify(transactions), 200


@node.route('/block/<int:id_block>/transactions/<int:id_transaction>', methods=['GET'])
def block_transaction_by_id(id_block, id_transaction):
    global blockchain
    if request.method == 'GET':
        transaction = blockchain.get_block(
            id_block).get_transaction(id_transaction)
        return jsonify(transaction), 200


@node.route('/create_new_chain', methods=['POST'])
def create_chain():
    global blockchain
    blockchain = Blockchain(difficulty, address)
    blockchain.create_genesis_block()
    return "Success\n", 200


@node.route('/mine_block', methods=['POST'])
def mine():
    global blockchain
    if blockchain == None:
        blockchain = Blockchain(difficulty)
        blockchain.create_genesis_block()
        return "Blockchain created \n", 200
    else:
        blockchain.mine_block()
        return "Block mined\n", 200


@node.route('/transaction', methods=['POST'])
def new_transaction():
    global blockchain
    if blockchain:
        sender = address  # tx_data["sender"]
        tx_data = request.get_json()
        receiver = tx_data["receiver"]
        amount = tx_data["amount"]
        blockchain.add_transaction(sender, receiver, amount)
        return "Success\n", 200
    else:
        return "No blockchain, please create a new chain or get the chain from another peer"


# endpoint to add new peers to the network.
@node.route('/node', methods=['POST'])
def register_new_peer():
    data = request.get_json()
    node = data["node_url"]
    peers.add(node)
    return "Success\n", 201


@node.route('/nodes', methods=['GET'])
def get_peers():
    return jsonify(list(peers)), 201


@node.route('/consensus', methods=['POST'])
def consensus():
    """
    Our simple consensus algorithm. If a longer valid chain is found, our chain is replaced with it.
    
    ps : To request a node do: 
    r = requests.get("ip_node:500/chain")
    chain = r.json
    """
    global blockchain
    # todo


# endpoint to add a block mined by someone else to the node's chain.
@node.route('/add_block', methods=['POST'])
def add_block():
    if blockchain:
        block_data = request.get_json()
        block = Block(block_data["index"],
                      block_data["previous_hash"],
                      block_data["nonce"], block_data["timestamp"],
                      block_data["transactions"],
                      block_data["hashval"],
                      block_data["miner"],
                      block_data["signature"])
        blockchain.add_block(block)
        return "Block added to the chain", 200
    else:
        return "No blockchain, please create a new chain or get the chain from another peer"

# endpoint to query unconfirmed transactions
@node.route('/pending_transactions', methods=['GET'])
def get_pending_transactions():
    if blockchain:
        return jsonify(blockchain.tx_pool)
    else:
        return "No blockchain, please create a new chain or get the chain from another peer"

# endpoint to query an unconfirmed transaction by id
@node.route('/pending_transactions/<int:id>', methods=['GET'])
def get_pending_transaction(id):
    if blockchain:
        return jsonify(blockchain.tx_pool[id])
    else:
        return "No blockchain, please create a new chain or get the chain from another peer"



def clean_file():
    os.remove(file_name)


atexit.register(clean_file)

if __name__ == '__main__':
    node.run(debug=False, port=portServer, host=hostIP)
