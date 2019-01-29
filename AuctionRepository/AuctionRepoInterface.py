import cherrypy
import json
import sqlite3
import uuid
import jwt
import datetime
from random import randint
from Objects import Auction, Bid
from DBRepo import AuctionRepo, BidRepo, UserRepo, ReceiptRepo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

cherrypy.server.socket_host = '192.168.1.70'
cherrypy.server.socket_port = 8080

# an Engine, which the Session will use for connection
# resources
engine = create_engine('sqlite:///AuctionData.db')

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

testUser = UserRepo()
testUser.UserID = '1567'
testUser.password = 'gaf'
session.add(testUser)
session.commit()
testAuction = Auction(testUser, '2', '0')
testAuctionDB = AuctionRepo()
testAuctionDB.create(auction = testAuction)
session.add(testAuctionDB)
session.commit()

def verify (bid, miningDifficulty):
    zeros = ['0'] * miningDifficulty
    bid.miningDifficulty = miningDifficulty

    if list(bid.hashFunction())[:miningDifficulty] != zeros:
        return False

    return True 

def createReceipt(bid):
    return "Success"

class AuctionRepository(object):

    # Most auctions are public and anyone can see the description, image and current value of the auction.
    # This endpoint should return a list of auctions

    # INPUT: none
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def listAllPublicAuctions(self):
        auctionsDB = session.query(AuctionRepo).all()
        auctions = [ob.__dict__ for ob in auctionsDB]
        for dict in auctions:
            del dict['_sa_instance_state']
        return auctions
    

    # A logged in client should be able to see their bid history. This endpoint only requires session authentication.
    
    # INPUT: header: 'sessionToken'
    # JSON {'UserID': _____ }
    @cherrypy.expose
    def listBids(self):
        sesToken = cherrypy.request.headers['sessionToken']

        user = session.query(UserRepo).filter_by(sessionToken = sesToken)

        return user.bids

    
    # A logged in client should be able to see their active and finished auctions. This endpoint only requires session authentication
    # INPUT: header: 'sessionToken'
    # JSON {'UserID': _____ }
    @cherrypy.expose
    def listMyAuctions(self):
        sesToken = cherrypy.request.headers['sessionToken']
        user = session.query(UserRepo).filter_by(sessionToken = sesToken)
        return user.auctions

    # When a client wants to submit a bid for a given auction, they first need to get a puzzle to solve as proof of work.
    # The puzzle is only returned to the client IF the bid has a valid value
    # The puzzle is only returned to the client IF he has a VALID SESSION TOKEN AND CC AUTHENTICATION

    # INPUT: headers: 'sessionToken', 'auctionID'
    # JSON: {"UserID": }
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getPuzzle(self):
        auctionID = str(cherrypy.request.headers['auctionID'])
        sesToken = cherrypy.request.headers['sessionToken']
        user = session.query(UserRepo).filter_by(sessionToken = sesToken)
        auctionBids = session.query(AuctionRepo).get(auctionID)
        lastBid = None
        for bid in auctionBids:
            if lastBid == None:
                lastBid = bid
            if lastBid.BidID <= bid.BidID:
                lastBid = bid
        difficulty = randint(4, 8)
        ind = int(lastBid.BidID)
        ind += 1
        return {'index': ind, 'previousHash': lastBid.hash, 'miningDifficulty': difficulty}

    # After the cryptopuzzle is solved, the client can access this endpoint to submit the bid.
    # To submit the bid, it should have a VALID VALUE
    # The client must have a VALID SESSION TOKEN AND CC AUTHENTICAITON

    # INPUT: headers: 'sessionToken' and 'auctionID'
    # JSON: {'UserID': ___, 'bid': {'timestamp': ___, 'value': ___, 'nonce': ___, 'hash': ___, 'miningDifficulty': ___}}
    @cherrypy.expose
    def submitBid(self):
        data = cherrypy.request.json
        sesToken = cherrypy.request.headers['sessionToken']
        auctionID = str(cherrypy.request.headers['auctionID'])
        user = session.query(UserRepo).get(data['UserID']).filter_by(sessionToken = sesToken)
        auction = session.query(AuctionRepo).get(auctionID)
        nextID = 1
        prevHash = None
        for b in auction.bids:
            if int(b.BidID) >= nextID:
                nextID = int(b.BidID) + 1
                prevHash = b.previousHash
        bid = Bid(nextID, data['bid']['timestamp'], data['UserID'], data['bid']['value'], prevHash)
        bid.nonce = data['bid']['nonce']
        bid.hash = data['bid']['hash']

        miningDifficulty = data['bid']['miningDifficulty']

        if verify(bid, miningDifficulty):
            bid.miningDifficulty = miningDifficulty
            bidDB = BidRepo()
            bidDB.create(bid)
            session.add(bidDB)
            session.commit()
            return createReceipt(bid)
        return {'error': 405, 'description': 'Request failed'}
    

    # A client can access this endpoint to create a new Auction ONLY IF HE HAS VALID SESSION TOKEN AND CC AUTHENTICATION

    # INPUT: headers: 'sessionToken'
    # JSON: {'UserID': ___, 'auction': {'deltaTime': ___, 'exposedIdentities': ___}}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def createAuction(self):
        data = cherrypy.request.json
        user = session.query(UserRepo).get(data['UserID']).filter_by(sessionToken = data['sessionToken'])
        auction = Auction(user, data['auction']['deltaTime'], data['auction']['exposedIdentities'])
        auctionDB = AuctionRepo()
        auctionDB.create(auction)
        session.add(auctionDB)
        session.commit()
        return 'Success'


    # A client must log in to the system to use its functionalities (the other endpoints only work with a valid session token)
    # This endpoint gets a user name and password and returns a session token

    # JSON: {'UserID': ___, 'password': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def login(self):
        account = cherrypy.request.json
        user = session.query(UserRepo).get(account['UserID'])
        if user == None:
            return {'error': 400, 'description': 'User name doesn\'t exist'}
        if user.password != account['password']:
            return {'error': 401, 'description': 'Wrong Password'}
        user.sessionExpires = datetime.datetime.now() + datetime.timedelta(hours=0.5)
        sessionToken = jwt.encode({'UserID': user.UserID, 'expiration': str(user.sessionExpires)}, account['password'], algorithm='HS256')
        user.sessionToken = sessionToken
        session.commit()
        return {'sessionToken': sessionToken}

    # To create an account, a client must access this endpoint and provide a user name and encrypted password.

    # JSON: {'UserID': ___, 'password': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def createAccount(self):
        account = cherrypy.request.json
        user = UserRepo()
        user.UserID = account['UserID']
        user.password = account['password']
        session.add(user)
        session.commit()

cherrypy.quickstart(AuctionRepository())