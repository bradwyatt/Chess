import pygame
import load_images_sounds as lis
import board

PLACED_SPRITES = pygame.sprite.Group()

def remove_placed_object(mousepos):
    for placed_item_list in (PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list,
                             PlacedKnight.white_knight_list, PlacedRook.white_rook_list,
                             PlacedQueen.white_queen_list, PlacedKing.white_king_list,
                             PlacedPawn.black_pawn_list, PlacedBishop.black_bishop_list,
                             PlacedKnight.black_knight_list, PlacedRook.black_rook_list,
                             PlacedQueen.black_queen_list, PlacedKing.black_king_list):
        for placed_item in placed_item_list:
            if placed_item.rect.collidepoint(mousepos):
                PLACED_SPRITES.remove(placed_item)
                placed_item_list.remove(placed_item)
    return

def remove_all_placed():
    for spr_list in [PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list,
                     PlacedKnight.white_knight_list, PlacedRook.white_rook_list,
                     PlacedQueen.white_queen_list, PlacedKing.white_king_list,
                     PlacedPawn.black_pawn_list, PlacedBishop.black_bishop_list,
                     PlacedKnight.black_knight_list, PlacedRook.black_rook_list,
                     PlacedQueen.black_queen_list, PlacedKing.black_king_list]:
        for obj in spr_list:
            obj.kill()
    PlacedPawn.white_pawn_list = []
    PlacedBishop.white_bishop_list = []
    PlacedKnight.white_knight_list = []
    PlacedRook.white_rook_list = []
    PlacedQueen.white_queen_list = []
    PlacedKing.white_king_list = []
    PlacedPawn.black_pawn_list = []
    PlacedBishop.black_bishop_list = []
    PlacedKnight.black_knight_list = []
    PlacedRook.black_rook_list = []
    PlacedQueen.black_queen_list = []
    PlacedKing.black_king_list = []

class PlacedPiece(pygame.sprite.Sprite):
    def __init__(self, piece_type, coord, color, own_list):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        self.image = lis.IMAGES[f"SPR_{color.upper()}_{piece_type.upper()}"]
        PLACED_SPRITES.add(self)
        own_list.append(self)
        self._own_list = own_list
        self.coordinate = coord
        self.rect = self.image.get_rect()
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
    def update(self):
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def destroy(self):
        self._own_list.remove(self)
        self.kill()

class PlacedPawn(PlacedPiece):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, coord, color):
        lst = PlacedPawn.white_pawn_list if color == "white" else PlacedPawn.black_pawn_list
        super().__init__("pawn", coord, color, lst)

class PlacedBishop(PlacedPiece):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, coord, color):
        lst = PlacedBishop.white_bishop_list if color == "white" else PlacedBishop.black_bishop_list
        super().__init__("bishop", coord, color, lst)

class PlacedKnight(PlacedPiece):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, coord, color):
        lst = PlacedKnight.white_knight_list if color == "white" else PlacedKnight.black_knight_list
        super().__init__("knight", coord, color, lst)

class PlacedRook(PlacedPiece):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, coord, color):
        lst = PlacedRook.white_rook_list if color == "white" else PlacedRook.black_rook_list
        super().__init__("rook", coord, color, lst)

class PlacedQueen(PlacedPiece):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, coord, color):
        lst = PlacedQueen.white_queen_list if color == "white" else PlacedQueen.black_queen_list
        super().__init__("queen", coord, color, lst)

class PlacedKing(PlacedPiece):
    white_king_list = []
    black_king_list = []
    def __init__(self, coord, color):
        lst = PlacedKing.white_king_list if color == "white" else PlacedKing.black_king_list
        super().__init__("king", coord, color, lst)
