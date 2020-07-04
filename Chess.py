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

#Grouping Images and Sounds
start_pos = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
            'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
            'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
            'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}
images = {}
sounds = {}

START_SPRITES = pygame.sprite.Group()

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

def load_sound(file, name):
    sound = pygame.mixer.Sound(file)
    sounds[name] = sound
    
def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha == True:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0,0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    images[name] = new_image

def snap_to_grid(pos, screen_width, screen_height):
    best_num_x, best_num_y = 0, 48 # Y is 48 so it doesn't go above the menu
    for x_coord in range(0, screen_width, 24):
        if pos[0]-x_coord <= 24 and pos[0]-x_coord >= 0:
            best_num_x = x_coord
    for y_coord in range(48, screen_height, 24):
        if pos[1]-y_coord <= 24 and pos[1]-y_coord >= 0:
            best_num_y = y_coord
    return (best_num_x, best_num_y)
             
def remove_placed_object(PLACED_SPRITES, mousepos):
    for placed_item_list in (PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list,
                             PlacedKnight.white_knight_list, PlacedRook.white_rook_list,
                             PlacedQueen.white_queen_list, PlacedKing.white_king_list,
                             PlacedPawn.black_pawn_list, PlacedBishop.black_bishop_list,
                             PlacedKnight.black_knight_list, PlacedRook.black_rook_list,
                             PlacedQueen.black_queen_list, PlacedKing.black_king_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mousepos):
                PLACED_SPRITES.remove(placed_item)
                placed_item_list.remove(placed_item)
    return PLACED_SPRITES

def load_file(PLACED_SPRITES, colorkey):
    request_file_name = askopenfilename(defaultextension=".lvl")
    open_file = open(request_file_name, "r")
    loaded_file = open_file.read()
    loaded_dict = literal_eval(loaded_file)
            
    for play_white_pawn in PlayPawn.white_pawn_list:
        play_white_pawn.destroy()
    for play_white_bishop in PlayBishop.white_bishop_list:
        play_white_bishop.destroy()
    for play_white_knight in PlayKnight.white_knight_list:
        play_white_knight.destroy()
    for play_white_rook in PlayRook.white_rook_list:
        play_white_rook.destroy()
    for play_white_queen in PlayQueen.white_queen_list:
        play_white_queen.destroy()
    for play_white_king in PlayKing.white_king_list:
        play_white_king.destroy()
    for play_black_pawn in PlayPawn.black_pawn_list:
        play_black_pawn.destroy()
    for play_black_bishop in PlayBishop.black_bishop_list:
        play_black_bishop.destroy()
    for play_black_knight in PlayKnight.black_knight_list:
        play_black_knight.destroy()
    for play_black_rook in PlayRook.black_rook_list:
        play_black_rook.destroy()
    for play_black_queen in PlayQueen.black_queen_list:
        play_black_queen.destroy()
    for play_black_king in PlayKing.black_king_list:
        play_black_king.destroy()
    open_file.close()
    
    # Removes all placed lists
    remove_all_placed()
    
    print("Removed all sprites. Now creating lists for loaded level.")
    
    for white_pawn_pos in loaded_dict['white_pawn']:
        PlacedPawn(white_pawn_pos, PLACED_SPRITES)
    for white_bishop_pos in loaded_dict['white_bishop']:
        PlacedBishop(white_bishop_pos, PLACED_SPRITES)
    for white_knight_pos in loaded_dict['white_knight']:
        PlacedKnight(white_knight_pos, PLACED_SPRITES)
    for white_rook_pos in loaded_dict['white_rook']:
        PlacedRook(white_rook_pos, PLACED_SPRITES)
    for white_queen_pos in loaded_dict['white_queen']:
        PlacedQueen(white_queen_pos, PLACED_SPRITES)
    for white_king_pos in loaded_dict['white_king']:
        PlacedKing(white_king_pos, PLACED_SPRITES)
    for black_pawn_pos in loaded_dict['black_pawn']:
        PlacedPawn(black_pawn_pos, PLACED_SPRITES)
    for black_bishop_pos in loaded_dict['black_bishop']:
        PlacedBishop(black_bishop_pos, PLACED_SPRITES)
    for black_knight_pos in loaded_dict['black_knight']:
        PlacedKnight(black_knight_pos, PLACED_SPRITES)
    for black_rook_pos in loaded_dict['black_rook']:
        PlacedRook(black_rook_pos, PLACED_SPRITES)
    for black_queen_pos in loaded_dict['black_queen']:
        PlacedQueen(black_queen_pos, PLACED_SPRITES)
    for black_king_pos in loaded_dict['black_king']:
        PlacedKing(black_king_pos, PLACED_SPRITES)
    colorkey = loaded_dict['RGB']
    
    print("File Loaded")
    return PLACED_SPRITES, colorkey

def save_file(colorkey):
    try:
        # default extension is optional, here will add .txt if missing
        save_file_prompt = asksaveasfilename(defaultextension=".lvl")
        save_file_name = open(save_file_prompt, "w")
        if save_file_name is not None:
            # Write the file to disk
            obj_locations = copy.deepcopy(get_dict_rect_positions())
            obj_locations['RGB'] = colorkey
            save_file_name.write(str(obj_locations))
            save_file_name.close()
            print("File Saved Successfully.")
        else:
            print("Error! Need player and door to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")

def quit():
    print('Thanks for playing')
    sys.exit()
    
def clearGrid():
    for grid in room.gridList:
        grid.no_highlight()

def deactivatePiece(coord, pin):
    #pin parameter determines whether we want pinned piece to be able to move
    for grid in room.gridList:
        for colorList in play.total_play_list:
            for pieceList in colorList:
                for piece in pieceList:
                    if(piece.coordinate == coord and pin == True):
                        piece.pinned = True
                    else:
                        piece.pinned = False
                
# Projected Bishop Path
def bishopProjected(piece, col):
    global CHECKTEXT
    pieces_in_way = 0 #Pieces between the bishop and the enemy King
    king_counter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1): #Counts pieces that are in bishops projected range
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 50 or pieces_in_way > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #northwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #southwest
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): 
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #northeast
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
    except:
        pass
    
# ProjectedRookPath
def rookProjected(piece, col):
    global CHECKTEXT
    pieces_in_way = 0 #Pieces between the rook and the enemy King
    king_counter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1,8): #West
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1): #Counts pieces that are in rook's projected range
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #east
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]

        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #north
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): 
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #south
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivatePiece(grid.coordinate, True)
                    #grid.image = images["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivatePiece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
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
        START_SPRITES.add(self)
    def update(self):
        if dragging.white_pawn:
            self.image = images["sprwhite_pawn"]
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
        if(classname == "white_pawn"):
            self.image = images["sprwhite_pawn"]
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
        START_SPRITES.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        global mouse_pos
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.classname == "white_pawn"):
            if dragging.white_pawn:
                start.blankBox.rect.topleft = start_pos['white_pawn'] #Replaces in Menu
                start.white_pawn.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.white_pawn.rect.topleft = start_pos['white_pawn']
        elif(self.classname == "whitebishop"):
            if dragging.whiteBishop:
                start.blankBox.rect.topleft = start_pos['whiteBishop'] #Replaces in Menu
                start.whiteBishop.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.whiteBishop.rect.topleft = start_pos['whiteBishop']
        elif(self.classname == "whiteknight"):
            if dragging.whiteKnight:
                start.blankBox.rect.topleft = start_pos['whiteKnight'] #Replaces in Menu
                start.whiteKnight.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.whiteKnight.rect.topleft = start_pos['whiteKnight']
        elif(self.classname == "whiterook"):
            if dragging.whiteRook:
                start.blankBox.rect.topleft = start_pos['whiteRook'] #Replaces in Menu
                start.whiteRook.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.whiteRook.rect.topleft = start_pos['whiteRook']
        elif(self.classname == "whitequeen"):
            if dragging.whiteQueen:
                start.blankBox.rect.topleft = start_pos['whiteQueen'] #Replaces in Menu
                start.whiteQueen.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.whiteQueen.rect.topleft = start_pos['whiteQueen']
        elif(self.classname == "whiteking"):
            if dragging.whiteKing and len(placed.white_king_list) == 0:
                start.blankBox.rect.topleft = start_pos['whiteKing'] #Replaces in Menu
                start.whiteKing.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.whiteKing.rect.topleft = start_pos['whiteKing']
        elif(self.classname == "blackpawn"):
            if dragging.blackPawn:
                start.blankBox.rect.topleft = start_pos['blackPawn'] #Replaces in Menu
                start.blackPawn.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackPawn.rect.topleft = start_pos['blackPawn']
        elif(self.classname == "blackbishop"):
            if dragging.blackBishop:
                start.blankBox.rect.topleft = start_pos['blackBishop'] #Replaces in Menu
                start.blackBishop.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackBishop.rect.topleft = start_pos['blackBishop']
        elif(self.classname == "blackknight"):
            if dragging.blackKnight:
                start.blankBox.rect.topleft = start_pos['blackKnight'] #Replaces in Menu
                start.blackKnight.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackKnight.rect.topleft = start_pos['blackKnight']
        elif(self.classname == "blackrook"):
            if dragging.blackRook:
                start.blankBox.rect.topleft = start_pos['blackRook'] #Replaces in Menu
                start.blackRook.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackRook.rect.topleft = start_pos['blackRook']
        elif(self.classname == "blackqueen"):
            if dragging.blackQueen:
                start.blankBox.rect.topleft = start_pos['blackQueen'] #Replaces in Menu
                start.blackQueen.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackQueen.rect.topleft = start_pos['blackQueen']
        elif(self.classname == "blackking"):
            if dragging.blackKing and len(placed.black_king_list) == 0:
                start.blankBox.rect.topleft = start_pos['blackKing'] #Replaces in Menu
                start.blackKing.rect.topleft = mouse_pos[0]-(self.image.get_width()/2), mouse_pos[1]-(self.image.get_height()/2)
            else:
                start.blackKing.rect.topleft = start_pos['blackKing']
                
class PlacedObjects(pygame.sprite.Sprite):
    def __init__(self, classname):
        pygame.sprite.Sprite.__init__(self)
        self.classname = classname
        if(self.classname == "white_pawn"):
            self.image = images["sprwhite_pawn"]
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
        PLACED_SPRITES.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        
class PlayBishop(pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteBishop"]
        elif(self.color == "black"):
            self.image = images["sprBlackBishop"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
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
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteBishop"]
        elif(self.color == "black"):
            self.image = images["sprBlackBishop"]
        self.select = 0
        
class PlayKnight(pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteKnight"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnight"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKnightHighlighted"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnightHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            for grid in room.gridList:
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-2 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+2 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-2 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+2 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                    grid.highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKnight"]
        elif(self.color == "black"):
            self.image = images["sprBlackKnight"]
        self.select = 0
        
class PlayRook(pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
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
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
        if(self.select == 0): # Projected Spaces Attacked
            rookProjected(self, self.color)
    def moveSquare(self, coordinateParameter, castle=False):
        if castle == False:
            for grid in room.gridList:
                if grid.coordinate == coordinate:
                    self.rect.topleft = grid.rect.topleft
        if castle == True and self.coordinate == ['h', self.ranknum]:
            if play.white_king_list[0].right_castle_ability == 1 and play.white_king_list[0].coordinate == ['g', 1]:
                for grid in room.gridList:
                    if grid.coordinate == ['f', self.ranknum]:
                        self.rect.topleft = grid.rect.topleft
                        self.coordinate = grid.coordinate
        if castle == True and self.coordinate == ['a', self.ranknum]:
            if play.white_king_list[0].leftCastleAbility == 1 and play.white_king_list[0].coordinate == ['c', 1]:
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
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteRook"]
        elif(self.color == "black"):
            self.image = images["sprBlackRook"]
        self.select = 0

class PlayQueen(pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteQueen"]
        elif(self.color == "black"):
            self.image = images["sprBlackQueen"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteQueenHighlighted"]
        if(self.color == "black"):
            self.image = images["sprBlackQueenHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            queenMove(self, self.color)
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteQueen"]
        if(self.color == "black"):
            self.image = images["sprBlackQueen"]
        self.select = 0

class PlayKing(pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprWhiteKing"]
        elif(self.color == "black"):
            self.image = images["sprBlackKing"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.leftCastleAbility = 0
        self.right_castle_ability = 0
        self.right_clear_way = [0, 0]
        self.left_clear_way = [0, 0, 0]
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.leftCastleAbility == 2 or self.right_castle_ability == 2):
            self.leftCastleAbility = 2
            self.right_castle_ability = 2
        elif((self.color == "white" and self.coordinate == ['e', 1]) or (self.color == "black" and self.coordinate == ['e', 8])):
            self.castle_check(self.color)
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
    def castle_check(self, color):
        if color == "white":
            rookList = play.white_rook_list
            ranknum = 1
        elif color == "black":
            rookList = play.black_rook_list
            ranknum = 8
        for rook in rookList:
            if(rook.coordinate == ['h', ranknum]):
                self.right_clear_way = [0, 0]
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['f', ranknum] and room.gridList[i].occupied == 0):
                        self.right_clear_way[0] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['g', ranknum] and room.gridList[i].occupied == 0):
                        self.right_clear_way[1] = 1
                if(self.right_clear_way == [1, 1]):
                    self.right_castle_ability = 1
                else:
                    self.right_castle_ability = 0
            if(rook.coordinate == ['a', ranknum]):
                left_clear_way = [0, 0, 0]
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['b', ranknum] and room.gridList[i].occupied == 0):
                        self.left_clear_way[0] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['c', ranknum] and room.gridList[i].occupied == 0):
                        self.left_clear_way[1] = 1
                for i in range(0, len(room.gridList)):
                    if(room.gridList[i].coordinate == ['d', ranknum] and room.gridList[i].occupied == 0):
                        self.left_clear_way[2] = 1
                if(self.left_clear_way == [1, 1, 1]):
                    self.leftCastleAbility = 1
                else:
                    self.leftCastleAbility = 0
    def highlight(self):
        if(self.color == "white"):
            self.image = images["SPR_WHITE_KING_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = images["SPR_BLACK_KING_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        # Try and Except for each direction
        for grid in room.gridList:
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+1 and (grid.occupied == 0 or grid.occ_white_or_black != self.color):
                grid.highlight()
            if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occ_white_or_black != self.color) and
                self.right_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                    grid.highlight()
            if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1] and (grid.occupied == 0 or grid.occ_white_or_black != self.color) and
                self.leftCastleAbility == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                    grid.highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprWhiteKing"]
        elif(self.color == "black"):
            self.image = images["sprBlackKing"]
        self.select = 0
        
class PlayPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = images["sprwhite_pawn"]
        elif(self.color == "black"):
            self.image = images["sprBlackPawn"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in room.gridList:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(playSwitchButton.playSwitch is None):
            PLAY_SPRITES.remove(self)
    def highlight(self):
        if(self.color == "white"):
            self.image = images["sprwhite_pawnHighlighted"]
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
                    room.gridList[grid].occ_white_or_black == "black"):
                        room.gridList[grid].highlight()
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])+1 and room.gridList[grid].coordinate[1] == self.coordinate[1]+1 and \
                    room.gridList[grid].occ_white_or_black == "black"):
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
                    room.gridList[grid].occ_white_or_black == "white"):
                        room.gridList[grid].highlight()
                    if (ord(room.gridList[grid].coordinate[0]) == ord(self.coordinate[0])+1 and room.gridList[grid].coordinate[1] == self.coordinate[1]-1 and \
                    room.gridList[grid].occ_white_or_black == "white"):
                        room.gridList[grid].highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = images["sprwhite_pawn"]
        elif(self.color == "black"):
            self.image = images["sprBlackPawn"]
        self.select = 0
                    
class PlaySwitchButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprPlayButton"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self) #Play button only available when NOT in-play
        self.playSwitch = None
    def update(self):
        if(self.playSwitch is None):
            PLAY_SPRITES.remove(self)
            self.image = images["sprPlayButton"]
            START_SPRITES.add(self)
        elif(self.playSwitch is not None):
            START_SPRITES.remove(self)
            self.image = images["sprStopButton"]
            PLAY_SPRITES.add(self)
    
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
        self.occ_white_or_black = ""
        self.occ_king = 0
    def update(self):
        global SCREENHEIGHT, SCREENWIDTH
        if self.rect.bottom > SCREENHEIGHT:
            START_SPRITES.remove(self)
        if self.rect.right > SCREENWIDTH:
            START_SPRITES.remove(self)
        if(self.occupied == 1):
            self.piece_captured("white", "black", play.white_list) # White piece stays
            self.piece_captured("black", "white", play.black_list) # Black piece stays
        elif(self.occupied == 0):
            self.occ_white_or_black = ""
            self.occ_king = 0
        for whiteKing in play.white_king_list:
            if self.coordinate == whiteKing.coordinate:
                self.occ_king = 1
        for blackKing in play.black_king_list:
            if self.coordinate == blackKing.coordinate:
                self.occ_king = 1
    def piece_captured(self, col, notcol, colorList):
        global TAKENPIECEXWHITE, TAKENPIECEYWHITE, TAKENPIECEXBLACK, TAKENPIECEYBLACK
        for pieceList in colorList:
            for piece in pieceList:
                if(self.coordinate == piece.coordinate and self.occ_white_or_black == ""): # Resets the White Or Black Check if not occupied at all
                    self.occ_white_or_black = col
                elif(self.coordinate == piece.coordinate and self.occ_white_or_black == notcol): #Was Black/White Before (Meaning Prior Piece gets Moved)
                    for color_pieces in play.total_play_list:
                        for pieceList in color_pieces:
                            for piece in pieceList:
                                if (self.coordinate == piece.coordinate and piece.color == notcol):
                                    if(piece.color == "white"):
                                        piece.rect.topleft = (TAKENPIECEXWHITE, TAKENPIECEYWHITE)
                                        TAKENPIECEXWHITE += 50
                                    elif(piece.color == "black"):
                                        piece.rect.topleft = (TAKENPIECEXBLACK, TAKENPIECEYBLACK)
                                        TAKENPIECEXBLACK += 50
                                    piece.no_highlight()
                                    piece.coordinate = ['z', 0]
                                    clearGrid()
                                    
                    self.occ_white_or_black = col
    def which_square(self): # This calculates the coordinate of the grid
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
    def no_highlight(self):
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
        START_SPRITES.add(self)
    def update(self):
        pass
    
class InfoButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprInfoButton"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass
    
class RestartButton(pygame.sprite.Sprite):
    def __init__(self, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprRestartButton"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
    def update(self):
        pass
    
class ColorButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprColorButton"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
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
        START_SPRITES.add(self)
    def update(self):
        pass
    
class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = images["sprLoadFileButton"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass
    
class Dragging():
    def __init__(self):
        self.white_pawn = None
        self.white_bishop = None
        self.white_knight = None
        self.white_rook = None
        self.white_queen = None
        self.white_king = None
        self.black_pawn = None
        self.black_bishop = None
        self.black_knight = None
        self.black_rook = None
        self.black_queen = None
        self.black_king = None
    def draggingNone(self):
        self.white_pawn = None
        self.white_bishop = None
        self.white_knight = None
        self.white_rook = None
        self.white_queen = None
        self.white_king = None
        self.black_pawn = None
        self.black_bishop = None
        self.black_knight = None
        self.black_rook = None
        self.black_queen = None
        self.black_king = None

class Start():
    def __init__(self):
        self.blankBox = StartBlankBox()
        self.white_pawn = StartObjects("white_pawn")
        self.white_bishop = StartObjects("white_bishop")
        self.white_knight = StartObjects("white_knight")
        self.white_rook = StartObjects("white_rook")
        self.white_queen = StartObjects("white_queen")
        self.white_king = StartObjects("white_king")
        self.black_pawn = StartObjects("black_pawn")
        self.black_bishop = StartObjects("black_bishop")
        self.black_knight = StartObjects("black_knight")
        self.black_rook = StartObjects("black_rook")
        self.black_queen = StartObjects("black_queen")
        self.black_king = StartObjects("black_king")

class Play():
    def __init__(self):
        self.white_pawn_list = []
        self.white_bishop_list = []
        self.white_knight_list = []
        self.white_rook_list = []
        self.white_queen_list = []
        self.white_king_list = []
        self.black_pawn_list = []
        self.black_bishop_list = []
        self.black_knight_list = []
        self.black_rook_list = []
        self.black_queen_list = []
        self.black_king_list = []
        self.white_list = [self.white_pawn_list, self.white_bishop_list, self.white_knight_list, self.white_rook_list,
                              self.white_queen_list, self.white_king_list]
        self.black_list = [self.black_pawn_list, self.black_bishop_list, self.black_knight_list, self.black_rook_list,
                          self.black_queen_list, self.black_king_list]
        self.total_play_list = [self.white_list, self.black_list]
    def PlayNone(self):
        self.white_pawn_list = []
        self.white_bishop_list = []
        self.white_knight_list = []
        self.white_rook_list = []
        self.white_queen_list = []
        self.white_king_list = []
        self.black_pawn_list = []
        self.black_bishop_list = []
        self.black_knight_list = []
        self.black_rook_list = []
        self.black_queen_list = []
        self.black_king_list = []
        self.white_list = [self.white_pawn_list, self.white_bishop_list, self.white_knight_list, self.white_rook_list,
                              self.white_queen_list, self.white_king_list]
        self.black_list = [self.black_pawn_list, self.black_bishop_list, self.black_knight_list, self.black_rook_list,
                          self.black_queen_list, self.black_king_list]
        self.total_play_list = [self.white_list, self.black_list]
        
class Room():
    def __init__(self):
        global WHOSETURN
        #Start Objects
        start.white_pawn.rect.topleft = start_pos['white_pawn']
        start.white_bishop.rect.topleft = start_pos['white_bishop']
        start.white_knight.rect.topleft = start_pos['white_knight']
        start.whiteRook.rect.topleft = start_pos['white_rook']
        start.whiteQueen.rect.topleft = start_pos['white_queen']
        start.whiteKing.rect.topleft = start_pos['white_king']
        start.black_pawn.rect.topleft = start_pos['black_pawn']
        start.black_bishop.rect.topleft = start_pos['black_bishop']
        start.black_knight.rect.topleft = start_pos['black_knight']
        start.black_rook.rect.topleft = start_pos['black_rook']
        start.black_queen.rect.topleft = start_pos['black_queen']
        start.black_king.rect.topleft = start_pos['black_king']
        #Play and Stop Buttons
        playSwitchButton.rect.topleft = (SCREENWIDTH-50, 8)
        CLEAR_BUTTON.rect.topleft = (SCREENWIDTH-115, 10)
        RESTART_BUTTON.rect.topleft = (SCREENWIDTH-175, 10)
        COLOR_BUTTON.rect.topleft = (SCREENWIDTH-195, 10)
        SAVE_FILE_BUTTON.rect.topleft = (SCREENWIDTH-230, 10)
        LOAD_FILE_BUTTON.rect.topleft = (SCREENWIDTH-265, 10)
        INFO_BUTTON.rect.topleft = (SCREENWIDTH-320, 10)
        #Default White Turn
        WHOSETURN = "white"
        # Creates grid
        self.gridList = []
        for i in range(XGRIDRANGE[0], XGRIDRANGE[1], XGRIDRANGE[2]): 
            for j in range(YGRIDRANGE[0], YGRIDRANGE[1], YGRIDRANGE[2]): 
                grid = Grid()
                grid.rect.topleft = i, j
                self.gridList.append(grid)
                grid.which_square()
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
    WHOSETURN = 1 # DEFAULT TURN
    TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
    TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
    TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
    TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
    # Resets grid
    for grid in self.gridList:
        grid.no_highlight()
        grid.occupied = 0
            
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'white_pawn': PlacedPawn.white_pawn_list, 'white_bishop': PlacedBishop.white_bishop_list, 
                         'white_knight': PlacedKnight.white_knight_list, 'white_rook': PlacedRook.white_rook_list,
                         'white_queen': PlacedQueen.white_queen_list, 'white_king': PlacedKing.white_king_list,
                         'black_pawn': PlacedPawn.black_pawn_list, 'black_bishop': PlacedBishop.black_bishop_list,
                         'black_knight': PlacedKnight.black_knight_list, 'black_rook': PlacedRook.black_rook_list,
                         'black_queen': PlacedQueen.black_queen_list, 'black_king': PlacedKing.black_king_list}
    get_rect_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_rect in item_list:
            item_list_in_name.append(item_rect.rect.topleft)
        get_rect_for_all_obj[item_key] = item_list_in_name
    return get_rect_for_all_obj

def remove_all_placed():
    for spr_list in [PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list,
                     PlacedKnight.white_knight_list, PlacedQueen.white_queen_list, 
                     PlacedKing.white_king_list, PlacedPawn.black_pawn_list,
                     PlacedBishop.black_bishop_list, PlacedKnight.black_knight_list, 
                     PlacedQueen.black_queen_list, PlacedKing.black_king_list]:
        for obj in spr_list:
            obj.kill()
    PlacedPlayer.player_list = []
    PlacedWall.wall_list = []
    PlacedFlyer.flyer_list = []
    PlacedReverseWall.reverse_wall_list = []
    PlacedSpring.spring_list = []
    PlacedSmilyRobot.smily_robot_list = []
    PlacedDoor.door_list = []
    PlacedDiamonds.diamonds_list = []
    PlacedStickyBlock.sticky_block_list = []
    PlacedFallSpikes.fall_spikes_list = []
    PlacedStandSpikes.stand_spikes_list = []

def remove_all_play():
    for spr_list in [PlayPlayer.player_list, PlayWall.wall_list, PlayFlyer.flyer_list,
                     PlayReverseWall.reverse_wall_list, PlaySpring.spring_list, PlaySmilyRobot.smily_robot_list,
                     PlayDoor.door_list, PlayDiamonds.diamonds_list, PlayStickyBlock.sticky_block_list,
                     PlayFallSpikes.fall_spikes_list, PlayStandSpikes.stand_spikes_list]:
        for obj in spr_list:
            obj.kill()
    PlayPlayer.player_list = []
    PlayWall.wall_list = []
    PlayFlyer.flyer_list = []
    PlayReverseWall.reverse_wall_list = []
    PlaySpring.spring_list = []
    PlaySmilyRobot.smily_robot_list = []
    PlayDoor.door_list = []
    PlayDiamonds.diamonds_list = []
    PlayStickyBlock.sticky_block_list = []
    PlayFallSpikes.fall_spikes_list = []
    PlayStandSpikes.stand_spikes_list = []


def main():
    
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
    WHOSETURN = 1
    TAKENPIECECOORDS = [50, 15, 50, 525]
    TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
    TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
    TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
    TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
    CHECKTEXT = ""
    
    #Init
    pygame.init()
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT)) #, pygame.FULLSCREEN for fullscreen
    
    gridsprites = pygame.sprite.Group()
    PLACED_SPRITES = pygame.sprite.Group()
    PLAY_SPRITES = pygame.sprite.Group()
    CLOCK = pygame.time.Clock()
    
    #Fonts
    arialFont = pygame.font.SysFont('Arial', 24)
    #Sprites
    load_image("Sprites/blankbox.png", "SPR_BLANKBOX", True, False)
    load_image("Sprites/Chess/white_pawn.png", "SPR_WHITE_PAWN", True, True)
    load_image("Sprites/Chess/white_pawn_highlighted.png", "SPR_WHITE_PAWN_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/white_bishop.png", "SPR_WHITE_BISHOP", True, True)
    load_image("Sprites/Chess/white_bishop_highlighted.png", "SPR_WHITE_BISHOP_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/white_knight.png", "SPR_WHITE_KNIGHT", True, True)
    load_image("Sprites/Chess/white_knight_highlighted.png", "SPR_WHITE_KNIGHT_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/white_rook.png", "SPR_WHITE_ROOK", True, True)
    load_image("Sprites/Chess/white_rook_highlighted.png", "SPR_WHITE_ROOK_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/white_queen.png", "SPR_WHITE_QUEEN", True, True)
    load_image("Sprites/Chess/white_queen_highlighted.png", "SPR_WHITE_QUEEN_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/white_king.png", "SPR_WHITE_KING", True, True)
    load_image("Sprites/Chess/white_king_highlighted.png", "SPR_WHITE_KING_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/black_pawn.png", "SPR_BLACK_PAWN", True, True)
    load_image("Sprites/Chess/black_pawn_highlighted.png", "SPR_BLACK_PAWN_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/black_bishop.png", "SPR_BLACK_BISHOP", True, True)
    load_image("Sprites/Chess/black_bishop_highlighted.png", "SPR_BLACK_BISHOP_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/black_knight.png", "SPR_BLACK_KNIGHT", True, True)
    load_image("Sprites/Chess/black_knight_highlighted.png", "SPR_BLACK_KNIGHT_HIGHLITED", True, True)
    load_image("Sprites/Chess/black_rook.png", "SPR_BLACK_ROOK", True, True)
    load_image("Sprites/Chess/black_rook_highlighted.png", "SPR_BLACK_ROOK_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/black_queen.png", "SPR_BLACK_QUEEN", True, True)
    load_image("Sprites/Chess/black_queen_highlighted.png", "SPR_BLACK_QUEEN_HIGHLIGHTED", True, True)
    load_image("Sprites/Chess/black_king.png", "SPR_BLACK_KING", True, True)
    load_image("Sprites/Chess/black_king_highlighted.png", "SPR_BLACK_KING_HIGHLIGHTED", True, True)
    load_image("Sprites/grid.png", "SPR_GRID", True, True)
    load_image("Sprites/whiteGrid.png", "SPR_WHITE_GRID", True, True)
    load_image("Sprites/greenGrid.png", "SPR_GREEN_GRID", True, True)
    load_image("Sprites/Chess/highlight.png", "SPR_HIGHLIGHT", True, True)
    load_image("Sprites/Chess/highlight2.png", "SPR_HIGHLIGHT2", True, True)
    #Start (Menu) Objects
    START = Start()
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
    RESTART_BUTTON = RestartButton(PLAY_SPRITES)
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
    
    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        if MENUON == 0: # Initiate room
            room = Room()
            MENUON = 1 # No initiation
        if MENUON == 2: # Info screen
            InfoScreen(screen)
        # GRID OCCUPIED
        try:
            for grid in range(0,len(room.gridList)):
                for color_pieces in play.total_play_list:
                    for pieceList in color_pieces:
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
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    MENUON = 1 #Getting out of menus
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and mouse_pos[0] > XGRIDRANGE[1]: #DRAG (only for menu and inanimate buttons at top)
                if playSwitchButton.playSwitch is None: #Checks if in Editing Mode
                    #BUTTONS
                    if colorButton.rect.collidepoint(mouse_pos):
                        colorButton.getColor()
                    if saveFileButton.rect.collidepoint(mouse_pos):
                        saveFile()
                    if loadFileButton.rect.collidepoint(mouse_pos):
                        loadFile()
                    #DRAG OBJECTS
                    if start.white_pawn.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.white_pawn = not None
                    if start.white_bishop.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.white_bishop = not None
                    if start.whiteKnight.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.white_knight = not None
                    if start.white_rook.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.whiteRook = not None
                    if start.whiteQueen.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.whiteQueen = not None
                    if start.whiteKing.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.whiteKing = not None
                    if start.blackPawn.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackPawn = not None
                    if start.blackBishop.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackBishop = not None
                    if start.blackKnight.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackKnight = not None
                    if start.blackRook.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackRook = not None
                    if start.blackQueen.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackQueen = not None
                    if start.blackKing.rect.collidepoint(mouse_pos):
                        dragging_function()
                        dragging.blackKing = not None
            # LEFT CLICK
            elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                  mouse_pos[0] > XGRIDRANGE[0] and mouse_pos[0] < XGRIDRANGE[1] and
                  mouse_pos[1] > YGRIDRANGE[0] and mouse_pos[1] < YGRIDRANGE[1] and
                  start.white_pawn.coordinate[1] != 1 and start.white_pawn.coordinate[1] != 8 and
                  start.black_pawn.coordinate[1] != 1 and start.black_pawn.coordinate[1] != 8): #placedObject placed on location of mouse release AND white pawn not put on first or last row
    
                def drag_to_placed(drag, piece, placed_list):
                    if pygame.mouse.get_pressed()[0] and drag is not None:
                        remove_object() #Remove what is already there
                        placedobj = PlacedObjects(piece)
                        placedobj.rect.topleft = snap_to_grid(mouse_pos)
                        PLACED_SPRITES.add(placedobj)
                        placed_list.append(placedobj)
    
                drag_to_placed(dragging.white_pawn, "white_pawn", placed.white_pawn_list)
                drag_to_placed(dragging.white_bishop, "whitebishop", placed.white_bishop_list)
                drag_to_placed(dragging.white_knight, "whiteknight", placed.white_knight_list)
                drag_to_placed(dragging.white_rook, "whiterook", placed.white_rook_list)
                drag_to_placed(dragging.white_queen, "whitequeen", placed.white_queen_list)
                if len(placed.white_king_list) == 0:
                    drag_to_placed(dragging.white_king, "whiteking", placed.white_king_list)
                drag_to_placed(dragging.black_pawn, "blackpawn", placed.black_pawn_list)
                drag_to_placed(dragging.black_bishop, "blackbishop", placed.black_bishop_list)
                drag_to_placed(dragging.black_knight, "blackknight", placed.black_knight_list)
                drag_to_placed(dragging.black_rook, "blackrook", placed.black_rook_list)
                drag_to_placed(dragging.black_queen, "blackqueen", placed.black_queen_list)
                if len(placed.black_king_list) == 0:
                    drag_to_placed(dragging.black_king, "blackking", placed.black_king_list)
                # Moves piece
                for grid in room.gridList:
                    for color_pieces in play.total_play_list:
                        for pieceList in color_pieces:
                            for piece in pieceList:
                                if (grid.rect.collidepoint(mouse_pos) and grid.highlighted==1):
                                    if(piece.select == 1):
                                        piece.rect.topleft = grid.rect.topleft
                                        if piece == play.white_king_list[0]:
                                            play.white_king_list[0].coordinate = grid.coordinate
                                            for whiteRook in play.white_rook_list:
                                                if grid.coordinate == ['g', 1]:
                                                    whiteRook.moveSquare(['f', 1], True)
                                                elif grid.coordinate == ['c', 1]:
                                                    whiteRook.moveSquare(['d', 1], True)
                                            piece.leftCastleAbility = 2
                                            piece.right_castle_ability = 2
                                        if(WHOSETURN == 1):
                                            WHOSETURN = 0
                                        elif(WHOSETURN == 0):
                                            WHOSETURN = 1

    
                clicked_piece = None
                # HIGHLIGHTS PIECE YOU CLICK ON
                for color_pieces in play.total_play_list:
                    for pieceList in color_pieces:
                        for piece in pieceList:
                            if (piece.rect.collidepoint(mouse_pos) and piece.select == 0 and WHOSETURN == piece.color):
                                clicked_piece = piece
                            else:
                                piece.no_highlight()
                                clearGrid()
    
                if clicked_piece is not None:
                    # Just do this last, since we know only one piece will be selected
                    clicked_piece.highlight()
                    clicked_piece.projected()
                    clicked_piece = None
    
            if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                #LEFT CLICK PLAY BUTTON
                if playSwitchButton.rect.collidepoint(mouse_pos) and playSwitchButton.playSwitch is None: 
                    if playSwitchButton.playSwitch is None: #Makes clicking play again unclickable
                        print("Play Mode Activated")
                        playSwitchButton.playSwitch = not None #Switches to Play Mode
    
                        def placed_to_play(placed_list, playList, playClass, col):
                            if placed_list is not None:
                                for i in range(0, len(placed_list)):
                                    playList.append(playClass(col)) #Adds to list same amount of Playwhite_pawns as Placewhite_pawns
                                    playList[i].rect.topleft = placed_list[i].rect.topleft #Each Playwhite_pawn in respective Placedwhite_pawn location
                                    for grid in room.gridList:
                                        if playList[i].rect.colliderect(grid):
                                            playList[i].coordinate = grid.coordinate
                                    
                        placed_to_play(placed.white_pawn_list, play.white_pawn_list, PlayPawn, col="white")
                        placed_to_play(placed.white_bishop_list, play.white_bishop_list, PlayBishop, col="white")
                        placed_to_play(placed.white_knight_list, play.white_knight_list, PlayKnight, col="white")
                        placed_to_play(placed.white_rook_list, play.white_rook_list, PlayRook, col="white")
                        placed_to_play(placed.white_queen_list, play.white_queen_list, PlayQueen, col="white")
                        placed_to_play(placed.white_king_list, play.white_king_list, PlayKing, col="white")
                        placed_to_play(placed.black_pawn_list, play.black_pawn_list, PlayPawn, col="black")
                        placed_to_play(placed.black_bishop_list, play.black_bishop_list, PlayBishop, col="black")
                        placed_to_play(placed.black_knight_list, play.black_knight_list, PlayKnight, col="black")
                        placed_to_play(placed.black_rook_list, play.black_rook_list, PlayRook, col="black")
                        placed_to_play(placed.black_queen_list, play.black_queen_list, PlayQueen, col="black")
                        placed_to_play(placed.black_king_list, play.black_king_list, PlayKing, col="black")
                # LEFT CLICK STOP BUTTON
                elif playSwitchButton.rect.collidepoint(mouse_pos) and playSwitchButton.playSwitch is not None:
                    if playSwitchButton.playSwitch is not None: #Makes sure you are not in editing mode to enter editing mode
                        print("Editing Mode Activated")
                        playSwitchButton.playSwitch = None
                        #All Play objects removed
                        play.PlayNone()
                    room.restart()
                if RESTART_BUTTON.rect.collidepoint(mouse_pos):
                    pass
                if infoButton.rect.collidepoint(mouse_pos):
                    MENUON = 2
                if clearButton.rect.collidepoint(mouse_pos):
                    if playSwitchButton.playSwitch is None: #Editing mode
                        dragging_function()
                        def placed_to_remove(placed_list):
                            for placed in placed_list:
                                PLACED_SPRITES.remove(placed)
                            placed_list = []
                            return placed_list
                        placed.white_pawn_list = placed_to_remove(placed.white_pawn_list)
                        placed.white_bishop_list = placed_to_remove(placed.white_bishop_list)
                        placed.white_knight_list = placed_to_remove(placed.white_knight_list)
                        placed.white_rook_list = placed_to_remove(placed.white_rook_list)
                        placed.white_queen_list = placed_to_remove(placed.white_queen_list)
                        placed.white_king_list = placed_to_remove(placed.white_king_list)
                        placed.black_pawn_list = placed_to_remove(placed.black_pawn_list)
                        placed.black_bishop_list = placed_to_remove(placed.black_bishop_list)
                        placed.black_knight_list = placed_to_remove(placed.black_knight_list)
                        placed.black_rook_list = placed_to_remove(placed.black_rook_list)
                        placed.black_queen_list = placed_to_remove(placed.black_queen_list)
                        placed.black_king_list = placed_to_remove(placed.black_king_list)
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]: #Right click on obj, destroy
                if playSwitchButton.playSwitch is None: #Editing mode
                    dragging_function()
                    remove_object()
            # MIDDLE MOUSE DEBUGGER
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                for grid in room.gridList:
                    if grid.rect.collidepoint(mouse_pos):
                        print(grid.coordinate)
            #PLAYER MOVEMENTS
            if(playSwitchButton.playSwitch is not None):
                pass
        if(playSwitchButton.playSwitch is not None): #ALL GAME ACTIONS
            pass
    
        #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
    
        #Update all sprites
        START_SPRITES.update()
        PLACED_SPRITES.update()
        PLAY_SPRITES.update()
        screen.fill(COLORKEY)
        if(playSwitchButton.playSwitch is None): #Only draw placed sprites in editing mode
            gridsprites.draw(screen)
            START_SPRITES.draw(screen)
            PLACED_SPRITES.draw(screen)
        elif(playSwitchButton.playSwitch is not None): #Only draw play sprites in play mode
            gridsprites.draw(screen)
            PLAY_SPRITES.draw(screen)
        # Board Coordinates Drawing
        coorLetterTextList = [coorAText, coorBText, coorCText, coorDText, coorEText, coorFText, coorGText, coorHText]
        for text in range(0,len(coorLetterTextList)):
            screen.blit(coorLetterTextList[text], (XGRIDRANGE[0]+XGRIDRANGE[2]/3+(XGRIDRANGE[2]*text),YGRIDRANGE[0]-(YGRIDRANGE[2]*0.75)))
            screen.blit(coorLetterTextList[text], (XGRIDRANGE[0]+XGRIDRANGE[2]/3+(XGRIDRANGE[2]*text),YGRIDRANGE[1]+(YGRIDRANGE[2]*0.25)))
        coor_number_text_list = [coor8Text, coor7Text, coor6Text, coor5Text, coor4Text, coor3Text, coor2Text, coor1Text]
        for text in range(0,len(coor_number_text_list)):
            screen.blit(coor_number_text_list[text], (XGRIDRANGE[0]-XGRIDRANGE[2]/2,YGRIDRANGE[0]+YGRIDRANGE[2]/4+(YGRIDRANGE[2]*text)))
            screen.blit(coor_number_text_list[text], (XGRIDRANGE[1]+XGRIDRANGE[2]/3,YGRIDRANGE[0]+YGRIDRANGE[2]/4+(YGRIDRANGE[2]*text)))
        if(playSwitchButton.playSwitch is not None):
            whose_turn_text = arialFont.render(WHOSETURN + "'s move to turn", 1, (0,0,0))
            pin_check_text = arialFont.render(CHECKTEXT, 1, (0,0,0))
            screen.blit(whose_turn_text, (XGRIDRANGE[1]+XGRIDRANGE[2],SCREENHEIGHT/2))
            screen.blit(pin_check_text, (XGRIDRANGE[1]+XGRIDRANGE[2],200))
        pygame.display.flip()
        pygame.display.update()
        
if __name__ == "__main__":
    main()