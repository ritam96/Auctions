from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class UserRepo(Base):
    __tablename__ = 'User'

    UserID = Column(TEXT, primary_key = True)
    password = Column(TEXT, nullable = False)
    sessionToken  = Column(TEXT, nullable = True)
    sessionExpires = Column(TEXT, nullable = True)

    sharedKey = Column(TEXT, nullable = True)
    certificate = Column(TEXT, nullable = True)

    auctions = relationship('AuctionRepo', back_populates = 'user')

    bids = relationship('BidRepo', back_populates = 'user')

    receipts = relationship('ReceiptRepo', back_populates = 'user')

class AuctionRepo(Base):
    __tablename__ = 'Auction'

    AuctionID = Column(TEXT, primary_key = True)
    image = Column(TEXT, nullable = True)
    description = Column(TEXT, nullable = True)
    currentPrice = Column(TEXT, nullable = True)
    startingPrice = Column(TEXT, nullable = True)
    englishAuction = Column(TEXT, nullable = False)
    blindAuction = Column(TEXT, nullable = False)
    exposedIdentitites = Column(TEXT, nullable = False)
    maximumNumberBids = Column(TEXT, nullable = True)
    maximumNumberBidders = Column(TEXT, nullable = True)
    endTime = Column(TEXT, nullable = False)
    ended = Column(TEXT, nullable = False)

    UserID = Column(TEXT, ForeignKey('User.UserID'), nullable = False)
    user = relationship('UserRepo', back_populates = 'auctions')

    bids = relationship('BidRepo', back_populates = 'auction')

    def create(self, auction):
        self.AuctionID = auction.auctionID
        self.UserID = auction.userID
        self.image = auction.image
        self.description = auction.desc
        self.currentPrice = auction.currentPrice
        self.startingPrice = auction.startingPrice
        self.englishAuction = auction.englishAuction
        self.blindAuction = auction.blindAuction
        self.exposedIdentitites = auction.exposedIdentities
        self.maximumNumberBids = auction.maximumNumberBids
        self.maximumNumberBidders = auction.maximumNumberBidders
        self.endTime = auction.endTime
        self.ended = auction.ended 


class BidRepo(Base):
    __tablename__ = 'Bid'

    AuctionID = Column(TEXT, ForeignKey('Auction.AuctionID'), primary_key = True)
    auction = relationship('AuctionRepo', back_populates= 'bids')

    BidID = Column(TEXT, nullable = False, primary_key = True)

    UserID = Column(TEXT, ForeignKey('User.UserID'))
    user = relationship('UserRepo', back_populates = 'bids')

    ReceiptID = Column(TEXT, ForeignKey('Receipt.ReceiptID'))
    receipt = relationship('ReceiptRepo', back_populates = 'bid', foreign_keys = 'BidRepo.ReceiptID', uselist = False)

    timestamp = Column(TEXT, nullable = False)
    value = Column(TEXT, nullable = False)
    nonce = Column(TEXT, nullable = False)
    previousHash = Column(TEXT, nullable = False)
    hash = Column(TEXT, nullable = False)
    miningDifficulty = Column(TEXT, nullable = False)

    def create(self, bid, auctionID, userID):
        self.AuctionID = auctionID
        self.BidID = bid.index
        self.UserID = userID
        self.timestamp = bid.timestamp
        self.value = bid.value
        self.nonce = bid.nonce
        self.previousHash = bid.previousHash
        self.hash = bid.hash
        self.miningDifficulty = bid.miningDifficulty




class ReceiptRepo(Base):
    __tablename__ = 'Receipt'

    ReceiptID = Column(TEXT, primary_key = True)

    UserID = Column(TEXT, ForeignKey('User.UserID'))
    user = relationship('UserRepo', back_populates = 'receipts')

    AuctionID = Column(TEXT, ForeignKey('Bid.AuctionID'))
    BidID = Column(TEXT, ForeignKey('Bid.BidID'), primary_key = True)
    
    bid = relationship('BidRepo', back_populates = 'receipt', foreign_keys='BidRepo.ReceiptID')
    
    identity = Column(TEXT, nullable = True)



# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///AuctionData.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)