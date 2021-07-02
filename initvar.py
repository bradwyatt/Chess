import pygame

#################
# USER CAN SET BELOW PARAMETERS
#################

exe_mode = False
test_mode = False

SCREEN_WIDTH, SCREEN_HEIGHT = 1440, 960

MOVE_BG_IMAGE_X = 1150
MOVE_BG_IMAGE_Y = 70

STARTPOS = {'white_pawn': (930, 630), 'white_bishop':(930, 550), 'white_knight':(930, 470),
             'white_rook':(930, 380), 'white_queen':(930, 300), 'white_king':(930, 220),
             'black_pawn': (1000, 630), 'black_bishop':(1000, 550), 'black_knight':(1000, 470),
             'black_rook':(1000, 380), 'black_queen':(1000, 300), 'black_king':(1000, 220)}

COLORKEY_RGB = [160, 160, 160]
X_GRID_START = 300 # First board coordinate for X
Y_GRID_START = 200 # First board coordinate for Y


BLACKANDWHITE_CAPTURED_X = 50
BLACKANDWHITE_INCREMENTAL_X = 40
BLACK_CAPTURED_Y = 525
WHITE_CAPTURED_Y = 15

WHITE_X_Y = (470, 450)
BLACK_X_Y = (470, 80)
WHITE_ELO_X_Y = (470, 480)
BLACK_ELO_X_Y = (470, 110)

WHITE_MOVE_X_Y = (950, 645)
BLACK_MOVE_X_Y = (950, 300)
CHECK_CHECKMATE_X_Y = (950, 270)

PLAY_EDIT_SWITCH_BUTTON_TOPLEFT = (30, 350)
FLIP_BOARD_BUTTON_TOPLEFT = (SCREEN_WIDTH-480, 10)
CPU_BUTTON_TOPLEFT = (30, 10)
GAME_PROPERTIES_BUTTON_TOPLEFT = (30, 10)
INFO_BUTTON_TOPLEFT = (SCREEN_WIDTH-360, 10)
POS_LOAD_FILE_BUTTON_TOPLEFT = (30, 250)
POS_SAVE_FILE_BUTTON_TOPLEFT = (30, 150)
PGN_LOAD_FILE_BUTTON_TOPLEFT = (30, 300)
PGN_SAVE_FILE_BUTTON_TOPLEFT = (30, 200)
COLOR_BUTTON_TOPLEFT = (SCREEN_WIDTH-235, 10)
RESET_BOARD_BUTTON_TOPLEFT = (SCREEN_WIDTH-190, 10)
CLEAR_BUTTON_TOPLEFT = (SCREEN_WIDTH-115, 10)
SCROLL_UP_BUTTON_TOPLEFT = (686, 80)
SCROLL_DOWN_BUTTON_TOPLEFT = (686, 510)
BEGINNING_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-235, 545)
PREV_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-195, 545)
NEXT_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-155, 545)
LAST_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-115, 545)
UNDO_MOVE_BUTTON_TOPLEFT = (SCREEN_WIDTH-191, 605)

# With the current pane, font, line spacing, it is recommended we keep 19 moves as maximum before having to scroll
MOVES_PANE_MAX_MOVES = 19
LINE_SPACING = 21
MOVES_PANE_Y_BEGIN = 89
RECTANGLE_WIDTH = 20
RECTANGLE_HEIGHT = 56
MOVES_PANE_MOVE_NUMBER_X = SCREEN_WIDTH-220
MOVES_PANE_WHITE_X = SCREEN_WIDTH-206
MOVES_PANE_BLACK_X = SCREEN_WIDTH-127

MOVE_TEXT_COLOR_ON_PANE = [255,255,255]
RECTANGLE_FILL_COLOR = (152, 193, 248)
UNIVERSAL_TEXT_COLOR = (44, 144, 218)

# Piece Square Table for Analyzing Board (from White's perspective)
# Rook and Queen should not have any position advantages
WHITE_PAWN_POS_SCORE = [0, 0, 0, 0, 0, 0, 0, 0,
                        50, 50, 50, 50, 50, 50, 50, 50,
                        10, 10, 20, 30, 30, 20, 10, 10,
                        5, 5, 10, 27, 27, 10, 5, 5,
                        0, 0, 0, 25, 25, 0, 0, 0,
                        5, -5, -10, 0, 0, -10, -5, 5,
                        5, 10, 10, -25, -25, 10, 10, 5,
                        0, 0, 0, 0, 0, 0, 0, 0]

WHITE_KNIGHT_POS_SCORE = [-50, -40, -30, -30, -30, -30, -40, -50,
                          -40, -20, 0, 0,  0, 0, -20, -40,
                          -30, 0, 10, 15, 15, 10, 0, -30,
                          -30, 5, 15, 20, 20, 15, 5, -30,
                          -30, 0, 15, 20, 20, 15, 0, -30,
                          -30, 5, 10, 15, 15, 10, 5 ,-30,
                          -40, -20, 0, 5, 5, 0, -20, -40,
                          -50, -40, -20, -30, -30, -20, -40, -50]

WHITE_BISHOP_POS_SCORE = [-20, -10, -10, -10, -10, -10, -10, -20,
                          -10, 0, 0, 0, 0, 0, 0, -10,
                          -10, 0, 5, 10, 10, 5, 0, -10,
                          -10, 5, 5, 10, 10, 5, 5, -10,
                          -10, 0, 10, 10, 10, 10,  0, -10,
                          -10, 10, 10, 10, 10, 10, 10, -10,
                          -10, 5, 0, 0, 0, 0, 5, -10,
                          -20, -10, -40, -10, -10, -40, -10, -20]

WHITE_KING_POS_SCORE = [-30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -30, -40, -40, -50, -50, -40, -40, -30,
                        -20, -30, -30, -40, -40, -30, -30, -20,
                        -10, -20, -20, -20, -20, -20, -20, -10, 
                        20, 20, 0, 0, 0, 0, 20, 20,
                        20, 30, 10, 0, 0, 10, 30, 20]

piece_values_dict = {"pawn": 100,
                     "knight": 320,
                     "bishop": 330,
                     "rook": 500,
                     "queen": 975,
                     "king": 20000}