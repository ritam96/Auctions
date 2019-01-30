class ClientAuction(object):

    def __init__(self, deltaTime, exposedIdentities, startingPrice = None, englishAuction = False, blindAuction = False, maximumNumberBids = None, maximumNumberBidders = None, image = "https://tinyurl.com/ydy8sbnd", description = "No description"):

        self.image = image
        self.desc = description
        self.startingPrice = startingPrice
        self.englishAuction = englishAuction
        self.blindAuction = blindAuction
        self.exposedIdentities = exposedIdentities
        self.maximumNumberBids = maximumNumberBids
        self.maximumNumberBidders = maximumNumberBidders