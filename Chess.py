"""
Chess created by Brad Wyatt
Python 3.4.4.4
"""
import pygame, random, sys, ast, os
from pygame.constants import RLEACCEL
from pygame.locals import *
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import *
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

#Grouping Images and Sounds
startPos = {'whitePawn': (40, 12), 'whiteBishop':(90, 12)}
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
    for placedItemList in (placed.whitePawnList, placed.whiteBishopList):
        for placedItem in placedItemList: 
            if placedItem.rect.collidepoint(mousePos):
                placedsprites.remove(placedItem)
                placedItemList.remove(placedItem)

def draggingFunction():
    dragging.draggingNone()
    start.whitePawn.rect.topleft = startPos['whitePawn']
    start.whiteBishop.rect.topleft = startPos['whiteBishop']
    
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
        def loadObj(placedList, PlacedClass, position):
            #Removes current stage's sprites
            for placedObj in placedList:
                placedsprites.remove(placedObj)
            placedList = []
            #Read lines from lengths and match up with positions
            global eachLengthLine, previousLocation, objLocation
            if len(eachLengthLine) > position:
                objLocation = int(eachLengthLine[position])
                for i in range(previousLocation, objLocation+previousLocation):
                    placedObj = PlacedClass()
                    placedObj.rect.topleft = rectList[i]
                    placedsprites.add(placedObj)
                    placedList.append(placedObj)
                previousLocation += objLocation
                return placedList
            else:
                print("Warning: You have an old version!")
        placed.whitePawnList = loadObj(placed.whitePawnList, PlacedWhitePawn, 3)
        placed.whiteBishopList = loadObj(placed.whitePawnList, PlacedWhitePawn, 4)
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
        else:
            self.image = images["sprBlankBox"]

class StartWhitePawn(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhitePawn"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        global mousePos
        if dragging.whitePawn:
            start.blankBox.rect.topleft = startPos['whitePawn'] #Replaces in Menu
            start.whitePawn.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
        else:
            start.whitePawn.rect.topleft = startPos['whitePawn']
            
class StartWhiteBishop(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhiteBishop"]
        self.rect = self.image.get_rect()
        startsprites.add(self)
    def update(self):
        global mousePos
        if dragging.whiteBishop:
            start.blankBox.rect.topleft = startPos['whiteBishop'] #Replaces in Menu
            start.whiteBishop.rect.topleft = mousePos[0]-(self.image.get_width()/2), mousePos[1]-(self.image.get_height()/2)
        else:
            start.whiteBishop.rect.topleft = startPos['whiteBishop']

class PlacedWhitePawn(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhitePawn"]
        self.rect = self.image.get_rect()
        placedsprites.add(self)
    def update(self):
        pass
    
class PlacedWhiteBishop(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhiteBishop"]
        self.rect = self.image.get_rect()
        placedsprites.add(self)
    def update(self):
        pass
    
class PlayWhitePawn(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhitePawn"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def highlight(self):
        self.image = images["sprWhitePawnHighlighted"]
        self.select = 1
    def projected(self):
        for grid in range(0,len(room.gridList)):
            if room.gridList[grid].coordinate[0] == self.coordinate[0] and room.gridList[grid].coordinate[1] == self.coordinate[1]+1 and room.gridList[grid].occupied == 0: # Move one space up
                room.gridList[grid].highlight()
        for grid in range(0,len(room.gridList)):
            if (self.coordinate[1] == 2 and room.gridList[grid].coordinate[0] == self.coordinate[0] and room.gridList[grid].coordinate[1] == 4 and room.gridList[grid].occupied == 0):
                room.gridList[grid].highlight()
    def noHighlight(self):
        self.image = images["sprWhitePawn"]
        self.select = 0
    def noProjected(self):
        for grid in room.gridList:
            if grid.coordinate[0] == self.coordinate[0] and grid.coordinate[1] == self.coordinate[1]+1 and grid.occupied == 0: # Remove highlight one space up
                grid.noHighlight()
        for grid in room.gridList:
            if (self.coordinate[1] == 2 and grid.coordinate[0] == self.coordinate[0] and grid.coordinate[1] == 4 and grid.occupied == 0):
                grid.noHighlight()
                
class PlayWhiteBishop(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprWhiteBishop"]
        self.rect = self.image.get_rect()
        playsprites.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            playsprites.remove(self)
    def highlight(self):
        self.image = images["sprWhiteBishopHighlighted"]
        self.select = 1
    def projected(self):
        for grid in room.gridList:
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-i and grid.coordinate[1] == self.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-i and grid.coordinate[1] == self.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+i and grid.coordinate[1] == self.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+i and grid.coordinate[1] == self.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
    def noHighlight(self):
        self.image = images["sprWhiteBishop"]
        self.select = 0
    def noProjected(self):
        for grid in room.gridList:
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-i and grid.coordinate[1] == self.coordinate[1]-i and grid.occupied == 0:
                    grid.noHighlight()
        for grid in room.gridList:
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-i and grid.coordinate[1] == self.coordinate[1]+i and grid.occupied == 0:
                    grid.noHighlight()
        for grid in room.gridList:
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+i and grid.coordinate[1] == self.coordinate[1]-i and grid.occupied == 0:
                    grid.noHighlight()
        for grid in room.gridList:
            for i in range(1,8):
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+i and grid.coordinate[1] == self.coordinate[1]+i and grid.occupied == 0:
                    grid.noHighlight()
                    
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
        
    def update(self):
        global SCREENHEIGHT, SCREENWIDTH
        if self.rect.bottom > SCREENHEIGHT:
            startsprites.remove(self)
        if self.rect.right > SCREENWIDTH:
            startsprites.remove(self)
        if self.coordinate == ["z",0]: #If it equals to default
            self.whichSquare()
    def whichSquare(self): # This calculated the coordinate of the grid
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
        self.image = images["sprGrid"]
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
    def draggingNone(self):
        self.whitePawn = None
        self.whiteBishop = None

class Start():
    def __init__(self):
        self.blankBox = StartBlankBox()
        self.whitePawn = StartWhitePawn()
        self.whiteBishop = StartWhiteBishop()

class Placed():
    def __init__(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.totalPlacedList = [self.whitePawnList, self.whiteBishopList]
        
class Play():
    def __init__(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.totalPlayList = [self.whitePawnList, self.whiteBishopList]
    def PlayNone(self):
        self.whitePawnList = []
        self.whiteBishopList = []
        self.totalPlayList = [self.whitePawnList, self.whiteBishopList]
        
class Room():
    def __init__(self):
        #Start Objects
        start.whitePawn.rect.topleft = startPos['whitePawn']
        start.whiteBishop.rect.topleft = startPos['whiteBishop']
        #Play and Stop Buttons
        playSwitchButton.rect.topleft = (SCREENWIDTH-50, 8)
        clearButton.rect.topleft = (SCREENWIDTH-115, 10)
        restartButton.rect.topleft = (SCREENWIDTH-175, 10)
        colorButton.rect.topleft = (SCREENWIDTH-195, 10)
        saveFileButton.rect.topleft = (SCREENWIDTH-230, 10)
        loadFileButton.rect.topleft = (SCREENWIDTH-265, 10)
        infoButton.rect.topleft = (SCREENWIDTH-320, 10)
        # Creates grid
        self.gridList = []
        for i in range(XGRIDRANGE[0], XGRIDRANGE[1], XGRIDRANGE[2]): 
            for j in range(YGRIDRANGE[0], YGRIDRANGE[1], YGRIDRANGE[2]): 
                grid = Grid()
                grid.rect.topleft = i, j
                self.gridList.append(grid)
        
   
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
sprHighlight = loadImage("Sprites/Chess/highlight.png", "sprHighlight", True, True)
#Start (Menu) Objects
start = Start()
#Placed Lists
placed = Placed()
#List of Play Objects (Start out empty until placed somewhere and playSwitch is not None)
play = Play()
#Dragging Variables
dragging = Dragging()
#Play and Stop Buttons
sprPlayButton = loadImage("sprites/play_button.png", "sprPlayButton", True, True)
playSwitchButton = PlaySwitchButton()
sprStopButton = loadImage("sprites/stopbutton.png", "sprStopButton", True, True)
sprClearButton = loadImage("sprites/clear.png", "sprClearButton", True, True)
clearButton = ClearButton()
sprInfoButton = loadImage("sprites/infobutton.png", "sprInfoButton", True, True)
infoButton = InfoButton()
sprRestartButton = loadImage("sprites/restart.png", "sprRestartButton", True, True)
restartButton = RestartButton()
sprColorButton = loadImage("sprites/colorbutton.png", "sprColorButton", True, True)
colorButton = ColorButton()
sprSaveFileButton = loadImage("sprites/savefile.png", "sprSaveFileButton", True, True)
saveFileButton = SaveFileButton()
sprLoadFileButton = loadImage("sprites/loadfile.png", "sprLoadFileButton", True, True)
loadFileButton = LoadFileButton()
sprGrid = loadImage("sprites/grid.png", "sprGrid", True, True)
#Backgrounds
infoScreen = pygame.image.load("sprites/infoscreen.bmp").convert()
infoScreen = pygame.transform.scale(infoScreen, (SCREENWIDTH, SCREENHEIGHT))
#window
gameicon = pygame.image.load("sprites/chessico.png")
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
while RUNNING:
    clock.tick(60)
    mousePos = pygame.mouse.get_pos()
    if MENUON == 0: # Initiate room
        room = Room()
        MENUON = 1 # No initiation
    if MENUON == 2: # Info screen
        InfoScreen(screen)
    # GRID OCCUPIED
    for grid in range(0,len(room.gridList)):
        for pieceList in play.totalPlayList:
            for piece in pieceList:
                if piece.rect.topleft == room.gridList[grid].rect.topleft:
                    room.gridList[grid].occupied = 1
                    grid += 1
                else:
                    room.gridList[grid].occupied = 0
    for event in pygame.event.get():
        if event.type == QUIT:
            RUNNING = False
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                MENUON = 1 #Getting out of menus
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and mousePos[1] < 48: #DRAG (only for menu and inanimate buttons at top)
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
        # LEFT CLICK
        elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
              mousePos[0] > XGRIDRANGE[0] and mousePos[0] < XGRIDRANGE[1] and
              mousePos[1] > YGRIDRANGE[0] and mousePos[1] < YGRIDRANGE[1]): #placedObject placed on location of mouse release
            def dragToPlaced(drag, PlacedClass, placedList):
                if pygame.mouse.get_pressed()[0] and drag is not None:
                    removeObject() #Remove what is already there
                    placedobj = PlacedClass()
                    placedobj.rect.topleft = snapToGrid(mousePos)
                    placedsprites.add(placedobj)
                    placedList.append(placedobj)
            dragToPlaced(dragging.whitePawn, PlacedWhitePawn, placed.whitePawnList)
            dragToPlaced(dragging.whiteBishop, PlacedWhiteBishop, placed.whiteBishopList)
            # Moves piece
            for grid in room.gridList: # Move piece
                for pieceList in play.totalPlayList:
                    for piece in pieceList:
                        if (grid.rect.collidepoint(mousePos) and grid.highlighted==1):
                            if(piece.select == 1):
                                piece.rect.topleft = grid.rect.topleft
            # HIGHLIGHTS PIECE YOU CLICK ON
            for pieceList in play.totalPlayList:
                for piece in pieceList:
                    if (piece.rect.collidepoint(mousePos) and piece.select == 0):
                        piece.highlight()
                        piece.projected()
                    else:
                        piece.noHighlight()
                        piece.noProjected()
        if event.type == pygame.MOUSEBUTTONUP: #Release Drag
            if playSwitchButton.rect.collidepoint(mousePos) and playSwitchButton.playSwitch is None: #LEFT CLICK PLAY BUTTON
                if playSwitchButton.playSwitch is None: #Makes clicking play again unclickable
                    print("Play Mode Activated")
                    playSwitchButton.playSwitch = not None #Switches to Play Mode
                    def placedToPlay(placedList, playList, playClass):
                        if placedList is not None:
                            for i in range(0, len(placedList)):
                                playList.append(playClass()) #Adds to list same amount of PlayWhitePawns as PlaceWhitePawns
                                playList[i].rect.topleft = placedList[i].rect.topleft #Each PlayWhitePawn in respective PlacedWhitePawn location
                    placedToPlay(placed.whitePawnList, play.whitePawnList, PlayWhitePawn)
                    placedToPlay(placed.whiteBishopList, play.whiteBishopList, PlayWhiteBishop)
            # LEFT CLICK STOP BUTTON
            elif playSwitchButton.rect.collidepoint(mousePos) and playSwitchButton.playSwitch is not None:
                if playSwitchButton.playSwitch is not None: #Makes sure you are not in editing mode to enter editing mode
                    print("Editing Mode Activated")
                    playSwitchButton.playSwitch = None
                    #All Play objects removed
                    play.PlayNone()
                # Resets grid
                for grid in room.gridList:
                    grid.noHighlight()
                    grid.occupied = 0
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
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]: #Right click on obj, destroy
            if playSwitchButton.playSwitch is None: #Editing mode
                draggingFunction()
                removeObject()
        # MIDDLE MOUSE DEBUGGER
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
            for grid in room.gridList:
                if grid.rect.collidepoint(mousePos):
                    print(grid.occupied)
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
    pygame.display.flip()
    pygame.display.update()
