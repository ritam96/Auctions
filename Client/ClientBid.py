import hashlib
import datetime


class ClientBid(object):
    def __init__(self, index, timestamp, previousHash, nonce = 0):
        self.index = index
        self.timestamp = str(timestamp)
        self.nonce = nonce
        self.previousHash = previousHash
        self.hash = self.hashFunction()
        
    
    def hashFunction(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') + str(self.timestamp).encode('utf-8') + str(self.nonce).encode('utf-8') + str(self.previousHash).encode('utf-8'))
        return sha.hexdigest()

    def mine(self, difficulty):
        print("Mining block " + str(self.index))
        zeros = ['0'] * difficulty
        while list(self.hash)[:difficulty] != zeros:
            #incrementing the nonce value everytime the loop runs.
            self.nonce += 1

            #recalculating the hash value
            self.hash = self.hashFunction()
        print('Block mined: ' + self.hash)
