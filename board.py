import pygame
from load_images_sounds import *
import initvar

GRID_SPRITES = pygame.sprite.Group()

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
        self.available = False
        self.occupied = False
        self.color = None
        self.occupied_piece = ""
        self.occupied_piece_color = ""
        Grid.grid_list.append(self)
        Grid.grid_dict[self.coordinate] = self
        self.coords_of_attacking_pieces = {'white': [], 'black': []}
        self.coords_of_available_pieces = {'white': [], 'black': []}
        self.en_passant_skipover = False
        self.prior_move_color = False
    def reset_board(self):
        self.prior_move_color = False
        self.no_highlight()
        self.coords_of_attacking_pieces = {'white': [], 'black': []}
        self.coords_of_available_pieces = {'white': [], 'black': []}
        self.attack_count_reset()
    def attack_count_reset(self):
        self.coords_of_attacking_pieces = {'white': [], 'black': []}
    def attack_count_increment(self, color, attack_coord):
        if color == "white":
            self.coords_of_attacking_pieces['white'].append(attack_coord)
        elif color == "black":
            self.coords_of_attacking_pieces['black'].append(attack_coord)
    def update(self, game_controller):
        pass
    def set_availability(self, availability):
        if availability == True:
            self.available = True
        else:
            self.available = False
    def available_count_increment(self, color, piece_coord):
        if color == "white" and piece_coord not in self.coords_of_available_pieces['white']:
            self.coords_of_available_pieces['white'].append(piece_coord)
        elif color == "black" and piece_coord not in self.coords_of_available_pieces['black']:
            self.coords_of_available_pieces['black'].append(piece_coord)
    def highlight(self, color, piece_coord):
        self.image = IMAGES["SPR_HIGHLIGHT"]
        self.highlighted = True
        self.set_availability(True)
        self.available_count_increment(color, piece_coord)
    def no_highlight(self):
        if(self.prior_move_color == True):
            self.image = IMAGES["SPR_PRIOR_MOVE_GRID"]
        elif(self.color == "green"):
            self.image = IMAGES["SPR_GREEN_GRID"]
        elif(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_GRID"]
        self.highlighted = False

X_GRID_END = initvar.X_GRID_START+(initvar.X_GRID_WIDTH*8)
Y_GRID_END = initvar.Y_GRID_START+(initvar.Y_GRID_HEIGHT*8)
XGRIDRANGE = [initvar.X_GRID_START, X_GRID_END, initvar.X_GRID_WIDTH] #1st num: begin 2nd: end 3rd: step
YGRIDRANGE = [initvar.Y_GRID_START, Y_GRID_END, initvar.Y_GRID_HEIGHT] #1st num: begin 2nd: end 3rd: step
        
# Creates grid setting coordinate as list with first element being letter and second being number
for x in range(initvar.X_GRID_START, X_GRID_END, initvar.X_GRID_WIDTH): 
    for y in range(initvar.Y_GRID_START, Y_GRID_END, initvar.Y_GRID_HEIGHT): 
        grid_pos = x, y
        grid_coordinate_as_list_element = [chr(int((x-initvar.X_GRID_START)/initvar.X_GRID_WIDTH)+97), int((Y_GRID_END-y)/initvar.Y_GRID_HEIGHT)]
        grid_coordinate = "".join(map(str, (grid_coordinate_as_list_element)))
        grid = Grid(GRID_SPRITES, grid_pos, grid_coordinate)
for grid in Grid.grid_list:
    for i in range(ord("a"), ord("h"), 2):
        for j in range(2, 9, 2):
            if(ord(grid.coordinate[0]) == i and int(grid.coordinate[1]) == j):
                grid.image = IMAGES["SPR_WHITE_GRID"]
                grid.color = "white"
    for i in range(ord("b"), ord("i"), 2):
        for j in range(1, 8, 2):
            if(ord(grid.coordinate[0]) == i and int(grid.coordinate[1]) == j):
                grid.image = IMAGES["SPR_WHITE_GRID"]
                grid.color = "white"
    for i in range(ord("a"), ord("h"), 2):
        for j in range(1, 8, 2):
            if(ord(grid.coordinate[0]) == i and int(grid.coordinate[1]) == j):
                grid.image = IMAGES["SPR_GREEN_GRID"]
                grid.color = "green"
    for i in range(ord("b"), ord("i"), 2):
        for j in range(2, 9, 2):
            if(ord(grid.coordinate[0]) == i and int(grid.coordinate[1]) == j):
                grid.image = IMAGES["SPR_GREEN_GRID"]
                grid.color = "green"