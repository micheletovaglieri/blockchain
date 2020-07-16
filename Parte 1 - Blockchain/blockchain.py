# Module 1 - Create a blockchain
# Install flask
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a blockchain

# Definire la nuova classe

class Blockchain:
    def __init__(self):
        '''Metodo costruttore __init__'''
        self.chain =[]
        self.create_block(proof = 1, previous_hash ='0')
    def create_block(self, proof, previous_hash):
        '''Funzione per creare un nuovo blocco'''
        #Creo un dizionario che racchiuda le varie caratteristiche di un blocco
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash}
        #Aggiungo il blocco alla catena di blocchi
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
    
# Part 2 - Mining Blockchain
# Creo ora la web app che supporti la blockchain
app = Flask(__name__)

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
                'previous_hash':block['previous_hash']}
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
#Ora facciamo partire l'app
app.run(host="0.0.0.0",port=5000)
