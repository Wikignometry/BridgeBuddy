###################################################################
#       Imported Files
from button import *
###################################################################

class Card(Button):

    def __init__(self, number, suit):

        self.suit = suit # 'C', 'D', 'H', or 'S'
        self.number = number # int
        
        self.setColor() # self.color: 'red' or 'black'

        self.location = None # tuple(x, y) or None

        # actual dimensions (in mm) according to http://greatbridgelinks.com/poker-size-cards-vs-bridge-size-cards/
        self.width = 57 # constant int
        self.height = 89 # constant int


    # assigns color to card based on suit
    def setColor(self):
        if self.suit in 'DH': 
            self.color = 'red'
        else: 
            self.color = 'black'

    # i.e. 3C, AS, 10H, JD, 8H
    def __repr__(self):
        if self.number < 11:
            return str(self.number) + self.suit
        return 'JQKA'[self.number % 11] + self.suit

    # will crash if fed non Card other argument
    # orders by suit first, then number
    def __lt__(self, other):
        suitOrder = 'SHCD' # order from greatest to least
        if suitOrder.find(self.suit) > suitOrder.find(other.suit):
            return True
        return self.number < other.number


###################################################################
#       Test Functions

def testCardClass():
    print('Testing Card...', end='')
    card1 = Card(5, 'C')
    assert(str(card1) == '5C')
    assert(card1.location == None)
    assert(card1.color == 'black')
    assert(card1.width, card1.height == 57, 89)
    card1.location = (15, 20)
    assert(card1.location == 15, 20)
    assert(card1.isPressed(16, 24) == True)
    assert(card1.isPressed(200, 500) == False)
    assert((card1 < Card(4,'C')) == False)
    assert((card1 < Card(7,'C')) == True)
    assert((card1 < Card(7,'H')) == True)
    assert((card1 < Card(4,'H')) == True)
    assert((Card(8,'S') < Card(8,'C')) == False)
    assert((Card(8,'H') < Card(8,'S')) == True)
    print('Passed!')

###################################################################
#       Code to run

testCardClass()

