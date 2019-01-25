import hashlib
import datetime
import uuid
from ClientBid import ClientBid


class Auction(object):
    def __init__(self, startingPrice, deltaTime, exposedIdentities, englishAuction = False, blindAuction = False, maximumNumberBids = None, maximumNumberBidders = None, image = "https://tinyurl.com/ydy8sbnd", description = "No description"):

        self.auctionID = str(uuid.uuid4())
        self.image = image
        self.desc = description
        self.currentPrice = None
        self.startingPrice = None
        self.englishAuction = englishAuction
        self.blindAuction = blindAuction
        self.exposedIdentities = exposedIdentities
        self.maximumNumberBids = maximumNumberBids
        self.maximumNumberBidders = maximumNumberBidders
        self.endTime = datetime.datetime.now() + datetime.timedelta(hours=deltaTime)
        self.ended = False
        self.bidChain = [self.createGenesisBid()]

    def hashFunction(self):
        sha = hashlib.sha256()
        sha.update(str(self.image).encode('utf-8') + \
        str(self.desc).encode('utf-8') + \
        str(self.currentPrice).encode('utf-8') + \
        str(self.auctionID).encode('utf-8') + \
        str(self.englishAuction).encode('utf-8') + \
        str(self.blindAuction).encode('utf-8') + \
        str(self.exposedIdentities).encode('utf-8'))
        return sha.hexdigest()

    def createGenesisBid(self):
        # Manually construct a block with
        # index zero and arbitrary previous hash (we'll use the auction hash)
        return Bid(0, str(datetime.datetime.now()), "Genesis Bid" , 0, self.hashFunction())

    def createNextBid(self, lastBid, bidder, value):
        index = lastBid.index + 1
        timestamp = str(datetime.datetime.now())
        bidder = bidder
        hash = lastBid.hash
        return Bid(index, timestamp, bidder, value, hash)

    def getLastBid(self):
        bid = self.bidChain[len(self.bidChain)-1]
        return ClientBid(bid.index, bid.timestamp, bid.previousHash, bid.nonce)

    def data(self):
        result = {}
        result["image"] = self.image
        result["auctionID"] = self.auctionID
        result["desc"] = self.desc
        result["currentPrice"] = self.currentPrice
        result["startingPrice"] = self.startingPrice
        return result 


class Bid(object):
    def __init__(self, index, timestamp, bidder, value, previousHash):
        self.index = index
        self.timestamp = str(timestamp)
        self.bidder = bidder
        self.value = value
        self.nonce = 0
        self.previousHash = previousHash
        self.hash = self.hashFunction()
        
    
    def hashFunction(self):
        sha = hashlib.sha256()
        sha.update(str(self.index).encode('utf-8') + str(self.timestamp).encode('utf-8') + str(self.nonce).encode('utf-8') + str(self.previousHash).encode('utf-8'))
        return sha.hexdigest()

    # Proof of work
    def mine(self, difficulty):
        print("Mining block " + str(self.index))
        zeros = ['0'] * difficulty
        while list(self.hash)[:difficulty] != zeros:
            #incrementing the nonce value everytime the loop runs.
            self.nonce += 1

            #recalculating the hash value
            self.hash = self.hashFunction()
        print('Block mined: ' + self.hash)

    