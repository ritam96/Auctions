import hashlib
import datetime

class Auction(object):

    def __init__(self, startingPrice, image = "https://tinyurl.com/ydy8sbnd", description = "No description"):
        self.image = image
        self.desc = description
        self.currentPrice = None
        self.startingPrice = None
        self.bidChain = [self.createGenesisBid()]

    def hashFunction(self):
        sha = hashlib.sha256()
        sha.update(str(self.image).encode('utf-8') + str(self.desc).encode('utf-8') + str(self.currentPrice).encode('utf-8'))
        return sha.hexdigest()

    def createGenesisBid(self):
        # Manually construct a block with
        # index zero and arbitrary previous hash (we'll use the auction hash)
        return Bid(0, datetime.datetime.now(), "Genesis Bid" , 0, self.hashFunction())

    def createNextBid(self, lastBid, bidder, value):
        index = lastBid.index + 1
        timestamp = datetime.datetime.now()
        bidder = bidder
        hash = lastBid.hash
        return Bid(index, timestamp, bidder, value, hash)


class Bid(object):
    def __init__(self, index, timestamp, bidder, value, previousHash):
        self.index = index
        self.timestamp = timestamp
        self.bidder = bidder
        self.value = value
        self.nonce = 0
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

    