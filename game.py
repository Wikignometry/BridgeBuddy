###################################################################
#       Imported Files
from board import *
# 112_graphs, random, card, bid,
# special_bid, helper button imported via board
from bot import *
###################################################################

class Game():

    def __init__(self, playerDict):
        self.boardNumber = 1
        self.board = Board(self.boardNumber)
        self.ewPoints = 0
        self.nsPoints = 0
        self.players = playerDict # dict where key=position, value=Player
        self.history = [] # list of previous boards
        self.getBotPosition() # self.botPosition as a str

    # creates new board, stores old board, and increases board number
    def newBoard(self):
        self.history.append(self.board)
        self.boardNumber += 1
        self.board = Board(self.boardNumber)

    # assigns a str of botPositions to self.botPosition
    def getBotPosition(self):
        self.botPosition = '' 
        for position in self.players:
            if isinstance(position, Bot):
                self.botPosition += position
        