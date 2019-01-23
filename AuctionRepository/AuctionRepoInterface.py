import cherrypy
import json
from Objects import Auction, Bid

cherrypy.server.socket_host = '192.168.1.70'
cherrypy.server.socket_port = 8080

auctions = []
auctions.append(Auction(40))
auctions.append(Auction(10))

# How many blocks should we add to the chain
# after the genesis block
num_of_blocks_to_add = 20
previous_block = auctions[0].bidChain[0]

# Add blocks to the chain
for i in range(0, num_of_blocks_to_add):
    block_to_add = auctions[0].createNextBid(previous_block, "Antonio", 100)
    block_to_add.mine(5)
    auctions[0].bidChain.append(block_to_add)

    previous_block = block_to_add
    # Tell everyone about it!
    print("Block #{} has been added to the blockchain!".format(block_to_add.index))
    print("Hash: {}\n".format(block_to_add.hash))


class AuctionRepository(object):
    @cherrypy.expose
    def list(self):
        return json.dumps([ob.__dict__ for ob in auctions])

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def postTest(self):
        result = {"operation": "testRequest", "result": "success"}
        input_json = cherrypy.request.json
        print(input_json)
        return result

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def createBid(self):
        input_json = cherrypy.request.json


cherrypy.quickstart(AuctionRepository())