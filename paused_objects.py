import pygame
from load_images_sounds import *
import board

PAUSED_SPRITES = pygame.sprite.Group()

def remove_all_paused():
    for spr_list in [PausedPawn.white_pawn_list, PausedBishop.white_bishop_list,
                     PausedKnight.white_knight_list, PausedRook.white_rook_list,
                     PausedQueen.white_queen_list, PausedKing.white_king_list, 
                     PausedPawn.black_pawn_list, PausedBishop.black_bishop_list, 
                     PausedKnight.black_knight_list, PausedRook.black_rook_list,
                     PausedQueen.black_queen_list, PausedKing.black_king_list]:
        for obj in spr_list:
            obj.kill()
    PausedPawn.white_pawn_list = []
    PausedBishop.white_bishop_list = []
    PausedKnight.white_knight_list = []
    PausedRook.white_rook_list = []
    PausedQueen.white_queen_list = []
    PausedKing.white_king_list = []
    PausedPawn.black_pawn_list = []
    PausedBishop.black_bishop_list = []
    PausedKnight.black_knight_list = []
    PausedRook.black_rook_list = []
    PausedQueen.black_queen_list = []
    PausedKing.black_king_list = []
    
class Piece_Lists_Shortcut():
    def all_pieces():
        return [PausedPawn.white_pawn_list, PausedBishop.white_bishop_list, 
                PausedKnight.white_knight_list, PausedRook.white_rook_list, 
                PausedQueen.white_queen_list, PausedKing.white_king_list,
                PausedPawn.black_pawn_list, PausedBishop.black_bishop_list, 
                PausedKnight.black_knight_list, PausedRook.black_rook_list, 
                PausedQueen.black_queen_list, PausedKing.black_king_list]
    def white_pieces():
        return [PausedPawn.white_pawn_list, PausedBishop.white_bishop_list, 
                PausedKnight.white_knight_list, PausedRook.white_rook_list, 
                PausedQueen.white_queen_list, PausedKing.white_king_list]
    def black_pieces():
        return [PausedPawn.black_pawn_list, PausedBishop.black_bishop_list, 
                PausedKnight.black_knight_list, PausedRook.black_rook_list, 
                PausedQueen.black_queen_list, PausedKing.black_king_list]

class PausedPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_PAWN"]
            PAUSED_SPRITES.add(self)
            PausedPawn.white_pawn_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_PAWN"]
            PAUSED_SPRITES.add(self)
            PausedPawn.black_pawn_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedPawn.white_pawn_list.remove(self)
        elif self.col == "black":
            PausedPawn.black_pawn_list.remove(self)
        self.kill()

class PausedBishop(pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
            PAUSED_SPRITES.add(self)
            PausedBishop.white_bishop_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
            PAUSED_SPRITES.add(self)
            PausedBishop.black_bishop_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedBishop.white_bishop_list.remove(self)
        elif self.col == "black":
            PausedBishop.black_bishop_list.remove(self)
        self.kill()

class PausedKnight(pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
            PAUSED_SPRITES.add(self)
            PausedKnight.white_knight_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
            PAUSED_SPRITES.add(self)
            PausedKnight.black_knight_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedKnight.white_knight_list.remove(self)
        elif self.col == "black":
            PausedKnight.black_knight_list.remove(self)
        self.kill()
        
class PausedRook(pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_ROOK"]
            PAUSED_SPRITES.add(self)
            PausedRook.white_rook_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_ROOK"]
            PAUSED_SPRITES.add(self)
            PausedRook.black_rook_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedRook.white_rook_list.remove(self)
        elif self.col == "black":
            PausedRook.black_rook_list.remove(self)
        self.kill()
        
class PausedQueen(pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
            PAUSED_SPRITES.add(self)
            PausedQueen.white_queen_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
            PAUSED_SPRITES.add(self)
            PausedQueen.black_queen_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedQueen.white_queen_list.remove(self)
        elif self.col == "black":
            PausedQueen.black_queen_list.remove(self)
        self.kill()
        
class PausedKing(pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, col, coordinate_history, coord=None):
        pygame.sprite.Sprite.__init__(self)
        self.col = col
        if self.col == "white":
            self.image = IMAGES["SPR_WHITE_KING"]
            PAUSED_SPRITES.add(self)
            PausedKing.white_king_list.append(self)
        elif self.col == "black":
            self.image = IMAGES["SPR_BLACK_KING"]
            PAUSED_SPRITES.add(self)
            PausedKing.black_king_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.col == "white":
            PausedKing.white_king_list.remove(self)
        elif self.col == "black":
            PausedKing.black_king_list.remove(self)
        self.kill()