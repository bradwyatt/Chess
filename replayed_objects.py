import pygame
import load_images_sounds as lis
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

class ReplayedPiece(pygame.sprite.Sprite):
    def __init__(self, piece_type, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None,
                 own_list=None):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = lis.IMAGES[f"SPR_{color.upper()}_{piece_type.upper()}"]
        REPLAYED_SPRITES.add(self)
        own_list.append(self)
        self._own_list = own_list
        self._image_keys = {
            "normal":    f"SPR_{color.upper()}_{piece_type.upper()}",
            "priormove": f"SPR_{color.upper()}_{piece_type.upper()}_PRIORMOVE",
        }
        self.coordinate = coord
        self.coordinate_history = coordinate_history
        self.rect = self.image.get_rect()
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
        else:
            self.rect.topleft = out_of_bounds_x_y
        self.prior_move_color = False
        self.taken_off_board = False
        self.captured_move_number_and_coordinate = captured_move_number_and_coordinate
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        self._own_list.remove(self)
        self.kill()
    def prior_move_update(self):
        if not self.taken_off_board:
            key = "priormove" if self.prior_move_color else "normal"
            self.image = lis.IMAGES[self._image_keys[key]]

class ReplayedPawn(ReplayedPiece):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedPawn.white_pawn_list if color == "white" else ReplayedPawn.black_pawn_list
        super().__init__("pawn", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)

class ReplayedBishop(ReplayedPiece):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedBishop.white_bishop_list if color == "white" else ReplayedBishop.black_bishop_list
        super().__init__("bishop", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)

class ReplayedKnight(ReplayedPiece):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedKnight.white_knight_list if color == "white" else ReplayedKnight.black_knight_list
        super().__init__("knight", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)

class ReplayedRook(ReplayedPiece):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedRook.white_rook_list if color == "white" else ReplayedRook.black_rook_list
        super().__init__("rook", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)

class ReplayedQueen(ReplayedPiece):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedQueen.white_queen_list if color == "white" else ReplayedQueen.black_queen_list
        super().__init__("queen", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)

class ReplayedKing(ReplayedPiece):
    white_king_list = []
    black_king_list = []
    def __init__(self, color, coordinate_history, coord=None,
                 captured_move_number_and_coordinate=None, out_of_bounds_x_y=None):
        lst = ReplayedKing.white_king_list if color == "white" else ReplayedKing.black_king_list
        super().__init__("king", color, coordinate_history, coord,
                         captured_move_number_and_coordinate, out_of_bounds_x_y, lst)
