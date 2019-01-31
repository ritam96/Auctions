import cherrypy
import schedule
import datetime
import time
from DBRepo import AuctionRepo, BidRepo, UserRepo, ReceiptRepo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///AuctionData.db')

Session = sessionmaker(bind=engine)

def verify (bid, miningDifficulty):
    zeros = ['0'] * miningDifficulty
    bid.miningDifficulty = miningDifficulty
    if list(bid.hashFunction())[:miningDifficulty] != zeros:
        print(list(bid.hashFunction()))
        return False

    return True 

def verifyAuctions():
    print('Verifying auctions')
    # Create DB Session
    session = Session()

    session.rollback()
    # Get all auctions from DB
    auctionsDB = session.query(AuctionRepo).all()
    for auction in auctionsDB:
        
        if str(auction.ended) == '0' and datetime.datetime.strptime(auction.endTime, '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
            print('FOUND ONE!')
            auction.ended = '1'
            
    session.commit()
    session.close()



schedule.every(0.1).minutes.do(verifyAuctions)

while True:
    schedule.run_pending()
    time.sleep(1)