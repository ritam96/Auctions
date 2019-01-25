from sqlalchemy.dialects.sqlite import TEXT
from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

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

class UserRepo(Base):
    __tablename__ = 'User'

    UserID = Column(TEXT, primary_key = True)
    password = Column(TEXT, nullable = False)
    sessionToken  = Column(TEXT, nullable = True)
    sessionExpires = Column(TEXT, nullable = True)

class ReceiptRepo(Base):
    __tablename__ = 'Receipt'

    ReceiptID = Column(TEXT, primary_key = True)
    UserID = Column(TEXT, ForeignKey('User.UserID'), primary_key = True)
    user = relationship(UserRepo)

class BidRepo(Base):
    __tablename__ = 'Bid'

    AuctionID = Column(TEXT, ForeignKey('Auction.AuctionID'), primary_key = True)
    auction = relationship(AuctionRepo)
    BidID = Column(TEXT, primary_key = True)
    UserID = Column(TEXT, ForeignKey('User.UserID'))
    user = relationship(UserRepo)
    ReceiptID = Column(TEXT, ForeignKey('Receipt.ReceiptID'), nullable = False)
    receipt = relationship(ReceiptRepo)
    timestamp = Column(TEXT, nullable = False)
    value = Column(TEXT, nullable = False)
    nonce = Column(TEXT, nullable = False)
    previousHash = Column(TEXT, nullable = False)
    hash = Column(TEXT, nullable = False)
    miningDifficulty = Column(TEXT, nullable = False)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///AuctionData.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)