import cherrypy
import json
import sqlite3
import uuid
import jwt
import datetime
import copy
import os
from random import randint
from Objects import Auction, Bid
from DBRepo import AuctionRepo, BidRepo, UserRepo, ReceiptRepo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

cherrypy.server.socket_host = '192.168.1.70'
cherrypy.server.socket_port = 8080
#cherrypy.ssl_module = 'pyopenssl'
#cherrypy.server.ssl_certificate = 'AuctionSystem.crt'
#cherrypy.server.ssl_certificate_chain = "AuctionRepo.pem"
#cherrypy.server.ssl_private_key = "AuctionRepoPKey.pem"

# an Engine, which the Session will use for connection
# resources
engine = create_engine('sqlite:///AuctionData.db')

# create a configured "Session" class
Session = sessionmaker(bind=engine)

def verify(bid):
    zeros = ['0'] * bid.miningDifficulty
    if list(bid.hashFunction())[:bid.miningDifficulty] != zeros:
        return False
    return True 

def verifyUserSession(user, sessionToken):
    # verify token
    if user.sessionToken != str.encode(sessionToken):
        return False

    # verify expiration of token
    if datetime.datetime.strptime(user.sessionExpires, '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
        return False

    return True

def verifyBidValidity(bidValues, auction, user):
    
    # The lowest nextBidID possible for this auction (genesis bid)
    nextID = 1

    # The lowest previousHash possible for this auction (genesis bid)
    prevHash = auction.bids[0].hash

    # Verify the previous parameters and update them (if there are other bids besides the genesis bid)
    for b in auction.bids:
        if int(b.BidID) >= nextID:
            nextID = int(b.BidID) + 1
            prevHash = b.hash

    # If the ID of the input bid does not match the expected ID for the next bid in the chain (same for previous Hash)
    if not bidValues['BidID'] == nextID or not bidValues['previousHash'] == prevHash:
        return False

    # Create a bid with the parameters from the input
    bid = Bid(nextID, bidValues['timestamp'], user.UserID, bidValues['value'], prevHash)
    bid.nonce = int(bidValues['nonce'])

    # Get the bid difficulty for the validation
    miningDifficulty = bidValues['miningDifficulty']
    bid.miningDifficulty = miningDifficulty

    # Verify the bid validity (hash, based on miningDifficulty)
    if not verify(bid):
        return False

    # Create BD bid object based on parameters
    bidDB = BidRepo()
    bidDB.create(bid, auction.AuctionID, user.UserID)

    # Add bid to auction bids list
    auction.bids.append(bidDB)
    newBidList = auction.bids

    # Sort bid list by bid ID
    newBidList.sort(key = lambda bid : int(bid.BidID))

    # Verify the list of bids
    i = 0
    for bid in newBidList:
        if i > 0:
            if not int(bid.BidID) == int(newBidList[i-1].BidID) + 1:
                return False
            
            if not bid.previousHash == newBidList[i-1].hash:
                return False
            
            if auction.englishAuction == '1' and not bid.value > newBidList[i-1].value:
                return False
        i+=1

    return True
    
def createReceipt(bid):
    return "Success"

class AuctionRepository(object):

    # Most auctions are public and anyone can see the description, image and current value of the auction.
    # This endpoint should return a list of auctions
    # INPUT JSON: none
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def listAllPublicAuctions(self):
        # create a DB Session
        session = Session()

        # get all auctions from db
        auctionsDB = session.query(AuctionRepo).all()

        # make auction json serializable
        auctions = [ob.__dict__ for ob in auctionsDB]

        # remove weird non json serializable attribute
        for dict in auctions:
            del dict['_sa_instance_state']
        
        session.close()
        return auctions
    

    # A logged in client should be able to see their bid history. This endpoint only requires session authentication.
    # INPUT JSON {'UserID': _____, 'sessionToken': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def listBids(self):
        # create a Session
        session = Session()

        # get data from input json
        data = cherrypy.request.json

        # get user from DB based on input
        user = session.query(UserRepo).get(data['UserID'])

        # verify user session
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 407, 'description': 'Invalid session'}

        # create list of json serializable bids
        ret = [ob.__dict__ for ob in user.bids]

        for dict in ret:

            # remove weird non json serializable attribute
            del dict['_sa_instance_state']

            # get auction relative to this bid
            auction = session.query(AuctionRepo).get(dict['AuctionID'])

            # add relevant auction parameters to the response
            dict['AuctionImage'] = auction.image
            dict['AuctionDescription'] = auction.description
            dict['ended'] = auction.ended

        session.close()
        return ret

    
    # A logged in client should be able to see their active and finished auctions. This endpoint only requires session authentication
    # INPUT JSON {'UserID': _____, 'sessionToken': ___ }
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def listMyAuctions(self):
        # create a Session
        session = Session()

        # get data from input json
        data = cherrypy.request.json

        # get user from database
        user = session.query(UserRepo).get(data['UserID'])

        # verify valid sessionToken
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 406, 'description': 'Invalid Session'}
        
        # get auctions created by this user from database
        auctionsDB = user.auctions

        # create list of auction dictionaries (with their parameters)
        auctions = [ob.__dict__ for ob in auctionsDB]

        # delete weird non json serializable parameter from list of auction dictionaries
        for dict in auctions:
            del dict['_sa_instance_state']
        
        # close DB session
        session.close()
        return auctions


    # When a client wants to submit a bid for a given auction, they first need to get a puzzle to solve as proof of work.
    # The puzzle is only returned to the client IF the bid has a valid value
    # The puzzle is only returned to the client IF he has a VALID SESSION TOKEN AND CC AUTHENTICATION
    # INPUT JSON: {"UserID": ___, 'sessionToken': ___, 'AuctionID': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getPuzzle(self):
        # create a DB Session
        session = Session()

        # get data from input json
        data = cherrypy.request.json

        # get user from database
        user = session.query(UserRepo).get(data['UserID'])

        # verify valid sessionToken
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 406, 'description': 'Invalid Session'}

        # get bids from the auction we want
        auctionBids = session.query(AuctionRepo).get(data['AuctionID']).bids

        # To create a puzzle, we need to know some values regarding the last bid, so we go get them
        lastBid = None
        for bid in auctionBids:
            if lastBid == None:
                lastBid = bid
            if lastBid.BidID <= bid.BidID:
                lastBid = bid

        # Randomly create the mining difficulty of the next bid
        difficulty = randint(1, 3)

        # Get the index of the last auction to send the index of the new bid with the puzzle
        ind = int(lastBid.BidID)
        ind += 1

        # Create return string with the required arguments for the puzzle
        ret = {'index': ind, 'previousHash': lastBid.hash, 'miningDifficulty': difficulty}

        session.close()
        return ret

    # After the cryptopuzzle is solved, the client can access this endpoint to submit the bid.
    # To submit the bid, it should have a VALID VALUE
    # The client must have a VALID SESSION TOKEN AND CC AUTHENTICAITON
    # JSON: {'UserID': ___, 'sessionToken': ___, 'AuctionID': ___, 'bid': {'timestamp': ___, 'value': ___, 'nonce': ___, 'BidID': ___, 'miningDifficulty': ___}}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def submitBid(self):
        # create a DB Session
        session = Session()

        # Get data from input json
        data = cherrypy.request.json

        # Get user from DB
        user = session.query(UserRepo).get(data['UserID'])

        # Validate user session
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 406, 'description': 'Invalid Session'}
        
        # Get auction to which the bid is going to be submitted
        auction = session.query(AuctionRepo).get(data['AuctionID'])

        if verifyBidValidity(data['bid'], auction, user):
            
            # Create bid object based on parameters
            bid = Bid(data['bid']['BidID'], data['bid']['timestamp'], user.UserID, data['bid']['value'], data['bid']['previousHash'])
            print(data['bid']['BidID'])
            bid.miningDifficulty = data['bid']['miningDifficulty']

            session.rollback()
            # Add bid to DB
            bidDB = BidRepo()
            bidDB.create(bid, auction.AuctionID, user.UserID)
            session.add(bidDB)
            session.commit()

            # Create Receipt and return it
            receipt = createReceipt(bid)
            session.close()
            return {'result': receipt}

        session.close()
        return {'error': 405, 'description': 'Request failed'}
    

    # A client can access this endpoint to create a new Auction ONLY IF HE HAS VALID SESSION TOKEN AND CC AUTHENTICATION
    # INPUT: headers: 'sessionToken'
    # JSON: {'UserID': ___, 'sessionToken':___, 'auction': {'deltaTime': ___, 'exposedIdentities': ___}}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def createAuction(self):
        # create a DB Session
        session = Session()

        # get data from input json
        data = cherrypy.request.json

        #get user from database
        user = session.query(UserRepo).get(data['UserID'])

        # verify user session
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 407, 'description': 'Invalid session'}

        try:
            #create new auction based on input json
            auctionData = data['auction']
            #auction = Auction(user, auctionData['deltaTime'], auctionData['exposedIdentities'], auctionData['startingPrice'], auctionData['englishAuction'], auctionData['blindAuction'], auctionData['maximumNumberBids'], auctionData['maximumNumberBidders'], auctionData['image'], auctionData['description'])
            auction = Auction(user, 0.01, auctionData['exposedIdentities'], auctionData['startingPrice'], auctionData['englishAuction'], auctionData['blindAuction'], auctionData['maximumNumberBids'], auctionData['maximumNumberBidders'], auctionData['image'], auctionData['description'])

            # create and save auction object for the database
            auctionDB = AuctionRepo()
            auctionDB.create(auction)
            session.add(auctionDB)

        except:
            session.rollback()
            session.close()
            {'error': 408, 'description': 'Failure during auction creation'}

        # save genesis bid in the database
        firstBid = BidRepo()
        firstBid.create(auction.bidChain[0], auction.auctionID, 'Genesis Bid')
        session.add(firstBid)
        session.commit()
        session.close()
        return {'result': 'Success'}


    # A client must log in to the system to use its functionalities (the other endpoints only work with a valid session token)
    # This endpoint gets a user name and encrypted password and returns a session token
    # JSON: {'UserID': ___, 'password': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def login(self):
        # create a DB Session
        session = Session()

        # get input json
        account = cherrypy.request.json

        # get user from database
        user = session.query(UserRepo).get(account['UserID'])

        # verify user data
        if user == None:
            session.close()
            return {'error': 400, 'description': 'User name doesn\'t exist'}
        if user.password != account['password']:
            session.close()
            return {'error': 401, 'description': 'Wrong Password'}

        # create user valid session data (each session is valid for half an hour)
        user.sessionExpires = datetime.datetime.now() + datetime.timedelta(hours=0.5)
        sessionToken = jwt.encode({'UserID': user.UserID, 'expiration': str(user.sessionExpires)}, account['password'], algorithm='HS256')
        user.sessionToken = sessionToken

        # save user session to database
        session.commit()
        session.close()

        return {'sessionToken': sessionToken}

    # To create an account, a client must access this endpoint and provide a user name and encrypted password.
    # JSON: {'UserID': ___, 'password': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def createAccount(self):
        # create a DB Session
        session = Session()

        # get input data
        account = cherrypy.request.json
        
        #verify if user already exists in DB
        user = session.query(UserRepo).get(account['UserID'])
        if user != None:
            session.close()
            return {'error': 400, 'description': 'User name already exists'}

        # Username is valid, so let's create a new database entry
        user = UserRepo()
        user.UserID = account['UserID']
        user.password = account['password']

        # Save user to database
        session.add(user)
        session.commit()
        session.close()
        return {'result': "Success"}

    # When an Auction is finished, a user that participated in it can have access to all the bids and validate the auction
    # JSON: {'AuctionID': ___ , 'UserID': ___, 'sessionToken': ___ }
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getAuctionInfo(self):
        # create a DB Session
        session = Session()

        # get input data
        data = cherrypy.request.json

        #get user from database
        user = session.query(UserRepo).get(data['UserID'])

        # verify user session
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 407, 'description': 'Invalid session'}

        # Get auction from DB
        auction = session.query(AuctionRepo).get(data['AuctionID'])

        # Verify if auction has ended
        if not auction.ended == '1':
            return {'error': 409, 'description': 'Auction has not ended yet'}
        
        act = copy.deepcopy(auction.__dict__)

        # Delete weird parameter thingy
        del act['_sa_instance_state']
        ret = {}
        ret['Auction'] = act
        ret['Bids'] = []

        for bid in auction.bids:
            bd = bid.__dict__
            del bd['_sa_instance_state']
            ret['Bids'].append(bd)

        session.close()
        return ret


    # When user needs to send a message, first he must send a SIGNED diffie hellman request (cc and public key of server)
    # JSON: {'userID': ___, 'sessionToken': ___, sharedPrime':___, 'sharedBase': ___, 'value': ___, 'CCcert': ___, 'cert': ___}
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def handshake(self):

        # create a DB Session
        session = Session()

        # get input data
        data = cherrypy.request.json

        #get user from database
        user = session.query(UserRepo).get(data['UserID'])

        # verify user session
        if not verifyUserSession(user, data['sessionToken']):
            session.close()
            return {'error': 407, 'description': 'Invalid session'}

        secret = os.urandom(32)
        value = int((float(data['sharedBase']) ** secret) % float(data['sharedPrime']))

        sharedKey = (value ** secret) % int(data['sharedPrime'])

        user.sharedKey = sharedKey
        user.certificate = data['cert']
        session.commit()
        session.close()

        return {'value': value}


cherrypy.quickstart(AuctionRepository())
