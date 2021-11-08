###################################################################
#       Imported Files
from card import *
from bid import *
# 112_graphs, draw_helpers and button imported via card/bid
import random
###################################################################


class Board():

    def __init__(self, boardNumber):
        
        # int – index (starts at 0) because it's easier to use
        self.index = boardNumber - 1

        self.dealer = 'nesw'[self.index % 4] # 'n','e','s' or 'w'
        self.vul = self.getVulnerability() # '', 'ns', 'ew', 'nsew'

        self.bids = [] # list of tuples(position, Bid)
        self.bidOptions = self.getAllBids()
        self.bid = None

        self.dealHand() #self.hands = dict(key=position, value=list of Cards)
        #TODO: sort hand function
        self.currentRound = [] #list starting with leading position, then contains all the cards played in clockwise direction
        self.lead = None # Card of first card in each round

        #TODO: remember to remove hardcoding
        self.activePosition = 'n' # 'n','e','s', 'w' or None

        self.cardDislayWidth = 30 # width of the card shown when in hand format

        self.history = [] # tracks what cards have already been played

    # returns a list of all possible bids (excluding special ones)
    def getAllBids(self):
        bidOptions = []
        for contract in range(1,7):
            for trump in ['C', 'D', 'H', 'S', 'NT']:
                bidOptions.append(Bid(contract, trump))
        return bidOptions

    # returns str of vulnerable pair(s)
    def getVulnerability(self):
        vulnerabilities = ['', 'ns', 'ew', 'nsew']
        return vulnerabilities[(self.index//4 + self.index) % 4]

    # deals 13 cards to each hand
    def dealHand(self):
        hands = dict()
        cardsPerPlayer = 13
        allCards = self.makeDeck()
        for direction in 'nesw':
            hands[direction] = []
            for _ in range(cardsPerPlayer):
                dealtCard = random.choice(allCards)
                allCards.remove(dealtCard)
                hands[direction].append(dealtCard)
        self.hands = hands

    # make a deck of 52 cards
    def makeDeck(self):
        fullDeck = list()
        for suit in 'SHDC': 
            for number in range(2, 15): # ace is treated as 14
                fullDeck.append(Card(number, suit))
        return fullDeck

    # actions to perform when a card is pressed
    def playCard(self, card, position, targetLocation):
        self.hands[position].remove(card)
        self.currentRound.append((position, card))
        card.targetLocation = targetLocation
        # I want this to crash if it gets a non-string arg
        self.activePosition = 'nesw'[('nesw'.index(self.activePosition)+1)%4]

    # location is a tuple (x, y) of the center of the hand
    def locateHand(self, hand, location):
        xCenter, yCenter = location
        cardCount = len(hand)
        x = xCenter - (self.cardDislayWidth*(cardCount//2)) #leftmost center
        y = yCenter
        for card in hand:
            card.location = (x, y)
            x += self.cardDislayWidth

    # locateHand for all four positions
    def locateHands(self, positionDict):
        for position in 'nsew':
            self.locateHand(self.hands[position], positionDict[position])

    # performs all the neccesary actions for a round end
    def endRound(self):
        self.lead = self.currentRound[0][1] #TODO: this might have to move somewhere more efficient
        winner, winningCard = self.getWinner(self.currentRound)
        self.history.append(tuple(self.currentRound)) # make into a tuple to ensure it doesn't change
        self.currentRound = []
        self.activePosition = winner
        print(winner)

    # returns the winner in a round recursively
    def getWinner(self, cardList):
        if len(cardList) == 1:
            return cardList[0]
        else:
            bestOfTheRest = self.getWinner(cardList[1:])
            if cardList[0][1].isGreaterThanInGame(bestOfTheRest[1], self.bid, self.lead):
                return cardList[0]
            else: 
                return bestOfTheRest
    
    # draw each card in the hand
    def drawHands(self, canvas):
        for position in 'nsew':
            for card in self.hands[position]:
                card.draw(canvas)

    # draw played cards in the current round
    def drawPlayedCards(self, canvas):
        for _ , card in self.currentRound: 
            card.draw(canvas)

###################################################################
#       Test Functions

# returns True if there are duplicates
def hasDuplicates(L):
    strList = list(map(str, L))
    return (list(set(strList)) == strList)

def testBoardClass():
    print('Testing Board...', end='')
    board1 = Board(17)
    assert(board1.vul == '')
    assert(board1.dealer == 'n')
    assert(len(board1.hands['n']) == 13)
    assert(Bid(5,'C') in board1.bidOptions)
    assert(Bid(6,'NT') in board1.bidOptions)
    assert(Bid(1,'S') in board1.bidOptions)
    assert(Bid(4,'D') in board1.bidOptions)
    assert(not hasDuplicates(board1.makeDeck()))
    for position in 'nsew':
        assert(not hasDuplicates(board1.hands[position]))
    board1.lead = Card(8,'H')
    board1.bid = Bid(4,'S')
    assert(board1.getWinner([('n', Card(8,'H')), ('s', Card(2,'S')), ('e', Card(7,'D')), ('w', Card(3,'S'))]) == ('w', Card(3,'S'))) 
    assert(board1.getWinner([('s', Card(8,'H')), ('e', Card(9,'H')), ('w', Card(11,'H')), ('n', Card(13,'D'))])== ('w', Card(11,'H')))    
    print('Passed!')

def appStarted(app):
    app.board1 = Board(15)
    app.board1.bid = Bid(4,'S')

def mousePressed(app, event):
    for card in app.board1.hands[app.board1.activePosition]:
        if card.isPressed(event.x, event.y):
            app.board1.playCard(card, app.board1.activePosition, (app.width//2, app.height//2))
            if len(app.board1.currentRound) > 4:
                app.board1.endRound()

def timerFired(app):
    for _ , card in app.board1.currentRound:
        card.move(0.3)

def redrawAll(app, canvas):
    app.board1.locateHands({'n': (app.width//2, 50), 
                            'e': (app.width-200, app.height//2), 
                            's': (app.width//2, app.height-50), 
                            'w': (200, app.height//2)})
    app.board1.drawHands(canvas)
    app.board1.drawPlayedCards(canvas)

###################################################################
#       Code to run

testBoardClass()
runApp(width=1000, height=500)
