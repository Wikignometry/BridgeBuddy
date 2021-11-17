# mode for the bridge game
###################################################################
#       Imported Files

from node import *
# 112_graphs, random, card, bid, heuristic, copy
# special_bid, helper button imported via node
from game import *
from bot import *
# player imported via bot
###################################################################

def appStarted(app):
    app.mode = 'gameMode'
    app.game = Game({'n': Player('Fa'), 
                    's': Bot('s'), 
                    'e': Player('Fa'), 
                    'w': Player('Fa')})
    app.board = app.game.board
    app.board.locateBids((app.width//2, app.height//2)) #TODO: locate bids again if screen resizes

def gameMode_keyPressed(app, event):
    app.game.players['s'].makeNode(app.board.hands, 2, 's', app.board.currentRound, 0, 0, app.board.bid)

def gameMode_mousePressed(app, event):
    if app.board.status == 'p':
        # checks if card is pressed and does corresponding actions
        for card in (app.board.hands[app.board.activePosition])[::-1]:
            if card.isPressed(event.x, event.y):
                app.board.playCard(card, (app.width//2, app.height//2))
                if isinstance(app.game.players[app.board.activePosition], Bot):
                    botPlay(app)
                return
    # checks if bid is pressed and does corresponding actions
    if app.board.status == 'b':
        for row in app.board.bidOptions:
            for bid in row:
                if bid.isPressed(event.x, event.y):
                    app.board.playBid(bid)

def botPlay(app):
    app.game.players['s'].makeNode(app.board.hands, 2, 's', app.board.currentRound, 0, 0, app.board.bid)
    while isinstance(app.game.players[app.board.activePosition], Bot):
        chosenCard = app.game.players[app.board.activePosition].botTurn()
        print(chosenCard, app.board.activePosition)
        app.board.playCard(chosenCard, (app.width//2, app.height//2))

def gameMode_timerFired(app):
    for _ , card in app.board.currentRound:
        card.move(0.3) #TODO: fix magic number?

def gameMode_redrawAll(app, canvas):
    app.board.locateHands({'n': (app.width//2, 50), 
                            'e': (app.width-250, app.height//2), 
                            's': (app.width//2, app.height-50), 
                            'w': (250, app.height//2)})
    app.board.drawHands(canvas)
    app.board.drawPlayedCards(canvas)
    if app.board.status == 'b':
        app.board.drawPotentialBids(canvas)



###################################################################
#       Code to run

runApp(width=1200, height=700)
