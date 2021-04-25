import pygame
from load_images_sounds import *
import board

class PlacedPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
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
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
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
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
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
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
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
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
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
    def __init__(self, coord, PLACED_SPRITES, col):
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
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        pass
    def destroy(self):
        if self.col == "white":
            PlacedKing.white_king_list.remove(self)
        elif self.col == "black":
            PlacedKing.black_king_list.remove(self)
        self.kill()