import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request



class Blockchain:
    def __init__(self):
        self.chain = []
        self.currentTransactions = []
        # genesis Block
        # self.new_block(previous_hash=1,proof=100)
        genesis = {"index": len(self.chain) + 1,
                   "timestamp": time(),
                   "transactions": [],
                   "proof": 0,
                   "Previous Hash": "genesisBlock"
                   }
        self.chain.append(genesis)

    def new_block(self, proof, previous_hash):
        block = {"index": len(self.chain) + 1,
                 "timestamp": time(),
                 "transactions": self.currentTransactions,
                 "proof": proof,
                 "Previous Hash": self.hash(self.last_block())
                 }
        self.currentTransactions = []
        self.chain.append(block)
        return block

    def new_transactions(self, sender, article):
        self.currentTransactions.append({"Sender": sender, "Article": article})
        return self.last_block['index'] + 1

    @staticmethod
    def hash(Block):
        Block_string = json.dumps(Block, sort_keys=True)
        blkhash = hashlib.sha256(Block_string.encode).hexdigest()
        return blkhash

    @property
    def last_block(self):
        return self.chain[-1];

    def validblk(self, proof, last_proof, last_hash):
        blk = (str(proof) + str(last_proof), str(last_hash))
        blk_hh = hashlib.sha256(blk.encode).hexdigest()
        return blk_hh[:2] == "00"

    def pow(self, last_block):
        last_proff = last_block['proof']
        last_hash = self.hash(last_block())
        proof = 0
        while self.validblk(last_proff, proof, last_hash) == False:
            proof += 1
        return proof


# instantiate the node
app = Flask(__name__);
# generate a global and unique address for this node
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


# mine
@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block()
    proof = blockchain.pow(last_block)

    blockchain.new_transactions(sender="0", receiver=node_identifier, amount=1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    reponse = {'meesage': 'New Block created',
               'index': block['index'],
               'proof': block['proof'],
               'transactions': block['transactions'],
               'previous_hash': block['Previous Hash']}
    return jsonify(reponse), 200


@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # required fields
    required = ['sender','article']

    if not all(k in values for k in required):
        return 'Missing Values', 400
    # New Transaction
    index = blockchain.new_transactions(values['sender'], values['article'])

    response = {'Message': f'Transaction will be added to a block{index}'}

    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'Chain': blockchain.chain,
        'Length': len(blockchain.chain)
    }
    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=5000,debug= True)
