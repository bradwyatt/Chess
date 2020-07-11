"""
Chess created by Brad Wyatt
Python 3

To-Do (short-term):


To-Do (long-term):
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
import datetime

#Grouping Images and Sounds
STARTPOS = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
            'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
            'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
            'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}
IMAGES = {}
SOUNDS = {}
SCREEN_WIDTH, SCREEN_HEIGHT = 936, 650
START_SPRITES = pygame.sprite.Group()

def adjust_to_correct_appdir():
    try:
        appdir = sys.argv[0] #feel free to use __file__
        if not appdir:
            raise ValueError
        appdir = os.path.abspath(os.path.dirname(sys.argv[0]))
        os.chdir(appdir)
        if not appdir in sys.path:
            sys.path.insert(0, appdir)
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
    SOUNDS[name] = sound
    
def load_image(file, name, transparent, alpha):
    new_image = pygame.image.load(file)
    if alpha == True:
        new_image = new_image.convert_alpha()
    else:
        new_image = new_image.convert()
    if transparent:
        colorkey = new_image.get_at((0, 0))
        new_image.set_colorkey(colorkey, RLEACCEL)
    IMAGES[name] = new_image

def snap_to_grid(pos, x_range, y_range):
    best_num_X, best_num_Y = x_range[0], y_range[0] #So Y doesn't go above the menu
    for x in range(x_range[0], x_range[1], x_range[2]):
        if pos[0]-x <= 48 and pos[0]-x >= 0:
            best_num_X = x
    for y in range(y_range[0], y_range[1], y_range[2]):
        if pos[1]-y <= 48 and pos[1]-y >= 0:
            best_num_Y = y
    best_grid_snap = (best_num_X, best_num_Y)
    return best_grid_snap
             
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

def restart_start_objects(START):
    START.white_pawn.rect.topleft = STARTPOS['white_pawn']
    START.white_bishop.rect.topleft = STARTPOS['white_bishop']
    START.white_knight.rect.topleft = STARTPOS['white_knight']
    START.white_queen.rect.topleft = STARTPOS['white_queen']
    START.white_king.rect.topleft = STARTPOS['white_king']
    START.black_pawn.rect.topleft = STARTPOS['black_pawn']
    START.black_bishop.rect.topleft = STARTPOS['black_bishop']
    START.black_knight.rect.topleft = STARTPOS['black_knight']
    START.black_queen.rect.topleft = STARTPOS['black_queen']
    START.black_king.rect.topleft = STARTPOS['black_king']
    return START

def get_color():
    color = askcolor()
    return [color[0][0], color[0][1], color[0][2]]

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
        PlacedPawn(white_pawn_pos, PLACED_SPRITES, "white")
    for white_bishop_pos in loaded_dict['white_bishop']:
        PlacedBishop(white_bishop_pos, PLACED_SPRITES, "white")
    for white_knight_pos in loaded_dict['white_knight']:
        PlacedKnight(white_knight_pos, PLACED_SPRITES, "white")
    for white_rook_pos in loaded_dict['white_rook']:
        PlacedRook(white_rook_pos, PLACED_SPRITES, "white")
    for white_queen_pos in loaded_dict['white_queen']:
        PlacedQueen(white_queen_pos, PLACED_SPRITES, "white")
    for white_king_pos in loaded_dict['white_king']:
        PlacedKing(white_king_pos, PLACED_SPRITES, "white")
    for black_pawn_pos in loaded_dict['black_pawn']:
        PlacedPawn(black_pawn_pos, PLACED_SPRITES, "black")
    for black_bishop_pos in loaded_dict['black_bishop']:
        PlacedBishop(black_bishop_pos, PLACED_SPRITES, "black")
    for black_knight_pos in loaded_dict['black_knight']:
        PlacedKnight(black_knight_pos, PLACED_SPRITES, "black")
    for black_rook_pos in loaded_dict['black_rook']:
        PlacedRook(black_rook_pos, PLACED_SPRITES, "black")
    for black_queen_pos in loaded_dict['black_queen']:
        PlacedQueen(black_queen_pos, PLACED_SPRITES, "black")
    for black_king_pos in loaded_dict['black_king']:
        PlacedKing(black_king_pos, PLACED_SPRITES, "black")
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
    
def clear_grid(grid_list):
    for grid in grid_list:
        grid.no_highlight()

def deactivate_piece(coord, pin):
    pass
    """
    #pin parameter determines whether we want pinned piece to be able to move
    for grid in Grid.grid_list:
        for color_list in play.total_play_list:
            for piece_list in color_list:
                for piece in piece_list:
                    if(piece.coordinate == coord and pin == True):
                        piece.pinned = True
                    else:
                        piece.pinned = False
    """
                
# Projected Bishop Path
def bishop_projected(piece, col):
    global CHECKTEXT
    pass
    """
    pieces_in_way = 0 #Pieces between the bishop and the enemy King
    king_counter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1, 8): #southwest
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1): #Counts pieces that are in bishops projected range
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    grid.image = IMAGES["SPR_HIGHLIGHT2"]
        if(pieces_in_way == 2 and king_counter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 50 or pieces_in_way > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #northwest
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    grid.image = IMAGES["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #southwest
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    grid.image = IMAGES["SPR_HIGHLIGHT2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): 
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #northeast
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    grid.image = IMAGES["SPR_HIGHLIGHT2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
    except:
        pass
    """
    
# ProjectedRookPath
def rook_projected(piece, col):
    global CHECKTEXT
    pass
    """
    pieces_in_way = 0 #Pieces between the rook and the enemy King
    king_counter = 0 #Checks to see if there's a king in a direction
    try:
        for i in range(1,8): #West
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])-i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1): #Counts pieces that are in rook's projected range
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    #grid.image = IMAGES["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1): #2 Pieces in way, includes 1 king
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): # Either no pin, or too many pieces in the way of a potential pin
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #east
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    #grid.image = IMAGES["sprHighlight2"]

        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #north
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]+i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    #grid.image = IMAGES["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2): 
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
        for i in range(1,8): #south
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i:
                    if(grid.occupied == 1):
                        if(king_counter < 1): #Ignoring pieces that are past the king
                            pieces_in_way += 1
                            if(grid.occ_white_or_black != col):
                                if(grid.occ_king == 1 and grid.occ_white_or_black != col): #Finds the king
                                    king_counter += 1
                                else:
                                    deactivate_piece(grid.coordinate, True)
                    #grid.image = IMAGES["sprHighlight2"]
        if(pieces_in_way == 2 and king_counter == 1):
            CHECKTEXT = "Pinned"
            raise
        elif(pieces_in_way == 1 and king_counter == 1):
            CHECKTEXT = "Check"
            raise
        elif(king_counter == 0 or pieces_in_way > 2):
            deactivate_piece(grid.coordinate, False)
            CHECKTEXT = ""
        else:
            pieces_in_way = 0
            king_counter = 0
    except:
        pass
    """

# Moving pieces
def rook_move(piece, col):
    pass
    """
    try:
        for i in range(1,8): #west
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0]) and grid.coordinate[1] == piece.coordinate[1]-i and grid.occupied == 1:
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
"""

"""
def bishop_move(piece, col):
    try:
        for i in range(1,8): #southwest
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
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
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 0:
                    grid.highlight()
                elif ord(grid.coordinate[0]) == ord(piece.coordinate[0])+i and grid.coordinate[1] == piece.coordinate[1]+i and grid.occupied == 1:
                    if(grid.occ_white_or_black != col): # Highlights when enemy piece in path
                        grid.highlight()
                    raise
    except:
        pass
    """
    
def queen_move(piece, col):
    pass
    """
    rook_move(piece, col)
    bishop_move(piece, col)
    """
            
class InfoScreen():
    def __init__(self, screen):
        self.screen = screen
        self.title = INFO_SCREEN
        self.clock = pygame.time.Clock()
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
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
    def update(self):
        pass
    def flip_start_sprite(self, DRAGGING, pos):
        self.rect.topleft = pos
        if DRAGGING.white_pawn:
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif DRAGGING.white_bishop:
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif DRAGGING.white_knight:
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif DRAGGING.white_queen:
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif DRAGGING.white_king:
            self.image = IMAGES["SPR_WHITE_KING"]
        elif DRAGGING.black_pawn:
            self.image = IMAGES["SPR_BLACK_PAWN"]
        elif DRAGGING.black_bishop:
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        elif DRAGGING.black_knight:
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        elif DRAGGING.black_queen:
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        elif DRAGGING.black_king:
            self.image = IMAGES["SPR_BLACK_KING"]
        else:
            self.image = IMAGES["SPR_BLANKBOX"]
"""            
class StartObjects(pygame.sprite.Sprite):
    def __init__(self, classname, START_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.classname = classname
        if(classname == "white_pawn"):
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif(classname == "white_bishop"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif(classname == "white_knight"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif(classname == "white_rook"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(classname == "white_queen"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif(classname == "white_king"):
            self.image = IMAGES["SPR_WHITE_KING"]
        elif(classname == "black_pawn"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
        elif(classname == "black_bishop"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        elif(classname == "black_knight"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        elif(classname == "black_rook"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
        elif(classname == "black_queen"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        elif(classname == "black_king"):
            self.image = IMAGES["SPR_BLACK_KING"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        global MOUSEPOS
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.classname == "white_pawn"):
            if DRAGGING.white_pawn:
                start.blankbox.rect.topleft = STARTPOS['white_pawn'] #Replaces in Menu
                start.white_pawn.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_pawn.rect.topleft = STARTPOS['white_pawn']
        elif(self.classname == "white_bishop"):
            if DRAGGING.white_bishop:
                start.blankbox.rect.topleft = STARTPOS['white_bishop'] #Replaces in Menu
                start.white_bishop.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_bishop.rect.topleft = STARTPOS['white_bishop']
        elif(self.classname == "white_knight"):
            if DRAGGING.white_knight:
                start.blankbox.rect.topleft = STARTPOS['white_knight'] #Replaces in Menu
                start.white_knight.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_knight.rect.topleft = STARTPOS['white_knight']
        elif(self.classname == "white_rook"):
            if DRAGGING.white_rook:
                start.blankbox.rect.topleft = STARTPOS['white_rook'] #Replaces in Menu
                start.white_rook.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_rook.rect.topleft = STARTPOS['white_rook']
        elif(self.classname == "white_queen"):
            if DRAGGING.white_queen:
                start.blankbox.rect.topleft = STARTPOS['white_queen'] #Replaces in Menu
                start.white_queen.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_queen.rect.topleft = STARTPOS['white_queen']
        elif(self.classname == "white_king"):
            if DRAGGING.white_king and len(placed.white_king_list) == 0:
                start.blankbox.rect.topleft = STARTPOS['white_king'] #Replaces in Menu
                start.white_king.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.white_king.rect.topleft = STARTPOS['white_king']
        elif(self.classname == "black_pawn"):
            if DRAGGING.black_pawn:
                start.blankbox.rect.topleft = STARTPOS['black_pawn'] #Replaces in Menu
                start.black_pawn.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_pawn.rect.topleft = STARTPOS['black_pawn']
        elif(self.classname == "black_bishop"):
            if DRAGGING.black_bishop:
                start.blankbox.rect.topleft = STARTPOS['black_bishop'] #Replaces in Menu
                start.black_bishop.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_bishop.rect.topleft = STARTPOS['black_bishop']
        elif(self.classname == "black_knight"):
            if DRAGGING.black_knight:
                start.blankbox.rect.topleft = STARTPOS['black_knight'] #Replaces in Menu
                start.black_knight.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_knight.rect.topleft = STARTPOS['black_knight']
        elif(self.classname == "black_rook"):
            if DRAGGING.black_rook:
                start.blankbox.rect.topleft = STARTPOS['black_rook'] #Replaces in Menu
                start.black_rook.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_rook.rect.topleft = STARTPOS['black_rook']
        elif(self.classname == "black_queen"):
            if DRAGGING.black_queen:
                start.blankbox.rect.topleft = STARTPOS['black_queen'] #Replaces in Menu
                start.black_queen.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_queen.rect.topleft = STARTPOS['black_queen']
        elif(self.classname == "black_king"):
            if DRAGGING.black_king and len(placed.black_king_list) == 0:
                start.blankbox.rect.topleft = STARTPOS['black_king'] #Replaces in Menu
                start.black_king.rect.topleft = MOUSEPOS[0]-(self.image.get_width()/2), MOUSEPOS[1]-(self.image.get_height()/2)
            else:
                start.black_king.rect.topleft = STARTPOS['black_king']
"""
"""
class PlacedObjects(pygame.sprite.Sprite):
    def __init__(self, classname, PLACED_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.classname = classname
        if(self.classname == "white_pawn"):
            self.image = IMAGES["sprwhite_pawn"]
        elif(self.classname == "white_bishop"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif(self.classname == "white_knight"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif(self.classname == "white_rook"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(self.classname == "white_queen"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif(self.classname == "white_king"):
            self.image = IMAGES["SPR_WHITE_KING"]
        elif(self.classname == "black_pawn"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
        elif(self.classname == "black_bishop"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        elif(self.classname == "black_knight"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        elif(self.classname == "black_rook"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
        elif(self.classname == "black_queen"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        elif(self.classname == "black_king"):
            self.image = IMAGES["SPR_BLACK_KING"]
        self.rect = self.image.get_rect()
        PLACED_SPRITES.add(self)
        self.coordinate = ['z', 0]  # Starts as this
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
"""
             
class PlacedPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_PAWN"]
            PLACED_SPRITES.add(self)
            PlacedPawn.white_pawn_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_PAWN"]
            PLACED_SPRITES.add(self)
            PlacedPawn.black_pawn_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedPawn.white_pawn_list.remove(self)
        elif self.col == "black":
            PlacedPawn.black_pawn_list.remove(self)
        self.kill()

class PlacedBishop(pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
            PLACED_SPRITES.add(self)
            PlacedBishop.white_bishop_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
            PLACED_SPRITES.add(self)
            PlacedBishop.black_bishop_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedBishop.white_bishop_list.remove(self)
        elif self.col == "black":
            PlacedBishop.black_bishop_list.remove(self)
        self.kill()

class PlacedKnight(pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
            PLACED_SPRITES.add(self)
            PlacedKnight.white_knight_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
            PLACED_SPRITES.add(self)
            PlacedKnight.black_knight_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedKnight.white_knight_list.remove(self)
        elif self.col == "black":
            PlacedKnight.black_knight_list.remove(self)
        self.kill()
        
class PlacedRook(pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_ROOK"]
            PLACED_SPRITES.add(self)
            PlacedRook.white_rook_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_ROOK"]
            PLACED_SPRITES.add(self)
            PlacedRook.black_rook_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedRook.white_rook_list.remove(self)
        elif self.col == "black":
            PlacedRook.black_rook_list.remove(self)
        self.kill()
        
class PlacedQueen(pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
            PLACED_SPRITES.add(self)
            PlacedQueen.white_queen_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
            PLACED_SPRITES.add(self)
            PlacedQueen.black_queen_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedQueen.white_queen_list.remove(self)
        elif self.col == "black":
            PlacedQueen.black_queen_list.remove(self)
        self.kill()
        
class PlacedKing(pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, pos, PLACED_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KING"]
            PLACED_SPRITES.add(self)
            PlacedKing.white_king_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KING"]
            PLACED_SPRITES.add(self)
            PlacedKing.black_king_list.append(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedKing.white_king_list.remove(self)
        elif self.col == "black":
            PlacedKing.black_king_list.remove(self)
        self.kill()
        
class PlayBishop(pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.select == 0): # Projected Spaces Attacked
            bishop_projected(self, self.color)
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_BISHOP_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            bishop_move(self, self.color)
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        self.select = 0
        
class PlayKnight(pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KNIGHT_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            for grid in Grid.grid_list:
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
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        self.select = 0
        
class PlayRook(pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
            self.ranknum = 1
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
            self.ranknum = 8
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.select == 0): # Projected Spaces Attacked
            rook_projected(self, self.color)
    def move_square(self, coordinate_parameter, castle=False):
        if castle == False:
            for grid in Grid.grid_list:
                if grid.coordinate == coordinate_parameter:
                    self.rect.topleft = grid.rect.topleft
        if castle == True and self.coordinate == ['h', self.ranknum]:
            if PlayKing.white_king_list[0].right_castle_ability == 1 and PlayKing.white_king_list[0].coordinate == ['g', 1]:
                for grid in Grid.grid_list:
                    if grid.coordinate == ['f', self.ranknum]:
                        self.rect.topleft = grid.rect.topleft
                        self.coordinate = grid.coordinate
        if castle == True and self.coordinate == ['a', self.ranknum]:
            if PlayKing.white_king_list[0].left_castle_ability == 1 and PlayKing.white_king_list[0].coordinate == ['c', 1]:
                for grid in Grid.grid_list:
                    if grid.coordinate == ['d', self.ranknum]:
                        self.rect.topleft = grid.rect.topleft
                        self.coordinate = grid.coordinate
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        # Try and Except for each direction
        if(self.pinned == False):
            rook_move(self, self.color)
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
        self.select = 0

class PlayQueen(pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN_HIGHLIGHTED"]
        if(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            queen_move(self, self.color)
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        if(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        self.select = 0

class PlayKing(pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KING"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KING"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.left_castle_ability = 0
        self.right_castle_ability = 0
        self.right_clear_way = [0, 0]
        self.left_clear_way = [0, 0, 0]
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
        if(self.left_castle_ability == 2 or self.right_castle_ability == 2):
            self.left_castle_ability = 2
            self.right_castle_ability = 2
        elif((self.color == "white" and self.coordinate == ['e', 1]) or (self.color == "black" and self.coordinate == ['e', 8])):
            self.castle_check(self.color)
    """
    def castle_check(self, color):
        if color == "white":
            rook_list = play.white_rook_list
            ranknum = 1
        elif color == "black":
            rook_list = play.black_rook_list
            ranknum = 8
        for rook in rook_list:
            if(rook.coordinate == ['h', ranknum]):
                self.right_clear_way = [0, 0]
                for i in range(0, len(Grid.grid_list)):
                    if(Grid.grid_list[i].coordinate == ['f', ranknum] and Grid.grid_list[i].occupied == 0):
                        self.right_clear_way[0] = 1
                for i in range(0, len(Grid.grid_list)):
                    if(Grid.grid_list[i].coordinate == ['g', ranknum] and Grid.grid_list[i].occupied == 0):
                        self.right_clear_way[1] = 1
                if(self.right_clear_way == [1, 1]):
                    self.right_castle_ability = 1
                else:
                    self.right_castle_ability = 0
            if(rook.coordinate == ['a', ranknum]):
                #left_clear_way = [0, 0, 0]
                for i in range(0, len(Grid.grid_list)):
                    if(Grid.grid_list[i].coordinate == ['b', ranknum] and Grid.grid_list[i].occupied == 0):
                        self.left_clear_way[0] = 1
                for i in range(0, len(Grid.grid_list)):
                    if(Grid.grid_list[i].coordinate == ['c', ranknum] and Grid.grid_list[i].occupied == 0):
                        self.left_clear_way[1] = 1
                for i in range(0, len(Grid.grid_list)):
                    if(Grid.grid_list[i].coordinate == ['d', ranknum] and Grid.grid_list[i].occupied == 0):
                        self.left_clear_way[2] = 1
                if(self.left_clear_way == [1, 1, 1]):
                    self.left_castle_ability = 1
                else:
                    self.left_castle_ability = 0
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KING_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KING_HIGHLIGHTED"]
        self.select = 1
    def projected(self):
        # Try and Except for each direction
        for grid in Grid.grid_list:
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
                self.left_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                    grid.highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["sprWhiteKing"]
        elif(self.color == "black"):
            self.image = IMAGES["sprBlackKing"]
        self.select = 0
    """
        
class PlayPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, col, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.color = col
        if(self.color == "white"):
            self.image = IMAGES["sprwhite_pawn"]
        elif(self.color == "black"):
            self.image = IMAGES["sprBlackPawn"]
        self.rect = self.image.get_rect()
        PLAY_SPRITES.add(self)
        self.coordinate = ['z', 0] #blank coordinate, will change once it updates
        self.select = 0
        self.pinned = False
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["sprwhite_pawnHighlighted"]
        elif(self.color == "black"):
            self.image = IMAGES["sprBlackPawnHighlighted"]
        self.select = 1
    def projected(self):
        if(self.pinned == False):
            if(self.color == "white"):
                for grid in range(0,len(Grid.grid_list)):
                    if (Grid.grid_list[grid].coordinate[0] == self.coordinate[0] and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]+1 and \
                    Grid.grid_list[grid].occupied == 0): # Move one space up
                        Grid.grid_list[grid].highlight()
                        for grid in range(0,len(Grid.grid_list)):
                            if (self.coordinate[1] == 2 and Grid.grid_list[grid].coordinate[0] == self.coordinate[0] and \
                                Grid.grid_list[grid].coordinate[1] == 4 and Grid.grid_list[grid].occupied == 0):
                                Grid.grid_list[grid].highlight()
                    # Enemy pieces
                    if (ord(Grid.grid_list[grid].coordinate[0]) == ord(self.coordinate[0])-1 and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]+1 and \
                    Grid.grid_list[grid].occ_white_or_black == "black"):
                        Grid.grid_list[grid].highlight()
                    if (ord(Grid.grid_list[grid].coordinate[0]) == ord(self.coordinate[0])+1 and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]+1 and \
                    Grid.grid_list[grid].occ_white_or_black == "black"):
                        Grid.grid_list[grid].highlight()
            elif(self.color == "black"):
                for grid in range(0,len(Grid.grid_list)):
                    if (Grid.grid_list[grid].coordinate[0] == self.coordinate[0] and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]-1 and \
                    Grid.grid_list[grid].occupied == 0): # Move one space up
                        Grid.grid_list[grid].highlight()
                        for grid in range(0,len(Grid.grid_list)):
                            if (self.coordinate[1] == 7 and Grid.grid_list[grid].coordinate[0] == self.coordinate[0] and \
                                Grid.grid_list[grid].coordinate[1] == 5 and Grid.grid_list[grid].occupied == 0):
                                Grid.grid_list[grid].highlight()
                    # Enemy pieces
                    if (ord(Grid.grid_list[grid].coordinate[0]) == ord(self.coordinate[0])-1 and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]-1 and \
                    Grid.grid_list[grid].occ_white_or_black == "white"):
                        Grid.grid_list[grid].highlight()
                    if (ord(Grid.grid_list[grid].coordinate[0]) == ord(self.coordinate[0])+1 and Grid.grid_list[grid].coordinate[1] == self.coordinate[1]-1 and \
                    Grid.grid_list[grid].occ_white_or_black == "white"):
                        Grid.grid_list[grid].highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
        self.select = 0
            
class PlayEditSwitchButton(pygame.sprite.Sprite):
    def __init__(self, pos, GAME_MODE_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAY_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GAME_MODE_SPRITES.add(self)
    def game_mode_button(self, game_mode):
        if game_mode == 0:
            self.image = IMAGES["SPR_PLAY_BUTTON"]
        elif game_mode == 1:
            self.image = IMAGES["SPR_STOP_BUTTON"]
        return self.image
    
class Grid(pygame.sprite.Sprite):
    grid_list = []
    def __init__(self, GRID_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID"]
        self.rect = self.image.get_rect()
        GRID_SPRITES.add(self)
        self.coordinate = ["z", 0] #Default, Must be changed
        self.highlighted = 0
        self.occupied = 0
        self.color = None
        self.occ_white_or_black = ""
        self.occ_king = 0
        Grid.grid_list.append(self)
    def update(self):
        pass
    """
        global SCREEN_HEIGHT, SCREEN_WIDTH
        if self.rect.bottom > SCREEN_HEIGHT:
            START_SPRITES.remove(self)
        if self.rect.right > SCREEN_WIDTH:
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
    def piece_captured(self, col, notcol, color_list):
        global TAKENPIECEXWHITE, TAKENPIECEYWHITE, TAKENPIECEXBLACK, TAKENPIECEYBLACK
        for piece_list in color_list:
            for piece in piece_list:
                if(self.coordinate == piece.coordinate and self.occ_white_or_black == ""): # Resets the White Or Black Check if not occupied at all
                    self.occ_white_or_black = col
                elif(self.coordinate == piece.coordinate and self.occ_white_or_black == notcol): #Was Black/White Before (Meaning Prior Piece gets Moved)
                    for color_pieces in play.total_play_list:
                        for piece_list in color_pieces:
                            for piece in piece_list:
                                if (self.coordinate == piece.coordinate and piece.color == notcol):
                                    if(piece.color == "white"):
                                        piece.rect.topleft = (TAKENPIECEXWHITE, TAKENPIECEYWHITE)
                                        TAKENPIECEXWHITE += 50
                                    elif(piece.color == "black"):
                                        piece.rect.topleft = (TAKENPIECEXBLACK, TAKENPIECEYBLACK)
                                        TAKENPIECEXBLACK += 50
                                    piece.no_highlight()
                                    piece.coordinate = ['z', 0]
                                    Grid.grid_list = clear_grid(Grid.grid_list)
                                    
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
    """
    def highlight(self):
        self.image = IMAGES["sprHighlight"]
        self.highlighted = 1
    def no_highlight(self):
        if(self.color == "green"):
            self.image = IMAGES["sprGreenGrid"]
        elif(self.color == "white"):
            self.image = IMAGES["sprWhiteGrid"]
        self.highlighted = 0
            
class ClearButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_CLEAR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class InfoButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_INFO_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class RestartButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_RESTART_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)
    
class ColorButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_COLOR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class Dragging():
    def __init__(self):
        self.white_pawn = False
        self.white_bishop = False
        self.white_knight = False
        self.white_rook = False
        self.white_queen = False
        self.white_king = False
        self.black_pawn = False
        self.black_bishop = False
        self.black_knight = False
        self.black_rook = False
        self.black_queen = False
        self.black_king = False
    def dragging_all_false(self):
        self.white_pawn = False
        self.white_bishop = False
        self.white_knight = False
        self.white_rook = False
        self.white_queen = False
        self.white_king = False
        self.black_pawn = False
        self.black_bishop = False
        self.black_knight = False
        self.black_rook = False
        self.black_queen = False
        self.black_king = False
        
class Start():
    def __init__(self):
        self.blank_box = StartBlankBox()
        START_SPRITES.add(self.blank_box)
        self.white_pawn = StartPawn("white")
        START_SPRITES.add(self.white_pawn)
        self.white_bishop = StartBishop("white")
        START_SPRITES.add(self.white_bishop)
        self.white_knight = StartKnight("white")
        START_SPRITES.add(self.white_knight)        
        self.white_rook = StartRook("white")
        START_SPRITES.add(self.white_rook)        
        self.white_queen = StartQueen("white")
        START_SPRITES.add(self.white_queen)        
        self.white_king = StartKing("white")
        START_SPRITES.add(self.white_king)        
        self.black_pawn = StartPawn("black")
        START_SPRITES.add(self.black_pawn)
        self.black_bishop = StartBishop("black")
        START_SPRITES.add(self.black_bishop)
        self.black_knight = StartKnight("black")
        START_SPRITES.add(self.black_knight)        
        self.black_rook = StartRook("black")
        START_SPRITES.add(self.black_rook)        
        self.black_queen = StartQueen("black")
        START_SPRITES.add(self.black_queen)        
        self.black_king = StartKing("black")
        START_SPRITES.add(self.black_king)            
        
class StartPawn(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_PAWN"]
        self.rect = self.image.get_rect() 
    def update(self):
        pass

class StartBishop(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        self.rect = self.image.get_rect()
    def update(self):
        pass
    
class StartKnight(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        self.rect = self.image.get_rect()
    def update(self):
        pass

class StartRook(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_ROOK"]
        self.rect = self.image.get_rect()
    def update(self):
        pass
    
class StartQueen(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        self.rect = self.image.get_rect()
    def update(self):
        pass

class StartKing(pygame.sprite.Sprite):
    def __init__(self, col):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KING"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KING"]
        self.rect = self.image.get_rect()
    def update(self):
        pass

def restart(self):
    global WHOSETURN, TAKENPIECECOORDS, TAKENPIECEXWHITE, TAKENPIECEYWHITE, TAKENPIECEXBLACK, TAKENPIECEYBLACK
    WHOSETURN = 1 # DEFAULT TURN
    TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
    TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
    TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
    TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
    # Resets grid
    for grid in Grid.grid_list:
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
    PlacedPawn.white_pawn_list = []
    PlacedBishop.white_bishop_list = []
    PlacedKnight.white_knight_list = []
    PlacedQueen.white_queen_list = []
    PlacedKing.white_king_list = []
    PlacedPawn.black_pawn_list = []
    PlacedBishop.black_bishop_list = []
    PlacedKnight.black_knight_list = []
    PlacedQueen.black_queen_list = []
    PlacedKing.black_king_list = []

def remove_all_play():
    for spr_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                     PlayKnight.white_knight_list, PlayQueen.white_queen_list, 
                     PlayKing.white_king_list, PlayPawn.black_pawn_list,
                     PlayBishop.black_bishop_list, PlayKnight.black_knight_list, 
                     PlayQueen.black_queen_list, PlayKing.black_king_list]:
        for obj in spr_list:
            obj.kill()
    PlayPawn.white_pawn_list = []
    PlayBishop.white_bishop_list = []
    PlayKnight.white_knight_list = []
    PlayQueen.white_queen_list = []
    PlayKing.white_king_list = []
    PlayPawn.black_pawn_list = []
    PlayBishop.black_bishop_list = []
    PlayKnight.black_knight_list = []
    PlayQueen.black_queen_list = []
    PlayKing.black_king_list = []

def main():    
    #Tk box for color
    root = tk.Tk()
    root.withdraw()
    #Global variables
    MENUON = 1
    SCREEN = None
    
    #################
    # USER CAN SET BELOW PARAMETERS
    #################
    COLORKEY = [160, 160, 160]
    X_GRID_START = 48 # First board coordinate for X
    X_GRID_WIDTH = 48 # How many pixels X is separated by
    Y_GRID_START = 96 # First board coordinate for Y
    Y_GRID_HEIGHT = 48 # How many pixels Y is separated by
    
    #################
    #################
    X_GRID_END = X_GRID_START+(X_GRID_WIDTH*8)
    Y_GRID_END = Y_GRID_START+(Y_GRID_HEIGHT*8)
    XGRIDRANGE = [X_GRID_START, X_GRID_END, X_GRID_WIDTH] #1st num: begin 2nd: end 3rd: step
    YGRIDRANGE = [Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT] #1st num: begin 2nd: end 3rd: step
    
    WHOSETURN = 1
    TAKENPIECECOORDS = [50, 15, 50, 525]
    TAKENPIECEXWHITE = TAKENPIECECOORDS[0]
    TAKENPIECEYWHITE = TAKENPIECECOORDS[1]
    TAKENPIECEXBLACK = TAKENPIECECOORDS[2]
    TAKENPIECEYBLACK = TAKENPIECECOORDS[3]
    CHECKTEXT = ""
    
    RUNNING, DEBUG = 0, 1
    state = RUNNING
    debug_message = 0
    
    #Init
    pygame.init()
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #, pygame.FULLSCREEN for fullscreen
    
    GAME_MODE_SPRITES = pygame.sprite.Group()
    GRID_SPRITES = pygame.sprite.Group()
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
    load_image("Sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
    load_image("Sprites/stopbutton.png", "SPR_STOP_BUTTON", True, True)
    load_image("Sprites/clear.png", "SPR_CLEAR_BUTTON", True, True)
    load_image("Sprites/infobutton.png", "SPR_INFO_BUTTON", True, True)
    load_image("Sprites/restart.png", "SPR_RESTART_BUTTON", True, True)
    load_image("Sprites/colorbutton.png", "SPR_COLOR_BUTTON", True, True)
    load_image("Sprites/savefile.png", "SPR_SAVE_FILE_BUTTON", True, True)
    load_image("Sprites/loadfile.png", "SPR_LOAD_FILE_BUTTON", True, True)
    
    #Start (Menu) Objects
    START = Start()
    #DRAGGING Variables
    DRAGGING = Dragging()
    
    PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), GAME_MODE_SPRITES)

    CLEAR_BUTTON = ClearButton((SCREEN_WIDTH-115, 10))
    INFO_BUTTON = InfoButton((SCREEN_WIDTH-320, 10))
    RESTART_BUTTON = RestartButton((SCREEN_WIDTH-175, 10), PLAY_SPRITES)
    COLOR_BUTTON = ColorButton((SCREEN_WIDTH-195, 10))
    SAVE_FILE_BUTTON = SaveFileButton((SCREEN_WIDTH-230, 10))
    LOAD_FILE_BUTTON = LoadFileButton((SCREEN_WIDTH-265, 10))
    #Backgrounds
    INFO_SCREEN = pygame.image.load("Sprites/infoscreen.bmp").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #window
    gameicon = pygame.image.load("Sprites/chessico.png")
    pygame.display.set_icon(gameicon)
    pygame.display.set_caption('Chess')
    #fonts
    coor_A_text = arialFont.render("a", 1, (0,0,0))
    coor_B_text = arialFont.render("b", 1, (0,0,0))
    coor_C_text = arialFont.render("c", 1, (0,0,0))
    coor_D_text = arialFont.render("d", 1, (0,0,0))
    coor_E_text = arialFont.render("e", 1, (0,0,0))
    coor_F_text = arialFont.render("f", 1, (0,0,0))
    coor_G_text = arialFont.render("g", 1, (0,0,0))
    coor_H_text = arialFont.render("h", 1, (0,0,0))
    coor_1_text = arialFont.render("1", 1, (0,0,0))
    coor_2_text = arialFont.render("2", 1, (0,0,0))
    coor_3_text = arialFont.render("3", 1, (0,0,0))
    coor_4_text= arialFont.render("4", 1, (0,0,0))
    coor_5_text = arialFont.render("5", 1, (0,0,0))
    coor_6_text = arialFont.render("6", 1, (0,0,0))
    coor_7_text= arialFont.render("7", 1, (0,0,0))
    coor_8_text = arialFont.render("8", 1, (0,0,0))
    
    EDIT_MODE, PLAY_MODE = 0, 1
    game_mode = EDIT_MODE
    
    # Default White Turn
    WHOSETURN = "white"
    # Creates grid
    for x in range(X_GRID_START, X_GRID_END, X_GRID_WIDTH): 
        for y in range(Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT): 
            grid = Grid(GRID_SPRITES)
            grid.rect.topleft = x, y
            grid.coordinate[0] = chr(int((x-X_GRID_START)/X_GRID_WIDTH)+97)
            grid.coordinate[1] = int((Y_GRID_END-y)/Y_GRID_HEIGHT)
    for grid in Grid.grid_list:
        for i in range(ord("a"), ord("h"), 2):
            for j in range(2,9,2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_WHITE_GRID"]
                    grid.color = "white"
        for i in range(ord("b"), ord("i"), 2):
            for j in range(1,8,2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_WHITE_GRID"]
                    grid.color = "white"
        for i in range(ord("a"), ord("h"), 2):
            for j in range(1,8,2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_GREEN_GRID"]
                    grid.color = "green"
        for i in range(ord("b"), ord("i"), 2):
            for j in range(2,9,2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_GREEN_GRID"]
                    grid.color = "green"

    while True:
        CLOCK.tick(60)
        MOUSEPOS = pygame.mouse.get_pos()
        if state == RUNNING and MENUON == 1: # Initiate room
            #Start Objects
            START.white_pawn.rect.topleft = STARTPOS['white_pawn']
            START.white_bishop.rect.topleft = STARTPOS['white_bishop']
            START.white_knight.rect.topleft = STARTPOS['white_knight']
            START.white_rook.rect.topleft = STARTPOS['white_rook']
            START.white_queen.rect.topleft = STARTPOS['white_queen']
            START.white_king.rect.topleft = STARTPOS['white_king']
            START.black_pawn.rect.topleft = STARTPOS['black_pawn']
            START.black_bishop.rect.topleft = STARTPOS['black_bishop']
            START.black_knight.rect.topleft = STARTPOS['black_knight']
            START.black_rook.rect.topleft = STARTPOS['black_rook']
            START.black_queen.rect.topleft = STARTPOS['black_queen']
            START.black_king.rect.topleft = STARTPOS['black_king']
            # GRID OCCUPIED
            """
            try:
                for grid in range(0, len(Grid.grid_list)):
                    for color_pieces in play.total_play_list:
                        for piece_list in color_pieces:
                            for piece in piece_list:
                                if piece.rect.topleft == Grid.grid_list[grid].rect.topleft:
                                    Grid.grid_list[grid].occupied = 1
                                    grid += 1
                                else:
                                    Grid.grid_list[grid].occupied = 0
            except IndexError:
                pass
            """

    
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        MENUON = 1 #Getting out of menus
                # If user wants to debug
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[0] > X_GRID_END: #DRAG (only for menu and inanimate buttons at top)
                    if game_mode == EDIT_MODE: #Checks if in Editing Mode
                        #BUTTONS
                        if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                            COLORKEY = get_color()
                        if SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            save_file(COLORKEY)
                        if LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PLACED_SPRITES, COLORKEY = load_file(PLACED_SPRITES, COLORKEY)
                        # DRAG OBJECTS
                        if START.white_pawn.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_pawn = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_pawn.rect.topleft)
                        elif START.white_bishop.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_bishop = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_bishop.rect.topleft)
                        elif START.white_knight.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_knight = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_knight.rect.topleft)
                        elif START.white_rook.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_rook = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_rook.rect.topleft)
                        elif START.white_queen.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_queen = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_queen.rect.topleft)
                        elif START.white_king.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_king = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_king.rect.topleft)
                        elif START.black_pawn.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_pawn = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_pawn.rect.topleft)                    
                        elif START.black_bishop.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_bishop = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_bishop.rect.topleft)
                        elif START.black_knight.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_knight = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_knight.rect.topleft)
                        elif START.black_rook.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_rook = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_rook.rect.topleft)
                        elif START.black_queen.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_queen = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_queen.rect.topleft)
                        elif START.black_king.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_king = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_king.rect.topleft)
                            
                #################
                # LEFT CLICK (PRESSED DOWN)
                #################
                
                #placed object placed on location of mouse release
                elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                      MOUSEPOS[0] > X_GRID_START and MOUSEPOS[0] < X_GRID_END and
                      MOUSEPOS[1] > Y_GRID_START and MOUSEPOS[1] < Y_GRID_END): 
                    if DRAGGING.white_pawn:
                        PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.white_bishop:
                        PlacedBishop(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.white_knight:
                        PlacedKnight(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.white_rook:
                        PlacedRook(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.white_queen:
                        PlacedQueen(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.white_king:
                        PlacedKing(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                    elif DRAGGING.black_pawn:
                        PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    elif DRAGGING.black_bishop:
                        PlacedBishop(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    elif DRAGGING.black_knight:
                        PlacedKnight(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    elif DRAGGING.black_rook:
                        PlacedRook(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    elif DRAGGING.black_queen:
                        PlacedQueen(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    elif DRAGGING.black_king:
                        PlacedKing(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                    
                    """
                    # Moves piece
                    for grid in Grid.grid_list:
                        for color_pieces in play.total_play_list:
                            for piece_list in color_pieces:
                                for piece in piece_list:
                                    if (grid.rect.collidepoint(MOUSEPOS) and grid.highlighted==1):
                                        if(piece.select == 1):
                                            piece.rect.topleft = grid.rect.topleft
                                            if piece == play.white_king_list[0]:
                                                play.white_king_list[0].coordinate = grid.coordinate
                                                for white_rook in play.white_rook_list:
                                                    if grid.coordinate == ['g', 1]:
                                                        white_rook.move_square(['f', 1], True)
                                                    elif grid.coordinate == ['c', 1]:
                                                        white_rook.move_square(['d', 1], True)
                                                piece.left_castle_ability = 2
                                                piece.right_castle_ability = 2
                                            if(WHOSETURN == 1):
                                                WHOSETURN = 0
                                            elif(WHOSETURN == 0):
                                                WHOSETURN = 1
    
        
                    clicked_piece = None
                    # HIGHLIGHTS PIECE YOU CLICK ON
                    for color_pieces in play.total_play_list:
                        for piece_list in color_pieces:
                            for piece in piece_list:
                                if (piece.rect.collidepoint(MOUSEPOS) and piece.select == 0 and WHOSETURN == piece.color):
                                    clicked_piece = piece
                                else:
                                    piece.no_highlight()
                                    clear_grid()
        
                    if clicked_piece is not None:
                        # Just do this last, since we know only one piece will be selected
                        clicked_piece.highlight()
                        clicked_piece.projected()
                        clicked_piece = None
                    """
                #################
                # CLICK (RELEASE)
                ################# 
                
                if game_mode == EDIT_MODE:
                    # Right click on obj, destroy
                    if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                        DRAGGING.dragging_all_false()
                        START = restart_start_objects(START)
                        PLACED_SPRITES = remove_placed_object(PLACED_SPRITES, MOUSEPOS)
                
                if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                    #################
                    # PLAY BUTTON
                    #################
                    if PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == EDIT_MODE: 
                        # Makes clicking play again unclickable    
                        game_mode = PLAY_MODE
                        PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)                        
                        print("Play Mode Activated")
    
                        for placed_white_pawn in PlacedPawn.white_pawn_list:
                            PlayPawn(placed_white_pawn.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_bishop in PlacedBishop.white_bishop_list:
                            PlayBishop(placed_white_bishop.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_knight in PlacedKnight.white_knight_list:
                            PlayKnight(placed_white_knight.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_rook in PlacedRook.white_rook_list:
                            PlayRook(placed_white_rook.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_queen in PlacedQueen.white_queen_list:
                            PlayQueen(placed_white_queen.rect.topleft, PLAY_SPRITES, "white")    
                        for placed_white_king in PlacedPawn.white_king_list:
                            PlayKing(placed_white_king.rect.topleft, PLAY_SPRITES, "white")
                        for placed_black_pawn in PlacedPawn.black_pawn_list:
                            PlayPawn(placed_black_pawn.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_bishop in PlacedBishop.black_bishop_list:
                            PlayBishop(placed_black_bishop.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_knight in PlacedKnight.black_knight_list:
                            PlayKnight(placed_black_knight.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_rook in PlacedRook.black_rook_list:
                            PlayRook(placed_black_rook.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_queen in PlacedQueen.black_queen_list:
                            PlayQueen(placed_black_queen.rect.topleft, PLAY_SPRITES, "black")    
                        for placed_black_king in PlacedPawn.black_king_list:
                            PlayKing(placed_black_king.rect.topleft, PLAY_SPRITES, "black")
                                
                    #################
                    # LEFT CLICK (RELEASE) STOP BUTTON
                    #################
                    elif PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_mode == PLAY_MODE:
                        if game_mode == PLAY_MODE:
                            print("Editing Mode Activated")
                            game_mode = EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_mode)
                            remove_all_play()
                    if RESTART_BUTTON.rect.collidepoint(MOUSEPOS):
                        pass
                    if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                        MENUON = 2
                    if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_mode == EDIT_MODE: #Editing mode
                            START = restart_start_objects(START)
                            # REMOVE ALL SPRITES
                            remove_all_placed()
                # MIDDLE MOUSE DEBUGGER
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                    for grid in Grid.grid_list:
                        if grid.rect.collidepoint(MOUSEPOS):
                            print(grid.coordinate)
                            
            ##################
            # ALL EDIT ACTIONS
            ##################
            # Replace start sprite with blank box in top menu
            if game_mode == EDIT_MODE:
                if DRAGGING.white_pawn:
                    START.blank_box.rect.topleft = STARTPOS['white_pawn'] # Replaces in Menu
                    START.white_pawn.rect.topleft = (MOUSEPOS[0]-(START.white_pawn.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_pawn.image.get_height()/2))
                else:
                    START.white_pawn.rect.topleft = STARTPOS['white_pawn']
                if DRAGGING.white_bishop:
                    START.blank_box.rect.topleft = STARTPOS['white_bishop'] # Replaces in Menu
                    START.white_bishop.rect.topleft = (MOUSEPOS[0]-(START.white_bishop.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_bishop.image.get_height()/2))
                else:
                    START.white_bishop.rect.topleft = STARTPOS['white_bishop']
                if DRAGGING.white_knight:
                    START.blank_box.rect.topleft = STARTPOS['white_knight'] # Replaces in Menu
                    START.white_knight.rect.topleft = (MOUSEPOS[0]-(START.white_knight.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_knight.image.get_height()/2))
                else:
                    START.white_knight.rect.topleft = STARTPOS['white_knight']    
                if DRAGGING.white_rook:
                    START.blank_box.rect.topleft = STARTPOS['white_rook'] # Replaces in Menu
                    START.white_rook.rect.topleft = (MOUSEPOS[0]-(START.white_rook.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_rook.image.get_height()/2))
                else:
                    START.white_rook.rect.topleft = STARTPOS['white_rook']                       
                if DRAGGING.white_queen:
                    START.blank_box.rect.topleft = STARTPOS['white_queen'] # Replaces in Menu
                    START.white_queen.rect.topleft = (MOUSEPOS[0]-(START.white_queen.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_queen.image.get_height()/2))
                else:
                    START.white_queen.rect.topleft = STARTPOS['white_queen']                            
                if DRAGGING.white_king:
                    START.blank_box.rect.topleft = STARTPOS['white_king'] # Replaces in Menu
                    START.white_king.rect.topleft = (MOUSEPOS[0]-(START.white_king.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_king.image.get_height()/2))
                else:
                    START.white_king.rect.topleft = STARTPOS['white_king']                     
                if DRAGGING.black_pawn:
                    START.blank_box.rect.topleft = STARTPOS['black_pawn'] # Replaces in Menu
                    START.black_pawn.rect.topleft = (MOUSEPOS[0]-(START.black_pawn.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_pawn.image.get_height()/2))
                else:
                    START.black_pawn.rect.topleft = STARTPOS['black_pawn']
                if DRAGGING.black_bishop:
                    START.blank_box.rect.topleft = STARTPOS['black_bishop'] # Replaces in Menu
                    START.black_bishop.rect.topleft = (MOUSEPOS[0]-(START.black_bishop.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_bishop.image.get_height()/2))
                else:
                    START.black_bishop.rect.topleft = STARTPOS['black_bishop']
                if DRAGGING.black_knight:
                    START.blank_box.rect.topleft = STARTPOS['black_knight'] # Replaces in Menu
                    START.black_knight.rect.topleft = (MOUSEPOS[0]-(START.black_knight.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_knight.image.get_height()/2))
                else:
                    START.black_knight.rect.topleft = STARTPOS['black_knight']    
                if DRAGGING.black_rook:
                    START.blank_box.rect.topleft = STARTPOS['black_rook'] # Replaces in Menu
                    START.black_rook.rect.topleft = (MOUSEPOS[0]-(START.black_rook.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_rook.image.get_height()/2))
                else:
                    START.black_rook.rect.topleft = STARTPOS['black_rook']                       
                if DRAGGING.black_queen:
                    START.blank_box.rect.topleft = STARTPOS['black_queen'] # Replaces in Menu
                    START.black_queen.rect.topleft = (MOUSEPOS[0]-(START.black_queen.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_queen.image.get_height()/2))
                else:
                    START.black_queen.rect.topleft = STARTPOS['black_queen']                            
                if DRAGGING.black_king:
                    START.blank_box.rect.topleft = STARTPOS['black_king'] # Replaces in Menu
                    START.black_king.rect.topleft = (MOUSEPOS[0]-(START.black_king.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_king.image.get_height()/2))
                else:
                    START.black_king.rect.topleft = STARTPOS['black_king']                        
        
            ##################
            # IN-GAME ACTIONS
            ##################
            if game_mode == PLAY_MODE:
                pass
            #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
            
            #Update all sprites
            START_SPRITES.update()
            PLACED_SPRITES.update()
            PLAY_SPRITES.update()
            GAME_MODE_SPRITES.draw(SCREEN)
            SCREEN.fill(COLORKEY)
            if(game_mode == EDIT_MODE): #Only draw placed sprites in editing mode
                GRID_SPRITES.draw(SCREEN)
                START_SPRITES.draw(SCREEN)
                PLACED_SPRITES.draw(SCREEN)
            elif(game_mode == PLAY_MODE): #Only draw play sprites in play mode
                GRID_SPRITES.draw(SCREEN)
                PLAY_SPRITES.draw(SCREEN)
            # Board Coordinates Drawing
            coor_letter_text_list = [coor_A_text, coor_B_text, coor_C_text, coor_D_text, coor_E_text, coor_F_text, coor_G_text, coor_H_text]
            for text in range(0,len(coor_letter_text_list)):
                SCREEN.blit(coor_letter_text_list[text], (X_GRID_START+X_GRID_WIDTH/3+(X_GRID_WIDTH*text),Y_GRID_START-(Y_GRID_HEIGHT*0.75)))
                SCREEN.blit(coor_letter_text_list[text], (X_GRID_START+X_GRID_WIDTH/3+(X_GRID_WIDTH*text),Y_GRID_END+(Y_GRID_HEIGHT*0.25)))
            coor_number_text_list = [coor_8_text, coor_7_text, coor_6_text, coor_5_text, coor_4_text, coor_3_text, coor_2_text, coor_1_text]
            for text in range(0,len(coor_number_text_list)):
                SCREEN.blit(coor_number_text_list[text], (X_GRID_START-X_GRID_WIDTH/2,Y_GRID_START+Y_GRID_HEIGHT/4+(Y_GRID_HEIGHT*text)))
                SCREEN.blit(coor_number_text_list[text], (X_GRID_END+X_GRID_WIDTH/3,Y_GRID_START+Y_GRID_HEIGHT/4+(Y_GRID_HEIGHT*text)))
            if(game_mode == PLAY_MODE):
                whose_turn_text = arialFont.render(WHOSETURN + "'s move to turn", 1, (0,0,0))
                pin_check_text = arialFont.render(CHECKTEXT, 1, (0,0,0))
                SCREEN.blit(whose_turn_text, (X_GRID_END+X_GRID_WIDTH, SCREEN_HEIGHT/2))
                SCREEN.blit(pin_check_text, (X_GRID_END+X_GRID_WIDTH, 200))
            pygame.display.flip()
            pygame.display.update()
        elif state == DEBUG:
            if debug_message == 1:
                print("Entering debug mode")
                debug_message = 0
                # USE BREAKPOINT HERE
                print("zzzz")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        state = RUNNING
                        print("back to Running")
if __name__ == "__main__":
    main()