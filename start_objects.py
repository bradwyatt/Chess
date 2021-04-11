import pygame
from load_images_sounds import *

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