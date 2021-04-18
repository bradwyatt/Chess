import pygame

#################
# NOT RECOMMENDED TO CHANGE BELOW
#################
START_SPRITES = pygame.sprite.Group()

#################
# USER CAN SET BELOW PARAMETERS
#################
SCREEN_WIDTH, SCREEN_HEIGHT = 936, 650

MOVE_BG_IMAGE = pygame.image.load('Sprites/move_bg.png')
MOVE_BG_IMAGE_HEIGHT = 675
MOVE_BG_IMAGE_WIDTH = 70

STARTPOS = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
             'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
             'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
             'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}

COLORKEY_RGB = [160, 160, 160]
X_GRID_START = 48 # First board coordinate for X
X_GRID_WIDTH = 48 # How many pixels X is separated by
Y_GRID_START = 96 # First board coordinate for Y
Y_GRID_HEIGHT = 48 # How many pixels Y is separated by

PLAY_EDIT_SWITCH_BUTTON_TOPLEFT = (SCREEN_WIDTH-50, 8)
FLIP_BOARD_BUTTON_TOPLEFT = (SCREEN_WIDTH-480, 10)
GAME_PROPERTIES_BUTTON_TOPLEFT = (SCREEN_WIDTH-430, 10)
INFO_BUTTON_TOPLEFT = (SCREEN_WIDTH-360, 10)
POS_LOAD_FILE_BUTTON_TOPLEFT = (SCREEN_WIDTH-305, 10)
POS_SAVE_FILE_BUTTON_TOPLEFT = (SCREEN_WIDTH-270, 10)
PGN_LOAD_FILE_BUTTON_TOPLEFT = (SCREEN_WIDTH-50, 100)
PGN_SAVE_FILE_BUTTON_TOPLEFT = (SCREEN_WIDTH-50, 60)
COLOR_BUTTON_TOPLEFT = (SCREEN_WIDTH-235, 10)
RESET_BOARD_BUTTON_TOPLEFT = (SCREEN_WIDTH-190, 10)
CLEAR_BUTTON_TOPLEFT = (SCREEN_WIDTH-115, 10)
SCROLL_UP_BUTTON_TOPLEFT = (686, 80)
SCROLL_DOWN_BUTTON_TOPLEFT = (686, 510)
BEGINNING_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-235, 545)
PREV_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-195, 545)
NEXT_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-155, 545)
LAST_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-115, 545)

# With the current pane, font, line spacing, it is recommended we keep 19 moves as maximum before having to scroll
MOVES_PANE_MAX_MOVES = 19