import sys
import os
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)

IMAGES = {}
SOUNDS = {}
SCREEN_WIDTH, SCREEN_HEIGHT = 936, 650
#Init
pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #, pygame.FULLSCREEN for fullscreen

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
load_image("Sprites/Chess/black_knight_highlighted.png", "SPR_BLACK_KNIGHT_HIGHLIGHTED", True, True)
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
load_image("Sprites/Chess/highlight2.png", "SPR_HIGHLIGHT_PROJECTED", True, True)
load_image("Sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
load_image("Sprites/stopbutton.png", "SPR_STOP_BUTTON", True, True)
load_image("Sprites/clear.png", "SPR_CLEAR_BUTTON", True, True)
load_image("Sprites/infobutton.png", "SPR_INFO_BUTTON", True, True)
load_image("Sprites/restart.png", "SPR_RESTART_BUTTON", True, True)
load_image("Sprites/colorbutton.png", "SPR_COLOR_BUTTON", True, True)
load_image("Sprites/positions_savefile.png", "SPR_POS_SAVE_FILE_BUTTON", True, True)
load_image("Sprites/positions_loadfile.png", "SPR_POS_LOAD_FILE_BUTTON", True, True)
load_image("Sprites/flipboard.png", "SPR_FLIP_BOARD_BUTTON", True, True)
load_image("Sprites/gamepropertiesbutton.png", "SPR_GAME_PROPERTIES_BUTTON", True, True)
load_image("Sprites/beginning_move_button.png", "SPR_BEGINNING_MOVE_BUTTON", True, True)
load_image("Sprites/last_move_button.png", "SPR_LAST_MOVE_BUTTON", True, True)
load_image("Sprites/next_move_button.png", "SPR_NEXT_MOVE_BUTTON", True, True)
load_image("Sprites/prev_move_button.png", "SPR_PREV_MOVE_BUTTON", True, True)
load_image("Sprites/scroll_up.png", "SPR_SCROLL_UP_BUTTON", True, True)
load_image("Sprites/scroll_down.png", "SPR_SCROLL_DOWN_BUTTON", True, True)