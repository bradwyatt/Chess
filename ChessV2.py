"""
Chess created by Brad Wyatt
Python 2.7.13

To-Do:
Castling (can't do it through check) --> Need to be aware of left and right rook (if they moved or not)
En Passant
Check
Checkmate
Reset button for reset the board
Customized Turns for black and white
"""
import pygame, random, sys, ast, os
from pygame.constants import RLEACCEL
from pygame.locals import *
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import *
from ast import literal_eval

#Tk box for color
root = tk.Tk()
root.withdraw()
#Global variables
MENUON = 0
RUNNING = True #Flags game as on
SCREEN = None
SCREENWIDTH, SCREENHEIGHT = 936, 650
COLORKEY = [160,160,160]
XGRIDRANGE = [48, 432, 48] #1st num: begin 2nd: end 3rd: step
YGRIDRANGE = [96, 480, 48] #1st num: begin 2nd: end 3rd: step
WHOSETURN = ""
TAKENPIECECOORDS = [50, 15, 50, 525]
TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
CHECKTEXT = ""

#Grouping Images and Sounds
startPos = {'whitePawn': (480, 390), 'whiteBishop':(480, 340), 'whiteKnight':(480, 290),
            'whiteRook':(480, 240), 'whiteQueen':(480, 190), 'whiteKing':(480, 140),
            'blackPawn': (540, 390), 'blackBishop':(540, 340), 'blackKnight':(540, 290),
            'blackRook':(540, 240), 'blackQueen':(540, 190), 'blackKing':(540, 140)}
images = {}
sounds = {}
gridsprites = pygame.sprite.Group()
startsprites = pygame.sprite.Group()
placedsprites = pygame.sprite.Group()
playsprites = pygame.sprite.Group()
clock = pygame.time.Clock()

def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] #feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0,appdir)
    except:
        #placeholder for feedback, adjust to your app.
        #remember to use only python and python standard libraries
        #not any resource or module into the appdir 
        #a window in Tkinter can be adequate for apps without console
        #a simple print with a timeout can be enough for console apps
        print('Please run from an OS console.')
        import time
        time.sleep(10)
        sys.exit(1)
adjust_to_correct_appdir()

def loadSound(file, name):
    sound = pygame.mixer.Sound(file)
    sounds[name] = sound
    
def loadImage(file, name, transparent, alpha):
    newImage = pygame.image.load(file)
    if alpha == True:
        newImage = newImage.convert_alpha()
    else:
        newImage = newImage.convert()
    if transparent:
        colorkey = newImage.get_at((0,0))
        newImage.set_colorkey(colorkey, RLEACCEL)
    images[name] = newImage

def snapToGrid(mousePos):
    global XGRIDRANGE, YGRIDRANGE
    bestNumX, bestNumY = XGRIDRANGE[0], YGRIDRANGE[0] #So Y doesn't go above the menu
    for x in range(XGRIDRANGE[0], XGRIDRANGE[1], XGRIDRANGE[2]):
        if mousePos[0]-x <= 48 and mousePos[0]-x >= 0:
            bestNumX = x
    for y in range(YGRIDRANGE[0], YGRIDRANGE[1], YGRIDRANGE[2]):
        if mousePos[1]-y <= 48 and mousePos[1]-y >= 0:
            bestNumY = y
    bestGridSnap = (bestNumX, bestNumY)
    return bestGridSnap

def removeObject():
    for placedItemList in (placed.whitePawnList, placed.whiteBishopList, placed.whiteKnightList, placed.whiteRookList,
                           placed.whiteQueenList, placed.whiteKingList, placed.blackPawnList, placed.blackPawnList, placed.blackBishopList,
                           placed.blackKnightList, placed.blackRookList, placed.blackQueenList, placed.blackKingList):
        for placedItem in placedItemList: 
            if placedItem.rect.collidepoint(mousePos):
                placedsprites.remove(placedItem)
                placedItemList.remove(placedItem)

def draggingFunction():
    dragging.draggingNone()
    start.whitePawn.rect.topleft = startPos['whitePawn']
    start.whiteBishop.rect.topleft = startPos['whiteBishop']
    start.whiteKnight.rect.topleft = startPos['whiteKnight']
    start.whiteRook.rect.topleft = startPos['whiteRook']
    start.whiteQueen.rect.topleft = startPos['whiteQueen']
    start.whiteKing.rect.topleft = startPos['whiteKing']
    start.blackPawn.rect.topleft = startPos['blackPawn']
    start.blackBishop.rect.topleft = startPos['blackBishop']
    start.blackBishop.rect.topleft = startPos['blackKnight']
    start.blackRook.rect.topleft = startPos['blackRook']
    start.blackQueen.rect.topleft = startPos['blackQueen']
    start.blackKing.rect.topleft = startPos['blackKing']
    
def loadFile():
    global COLORKEY
    try:
        saveFileName = askopenfilename(defaultextension=".lvl")
        saveFile = open(saveFileName, "r")
        rectList = []
        # Try to load each line as a tuple
        with saveFile as f:
            for line in f:
                try:
                    rectList.extend(literal_eval(line.strip()))
                except:
                    pass #Ignore if not tuple
        global eachSaveFileLine, previousLocation, eachLengthLine
        rectListLen = len(rectList) #Length of end of Positions, and start of RGB/Lengths
        lengthsFile = open(saveFileName, "r") #Copy of saveFile
        eachSaveFileLine = lengthsFile.readlines()
        #Append each line after Positions to list
        eachLengthLine = []
        for i in range(rectListLen, len(eachSaveFileLine)):
            eachLengthLine.append(eachSaveFileLine[i])
        #RGB is first 3 lines after Positions
        COLORKEY[0] = int(eachLengthLine[0])
        COLORKEY[1] = int(eachLengthLine[1])
        COLORKEY[2] = int(eachLengthLine[2])
        previousLocation = 0
        def loadObj(placedList, obj, position):
            #Removes current stage's sprites
            for placedObj in placedList:
                placedsprites.remove(placedObj)
            placedList = []
            #Read lines from lengths and match up with positions
            global eachLengthLine, previousLocation, objLocation
            if len(eachLengthLine) > position:
                objLocation = int(eachLengthLine[position])
                for i in range(previousLocation, objLocation+previousLocation):
                    placedObj = PlacedObjects(obj)
                    placedObj.rect.topleft = rectList[i]
                    placedsprites.add(placedObj)
                    placedList.append(placedObj)
                previousLocation += objLocation
                return placedList
            else:
                print("Warning: You have an old version!")
        placed.whitePawnList = loadObj(placed.whitePawnList, "whitepawn", 3)
        placed.whiteBishopList = loadObj(placed.whiteBishopList, "whitebishop", 4)
        placed.whiteKnightList = loadObj(placed.whiteKnightList, "whiteknight", 5)
        placed.whiteRookList = loadObj(placed.whiteRookList, "whiterook", 6)
        placed.whiteQueenList = loadObj(placed.whiteQueenList, "whitequeen", 7)
        placed.whiteKingList = loadObj(placed.whiteKingList, "whiteking", 8)
        placed.blackPawnList = loadObj(placed.blackPawnList, "blackpawn", 9)
        placed.blackBishopList = loadObj(placed.blackBishopList, "blackbishop", 10)
        placed.blackKnightList = loadObj(placed.blackKnightList, "blackknight", 11)
        placed.blackRookList = loadObj(placed.blackRookList, "blackrook", 12)
        placed.blackQueenList = loadObj(placed.blackQueenList, "blackqueen", 13)
        placed.blackKingList = loadObj(placed.blackKingList, "blackking", 14)
        saveFile.close()
        print("File Loaded")
    except IOError:
        #Error reading file
        print("IOError")
    except ValueError:
        #There's a file there, but we don't understand the number.
        print("ValueError")

def saveFile():
    global COLORKEY
    try:
        # default extension is optional, here will add .txt if missing
        saveFile = asksaveasfilename(defaultextension=".lvl")
        saveFileName = open(saveFile, "w")
        if saveFileName is not None:
            # Write the file to disk
            lengths_file = open(saveFile, "a")
            lengths_file.write(str(COLORKEY[0]) + "\n")
            lengths_file.write(str(COLORKEY[1]) + "\n")
            lengths_file.write(str(COLORKEY[2]) + "\n")
            def saveObj(placedList):
                for i in range(0, len(placedList)):
                    saveFileName.write(str(placedList[i].rect.topleft) + ", \n")
                lengths_file.write(str(len(placedList)) + "\n")
            for itemList in placed.totalPlacedList:
                saveObj(itemList)
            saveFileName.close()
            print("File Saved Successfully.")
        else:
            print("Error!")
    except IOError:
        print("Save File Error, please restart game and try again.")

def quit():
    print('Thanks for playing')
    sys.exit()
    
def clearGrid():
    for grid in room.gridList:
        grid.noHighlight()

def deactivatePiece(coord, pin):
    #pin parameter determines whether we want pinned piece to be able to move
    for grid in room.gridList:
        for colorList in play.totalPlayList:
            for pieceList in colorList:
                for piece in pieceList:
                    if(piece.coordinate == coord and pin == True):
                        piece.pinned = True
                    else:
                        piece.pinned = False
                
# Projected Bishop Path
def bishopProjected(piece, col):
    global CHECKTEXT
    piecesInWay = 0 #Pieces between the bishop and the enemy King
    kingCounter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1): #Counts pieces that are in bishops projected range
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 50 or piecesInWay > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #northwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2): 
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #northeast
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
    except:
        pass
    
# ProjectedRookPath
def rookProjected(piece, col):
    global CHECKTEXT
    piecesInWay = 0 #Pieces between the rook and the enemy King
    kingCounter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1,8): #West
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1): #Counts pieces that are in rook's projected range
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #east
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]

        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #north
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2): 
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
        for i in range(1,8): #south
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(kingCounter < 1): #Ignoring pieces that are past the king
                            piecesInWay += 1
                            if(grid.occWhiteOrBlack != col):
                                if(grid.occKing == 1 and grid.occWhiteOrBlack != col): #Finds the king
                                    kingCounter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(piecesInWay == 2 and kingCounter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(piecesInWay == 1 and kingCounter == 1):
            CHECKTEXT = "Check"
            raise
        elif(kingCounter == 0 or piecesInWay > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            piecesInWay = 0
            kingCounter = 0
    except:
        pass



# Moving pieces
def rookMove(piece, col):
    try:
        for i in range(1,8): #west
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1] and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1] and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #east
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1] and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1] and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #north
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #south
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass

def bishopMove(piece, col):
    try:
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #northwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    try:
        for i in range(1,8): #northeast
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 1:
                    if(grid.occWhiteOrBlack != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    
def queenMove(piece, col):
    rookMove(piece, col)
    bishopMove(piece, col)
            
class InfoScreen(object):
    def __init__(self,screen):
        self.screen = screen
        self.title = infoScreen
        self.clock = pygame.time.Clock()
        event = pygame.event.get()
        self.main_loop()

    def main_loop(self):
        global MENUON
        while MENUON == 2:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            events = pygame.event.get()
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        MENUON = 1

class StartBlankBox(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprBlankBox"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        if dragging.whitePawn:
            self.image = images["sprWhitePawn"]
        elif dragging.whiteBishop:
            self.image = images["sprWhiteBishop"]
        elif dragging.whiteKnight:
            self.image = images["sprWhiteKnight"]
        elif dragging.whiteRook:
            self.image = images["sprWhiteRook"]
        elif dragging.whiteQueen:
            self.image = images["sprWhiteQueen"]
        elif dragging.whiteKing:
            self.image = images["sprWhiteKing"]
        elif dragging.blackPawn:
            self.image = images["sprBlackPawn"]
        elif dragging.blackBishop:
            self.image = images["sprBlackBishop"]
        elif dragging.blackKnight:
            self.image = images["sprBlackKnight"]
        elif dragging.blackRook:
            self.image = images["sprBlackRook"]
        elif dragging.blackQueen:
            self.image = images["sprBlackQueen"]
        elif dragging.blackKing:
            self.image = images["sprBlackKing"]
        else:
            self.image = images["sprBlankBox"]
            
class StartObjects(pygame.sprite.Sprite):
    def __init__(self, classname):
        pygame.sprite.Sprite.__init__(self)
        self.classname = classname
        if(classname == "whitepawn"):
            self.image = images["sprWhitePawn"]
        elif(classname == "whitebishop"):
            self.image = images["sprWhiteBishop"]
        elif(classname == "whiteknight"):
            self.image = images["sprWhiteKnight"]
        elif(classname == "whiterook"):
            self.image = images["sprWhiteRook"]
        elif(classname == "whitequeen"):
            self.image = images["sprWhiteQueen"]
        elif(classname == "whiteking"):
            self.image = images["sprWhiteKing"]
        elif(classname == "blackpawn"):
            self.image = images["sprBlackPawn"]
        elif(classname == "blackbishop"):
            self.image = images["sprBlackBishop"]
        elif(classname == "blackknight"):
            self.image = images["sprBlackKnight"]
        elif(classname == "blackrook"):
            self.image = images["sprBlackRook"]
        elif(classname == "blackqueen"):
            self.image = images["sprBlackQueen"]
        elif(classname == "blackking"):
            self.image = images["sprBlackKing"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        global mousePos
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.classname == "whitepawn"):
            if dragging.whitePawn:
                start.blankBox.rect.topleft = startPos['whitePawn'] #Replaces in Menu
                start.whitePawn.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whitePawn.rect.topleft = startPos['whitePawn']
        elif(self.classname == "whitebishop"):
            if dragging.whiteBishop:
                start.blankBox.rect.topleft = startPos['whiteBishop'] #Replaces in Menu
                start.whiteBishop.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whiteBishop.rect.topleft = startPos['whiteBishop']
        elif(self.classname == "whiteknight"):
            if dragging.whiteKnight:
                start.blankBox.rect.topleft = startPos['whiteKnight'] #Replaces in Menu
                start.whiteKnight.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whiteKnight.rect.topleft = startPos['whiteKnight']
        elif(self.classname == "whiterook"):
            if dragging.whiteRook:
                start.blankBox.rect.topleft = startPos['whiteRook'] #Replaces in Menu
                start.whiteRook.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whiteRook.rect.topleft = startPos['whiteRook']
        elif(self.classname == "whitequeen"):
            if dragging.whiteQueen:
                start.blankBox.rect.topleft = startPos['whiteQueen'] #Replaces in Menu
                start.whiteQueen.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whiteQueen.rect.topleft = startPos['whiteQueen']
        elif(self.classname == "whiteking"):
            if dragging.whiteKing and len(placed.whiteKingList) == 0:
                start.blankBox.rect.topleft = startPos['whiteKing'] #Replaces in Menu
                start.whiteKing.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.whiteKing.rect.topleft = startPos['whiteKing']
        elif(self.classname == "blackpawn"):
            if dragging.blackPawn:
                start.blankBox.rect.topleft = startPos['blackPawn'] #Replaces in Menu
                start.blackPawn.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackPawn.rect.topleft = startPos['blackPawn']
        elif(self.classname == "blackbishop"):
            if dragging.blackBishop:
                start.blankBox.rect.topleft = startPos['blackBishop'] #Replaces in Menu
                start.blackBishop.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackBishop.rect.topleft = startPos['blackBishop']
        elif(self.classname == "blackknight"):
            if dragging.blackKnight:
                start.blankBox.rect.topleft = startPos['blackKnight'] #Replaces in Menu
                start.blackKnight.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackKnight.rect.topleft = startPos['blackKnight']
        elif(self.classname == "blackrook"):
            if dragging.blackRook:
                start.blankBox.rect.topleft = startPos['blackRook'] #Replaces in Menu
                start.blackRook.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackRook.rect.topleft = startPos['blackRook']
        elif(self.classname == "blackqueen"):
            if dragging.blackQueen:
                start.blankBox.rect.topleft = startPos['blackQueen'] #Replaces in Menu
                start.blackQueen.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackQueen.rect.topleft = startPos['blackQueen']
        elif(self.classname == "blackking"):
            if dragging.blackKing and len(placed.blackKingList) == 0:
                start.blankBox.rect.topleft = startPos['blackKing'] #Replaces in Menu
                start.blackKing.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
            else:
                start.blackKing.rect.topleft = startPos['blackKing']
                
class PlacedObjects(pygame.sprite.Sprite):
    def __init__(self, classname):
        pygame.sprite.Sprite.__init__(self)
        self.classname = classname
        if(self.classname == "whitepawn"):
            self.image = images["sprWhitePawn"]
        elif(self.classname == "whitebishop"):
            self.image = images["sprWhiteBishop"]
        elif(self.classname == "whiteknight"):
            self.image = images["sprWhiteKnight"]
        elif(self.classname == "whiterook"):
            self.image = images["sprWhiteRook"]
        elif(self.classname == "whitequeen"):
            self.image = images["sprWhiteQueen"]
        elif(self.classname == "whiteking"):
            self.image = images["sprWhiteKing"]
        elif(self.classname == "blackpawn"):
            self.image = images["sprBlackPawn"]
        elif(self.classname == "blackbishop"):
            self.image = images["sprBlackBishop"]
        elif(self.classname == "blackknight"):
            self.image = images["sprBlackKnight"]
        elif(self.classname == "blackrook"):
            self.image = images["sprBlackRook"]
        elif(self.classname == "blackqueen"):
            self.image = images["sprBlackQueen"]
        elif(self.classname == "blackking"):
            self.image = images["sprBlackKing"]
        self.rect = self.image.get_rect()
        placedsprites.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        
class PlayBishop(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteBishop"]
        elif(self.color == "black"):
            self.image = images["sprBlackBishop"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
        if(self.select == 0): # Projected Spaces Attacked
            bishopProjected(self, self.color)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteBishopHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackBishopHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            bishopMove(self, self.color)
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteBishop"]
        elif(self.color == "black"):
            self.image = images["sprBlackBishop"]
        self.select = 0
        
class PlayKnight(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteKnight"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnight"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKnightHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnightHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-2 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+2 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-2 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+2 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                    grid.highlight()
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKnight"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnight"]
        self.select = 0
        
class PlayRook(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteRook"]
            self.ranknum = 1
        elif(self.color == "black"):
            self.image = images["sprBlackRook"]
            self.ranknum = 8
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
        if(self.select == 0): # Projected Spaces Attacked
            rookProjected(self, self.color)
    def moveSquare(self, coordinateParameter, castle=False):
        if castle == False:
            for grid in room.gridList:
                if grid.coordinate == coordinate:
                    self.rect.topleft = grid.rect.topleft
        if castle == True and self.coordinate == ['h', self.ranknum]:
            if play.whiteKingList[0].rightCastleAbility == 1 and play.whiteKingList[0].coordinate == ['g', 1]:
                for grid in room.gridList:
                    if grid.coordinate == ['f', self.ranknum]:
                        self.rect.topleft = grid.rect.topleft
                        self.coordinate = grid.coordinate
        if castle == True and self.coordinate == ['a', self.ranknum]:
            if play.whiteKingList[0].leftCastleAbility == 1 and play.whiteKingList[0].coordinate == ['c', 1]:
                for grid in room.gridList:
                    if grid.coordinate == ['d', self.ranknum]:
                        self.rect.topleft = grid.rect.topleft
                        self.coordinate = grid.coordinate
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteRookHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackRookHighlighted"]
        self.select = 1
    def projected(self):
        # Try and Except for each direction
        if(self.pinned == False):
            rookMove(self, self.color)
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteRook"]
        elif(self.color == "black"):
            self.image = images["sprBlackRook"]
        self.select = 0

class PlayQueen(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteQueen"]
        elif(self.color == "black"):
            self.image = images["sprBlackQueen"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteQueenHighlighted"]
        if(self.color == "black"):
            self.image = images["sprBlackQueenHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            queenMove(self, self.color)
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteQueen"]
        if(self.color == "black"):
            self.image = images["sprBlackQueen"]
        self.select = 0

class PlayKing(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteKing"]
        elif(self.color == "black"):
            self.image = images["sprBlackKing"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.leftCastleAbility = 0
        self.rightCastleAbility = 0
        self.rightClearWay = [0, 0]
        self.leftClearWay = [0, 0, 0]
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.leftCastleAbility == 2 or self.rightCastleAbility == 2):
            self.leftCastleAbility = 2
            self.rightCastleAbility = 2
        elif((self.color == "white" and self.coordinate == ['e', 1]) or (self.color == "black" and self.coordinate == ['e', 8])):
            self.castleCheck(self.color)
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def castleCheck(self, color):
        if color == "white":
            rookList = play.whiteRookList
            ranknum = 1
        elif color == "black":
            rookList = play.blackRookList
            ranknum = 8
        for rook in rookList:
            if(rook.coordinate == ['h', ranknum]):
                self.rightClearWay = [0, 0]
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['f', ranknum] and room.gridList[i].occupied == 0):
                        self.rightClearWay[0] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['g', ranknum] and room.gridList[i].occupied == 0):
                        self.rightClearWay[1] = 1
                if(self.rightClearWay == [1, 1]):
                    self.rightCastleAbility = 1
                else:
                    self.rightCastleAbility = 0
            if(rook.coordinate == ['a', ranknum]):
                leftClearWay = [0, 0, 0]
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['b', ranknum] and room.gridList[i].occupied == 0):
                        self.leftClearWay[0] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['c', ranknum] and room.gridList[i].occupied == 0):
                        self.leftClearWay[1] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['d', ranknum] and room.gridList[i].occupied == 0):
                        self.leftClearWay[2] = 1
                if(self.leftClearWay == [1, 1, 1]):
                    self.leftCastleAbility = 1
                else:
                    self.leftCastleAbility = 0
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKingHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackKingHighlighted"]
        self.select = 1
    def projected(self):
        # Try and Except for each direction
        for grid in room.gridList:
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color):
                grid.highlight()
            if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color) and
                self.rightCastleAbility == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                    grid.highlight()
            if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occWhiteOrBlack != self.color) and
                self.leftCastleAbility == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                    grid.highlight()
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKing"]
        elif(self.color == "black"):
            self.image = images["sprBlackKing"]
        self.select = 0
        
class PlayPawn(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhitePawn"]
        elif(self.color == "black"):
            self.image = images["sprBlackPawn"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhitePawnHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackPawnHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            if(self.color == "white"):
                for grid in range(0,len(room.gridList)):
                    if (room.gridList[grid].coordinate[0] == self.coordinate[0] and room.gridList[grid].coordinate[1] == self.coordinate[1]+1 and \
                    room.gridList[grid].occupied == 0): # Move one space up
                        room.gridList[grid].highlight()
                        for grid in range(0,len(room.gridList)):
                            if (self.coordinate[1] == 2 and room.gridList[grid].coordinate[0] == self.coordinate[0] and \
                                room.gridList[grid].coordinate[1] == 4 and room.gridList[grid].occupied == 0):
                                room.gridList[grid].highlight()
                    # Enemy pieces
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])-1 and room.gridList[grid].coordinate[1] == self.coordinate[1]+1 and \
                    room.gridList[grid].occWhiteOrBlack == "black"):
                        room.gridList[grid].highlight()
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])+1 and room.gridList[grid].coordinate[1] == self.coordinate[1]+1 and \
                    room.gridList[grid].occWhiteOrBlack == "black"):
                        room.gridList[grid].highlight()
            elif(self.color == "black"):
                for grid in range(0,len(room.gridList)):
                    if (room.gridList[grid].coordinate[0] == self.coordinate[0] and room.gridList[grid].coordinate[1] == self.coordinate[1]-1 and \
                    room.gridList[grid].occupied == 0): # Move one space up
                        room.gridList[grid].highlight()
                        for grid in range(0,len(room.gridList)):
                            if (self.coordinate[1] == 7 and room.gridList[grid].coordinate[0] == self.coordinate[0] and \
                                room.gridList[grid].coordinate[1] == 5 and room.gridList[grid].occupied == 0):
                                room.gridList[grid].highlight()
                    # Enemy pieces
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])-1 and room.gridList[grid].coordinate[1] == self.coordinate[1]-1 and \
                    room.gridList[grid].occWhiteOrBlack == "white"):
                        room.gridList[grid].highlight()
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])+1 and room.gridList[grid].coordinate[1] == self.coordinate[1]-1 and \
                    room.gridList[grid].occWhiteOrBlack == "white"):
                        room.gridList[grid].highlight()
    def noHighlight(self):
        if(self.color == "white"):
            self.image = images["sprWhitePawn"]
        elif(self.color == "black"):
            self.image = images["sprBlackPawn"]
        self.select = 0
                    
class PlaySwitchButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprPlayButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self) #Play button only available when NOT in-play
        self.playSwitch = None
    def update(self):
        if(self.playSwitch is None):
            playsprites.remove(self)
            self.image = images["sprPlayButton"]
            startsprites.add(self)
        elif(self.playSwitch is not None):
            startsprites.remove(self)
            self.image = images["sprStopButton"]
            playsprites.add(self)
    
class Grid(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprGrid"]
        self.rect = self.image.get_rect()
        gridsprites.add(self)
        self.coordinate = ["z",0] #Default, Must be changed
        self.highlighted = 0
        self.occupied = 0
        self.color = None
        self.occWhiteOrBlack = ""
        self.occKing = 0
    def update(self):
        global SCREENHEIGHT, SCREENWIDTH
        if self.rect.bottom > SCREENHEIGHT:
            startsprites.remove(self)
        if self.rect.right > SCREENWIDTH:
            startsprites.remove(self)
        if(self.occupied == 1):
            self.pieceCaptured("white", "black", play.whiteList) # White piece stays
            self.pieceCaptured("black", "white", play.blackList) # Black piece stays
        elif(self.occupied == 0):
            self.occWhiteOrBlack = ""
            self.occKing = 0
        for whiteKing in play.whiteKingList:
            if self.coordinate == whiteKing.coordinate:
                self.occKing = 1
        for blackKing in play.blackKingList:
            if self.coordinate == blackKing.coordinate:
                self.occKing = 1
    def pieceCaptured(self, col, notcol, colorList):
        global TAKENPIECEXWHITE, TAKENPIECEYWHITE, TAKENPIECEXBLACK, TAKENPIECEYBLACK
        for pieceList in colorList:
            for piece in pieceList:
                if(self.coordinate == piece.coordinate and self.occWhiteOrBlack == ""): # Resets the White Or Black Check if not occupied at all
                    self.occWhiteOrBlack = col
                elif(self.coordinate == piece.coordinate and self.occWhiteOrBlack == notcol): #Was Black/White Before (Meaning Prior Piece gets Moved)
                    for colorPieces in play.totalPlayList:
                        for pieceList in colorPieces:
                            for piece in pieceList:
                                if (self.coordinate == piece.coordinate and piece.color == notcol):
                                    if(piece.color == "white"):
                                        piece.rect.topleft = (TAKENPIECEXWHITE, TAKENPIECEYWHITE)
                                        TAKENPIECEXWHITE += 50
                                    elif(piece.color == "black"):
                                        piece.rect.topleft = (TAKENPIECEXBLACK, TAKENPIECEYBLACK)
                                        TAKENPIECEXBLACK += 50
                                    piece.noHighlight()
                                    piece.coordinate = ['z', 0]
                                    clearGrid()
                                    
                    self.occWhiteOrBlack = col
    def whichSquare(self): # This calculates the coordinate of the grid
        for i in range(XGRIDRANGE[0], XGRIDRANGE[1], XGRIDRANGE[2]):
            for j in range(0,8):
                if (self.rect.topleft[0] == XGRIDRANGE[0]+XGRIDRANGE[2]*j):
                    self.coordinate[0] = chr(97+j)
        for i in range(YGRIDRANGE[0], YGRIDRANGE[1], YGRIDRANGE[2]):
            for j in range(0,8):
                if (self.rect.topleft[1] == YGRIDRANGE[0]+YGRIDRANGE[2]*j):
                    self.coordinate[1] = 8-j
    def highlight(self):
        self.image = images["sprHighlight"]
        self.highlighted = 1
    def noHighlight(self):
        if(self.color == "green"):
            self.image = images["sprGreenGrid"]
        elif(self.color == "white"):
            self.image = images["sprWhiteGrid"]
        self.highlighted = 0
            
class ClearButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprClearButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        pass
    
class InfoButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprInfoButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        pass
    
class RestartButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprRestartButton"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
    def update(self):
        pass
    
class ColorButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprColorButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        pass
    def getColor(self):
        try:
            color = askcolor()
            COLORKEY[0] = color[0][0]
            COLORKEY[1] = color[0][1]
            COLORKEY[2] = color[0][2]
        except:
            pass
        
class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprSaveFileButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        pass
    
class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprLoadFileButton"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        pass
    
class Dragging():
    def __init__(self):
        self.whitePawn = None
        self.whiteBishop = None
        self.whiteKnight = None
        self.whiteRook = None
        self.whiteQueen = None
        self.whiteKing = None
        self.blackPawn = None
        self.blackBishop = None
        self.blackKnight = None
        self.blackRook = None
        self.blackQueen = None
        self.blackKing = None
    def draggingNone(self):
        self.whitePawn = None
        self.whiteBishop = None
        self.whiteKnight = None
        self.whiteRook = None
        self.whiteQueen = None
        self.whiteKing = None
        self.blackPawn = None
        self.blackBishop = None
        self.blackKnight = None
        self.blackRook = None
        self.blackQueen = None
        self.blackKing = None

class Start():
    def __init__(self):
        self.blankBox = StartBlankBox()
        self.whitePawn = StartObjects("whitepawn")
        self.whiteBishop = StartObjects("whitebishop")
        self.whiteKnight = StartObjects("whiteknight")
        self.whiteRook = StartObjects("whiterook")
        self.whiteQueen = StartObjects("whitequeen")
        self.whiteKing = StartObjects("whiteking")
        self.blackPawn = StartObjects("blackpawn")
        self.blackBishop = StartObjects("blackbishop")
        self.blackKnight = StartObjects("blackknight")
        self.blackRook = StartObjects("blackrook")
        self.blackQueen = StartObjects("blackqueen")
        self.blackKing = StartObjects("blackking")

class Placed():
    def __init__(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.whiteKnightList = []
        self.whiteRookList = []
        self.whiteQueenList = []
        self.whiteKingList = []
        self.blackPawnList = []
        self.blackBishopList = []
        self.blackKnightList = []
        self.blackRookList = []
        self.blackQueenList = []
        self.blackKingList = []
        self.totalPlacedList = [self.whitePawnList, self.whiteBishopList, self.whiteKnightList, self.whiteRookList,
                                self.whiteQueenList, self.whiteKingList, self.blackPawnList, self.blackBishopList,
                                self.blackKnightList, self.blackRookList, self.blackQueenList, self.blackKingList]
        
class Play():
    def __init__(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.whiteKnightList = []
        self.whiteRookList = []
        self.whiteQueenList = []
        self.whiteKingList = []
        self.blackPawnList = []
        self.blackBishopList = []
        self.blackKnightList = []
        self.blackRookList = []
        self.blackQueenList = []
        self.blackKingList = []
        self.whiteList = [self.whitePawnList, self.whiteBishopList, self.whiteKnightList, self.whiteRookList,
                              self.whiteQueenList, self.whiteKingList]
        self.blackList = [self.blackPawnList, self.blackBishopList, self.blackKnightList, self.blackRookList,
                          self.blackQueenList, self.blackKingList]
        self.totalPlayList = [self.whiteList, self.blackList]
    def PlayNone(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.whiteKnightList = []
        self.whiteRookList = []
        self.whiteQueenList = []
        self.whiteKingList = []
        self.blackPawnList = []
        self.blackBishopList = []
        self.blackKnightList = []
        self.blackRookList = []
        self.blackQueenList = []
        self.blackKingList = []
        self.whiteList = [self.whitePawnList, self.whiteBishopList, self.whiteKnightList, self.whiteRookList,
                              self.whiteQueenList, self.whiteKingList]
        self.blackList = [self.blackPawnList, self.blackBishopList, self.blackKnightList, self.blackRookList,
                          self.blackQueenList, self.blackKingList]
        self.totalPlayList = [self.whiteList, self.blackList]
        
class Room():
    def __init__(self):
        global WHOSETURN
        #Start Objects
        start.whitePawn.rect.topleft = startPos['whitePawn']
        start.whiteBishop.rect.topleft = startPos['whiteBishop']
        start.whiteKnight.rect.topleft = startPos['whiteKnight']
        start.whiteRook.rect.topleft = startPos['whiteRook']
        start.whiteQueen.rect.topleft = startPos['whiteQueen']
        start.whiteKing.rect.topleft = startPos['whiteKing']
        start.blackPawn.rect.topleft = startPos['blackPawn']
        start.blackBishop.rect.topleft = startPos['blackBishop']
        start.blackKnight.rect.topleft = startPos['blackKnight']
        start.blackRook.rect.topleft = startPos['blackRook']
        start.blackQueen.rect.topleft = startPos['blackQueen']
        start.blackKing.rect.topleft = startPos['blackKing']
        #Play and Stop Buttons
        playSwitchButton.rect.topleft = (SCREENWIDTH-50, 8)
        clearButton.rect.topleft = (SCREENWIDTH-115, 10)
        restartButton.rect.topleft = (SCREENWIDTH-175, 10)
        colorButton.rect.topleft = (SCREENWIDTH-195, 10)
        saveFileButton.rect.topleft = (SCREENWIDTH-230, 10)
        loadFileButton.rect.topleft = (SCREENWIDTH-265, 10)
        infoButton.rect.topleft = (SCREENWIDTH-320, 10)
        #Default White Turn
        WHOSETURN = "white"
        # Creates grid
        self.gridList = []
        for i in range(XGRIDRANGE[0], XGRIDRANGE[1], XGRIDRANGE[2]): 
            for j in range(YGRIDRANGE[0], YGRIDRANGE[1], YGRIDRANGE[2]): 
                grid = Grid()
                grid.rect.topleft = i, j
                self.gridList.append(grid)
                grid.whichSquare()
        for grid in self.gridList:
            for i in range(ord("a"), ord("h"), 2):
                for j in range(2,9,2):
                    if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                        grid.image = images["sprWhiteGrid"]
                        grid.color = "white"
            for i in range(ord("b"), ord("i"), 2):
                for j in range(1,8,2):
                    if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                        grid.image = images["sprWhiteGrid"]
                        grid.color = "white"
            for i in range(ord("a"), ord("h"), 2):
                for j in range(1,8,2):
                    if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                        grid.image = images["sprGreenGrid"]
                        grid.color = "green"
            for i in range(ord("b"), ord("i"), 2):
                for j in range(2,9,2):
                    if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                        grid.image = images["sprGreenGrid"]
                        grid.color = "green"
    def restart(self):
        global WHOSETURN, TAKENPIECECOORDS, TAKENPIECEXWHITE, TAKENPIECEYWHITE, TAKENPIECEXBLACK, TAKENPIECEYBLACK
        WHOSETURN = "white" # DEFAULT TURN
        TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
        TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
        TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
        TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
        # Resets grid
        for grid in self.gridList:
            grid.noHighlight()
            grid.occupied = 0
            
#Init
pygame.init()
screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #, pygame.FULLSCREEN for fullscreen
#Fonts
arialFont = pygame.font.SysFont('Arial', 24)
#Sprites
sprBlankBox = loadImage("Sprites/blankbox.png", "sprBlankBox", True, False)
sprWhitePawn = loadImage("Sprites/Chess/white_pawn.png", "sprWhitePawn", True, True)
sprWhitePawnHighlight = loadImage("Sprites/Chess/white_pawn_highlighted.png", "sprWhitePawnHighlighted", True, True)
sprWhiteBishop = loadImage("Sprites/Chess/white_bishop.png", "sprWhiteBishop", True, True)
sprWhiteBishopHighlight = loadImage("Sprites/Chess/white_bishop_highlighted.png", "sprWhiteBishopHighlighted", True, True)
sprWhiteKnight = loadImage("Sprites/Chess/white_knight.png", "sprWhiteKnight", True, True)
sprWhiteKnightHighlight = loadImage("Sprites/Chess/white_knight_highlighted.png", "sprWhiteKnightHighlighted", True, True)
sprWhiteRook = loadImage("Sprites/Chess/white_rook.png", "sprWhiteRook", True, True)
sprWhiteRookHighlight = loadImage("Sprites/Chess/white_rook_highlighted.png", "sprWhiteRookHighlighted", True, True)
sprWhiteQueen = loadImage("Sprites/Chess/white_queen.png", "sprWhiteQueen", True, True)
sprWhiteQueenHighlight = loadImage("Sprites/Chess/white_queen_highlighted.png", "sprWhiteQueenHighlighted", True, True)
sprWhiteKing = loadImage("Sprites/Chess/white_king.png", "sprWhiteKing", True, True)
sprWhiteKingHighlight = loadImage("Sprites/Chess/white_king_highlighted.png", "sprWhiteKingHighlighted", True, True)
sprBlackPawn = loadImage("Sprites/Chess/black_pawn.png", "sprBlackPawn", True, True)
sprBlackPawnHighlight = loadImage("Sprites/Chess/black_pawn_highlighted.png", "sprBlackPawnHighlighted", True, True)
sprBlackBishop = loadImage("Sprites/Chess/black_bishop.png", "sprBlackBishop", True, True)
sprBlackBishopHighlight = loadImage("Sprites/Chess/black_bishop_highlighted.png", "sprBlackBishopHighlighted", True, True)
sprBlackKnight = loadImage("Sprites/Chess/black_knight.png", "sprBlackKnight", True, True)
sprBlackKnightHighlight = loadImage("Sprites/Chess/black_knight_highlighted.png", "sprBlackKnightHighlighted", True, True)
sprBlackRook = loadImage("Sprites/Chess/black_rook.png", "sprBlackRook", True, True)
sprBlackRookHighlight = loadImage("Sprites/Chess/black_rook_highlighted.png", "sprBlackRookHighlighted", True, True)
sprBlackQueen = loadImage("Sprites/Chess/black_queen.png", "sprBlackQueen", True, True)
sprBlackQueenHighlight = loadImage("Sprites/Chess/black_queen_highlighted.png", "sprBlackQueenHighlighted", True, True)
sprBlackKing = loadImage("Sprites/Chess/black_king.png", "sprBlackKing", True, True)
sprBlackKingHighlight = loadImage("Sprites/Chess/black_king_highlighted.png", "sprBlackKingHighlighted", True, True)
sprGrid = loadImage("Sprites/grid.png", "sprGrid", True, True)
sprWhiteGrid = loadImage("Sprites/whiteGrid.png", "sprWhiteGrid", True, True)
sprGreenGrid = loadImage("Sprites/greenGrid.png", "sprGreenGrid", True, True)
sprHighlight = loadImage("Sprites/Chess/highlight.png", "sprHighlight", True, True)
sprHighlight2 = loadImage("Sprites/Chess/highlight2.png", "sprHighlight2", True, True)
#Start (Menu) Objects
start = Start()
#Placed Lists
placed = Placed()
#List of Play Objects (Start out empty until placed somewhere and playSwitch is not None)
play = Play()
#Dragging Variables
dragging = Dragging()
#Play and Stop Buttons
sprPlayButton = loadImage("Sprites/play_button.png", "sprPlayButton", True, True)
playSwitchButton = PlaySwitchButton()
sprStopButton = loadImage("Sprites/stopbutton.png", "sprStopButton", True, True)
sprClearButton = loadImage("Sprites/clear.png", "sprClearButton", True, True)
clearButton = ClearButton()
sprInfoButton = loadImage("Sprites/infobutton.png", "sprInfoButton", True, True)
infoButton = InfoButton()
sprRestartButton = loadImage("Sprites/restart.png", "sprRestartButton", True, True)
restartButton = RestartButton()
sprColorButton = loadImage("Sprites/colorbutton.png", "sprColorButton", True, True)
colorButton = ColorButton()
sprSaveFileButton = loadImage("Sprites/savefile.png", "sprSaveFileButton", True, True)
saveFileButton = SaveFileButton()
sprLoadFileButton = loadImage("Sprites/loadfile.png", "sprLoadFileButton", True, True)
loadFileButton = LoadFileButton()
#Backgrounds
infoScreen = pygame.image.load("Sprites/infoscreen.bmp").convert()
infoScreen = pygame.transform.scale(infoScreen, (SCREENWIDTH, SCREENHEIGHT))
#window
gameicon = pygame.image.load("Sprites/chessico.png")
pygame.display.set_icon(gameicon)
pygame.display.set_caption('Chess')
#fonts
coorAText = arialFont.render("a", 1, (0,0,0))
coorBText = arialFont.render("b", 1, (0,0,0))
coorCText = arialFont.render("c", 1, (0,0,0))
coorDText = arialFont.render("d", 1, (0,0,0))
coorEText = arialFont.render("e", 1, (0,0,0))
coorFText = arialFont.render("f", 1, (0,0,0))
coorGText = arialFont.render("g", 1, (0,0,0))
coorHText = arialFont.render("h", 1, (0,0,0))
coor1Text = arialFont.render("1", 1, (0,0,0))
coor2Text = arialFont.render("2", 1, (0,0,0))
coor3Text = arialFont.render("3", 1, (0,0,0))
coor4Text= arialFont.render("4", 1, (0,0,0))
coor5Text = arialFont.render("5", 1, (0,0,0))
coor6Text = arialFont.render("6", 1, (0,0,0))
coor7Text= arialFont.render("7", 1, (0,0,0))
coor8Text = arialFont.render("8", 1, (0,0,0))
#Main
if __name__ == '__main__':
    while RUNNING:
        clock.tick(60)
        mousePos = pygame.mouse.get_pos()
        if MENUON == 0: # Initiate room
            room = Room()
            MENUON = 1 # No initiation
        if MENUON == 2: # Info screen
            InfoScreen(screen)
        # GRID OCCUPIED
        try:
            for grid in range(0,len(room.gridList)):
                for colorPieces in play.totalPlayList:
                    for pieceList in colorPieces:
                        for piece in pieceList:
                            if piece.rect.topleft == room.gridList[grid].rect.topleft:
                                room.gridList[grid].occupied = 1
                                grid += 1
                            else:
                                room.gridList[grid].occupied = 0
        except IndexError:
            pass
    
        for event in pygame.event.get():
            if event.type == QUIT:
                RUNNING = False
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    MENUON = 1 #Getting out of menus
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and mousePos[0] > XGRIDRANGE[1]: #DRAG (only for menu and inanimate buttons at top)
                if playSwitchButton.playSwitch is None: #Checks if in Editing Mode
                    #BUTTONS
                    if colorButton.rect.collidepoint(mousePos):
                        colorButton.getColor()
                    if saveFileButton.rect.collidepoint(mousePos):
                        saveFile()
                    if loadFileButton.rect.collidepoint(mousePos):
                        loadFile()
                    #DRAG OBJECTS
                    if start.whitePawn.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whitePawn = not None
                    if start.whiteBishop.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whiteBishop = not None
                    if start.whiteKnight.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whiteKnight = not None
                    if start.whiteRook.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whiteRook = not None
                    if start.whiteQueen.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whiteQueen = not None
                    if start.whiteKing.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.whiteKing = not None
                    if start.blackPawn.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackPawn = not None
                    if start.blackBishop.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackBishop = not None
                    if start.blackKnight.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackKnight = not None
                    if start.blackRook.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackRook = not None
                    if start.blackQueen.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackQueen = not None
                    if start.blackKing.rect.collidepoint(mousePos):
                        draggingFunction()
                        dragging.blackKing = not None
            # LEFT CLICK
            elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                  mousePos[0] > XGRIDRANGE[0] and mousePos[0] < XGRIDRANGE[1] and
                  mousePos[1] > YGRIDRANGE[0] and mousePos[1] < YGRIDRANGE[1] and
                  start.whitePawn.coordinate[1] != 1 and start.whitePawn.coordinate[1] != 8 and
                  start.blackPawn.coordinate[1] != 1 and start.blackPawn.coordinate[1] != 8): #placedObject placed on location of mouse release AND white pawn not put on first or last row
    
                def dragToPlaced(drag, piece, placedList):
                    if pygame.mouse.get_pressed()[0] and drag is not None:
                        removeObject() #Remove what is already there
                        placedobj = PlacedObjects(piece)
                        placedobj.rect.topleft = snapToGrid(mousePos)
                        placedsprites.add(placedobj)
                        placedList.append(placedobj)
    
                dragToPlaced(dragging.whitePawn, "whitepawn", placed.whitePawnList)
                dragToPlaced(dragging.whiteBishop, "whitebishop", placed.whiteBishopList)
                dragToPlaced(dragging.whiteKnight, "whiteknight", placed.whiteKnightList)
                dragToPlaced(dragging.whiteRook, "whiterook", placed.whiteRookList)
                dragToPlaced(dragging.whiteQueen, "whitequeen", placed.whiteQueenList)
                if len(placed.whiteKingList) == 0:
                    dragToPlaced(dragging.whiteKing, "whiteking", placed.whiteKingList)
                dragToPlaced(dragging.blackPawn, "blackpawn", placed.blackPawnList)
                dragToPlaced(dragging.blackBishop, "blackbishop", placed.blackBishopList)
                dragToPlaced(dragging.blackKnight, "blackknight", placed.blackKnightList)
                dragToPlaced(dragging.blackRook, "blackrook", placed.blackRookList)
                dragToPlaced(dragging.blackQueen, "blackqueen", placed.blackQueenList)
                if len(placed.blackKingList) == 0:
                    dragToPlaced(dragging.blackKing, "blackking", placed.blackKingList)
                # Moves piece
                for grid in room.gridList:
                    for colorPieces in play.totalPlayList:
                        for pieceList in colorPieces:
                            for piece in pieceList:
                                if (grid.rect.collidepoint(mousePos) and grid.highlighted==1):
                                    if(piece.select == 1):
                                        piece.rect.topleft = grid.rect.topleft
                                        if piece == play.whiteKingList[0]:
                                            play.whiteKingList[0].coordinate = grid.coordinate
                                            for whiteRook in play.whiteRookList:
                                                if grid.coordinate == ['g', 1]:
                                                    whiteRook.moveSquare(['f', 1], True)
                                                elif grid.coordinate == ['c', 1]:
                                                    whiteRook.moveSquare(['d', 1], True)
                                            piece.leftCastleAbility = 2
                                            piece.rightCastleAbility = 2
                                        if(WHOSETURN == "white"):
                                            WHOSETURN = "black"
                                        elif(WHOSETURN == "black"):
                                            WHOSETURN = "white"

    
                clickedPiece = None
                # HIGHLIGHTS PIECE YOU CLICK ON
                for colorPieces in play.totalPlayList:
                    for pieceList in colorPieces:
                        for piece in pieceList:
                            if (piece.rect.collidepoint(mousePos) and piece.select == 0 and WHOSETURN == piece.color):
                                clickedPiece = piece
                            else:
                                piece.noHighlight()
                                clearGrid()
    
                if clickedPiece is not None:
                    # Just do this last, since we know only one piece will be selected
                    clickedPiece.highlight()
                    clickedPiece.projected()
                    clickedPiece = None
    
            if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                #LEFT CLICK PLAY BUTTON
                if playSwitchButton.rect.collidepoint(mousePos) and playSwitchButton.playSwitch is None: 
                    if playSwitchButton.playSwitch is None: #Makes clicking play again unclickable
                        print("Play Mode Activated")
                        playSwitchButton.playSwitch = not None #Switches to Play Mode
    
                        def placedToPlay(placedList, playList, playClass, col):
                            if placedList is not None:
                                for i in range(0, len(placedList)):
                                    playList.append(playClass(col)) #Adds to list same amount of PlayWhitePawns as PlaceWhitePawns
                                    playList[i].rect.topleft = placedList[i].rect.topleft #Each PlayWhitePawn in respective PlacedWhitePawn location
                                    for grid in room.gridList:
                                        if playList[i].rect.colliderect(grid):
                                            playList[i].coordinate = grid.coordinate
                                    
                        placedToPlay(placed.whitePawnList, play.whitePawnList, PlayPawn, col="white")
                        placedToPlay(placed.whiteBishopList, play.whiteBishopList, PlayBishop, col="white")
                        placedToPlay(placed.whiteKnightList, play.whiteKnightList, PlayKnight, col="white")
                        placedToPlay(placed.whiteRookList, play.whiteRookList, PlayRook, col="white")
                        placedToPlay(placed.whiteQueenList, play.whiteQueenList, PlayQueen, col="white")
                        placedToPlay(placed.whiteKingList, play.whiteKingList, PlayKing, col="white")
                        placedToPlay(placed.blackPawnList, play.blackPawnList, PlayPawn, col="black")
                        placedToPlay(placed.blackBishopList, play.blackBishopList, PlayBishop, col="black")
                        placedToPlay(placed.blackKnightList, play.blackKnightList, PlayKnight, col="black")
                        placedToPlay(placed.blackRookList, play.blackRookList, PlayRook, col="black")
                        placedToPlay(placed.blackQueenList, play.blackQueenList, PlayQueen, col="black")
                        placedToPlay(placed.blackKingList, play.blackKingList, PlayKing, col="black")
                # LEFT CLICK STOP BUTTON
                elif playSwitchButton.rect.collidepoint(mousePos) and playSwitchButton.playSwitch is not None:
                    if playSwitchButton.playSwitch is not None: #Makes sure you are not in editing mode to enter editing mode
                        print("Editing Mode Activated")
                        playSwitchButton.playSwitch = None
                        #All Play objects removed
                        play.PlayNone()
                    room.restart()
                if restartButton.rect.collidepoint(mousePos):
                    pass
                if infoButton.rect.collidepoint(mousePos):
                    MENUON = 2
                if clearButton.rect.collidepoint(mousePos):
                    if playSwitchButton.playSwitch is None: #Editing mode
                        draggingFunction()
                        def placedToRemove(placedList):
                            for placed in placedList:
                                placedsprites.remove(placed)
                            placedList = []
                            return placedList
                        placed.whitePawnList = placedToRemove(placed.whitePawnList)
                        placed.whiteBishopList = placedToRemove(placed.whiteBishopList)
                        placed.whiteKnightList = placedToRemove(placed.whiteKnightList)
                        placed.whiteRookList = placedToRemove(placed.whiteRookList)
                        placed.whiteQueenList = placedToRemove(placed.whiteQueenList)
                        placed.whiteKingList = placedToRemove(placed.whiteKingList)
                        placed.blackPawnList = placedToRemove(placed.blackPawnList)
                        placed.blackBishopList = placedToRemove(placed.blackBishopList)
                        placed.blackKnightList = placedToRemove(placed.blackKnightList)
                        placed.blackRookList = placedToRemove(placed.blackRookList)
                        placed.blackQueenList = placedToRemove(placed.blackQueenList)
                        placed.blackKingList = placedToRemove(placed.blackKingList)
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]: #Right click on obj, destroy
                if playSwitchButton.playSwitch is None: #Editing mode
                    draggingFunction()
                    removeObject()
            # MIDDLE MOUSE DEBUGGER
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                for grid in room.gridList:
                    if grid.rect.collidepoint(mousePos):
                        print(grid.coordinate)
            #PLAYER MOVEMENTS
            if(playSwitchButton.playSwitch is not None):
                pass
        if(playSwitchButton.playSwitch is not None): #ALL GAME ACTIONS
            pass
    
        #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
    
        #Update all sprites
        gridsprites.update()
        startsprites.update()
        placedsprites.update()
        playsprites.update()
        screen.fill(COLORKEY)
        if(playSwitchButton.playSwitch is None): #Only draw placed sprites in editing mode
            gridsprites.draw(screen)
            startsprites.draw(screen)
            placedsprites.draw(screen)
        elif(playSwitchButton.playSwitch is not None): #Only draw play sprites in play mode
            gridsprites.draw(screen)
            playsprites.draw(screen)
        # Board Coordinates Drawing
        coorLetterTextList = [coorAText, coorBText, coorCText, coorDText, coorEText, coorFText, coorGText, coorHText]
        for text in range(0,len(coorLetterTextList)):
            screen.blit(coorLetterTextList[text], (XGRIDRANGE[0]+XGRIDRANGE[2]/3+(XGRIDRANGE[2]*text),YGRIDRANGE[0]-(YGRIDRANGE[2]*0.75)))
            screen.blit(coorLetterTextList[text], (XGRIDRANGE[0]+XGRIDRANGE[2]/3+(XGRIDRANGE[2]*text),YGRIDRANGE[1]+(YGRIDRANGE[2]*0.25)))
        coorNumberTextList = [coor8Text, coor7Text, coor6Text, coor5Text, coor4Text, coor3Text, coor2Text, coor1Text]
        for text in range(0,len(coorNumberTextList)):
            screen.blit(coorNumberTextList[text], (XGRIDRANGE[0]-XGRIDRANGE[2]/2,YGRIDRANGE[0]+YGRIDRANGE[2]/4+(YGRIDRANGE[2]*text)))
            screen.blit(coorNumberTextList[text], (XGRIDRANGE[1]+XGRIDRANGE[2]/3,YGRIDRANGE[0]+YGRIDRANGE[2]/4+(YGRIDRANGE[2]*text)))
        if(playSwitchButton.playSwitch is not None):
            whoseTurnText = arialFont.render(WHOSETURN + "'s move to turn", 1, (0,0,0))
            pinCheckText = arialFont.render(CHECKTEXT, 1, (0,0,0))
            screen.blit(whoseTurnText, (XGRIDRANGE[1]+XGRIDRANGE[2],SCREENHEIGHT/2))
            screen.blit(pinCheckText, (XGRIDRANGE[1]+XGRIDRANGE[2],200))
        pygame.display.flip()
        pygame.display.update()
