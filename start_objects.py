import pygame
import initvar
from load_images_sounds import *

START_SPRITES = pygame.sprite.Group()

class Start():
    def __init__(self):
        self.start_obj_image_placeholder = StartObjImagePlaceholder()
        self.white_pawn = StartPawn("white", initvar.STARTPOS['white_pawn'])
        self.white_bishop = StartBishop("white", initvar.STARTPOS['white_bishop'])
        self.white_knight = StartKnight("white", initvar.STARTPOS['white_knight'])        
        self.white_rook = StartRook("white", initvar.STARTPOS['white_rook'])      
        self.white_queen = StartQueen("white", initvar.STARTPOS['white_queen'])      
        self.white_king = StartKing("white", initvar.STARTPOS['white_king'])      
        self.black_pawn = StartPawn("black", initvar.STARTPOS['black_pawn'])
        self.black_bishop = StartBishop("black", initvar.STARTPOS['black_bishop'])
        self.black_knight = StartKnight("black", initvar.STARTPOS['black_knight'])      
        self.black_rook = StartRook("black", initvar.STARTPOS['black_rook'])      
        self.black_queen = StartQueen("black", initvar.STARTPOS['black_queen'])      
        self.black_king = StartKing("black", initvar.STARTPOS['black_king'])
    def restart_start_positions(self):
        self.white_pawn.rect.topleft = initvar.STARTPOS['white_pawn']
        self.white_bishop.rect.topleft = initvar.STARTPOS['white_bishop']
        self.white_knight.rect.topleft = initvar.STARTPOS['white_knight']
        self.white_rook.rect.topleft = initvar.STARTPOS['white_rook']
        self.white_queen.rect.topleft = initvar.STARTPOS['white_queen']
        self.white_king.rect.topleft = initvar.STARTPOS['white_king']
        self.black_pawn.rect.topleft = initvar.STARTPOS['black_pawn']
        self.black_bishop.rect.topleft = initvar.STARTPOS['black_bishop']
        self.black_knight.rect.topleft = initvar.STARTPOS['black_knight']
        self.black_rook.rect.topleft = initvar.STARTPOS['black_rook']
        self.black_queen.rect.topleft = initvar.STARTPOS['black_queen']
        self.black_king.rect.topleft = initvar.STARTPOS['black_king']

class StartObjImagePlaceholder(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
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
        elif DRAGGING.white_rook:
            self.image = IMAGES["SPR_WHITE_ROOK"]
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
        elif DRAGGING.black_rook:
            self.image = IMAGES["SPR_BLACK_ROOK"]
        elif DRAGGING.black_queen:
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        elif DRAGGING.black_king:
            self.image = IMAGES["SPR_BLACK_KING"]
        else:
            self.image = IMAGES["SPR_BLANKBOX"]

class StartPawn(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_PAWN"]
        self.rect = self.image.get_rect() 
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass

class StartBishop(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass
    
class StartKnight(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass

class StartRook(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_ROOK"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass
    
class StartQueen(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass

class StartKing(pygame.sprite.Sprite):
    def __init__(self, col, pos):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KING"]
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KING"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        START_SPRITES.add(self)
    def update(self):
        pass