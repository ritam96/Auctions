import cherrypy
import json
import sqlite3
import uuid
import jwt
import datetime
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


class AuctionRepository(object):

    # Most auctions are public and anyone can see the description, image and current value of the auction.
    # This endpoint should return a list of auctions
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def listAllPublicAuctions(self):
        pass
    

    # A logged in client should be able to see their bid history. This endpoint only requires session authentication.
    @cherrypy.expose
    def listBids(self):
        sessionToken = cherrypy.request.headers['sessionToken']

    
    # A logged in client should be able to see their active and finished auctions. This endpoint only requires session authentication
    @cherrypy.expose
    def listMyAuctions(self):
        pass

    # When a client wants to submit a bid for a given auction, they first need to get a puzzle to solve as proof of work.
    # The puzzle is only returned to the client IF the bid has a valid value
    # The puzzle is only returned to the client IF he has a VALID SESSION TOKEN AND CC AUTHENTICATION
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getPuzzle(self):
        auctionID = str(cherrypy.request.headers['auctionID'])
    

    # After the cryptopuzzle is solved, the client can access this endpoint to submit the bid.
    # To submit the bid, it should have a VALID VALUE
    # The client must have a VALID SESSION TOKEN AND CC AUTHENTICAITON
    @cherrypy.expose
    def submitBid(self):
        pass
    

    # A client can access this endpoint to create a new Auction ONLY IF HE HAS VALID SESSION TOKEN AND CC AUTHENTICATION
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def createAuction(self):
        auctionData = cherrypy.request.json



    # A client must log in to the system to use its functionalities (the other endpoints only work with a valid session token)
    # This endpoint gets a user name and password and returns a session token
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def login(self):
        account = cherrypy.request.json
        user = session.query(UserRepo).get(account['name'])
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
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def createAccount(self):
        account = cherrypy.request.json
        user = UserRepo(UserID = account['name'], password = account['password'])
        session.add(user)
        session.commit()

cherrypy.quickstart(AuctionRepository())