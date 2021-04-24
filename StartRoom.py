import initvar
import pygame
from load_images_sounds import *

class Grid(pygame.sprite.Sprite):
    grid_list = []
    grid_dict = {}
    def __init__(self, GRID_SPRITES, pos, coordinate):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GRID"] # Default
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GRID_SPRITES.add(self)
        self.coordinate = coordinate
        self.highlighted = False
        self.occupied = False
        self.color = None
        self.occupied_piece = ""
        self.occupied_piece_color = ""
        Grid.grid_list.append(self)
        Grid.grid_dict[self.coordinate] = self
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
        self.en_passant_skipover = False
        self.prior_move_color = False
    def reset_board(self):
        self.prior_move_color = False
        self.no_highlight()
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
    def attack_count_reset(self):
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
    def attack_count_increment(self, color, attack_coord):
        if color == "white":
            self.list_of_white_pieces_attacking.append(attack_coord)
        elif color == "black":
            self.list_of_black_pieces_attacking.append(attack_coord)
    def update(self, game_controller):
        pass
    def highlight(self):
        self.image = IMAGES["SPR_HIGHLIGHT"]
        self.highlighted = True
    def no_highlight(self):
        if(self.prior_move_color == True):
            self.image = IMAGES["SPR_PRIOR_MOVE_GRID"]
        elif(self.color == "green"):
            self.image = IMAGES["SPR_GREEN_GRID"]
        elif(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_GRID"]
        self.highlighted = False