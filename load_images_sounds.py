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


def build_labeled_button(size, label, fill_top, fill_bottom, border, shadow, text_color):
    width, height = size
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(6, 8, width - 12, height - 10)
    pygame.draw.rect(button_surface, shadow, shadow_rect, border_radius=18)
    body_rect = pygame.Rect(0, 0, width - 10, height - 12)
    body_rect.center = (width // 2, height // 2 - 2)
    body_surface = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body_surface, fill_bottom + (255,), body_surface.get_rect(), border_radius=18)
    for row in range(body_rect.height):
        blend = row / max(1, body_rect.height - 1)
        color = (
            int(fill_top[0] + (fill_bottom[0] - fill_top[0]) * blend),
            int(fill_top[1] + (fill_bottom[1] - fill_top[1]) * blend),
            int(fill_top[2] + (fill_bottom[2] - fill_top[2]) * blend),
            235,
        )
        pygame.draw.line(body_surface, color, (0, row), (body_rect.width - 1, row))
    mask_surface = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), mask_surface.get_rect(), border_radius=18)
    body_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    button_surface.blit(body_surface, body_rect.topleft)
    pygame.draw.rect(button_surface, border, body_rect, width=2, border_radius=18)
    font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)
    text = font.render(label, True, text_color)
    text_rect = text.get_rect(center=body_rect.center)
    button_surface.blit(text, text_rect)
    return button_surface


def build_icon_button(size, icon_surface, fill_top, fill_bottom, border, shadow):
    width, height = size
    button_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    shadow_rect = pygame.Rect(6, 8, width - 12, height - 10)
    pygame.draw.rect(button_surface, shadow, shadow_rect, border_radius=18)
    body_rect = pygame.Rect(0, 0, width - 10, height - 12)
    body_rect.center = (width // 2, height // 2 - 2)
    body_surface = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(body_surface, fill_bottom + (255,), body_surface.get_rect(), border_radius=18)
    for row in range(body_rect.height):
        blend = row / max(1, body_rect.height - 1)
        color = (
            int(fill_top[0] + (fill_bottom[0] - fill_top[0]) * blend),
            int(fill_top[1] + (fill_bottom[1] - fill_top[1]) * blend),
            int(fill_top[2] + (fill_bottom[2] - fill_top[2]) * blend),
            235,
        )
        pygame.draw.line(body_surface, color, (0, row), (body_rect.width - 1, row))
    mask_surface = pygame.Surface(body_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask_surface, (255, 255, 255, 255), mask_surface.get_rect(), border_radius=18)
    body_surface.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    button_surface.blit(body_surface, body_rect.topleft)
    pygame.draw.rect(button_surface, border, body_rect, width=2, border_radius=18)

    icon_max_w = max(1, body_rect.width - 26)
    icon_max_h = max(1, body_rect.height - 18)
    icon_w, icon_h = icon_surface.get_size()
    scale = min(icon_max_w / icon_w, icon_max_h / icon_h)
    scaled_icon = pygame.transform.smoothscale(icon_surface, (max(1, int(icon_w * scale)), max(1, int(icon_h * scale))))
    icon_rect = scaled_icon.get_rect(center=body_rect.center)
    button_surface.blit(scaled_icon, icon_rect)
    return button_surface
    
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
IMAGES["SPR_CLEAR_BUTTON"] = build_labeled_button(
    (190, 78),
    "Clear Board",
    (36, 99, 176),
    (36, 99, 176),
    (155, 212, 255),
    (8, 18, 44, 130),
    (243, 248, 255),
)
IMAGES["SPR_RESET_BOARD_BUTTON"] = build_labeled_button(
    (190, 78),
    "Reset Board",
    (36, 99, 176),
    (36, 99, 176),
    (155, 212, 255),
    (8, 18, 44, 130),
    (243, 248, 255),
)
load_image("sprites/savepositions.png", "SPR_POS_SAVE_FILE_BUTTON", True, True)
load_image("sprites/loadpositions.png", "SPR_POS_LOAD_FILE_BUTTON", True, True)
load_image("sprites/flipboard.png", "SPR_FLIP_BOARD_BUTTON", True, True)
_flip_icon = IMAGES["SPR_FLIP_BOARD_BUTTON"]
IMAGES["SPR_FLIP_BOARD_BUTTON"] = build_icon_button(
    (120, 78),
    _flip_icon,
    (36, 99, 176),
    (36, 99, 176),
    (155, 212, 255),
    (8, 18, 44, 130),
)
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
IMAGES["SPR_UNDO_MOVE_BUTTON"] = build_labeled_button(
    (190, 78),
    "Undo Move",
    (36, 99, 176),
    (36, 99, 176),
    (155, 212, 255),
    (8, 18, 44, 130),
    (243, 248, 255),
)
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
