import sys
import os
import pygame
from pygame.constants import RLEACCEL
import initvar
import tkinter as tk

IMAGES = {}
SOUNDS = {}

#Init
root = tk.Tk()
root.withdraw()
pygame.init()
SCREEN = pygame.display.set_mode((initvar.SCREEN_WIDTH, initvar.SCREEN_HEIGHT)) #, pygame.FULLSCREEN for fullscreen

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
load_image("sprites/pieces/white_pawn.png", "SPR_WHITE_PAWN", True, True)
load_image("sprites/pieces/white_pawn_highlighted.png", "SPR_WHITE_PAWN_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_pawn_prior_move.png", "SPR_WHITE_PAWN_PRIOR_MOVE", True, True)
load_image("sprites/pieces/white_bishop.png", "SPR_WHITE_BISHOP", True, True)
load_image("sprites/pieces/white_bishop_highlighted.png", "SPR_WHITE_BISHOP_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_bishop_prior_move.png", "SPR_WHITE_BISHOP_PRIOR_MOVE", True, True)
load_image("sprites/pieces/white_knight.png", "SPR_WHITE_KNIGHT", True, True)
load_image("sprites/pieces/white_knight_highlighted.png", "SPR_WHITE_KNIGHT_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_knight_prior_move.png", "SPR_WHITE_KNIGHT_PRIOR_MOVE", True, True)
load_image("sprites/pieces/white_rook.png", "SPR_WHITE_ROOK", True, True)
load_image("sprites/pieces/white_rook_highlighted.png", "SPR_WHITE_ROOK_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_rook_prior_move.png", "SPR_WHITE_ROOK_PRIOR_MOVE", True, True)
load_image("sprites/pieces/white_queen.png", "SPR_WHITE_QUEEN", True, True)
load_image("sprites/pieces/white_queen_highlighted.png", "SPR_WHITE_QUEEN_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_queen_prior_move.png", "SPR_WHITE_QUEEN_PRIOR_MOVE", True, True)
load_image("sprites/pieces/white_king.png", "SPR_WHITE_KING", True, True)
load_image("sprites/pieces/white_king_highlighted.png", "SPR_WHITE_KING_HIGHLIGHTED", True, True)
load_image("sprites/pieces/white_king_prior_move.png", "SPR_WHITE_KING_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_pawn.png", "SPR_BLACK_PAWN", True, True)
load_image("sprites/pieces/black_pawn_highlighted.png", "SPR_BLACK_PAWN_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_pawn_prior_move.png", "SPR_BLACK_PAWN_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_bishop.png", "SPR_BLACK_BISHOP", True, True)
load_image("sprites/pieces/black_bishop_highlighted.png", "SPR_BLACK_BISHOP_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_bishop_prior_move.png", "SPR_BLACK_BISHOP_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_knight.png", "SPR_BLACK_KNIGHT", True, True)
load_image("sprites/pieces/black_knight_highlighted.png", "SPR_BLACK_KNIGHT_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_knight_prior_move.png", "SPR_BLACK_KNIGHT_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_rook.png", "SPR_BLACK_ROOK", True, True)
load_image("sprites/pieces/black_rook_highlighted.png", "SPR_BLACK_ROOK_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_rook_prior_move.png", "SPR_BLACK_ROOK_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_queen.png", "SPR_BLACK_QUEEN", True, True)
load_image("sprites/pieces/black_queen_highlighted.png", "SPR_BLACK_QUEEN_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_queen_prior_move.png", "SPR_BLACK_QUEEN_PRIOR_MOVE", True, True)
load_image("sprites/pieces/black_king.png", "SPR_BLACK_KING", True, True)
load_image("sprites/pieces/black_king_highlighted.png", "SPR_BLACK_KING_HIGHLIGHTED", True, True)
load_image("sprites/pieces/black_king_prior_move.png", "SPR_BLACK_KING_PRIOR_MOVE", True, True)
load_image("sprites/grid.png", "SPR_GRID", True, True)
load_image("sprites/white_grid.png", "SPR_WHITE_GRID", True, True)
load_image("sprites/green_grid.png", "SPR_GREEN_GRID", True, True)
load_image("sprites/prior_move_grid.png", "SPR_PRIOR_MOVE_GRID", True, True)
load_image("sprites/pieces/highlight.png", "SPR_HIGHLIGHT", True, True)
load_image("sprites/pieces/highlight2.png", "SPR_HIGHLIGHT_PROJECTED", True, True)
load_image("sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
load_image("sprites/stop_button.png", "SPR_STOP_BUTTON", True, True)
load_image("sprites/clear_board.png", "SPR_CLEAR_BUTTON", True, True)
load_image("sprites/reset_board.png", "SPR_RESET_BOARD_BUTTON", True, True)
load_image("sprites/save_positions.png", "SPR_POS_SAVE_FILE_BUTTON", True, True)
load_image("sprites/load_positions.png", "SPR_POS_LOAD_FILE_BUTTON", True, True)
load_image("sprites/flip_board.png", "SPR_FLIP_BOARD_BUTTON", True, True)
load_image("sprites/game_properties.png", "SPR_GAME_PROPERTIES_BUTTON", True, True)
load_image("sprites/beginning_move_button.png", "SPR_BEGINNING_MOVE_BUTTON", True, True)
load_image("sprites/undo_move.png", "SPR_UNDO_MOVE_BUTTON", True, True)
load_image("sprites/last_move_button.png", "SPR_LAST_MOVE_BUTTON", True, True)
load_image("sprites/next_move_button.png", "SPR_NEXT_MOVE_BUTTON", True, True)
load_image("sprites/prev_move_button.png", "SPR_PREV_MOVE_BUTTON", True, True)
load_image("sprites/scroll_up.png", "SPR_SCROLL_UP_BUTTON", True, True)
load_image("sprites/scroll_down.png", "SPR_SCROLL_DOWN_BUTTON", True, True)
load_image("sprites/save_pgn.png", "SPR_PGN_SAVE_FILE_BUTTON", True, True)
load_image("sprites/load_pgn.png", "SPR_PGN_LOAD_FILE_BUTTON", True, True)
load_image("sprites/save_file.png", "SPR_SAVE_FILE_PLACEHOLDER", True, True)
load_image("sprites/load_file.png", "SPR_LOAD_FILE_PLACEHOLDER", True, True)
load_image("sprites/cpu_icon_on.png", "SPR_CPU_BUTTON_ON", True, True)
load_image("sprites/cpu_icon_off.png", "SPR_CPU_BUTTON_OFF", True, True)
MOVE_BG_IMAGE = pygame.image.load('sprites/move_bg.png')
GAME_BACKGROUND = pygame.image.load('sprites/space_background.png')
