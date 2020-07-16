# Module 1 - Create a blockchain
# Install requests==2.18.4

# Install flask
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a blockchain

# Definire la nuova classe

class Blockchain:
    def __init__(self):
        '''Metodo costruttore __init__'''
        self.chain =[]
        self.transactions = []
        self.create_block(proof = 1, previous_hash ='0')
        self.nodes = set()
    def create_block(self, proof, previous_hash):
        '''Funzione per creare un nuovo blocco'''
        #Creo un dizionario che racchiuda le varie caratteristiche di un blocco
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions}
        #Aggiungo il blocco alla catena di blocchi
        self.transactions = []
        self.chain.append(block)
        return block
    def get_previous_block(self):
        '''Funzione per ottenere l'ultimo blocco'''
        return self.chain[-1]
    def proof_of_work(self, previous_proof):
        new_proof=1
        check_proof=False
        while check_proof==False:
            hash_operation=hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4]=='0000':
                check_proof=True
            else :
                new_proof=new_proof+1
        return new_proof
    def hash(self,block):
        '''Funzione per ottenere l'hash del blocco'''
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def is_chain_valid(self,chain):
        '''Funzione per verificare se il blocco nuovo è quello corretto'''
        previous_block=chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash']!=self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation=hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '00000':
                return False
            previous_block = block
            block_index += 1
        return True
    def add_transactions(self, sender,receiver, amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_lenght = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code==200:
               lenght = response.json()['lenght']
               chain = response.json()['chain']
               if lenght >max_lenght and self.is_chain_valid(chain):
                   max_lenght = lenght
                   longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
# Part 2 - Mining Blockchain
# Creo ora la web app che supporti la blockchain
app = Flask(__name__)

# Creating an address for the node on Port 5000
node_address = str(uuid4()).replace('-','')


# Creo ora la blockchain
blockchain = Blockchain()

# Mining del primo blocco
# Creo la prima GET request per minare il blocco
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    '''Funzione per minare un blocco'''
    #Devo prima prendere l'ultimo blocco
    previous_block = blockchain.get_previous_block()
    #Poi prendo la sua prova
    previous_proof = previous_block['proof']
    #Ora cerco di trovare un hash del blocco sotto il target richiesto
    proof = blockchain.proof_of_work(previous_proof)
    #Aggiungo le transazioni alla blockchain
    blockchain.add_transactions(sender = node_address,receiver = 'Michele', amount = 1)
    #Richiamo l'hash del precedente blocco
    previous_hash = blockchain.hash(previous_block)
    #Creo il blocco nuovo utilizzando anche l'hash del precedente
    block = blockchain.create_block(proof,previous_hash)
    #Creo il messaggio di successo per aver creato il blocco
    current_hash = blockchain.hash(block)
    response = {'message':'Congratulations, you just mined a block!',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'hash':current_hash,
                'previous_hash':block['previous_hash'],
                'transactions':block['transactions']}
    #Ho bisogno ora che mi venga restituita la risposta
    return jsonify(response), 200

#Ora voglio visualizzare l'intera blockchain
@app.route('/get_chain',methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'lenght': len(blockchain.chain)}
    return jsonify(response), 200
@app.route('/is_valid',methods=['GET'])
def is_valid():
    response ={'Is it valid?': str(blockchain.is_chain_valid(blockchain.chain))}
    return jsonify(response), 200

# Adding a new transaction to the Blockchain
@app.route('/add_transaction',methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all (key in json for key in transaction_keys):
        return 'Some element of the transaction are missing', 400
    index = blockchain.addtransactions(json['sender'],json['receiver'], json['amount'])
    response={'message':f'This transaction will be added to block{index}'}
    return jsonify(response), 201

#Part 3 -Decentralizing our Blockchain 

# Connecting new nodes
@app.route('/connect_node',methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No node',400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'All the nodes are now connected. The Tovacoin blockchain now contains the following nodes:',
              'total_nodes':list(blockchain.nodes)}
    return jsonify(response),201

#Replacing the chain by the longest chain if needed
@app.route('/replace_chain',methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response={'message':'The nodes had different chain so the chain was replaced with the longest one',
                  'new_chain':blockchain.chain}
    else:
        response={'message': 'All good, the chain is the largest one',
                  'actual_chain':blockchain.chain}
    return jsonify(response),200
#Ora facciamo partire l'app
app.run(host="0.0.0.0",port=5001)


    



