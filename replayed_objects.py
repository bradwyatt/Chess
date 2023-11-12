import pygame
from load_images_sounds import *
import board

REPLAYED_SPRITES = pygame.sprite.Group()

def remove_all_replayed():
    for spr_list in [ReplayedPawn.white_pawn_list, ReplayedBishop.white_bishop_list,
                     ReplayedKnight.white_knight_list, ReplayedRook.white_rook_list,
                     ReplayedQueen.white_queen_list, ReplayedKing.white_king_list, 
                     ReplayedPawn.black_pawn_list, ReplayedBishop.black_bishop_list, 
                     ReplayedKnight.black_knight_list, ReplayedRook.black_rook_list,
                     ReplayedQueen.black_queen_list, ReplayedKing.black_king_list]:
        for obj in spr_list:
            obj.kill()
    ReplayedPawn.white_pawn_list = []
    ReplayedBishop.white_bishop_list = []
    ReplayedKnight.white_knight_list = []
    ReplayedRook.white_rook_list = []
    ReplayedQueen.white_queen_list = []
    ReplayedKing.white_king_list = []
    ReplayedPawn.black_pawn_list = []
    ReplayedBishop.black_bishop_list = []
    ReplayedKnight.black_knight_list = []
    ReplayedRook.black_rook_list = []
    ReplayedQueen.black_queen_list = []
    ReplayedKing.black_king_list = []
    
class Piece_Lists_Shortcut():
    def all_pieces():
        return [ReplayedPawn.white_pawn_list, ReplayedBishop.white_bishop_list, 
                ReplayedKnight.white_knight_list, ReplayedRook.white_rook_list, 
                ReplayedQueen.white_queen_list, ReplayedKing.white_king_list,
                ReplayedPawn.black_pawn_list, ReplayedBishop.black_bishop_list, 
                ReplayedKnight.black_knight_list, ReplayedRook.black_rook_list, 
                ReplayedQueen.black_queen_list, ReplayedKing.black_king_list]
    def white_pieces():
        return [ReplayedPawn.white_pawn_list, ReplayedBishop.white_bishop_list, 
                ReplayedKnight.white_knight_list, ReplayedRook.white_rook_list, 
                ReplayedQueen.white_queen_list, ReplayedKing.white_king_list]
    def black_pieces():
        return [ReplayedPawn.black_pawn_list, ReplayedBishop.black_bishop_list, 
                ReplayedKnight.black_knight_list, ReplayedRook.black_rook_list, 
                ReplayedQueen.black_queen_list, ReplayedKing.black_king_list]

class ReplayedPawn(pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_PAWN"]
            REPLAYED_SPRITES.add(self)
            ReplayedPawn.white_pawn_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_PAWN"]
            REPLAYED_SPRITES.add(self)
            ReplayedPawn.black_pawn_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedPawn.white_pawn_list.remove(self)
        elif self.color == "black":
            ReplayedPawn.black_pawn_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_PAWN_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_PAWN"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_PAWN_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_PAWN"]

class ReplayedBishop(pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
            REPLAYED_SPRITES.add(self)
            ReplayedBishop.white_bishop_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
            REPLAYED_SPRITES.add(self)
            ReplayedBishop.black_bishop_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedBishop.white_bishop_list.remove(self)
        elif self.color == "black":
            ReplayedBishop.black_bishop_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_BISHOP_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_BISHOP"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_BISHOP_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_BISHOP"]

class ReplayedKnight(pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
            REPLAYED_SPRITES.add(self)
            ReplayedKnight.white_knight_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
            REPLAYED_SPRITES.add(self)
            ReplayedKnight.black_knight_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedKnight.white_knight_list.remove(self)
        elif self.color == "black":
            ReplayedKnight.black_knight_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_KNIGHT_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_KNIGHT"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_KNIGHT_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_KNIGHT"]
        
class ReplayedRook(pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_ROOK"]
            REPLAYED_SPRITES.add(self)
            ReplayedRook.white_rook_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_ROOK"]
            REPLAYED_SPRITES.add(self)
            ReplayedRook.black_rook_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedRook.white_rook_list.remove(self)
        elif self.color == "black":
            ReplayedRook.black_rook_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_ROOK_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_ROOK"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_ROOK_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_ROOK"]
        
class ReplayedQueen(pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
            REPLAYED_SPRITES.add(self)
            ReplayedQueen.white_queen_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
            REPLAYED_SPRITES.add(self)
            ReplayedQueen.black_queen_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedQueen.white_queen_list.remove(self)
        elif self.color == "black":
            ReplayedQueen.black_queen_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_QUEEN_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_QUEEN"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_QUEEN_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_QUEEN"]
        
class ReplayedKing(pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, color, coordinate_history, coord=None, captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "white":
            self.image = IMAGES["SPR_WHITE_KING"]
            REPLAYED_SPRITES.add(self)
            ReplayedKing.white_king_list.append(self)
        elif self.color == "black":
            self.image = IMAGES["SPR_BLACK_KING"]
            REPLAYED_SPRITES.add(self)
            ReplayedKing.black_king_list.append(self)
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            for grid in board.Grid.grid_list:
                if grid.coordinate == self.coordinate:
                    self.rect.topleft = grid.rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        if self.color == "white":
            ReplayedKing.white_king_list.remove(self)
        elif self.color == "black":
            ReplayedKing.black_king_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_KING_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_KING"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_KING_PRIOR_MOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_KING"]