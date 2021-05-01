import pygame
import initvar
import placed_objects
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

class Dragging():
    def __init__(self):
        self.drag_piece_name = ""
        #self.dragging_all_false()
    def dragging_all_false(self):
        #self.white_pawn = False
        #self.white_bishop = False
        #self.white_knight = False
        #self.white_rook = False
        #self.white_queen = False
        #self.white_king = False
        #self.black_pawn = False
        #self.black_bishop = False
        #self.black_knight = False
        #self.black_rook = False
        #self.black_queen = False
        #self.black_king = False
        self.drag_piece_name = ""
    def drag_piece(self, piece):
        self.dragging_all_false()
        self.drag_piece_name = piece
    def dragging_to_placed_no_dups(self, mouse_coord):
        for piece_list in [placed_objects.PlacedPawn.white_pawn_list, placed_objects.PlacedBishop.white_bishop_list, 
                           placed_objects.PlacedKnight.white_knight_list, placed_objects.PlacedRook.white_rook_list, 
                           placed_objects.PlacedQueen.white_queen_list, placed_objects.PlacedKing.white_king_list,
                           placed_objects.PlacedPawn.black_pawn_list, placed_objects.PlacedBishop.black_bishop_list, 
                           placed_objects.PlacedKnight.black_knight_list, placed_objects.PlacedRook.black_rook_list, 
                           placed_objects.PlacedQueen.black_queen_list, placed_objects.PlacedKing.black_king_list]:
            # If there is already a piece on grid then don't create new Placed object
            for piece in piece_list:
                if piece.coordinate == mouse_coord:
                    return
        # Created Placed objects at the snapped grid location of the piece that's being dragged
        if self.drag_piece_name == "white_pawn":
            if int(mouse_coord[1]) != 1 and int(mouse_coord[1]) != 8:
                placed_objects.PlacedPawn(mouse_coord, "white")
            else:
                log.info("You are not allowed to place a pawn on rank " + mouse_coord[1])
        elif self.drag_piece_name == "white_bishop":
            placed_objects.PlacedBishop(mouse_coord, "white")
        elif self.drag_piece_name == "white_knight":
            placed_objects.PlacedKnight(mouse_coord, "white")
        elif self.drag_piece_name == "white_rook":
            placed_objects.PlacedRook(mouse_coord, "white")
        elif self.drag_piece_name == "white_queen":
            placed_objects.PlacedQueen(mouse_coord, "white")
        elif self.drag_piece_name == "white_king":
            if not placed_objects.PlacedKing.white_king_list:
                placed_objects.PlacedKing(mouse_coord, "white")
            else:
                log.info("You can only have one white king.")
        elif self.drag_piece_name == "black_pawn":
            if int(mouse_coord[1]) != 1 and int(mouse_coord[1]) != 8:
                placed_objects.PlacedPawn(mouse_coord, "black")
            else:
                log.info("You are not allowed to place a pawn on rank " + mouse_coord[1])
        elif self.drag_piece_name == "black_bishop":
            placed_objects.PlacedBishop(mouse_coord, "black")
        elif self.drag_piece_name == "black_knight":
            placed_objects.PlacedKnight(mouse_coord, "black")
        elif self.drag_piece_name == "black_rook":
            placed_objects.PlacedRook(mouse_coord, "black")
        elif self.drag_piece_name == "black_queen":
            placed_objects.PlacedQueen(mouse_coord, "black")
        elif self.drag_piece_name == "black_king":
            if not placed_objects.PlacedKing.black_king_list:
                placed_objects.PlacedKing(mouse_coord, "black")
            else:
                log.info("You can only have one black king.")

class StartObjImagePlaceholder(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BLANKBOX"]
        self.rect = self.image.get_rect()
        START_SPRITES.add(self)
    def update(self):
        pass
    def flip_start_sprite(self, piece_name, pos):
        self.rect.topleft = pos
        if piece_name == "white_pawn":
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif piece_name == "white_bishop":
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif piece_name == "white_knight":
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif piece_name == "white_rook":
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif piece_name == "white_queen":
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif piece_name == "white_king":
            self.image = IMAGES["SPR_WHITE_KING"]
        elif piece_name == "black_pawn":
            self.image = IMAGES["SPR_BLACK_PAWN"]
        elif piece_name == "black_bishop":
            self.image = IMAGES["SPR_BLACK_BISHOP"]
        elif piece_name == "black_knight":
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
        elif piece_name == "black_rook":
            self.image = IMAGES["SPR_BLACK_ROOK"]
        elif piece_name == "black_queen":
            self.image = IMAGES["SPR_BLACK_QUEEN"]
        elif piece_name == "black_king":
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