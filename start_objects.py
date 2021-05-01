import pygame
import initvar
import placed_objects
from load_images_sounds import *
import logging

log = logging.getLogger(__name__)

START_SPRITES = pygame.sprite.Group()

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

START_OBJ_IMAGE_PLACEHOLDER = StartObjImagePlaceholder()

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
    
class Start():
    start_dict = {}
    start_dict['start_obj_image_placeholder'] = StartObjImagePlaceholder()
    start_dict['white_pawn'] = StartPawn("white", initvar.STARTPOS['white_pawn'])
    start_dict['white_bishop'] = StartBishop("white", initvar.STARTPOS['white_bishop'])
    start_dict['white_knight'] = StartKnight("white", initvar.STARTPOS['white_knight'])        
    start_dict['white_rook'] = StartRook("white", initvar.STARTPOS['white_rook'])      
    start_dict['white_queen'] = StartQueen("white", initvar.STARTPOS['white_queen'])      
    start_dict['white_king'] = StartKing("white", initvar.STARTPOS['white_king'])      
    start_dict['black_pawn'] = StartPawn("black", initvar.STARTPOS['black_pawn'])
    start_dict['black_bishop'] = StartBishop("black", initvar.STARTPOS['black_bishop'])
    start_dict['black_knight'] = StartKnight("black", initvar.STARTPOS['black_knight'])      
    start_dict['black_rook'] = StartRook("black", initvar.STARTPOS['black_rook'])      
    start_dict['black_queen'] = StartQueen("black", initvar.STARTPOS['black_queen'])      
    start_dict['black_king'] = StartKing("black", initvar.STARTPOS['black_king'])
    def restart_start_positions():
        Start.start_dict['white_pawn'].rect.topleft = initvar.STARTPOS['white_pawn']
        Start.start_dict['white_bishop'].rect.topleft = initvar.STARTPOS['white_bishop']
        Start.start_dict['white_knight'].rect.topleft = initvar.STARTPOS['white_knight']
        Start.start_dict['white_rook'].rect.topleft = initvar.STARTPOS['white_rook']
        Start.start_dict['white_queen'].rect.topleft = initvar.STARTPOS['white_queen']
        Start.start_dict['white_king'].rect.topleft = initvar.STARTPOS['white_king']
        Start.start_dict['black_pawn'].rect.topleft = initvar.STARTPOS['black_pawn']
        Start.start_dict['black_bishop'].rect.topleft = initvar.STARTPOS['black_bishop']
        Start.start_dict['black_knight'].rect.topleft = initvar.STARTPOS['black_knight']
        Start.start_dict['black_rook'].rect.topleft = initvar.STARTPOS['black_rook']
        Start.start_dict['black_queen'].rect.topleft = initvar.STARTPOS['black_queen']
        Start.start_dict['black_king'].rect.topleft = initvar.STARTPOS['black_king']
        
class Dragging():
    drag_piece_name = ""
    def dragging_all_false():
        Dragging.drag_piece_name = ""
    def drag_piece(piece):
        Dragging.dragging_all_false()
        Dragging.drag_piece_name = piece
    def start_drag_and_flip_start_sprite(piece_name):
        Start.restart_start_positions()
        Dragging.drag_piece(piece_name)
        Start.start_dict['start_obj_image_placeholder'].flip_start_sprite(piece_name, Start.start_dict.get(piece_name).rect.topleft)
    def update_position(mousepos):
        def drag_and_replace_start_obj_image(name_of_piece, mouse_pos):
            if Dragging.drag_piece_name == name_of_piece:
                Start.start_dict['start_obj_image_placeholder'].rect.topleft = initvar.STARTPOS[name_of_piece]
                Start.start_dict[name_of_piece].rect.topleft = (mousepos[0]-(Start.start_dict[name_of_piece].image.get_width()/2),
                                          mousepos[1]-(Start.start_dict[name_of_piece].image.get_height()/2))
            else:
                Start.start_dict[name_of_piece].rect.topleft = initvar.STARTPOS[name_of_piece]
        drag_and_replace_start_obj_image("white_pawn", mousepos)
        drag_and_replace_start_obj_image("white_bishop", mousepos)
        drag_and_replace_start_obj_image("white_knight", mousepos)
        drag_and_replace_start_obj_image("white_rook", mousepos)
        drag_and_replace_start_obj_image("white_queen", mousepos)
        drag_and_replace_start_obj_image("white_king", mousepos)
        drag_and_replace_start_obj_image("black_pawn", mousepos)
        drag_and_replace_start_obj_image("black_bishop", mousepos)
        drag_and_replace_start_obj_image("black_knight", mousepos)
        drag_and_replace_start_obj_image("black_rook", mousepos)
        drag_and_replace_start_obj_image("black_queen", mousepos)
        drag_and_replace_start_obj_image("black_king", mousepos)   
    def dragging_to_placed_no_dups(mouse_coord):
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
        if Dragging.drag_piece_name == "white_pawn":
            if int(mouse_coord[1]) != 1 and int(mouse_coord[1]) != 8:
                placed_objects.PlacedPawn(mouse_coord, "white")
            else:
                log.info("You are not allowed to place a pawn on rank " + mouse_coord[1])
        elif Dragging.drag_piece_name == "white_bishop":
            placed_objects.PlacedBishop(mouse_coord, "white")
        elif Dragging.drag_piece_name == "white_knight":
            placed_objects.PlacedKnight(mouse_coord, "white")
        elif Dragging.drag_piece_name == "white_rook":
            placed_objects.PlacedRook(mouse_coord, "white")
        elif Dragging.drag_piece_name == "white_queen":
            placed_objects.PlacedQueen(mouse_coord, "white")
        elif Dragging.drag_piece_name == "white_king":
            if not placed_objects.PlacedKing.white_king_list:
                placed_objects.PlacedKing(mouse_coord, "white")
            else:
                log.info("You can only have one white king.")
        elif Dragging.drag_piece_name == "black_pawn":
            if int(mouse_coord[1]) != 1 and int(mouse_coord[1]) != 8:
                placed_objects.PlacedPawn(mouse_coord, "black")
            else:
                log.info("You are not allowed to place a pawn on rank " + mouse_coord[1])
        elif Dragging.drag_piece_name == "black_bishop":
            placed_objects.PlacedBishop(mouse_coord, "black")
        elif Dragging.drag_piece_name == "black_knight":
            placed_objects.PlacedKnight(mouse_coord, "black")
        elif Dragging.drag_piece_name == "black_rook":
            placed_objects.PlacedRook(mouse_coord, "black")
        elif Dragging.drag_piece_name == "black_queen":
            placed_objects.PlacedQueen(mouse_coord, "black")
        elif Dragging.drag_piece_name == "black_king":
            if not placed_objects.PlacedKing.black_king_list:
                placed_objects.PlacedKing(mouse_coord, "black")
            else:
                log.info("You can only have one black king.")