import sys
import os
import math
import pygame
import initvar

if sys.platform != "emscripten":
    import tkinter as tk
else:
    tk = None

IMAGES = {}
SOUNDS = {}

#Init
root = None
if not initvar.ITCH_MODE and tk is not None and not os.environ.get("HEADLESS_TEST"):
    root = tk.Tk()
    root.withdraw()
pygame.init()
SCREEN = pygame.display.set_mode((initvar.SCREEN_WIDTH, initvar.SCREEN_HEIGHT)) #, pygame.FULLSCREEN for fullscreen

def adjust_to_correct_appdir():
    if sys.platform == "emscripten":
        return
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

def destroy_root():
    if root is not None:
        root.destroy()

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
        new_image.set_colorkey(colorkey, pygame.RLEACCEL)
    IMAGES[name] = new_image
    
#Sprites
_PIECE_COLORS   = ["white", "black"]
_PIECE_TYPES    = ["pawn", "bishop", "knight", "rook", "queen", "king"]
_PIECE_VARIANTS = [("", ""), ("_highlighted", "_HIGHLIGHTED"), ("_priormove", "_PRIORMOVE")]

for _color in _PIECE_COLORS:
    for _piece in _PIECE_TYPES:
        for _file_suffix, _key_suffix in _PIECE_VARIANTS:
            load_image(
                f"sprites/pieces/{_color}_{_piece}{_file_suffix}.png",
                f"SPR_{_color.upper()}_{_piece.upper()}{_key_suffix}",
                True, True,
            )
load_image("sprites/grid.png", "SPR_GRID", True, True)
load_image("sprites/whiteGrid.png", "SPR_WHITE_GRID", True, True)
load_image("sprites/greenGrid.png", "SPR_GREEN_GRID", True, True)
load_image("sprites/prior_move_grid.png", "SPR_PRIOR_MOVE_GRID", True, True)
load_image("sprites/pieces/highlight.png", "SPR_HIGHLIGHT", True, True)
load_image("sprites/pieces/highlight2.png", "SPR_HIGHLIGHT_PROJECTED", True, True)
load_image("sprites/play_button.png", "SPR_PLAY_BUTTON", True, True)
load_image("sprites/stopbutton.png", "SPR_STOP_BUTTON", True, True)
load_image("sprites/clear_board.png", "SPR_CLEAR_BUTTON", True, True)
load_image("sprites/reset_board.png", "SPR_RESET_BOARD_BUTTON", True, True)
load_image("sprites/savepositions.png", "SPR_POS_SAVE_FILE_BUTTON", True, True)
load_image("sprites/loadpositions.png", "SPR_POS_LOAD_FILE_BUTTON", True, True)
load_image("sprites/flipboard.png", "SPR_FLIP_BOARD_BUTTON", True, True)
_sz = 80
_s = pygame.Surface((_sz, _sz), pygame.SRCALPHA)
pygame.draw.circle(_s, (40, 65, 110), (_sz // 2, _sz // 2), _sz // 2 - 1)
pygame.draw.circle(_s, (80, 110, 160), (_sz // 2, _sz // 2), _sz // 2 - 1, 2)
_cx, _cy = _sz // 2, _sz // 2
_gc = (210, 225, 255)
_n, _ro, _ri, _rh, _tw = 8, 26, 19, 8, math.radians(8)
_pts = []
for _i in range(_n):
    _ba = math.radians(_i * 360 / _n)
    for _a, _r in [(_ba - _tw, _ri), (_ba - _tw, _ro), (_ba + _tw, _ro), (_ba + _tw, _ri)]:
        _pts.append((_cx + math.cos(_a) * _r, _cy + math.sin(_a) * _r))
pygame.draw.polygon(_s, _gc, _pts)
pygame.draw.circle(_s, (40, 65, 110), (_cx, _cy), _rh)
pygame.draw.circle(_s, _gc, (_cx, _cy), _rh, 2)
IMAGES["SPR_GAME_PROPERTIES_BUTTON"] = _s
load_image("sprites/beginning_move_button.png", "SPR_BEGINNING_MOVE_BUTTON", True, True)
load_image("sprites/undoMove.png", "SPR_UNDO_MOVE_BUTTON", True, True)
load_image("sprites/last_move_button.png", "SPR_LAST_MOVE_BUTTON", True, True)
load_image("sprites/next_move_button.png", "SPR_NEXT_MOVE_BUTTON", True, True)
load_image("sprites/prev_move_button.png", "SPR_PREV_MOVE_BUTTON", True, True)
load_image("sprites/scroll_up.png", "SPR_SCROLL_UP_BUTTON", True, True)
load_image("sprites/scroll_down.png", "SPR_SCROLL_DOWN_BUTTON", True, True)
load_image("sprites/savepgn.png", "SPR_PGN_SAVE_FILE_BUTTON", True, True)
load_image("sprites/loadpgn.png", "SPR_PGN_LOAD_FILE_BUTTON", True, True)
load_image("sprites/savefile.png", "SPR_SAVE_FILE_PLACEHOLDER", True, True)
load_image("sprites/loadfile.png", "SPR_LOAD_FILE_PLACEHOLDER", True, True)
load_image("sprites/cpu_icon_on.png", "SPR_CPU_BUTTON_ON", True, True)
load_image("sprites/cpu_icon_off.png", "SPR_CPU_BUTTON_OFF", True, True)
MOVE_BG_IMAGE = pygame.image.load('sprites/move_bg.png')
GAME_BACKGROUND = pygame.image.load('sprites/space_background.png')
