# bot class (contains Monte Carlo methods)
###################################################################
#       Imported Files
from player import *
from node import *
from special_bid import *
# 112_graphs, random, card, bid, board, copy
# special_bid, helper, button, heuristic imported via node
###################################################################
# the idea for using monte carlo experiments on a double-dummy solver
# came from https://en.wikipedia.org/wiki/Computer_bridge

class Bot():

    def __init__(self, position, depth, breadth):
        self.position = position # str of position
        self.history = []
        self.possibleNodes = [] # list of Nodes
        self.depth = depth # int of depth the bot will search
        self.bid = None
        self.hand = [] # list of Cards in the bot's hand
        self.breadth = breadth # refers to the number of Monte Carlo simulations to run

        self.knownCards = [] # list of cards we've seen (and therefore cannot be in opponent's hands)



###################################################################
# bidding

    def assignBid(self, bid):
        self.bid = bid

    # interprets hands for bidding purposes
    def interpretInitialHand(self, hand):
        self.hand = hand
        self.points = self.getHandPoints() # points in our hand
        self.partner = self.getPartner()
        self.getDistribution() # assigns distribution to self.distribution
        self.partnerDistribution = self.initialOtherDistribution() 
        self.partnerPoints = (0, 37) # min max inclusive of potential partner points range
        # partnerDistribution is a dict where key=suit and value=tuple(min, max)
        # min and max in inclusive
        self.forcing = False # otherwise, Bid
        self.conventionUsed = None # 's' for stayman, 'j' for jacoby
        print(self.position, self.distribution, self.points)

    # updates the distribution information based on bidding data
    def updateDistribution(self, otherDistribution, suit, min, max):
        oldMin, oldMax = otherDistribution[suit]
        if min > oldMin:
            otherDistribution[suit] = (min, otherDistribution[suit][1])
        if max < oldMax:
            otherDistribution[suit] = (otherDistribution[suit][0], max)

    # returns an updated narrower range of points
    def updatePoints(self, points, min, max):
        oldMin, oldMax = points
        if min > oldMin:
            points = (min, points[1])
        if max < oldMax:
            points = (points[0], max)
        return points


    # returns the partner given a position
    def getPartner(self):
        pair = [['n', 's'], ['e', 'w']][int(self.position in 'ew')]
        pair.remove(self.position)
        return pair[0]

    # returns a dict of the distribution of cards
    def getDistribution(self):
        self.distribution = {'S': 0, 'H': 0, 'D': 0, 'C': 0}
        for card in self.hand:
            self.distribution[card.suit] += 1

    # creates a dict of min and max distribution (0, 13)
    def initialOtherDistribution(self):
        distribution = dict()
        for suit in 'SHDC':
            distribution[suit] = (0, 13)
        return distribution

    def playBid(self, bids): # bids are list of tuple (position, bid)
        
        # returns the number of rounds that we have bidded
        self.round = self.getBiddingRound(bids)
        
        if self.hasNoBids(bids):
            return self.getOpeningBid() # returns the first 

        elif self.firstBid(bids)[0] == self.partner: # firstBidPosition = self.partner
            self.interpretPartnerBids(bids)
            return self.getRespondingBid(bids)

        elif self.firstBid(bids)[0] == self.position: # firstBidPosition = self.position
            self.interpretPartnerResponses(bids)
            return self.getOpenersBid(bids)
        # if you don't know what to do, pass
        return SpecialBid('Pass')
        # else:
        #     return self.getDefendingBid(bids)

    # return the number of rounds we have bidded
    def getBiddingRound(self, bids):
        count = 0
        for position, _ in bids:
            if position == self.position:
                count += 1
        return count

    # get the position's nth bid
    def getBid(self, position, n):
        for bidder, bid in self.bids:
            if bidder == position:
                n -= 1
                if n == 0:
                    return bid



    def getRespondingBid(self, bids):
        if self.isSlam():
            return self.bidSlam()
        elif self.isGame():
            pass


    def interpretPartnerBids(self, bids):
        if self.round == 0:
            self.interpretPartnerFirstBid()
        elif self.round == 1:
            self.interpretPartnerRebid()
        else:
            self.interpretEndRebids()

    def interpretPartnerRebid(self):
        rebid = self.getBid(self.partner, 2) # partner's bid
        response = self.getBid(self.partner, 1) # our bid
        biddingCategory = self.getBidCategory()
        if biddingCategory == 'NT':
            if self.conventionUsed == 's': # stayman convention
                if rebid.trump == 'S':
                    self.updateDistribution(self.partnerDistribution, 'S', 4, float('inf'))
                    self.updateDistribution(self.partnerDistribution, 'H', 0, 4)
                elif rebid.trump == 'H':
                    self.updateDistribution(self.partnerDistribution, 'H', 4, float('inf'))
                else:
                    self.updateDistribution(self.partnerDistribution, 'S', 0, 4)       
                    self.updateDistribution(self.partnerDistribution, 'H', 0, 4)     
            # jacoby convention has no semantic meaning
        elif biddingCategory == 'strong':
            if self.getBid(self.position, 1).trump == 'D':
                if rebid.trump == 'NT':
                    self.partnerPoints = self.updatePoints(self.partnerPoints, 22, 24)
                else:
                    self.forcing = Bid(3, rebid.trump) # refers to how high you need to go to before passing
        elif biddingCategory == 'weak':
            if rebid.suit == response.suit:
                self.partnerPoints = self.updatePoints(self.partnerPoints, 5, 8)
            else:
                self.partnerPoints = self.updatePoints(self.partnerPoints, 9, 11)
        else: # biddingCategory == 'normal'
            if rebid.suit == 'NT':
                if rebid.contract == response.contract:
                    self.partnerPoints = self.updatePoints(self.partnerPoints, 12, 14)



    def interpretPartnerFirstBid(self):
        partnerFirstBid = self.getBid(self.partner, 1)
        # 'NT', 'strong', 'weak', and  'normal'
        biddingCategory = self.getBidCategory()
        if biddingCategory == 'NT':
            for suit in self.partnerDistribution:
                self.updateDistribution(self.partnerDistribution, suit, 2, 5)
            NTPoints = {
                1: (15, 17),
                2: (20, 21),
                3: (25, 27)
            }
            self.partnerPoints = NTPoints[partnerFirstBid.contract]
        elif biddingCategory == 'strong':
            self.partnerPoints = self.updatePoints(self.partnerPoints, 21, float('inf'))
        elif biddingCategory == 'weak':
            self.partnerPoints = self.updatePoints(self.partnerPoints, 5, 11)
        else: # biddingCategory == 'normal'
            self.partnerPoints = self.updatePoints(self.partnerPoints, 12, 20)
            if partnerFirstBid.trump in 'SH':
                self.updateDistribution(self.partnerDistribution, partnerFirstBid.trump, 5, 'inf')
            elif partnerFirstBid.trump == 'D':
                self.updateDistribution(self.partnerDistribution, partnerFirstBid.trump, 4, 'inf')
            else:
                self.updateDistribution(self.partnerDistribution, partnerFirstBid.trump, 2, 'inf')
        

    # returns 'NT', 'strong', 'weak', and  'normal' based on firstBid
    def getBidCategory(self):
        firstBid = self.firstBid
        if firstBid.suit == 'NT':
            return 'NT'
        elif firstBid.number == 2:
            if firstBid.suit == 'C':
                return 'strong'
            else:
                return 'weak'
        else:
            return 'normal'

    # returns an opening bid
    def getOpeningBid(self):
        if self.points < 12:
            # either opens weak 2 or passes for when points less than 12
            return self.weakOpening()
        elif self.isEvenDistribution() and self.noTrumpOpening(): 
            # noTrump opening returns False if outside of points range
            return self.noTrumpOpening()
        elif 12 < self.points < 21:
            return self.normalOpening()
        else:
            # strong conventional bid
            return Bid(2,'C')

    def normalOpening(self):
        if self.distribution['S'] >= 5 or self.distribution['H'] >= 5:
            return Bid(1, self.longerMajor())
        elif self.distribution['D'] >= 4:
            return Bid(1, 'D') # 4+ diamonds
        else:
            return Bid(1, 'C') # 2+ clubs

    # returns the longer major suit
    def longerMajor(self):
        spadesLength = self.distribution['S']
        heartsLength = self.distribution['H']
        # returns spades if hearts length == spades length (as per SAYC system booklet)
        return ['S', 'H'][int(heartsLength > spadesLength)] 


    # returns NT opening in given ranges, returns False if it falls outside range
    def noTrumpOpening(self):
        if 15 <= self.points <= 17:
            return Bid(1,'NT')
        if 20 <= self.points <= 21:
            return Bid(2,'NT')
        if 25 <= self.points <= 27:
            return Bid(3,'NT')
        return False 

    # opening bid where points are less than 12
    def weakOpening(self):
        if self.points < 5 or self.points > 11: # self.points > 11 not necessary, but robustness
            return SpecialBid('Pass')
        for suit in self.distribution:
            if self.distribution[suit] > 5 and suit != 'C':
                return Bid(2, suit) # I'm going to ignore the very unlikely scenario where there are more than 1 6+ card suits
        return SpecialBid('Pass')

    # returns True if distribution is even (i.e. 5332, 4333, or 4432)
    def isEvenDistribution(self):
        for suit in self.distribution:
            if self.distribution[suit] > 5 or self.distribution[suit] < 2:
                return False
        return True

    # returns True if bids does not contain a Bid (only passes)
    def hasNoBids(self, bids):
        for _, bid in bids:
            if isinstance(bid, Bid): #specialBids have superclass button, not Bid
                return False
        return True

    # returns the position of the first bidder 
    # (returns None if no bids, but shouldn't occur here)
    # def firstBid(self, bids):
    #     for position, bid in bids:
    #         if isinstance(bid, Bid):
    #             return position, bid
        
    # getting points via the standard A=4, K=3, Q=2, J=1 evaluation system
    def getHandPoints(self):
        points = 0
        for card in self.hand:
            if card.number > 10:
                points += card.number - 10
        return points



###################################################################
# playing

    # actions to perform when the board is started
    def startPlay(self, hand):
        print('startPlay')
        self.hand = copy.deepcopy(hand)
        self.knownCards = self.knownCards + self.hand

    # simulate new Monte Carlo hands and returns chosen card     
    def playTurn(self, currentRound, nsTricks, ewTricks):
        self.possibleNodes = []
        self.simulate(currentRound, nsTricks, ewTricks)
        cardPicked = self.getCard()
        self.hand.remove(cardPicked)
        return cardPicked

    # generates Monte Carlo that fits known information
    def simulate(self, currentRound, nsTricks, ewTricks):
        for _, card in currentRound:
            self.knownCards.append(card)
        for _ in range(self.breadth):
            self.generateMonteCarlo(currentRound, nsTricks, ewTricks)

    # aggregates the cards from each node to get the modal card choice
    def getCard(self):
        # gets a dict of card mapped to number of times picked
        print(self.hand)
        cardCount = {'base': 0}
        print(len(self.possibleNodes[0].hands[self.position]))
        for node in self.possibleNodes:
            node.calculateMinimax(self.position in 'ns', baseHeuristic)
            proposedPlay = node.getPlay()
            value = cardCount.get(proposedPlay, 0)
            cardCount[proposedPlay] = value + 1
        print(cardCount)

        # get the modal card picked
        cardPick = 'base'
        for card in cardCount: #TODO: this feels so ugly
            if cardCount[card] > cardCount[cardPick]:
                cardPick = card
        print(cardPick)

        return cardPick
            
   
               
    # appends a new MonteCarlo-ed node to possibleNodes
    def generateMonteCarlo(self, currentRound, nsTricks, ewTricks):
        montyHands = dict()
        montyHands[self.position] = self.hand
        otherCards = self.makeUnkownDeck() # deck with known cards removed
        cardsPerPlayer = len(otherCards)//4 + 1
        if currentRound != []:
            leader = currentRound[0][0]
        else: leader = self.position
            # in case there is an uneven number of cards
        dealOrder = 'nesw'['nesw'.index(leader):] + 'nesw'[:'nesw'.index(leader)]
        for direction in dealOrder:
            if direction != self.position:
                montyHands[direction] = []
                for _ in range(cardsPerPlayer):
                    if otherCards == []: break
                    dealtCard = random.choice(otherCards) 
                    otherCards.remove(dealtCard) # prevents the card from being dealt twice
                    montyHands[direction].append(dealtCard)
        self.possibleNodes.append(Node(montyHands, self.depth, self.position, 
                                        currentRound, nsTricks, ewTricks, self.bid 
        ))

    # returns a deck with all the cards not in hand
    def makeUnkownDeck(self):
        deck = makeDeck()
        for card in self.knownCards:
            deck.remove(card)
        return deck

###################################################################
# old/irrelevant/tbd code

 # # TODO: update monte carlo when dummy reveals hand
    # def endBidding(self):
    #     pass

    # maybe #TODO? couldn't get this to work yet
    # # prunes Monte Carlo when a card becomes available    
    # def updateMonteCarlo(self, currentRound, nsTricks, ewTricks):
    #     # updating based on the cards played in the round
    #     for position, card in currentRound: 
    #         print(position, card)   
    #         for i in range(len(self.possibleNodes)):
    #             print(self.possibleNodes[i].hands[position])
    #             # if card shown does not correspond with guess, pop the possible Node and generate a new one
    #             if card not in self.possibleNodes[i].hands[position]:
    #                 self.possibleNodes.pop(i)
    #                 self.generateMonteCarlo(currentRound, nsTricks, ewTricks) # appends new node to possible nodes
    #             # check what card the bot played and update the nodes accordingly
    #             self.possibleNodes[i] = self.possibleNodes[i].children[card] 

# def makeNode(self, hands, depth, activePosition, currentRound, nsTricks, ewTricks, bid):
    #     self.node = Node(hands, depth, activePosition, currentRound, nsTricks, ewTricks, bid)

    # def botTurn(self):
    #     self.node.calculateMinimax(True, baseHeuristic)
    #     return self.node.getPlay()    
