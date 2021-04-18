import pygame
START_SPRITES = pygame.sprite.Group()
MOVE_BG_IMAGE = pygame.image.load('Sprites/move_bg.png')
MOVE_BG_IMAGE_HEIGHT = 675
MOVE_BG_IMAGE_WIDTH = 70

STARTPOS = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
             'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
             'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
             'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}

COLORKEY = [160, 160, 160]
X_GRID_START = 48 # First board coordinate for X
X_GRID_WIDTH = 48 # How many pixels X is separated by
Y_GRID_START = 96 # First board coordinate for Y
Y_GRID_HEIGHT = 48 # How many pixels Y is separated by
