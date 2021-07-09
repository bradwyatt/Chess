"""
Grid class along with the creation of grid squares with coordinate
"""
import pygame
import load_images_sounds as lis
import initvar

GRID_SPRITES = pygame.sprite.Group()

class Grid(pygame.sprite.Sprite):
    # pylint: disable=W0201
    # reset_play_interaction_vars defines init variables (not detected by pylint)
    grid_list = []
    grid_dict = {}
    def __init__(self, color, pos, given_coordinate):
        pygame.sprite.Sprite.__init__(self)
        self.color = color
        if self.color == "green":
            self.image = lis.IMAGES["SPR_GREEN_GRID"]
        elif self.color == "white":
            self.image = lis.IMAGES["SPR_WHITE_GRID"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GRID_SPRITES.add(self)
        self.initial_rect_top_left = pos
        self.coordinate = given_coordinate
        Grid.grid_list.append(self)
        Grid.grid_dict[self.coordinate] = self
        self.reset_play_interaction_vars()
    def reset_play_interaction_vars(self):
        """Reset all variables that interact with play pieces"""
        self.prior_move_color = False
        self.en_passant_skipover = False
        self.occupied = False
        self.occupied_piece = ""
        self.occupied_piece_color = ""
        self.no_highlight()
        self.coords_of_protecting_pieces = {'white': [], 'black': []}
        self.coords_of_attacking_pieces = {'white': [], 'black': []}
        self.coords_of_available_pieces = {'white': [], 'black': []}
        self.highlighted = False
    def attack_count_increment(self, piece_color, attack_coord):
        """
        Update coords_of_attacking_pieces list with the attacking piece,
        and the coordinate of that attacking piece
        """
        if piece_color == "white":
            self.coords_of_attacking_pieces['white'].append(attack_coord)
        elif piece_color == "black":
            self.coords_of_attacking_pieces['black'].append(attack_coord)
    def update(self, game_controller):
        """Update function required in pygame sprite group"""
    def available_count_increment(self, color, piece_coord):
        """
        Update coords_of_available_pieces list with the piece that is able to
        legally move there, and the coordinate of that piece
        """
        if color == "white" and piece_coord not in self.coords_of_available_pieces['white']:
            self.coords_of_available_pieces['white'].append(piece_coord)
        elif color == "black" and piece_coord not in self.coords_of_available_pieces['black']:
            self.coords_of_available_pieces['black'].append(piece_coord)
    def highlight(self, color, piece_coord):
        if initvar.TEST_MODE == True:
            # Yellow highlight for test mode, used for seeing the highlighted
            # square based on available move from selected piece
            self.image = lis.IMAGES["SPR_HIGHLIGHT"]
        self.highlighted = True
        self.available_count_increment(color, piece_coord)
    def no_highlight(self):
        if self.prior_move_color == True:
            self.image = lis.IMAGES["SPR_PRIOR_MOVE_GRID"]
        elif self.color == "green":
            self.image = lis.IMAGES["SPR_GREEN_GRID"]
        elif self.color == "white":
            self.image = lis.IMAGES["SPR_WHITE_GRID"]
        self.highlighted = False

# Retrieve Width and Height
assert lis.IMAGES["SPR_GREEN_GRID"].get_size() == lis.IMAGES["SPR_WHITE_GRID"].get_size()
X_GRID_WIDTH = lis.IMAGES["SPR_GREEN_GRID"].get_width()
Y_GRID_HEIGHT = lis.IMAGES["SPR_GREEN_GRID"].get_height()
X_GRID_END = initvar.X_GRID_START+(X_GRID_WIDTH*8)
Y_GRID_END = initvar.Y_GRID_START+(Y_GRID_HEIGHT*8)
XGRIDRANGE = [initvar.X_GRID_START, X_GRID_END, X_GRID_WIDTH] # 1st num: begin 2nd: end 3rd: step
YGRIDRANGE = [initvar.Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT] # 1st num: begin 2nd: end 3rd: step
# Creates grid setting coordinate as list with first element being letter and second being number
coordinates_dict_with_pos = {}
for x in range(initvar.X_GRID_START, X_GRID_END, X_GRID_WIDTH): 
    for y in range(initvar.Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT): 
        grid_pos = x, y
        grid_coordinate_as_list_element = [chr(int((x-initvar.X_GRID_START)/X_GRID_WIDTH)+97), int((Y_GRID_END-y)/Y_GRID_HEIGHT)]
        grid_coordinate = "".join(map(str, (grid_coordinate_as_list_element)))
        coordinates_dict_with_pos[grid_coordinate] = grid_pos
for coordinate in coordinates_dict_with_pos.keys():
    for i in range(ord("a"), ord("h"), 2):
        for j in range(2, 9, 2):
            if(ord(coordinate[0]) == i and int(coordinate[1]) == j):
                Grid("white", coordinates_dict_with_pos[coordinate], coordinate)
    for i in range(ord("b"), ord("i"), 2):
        for j in range(1, 8, 2):
            if(ord(coordinate[0]) == i and int(coordinate[1]) == j):
                Grid("white", coordinates_dict_with_pos[coordinate], coordinate)
    for i in range(ord("a"), ord("h"), 2):
        for j in range(1, 8, 2):
            if(ord(coordinate[0]) == i and int(coordinate[1]) == j):
                Grid("green", coordinates_dict_with_pos[coordinate], coordinate)
    for i in range(ord("b"), ord("i"), 2):
        for j in range(2, 9, 2):
            if(ord(coordinate[0]) == i and int(coordinate[1]) == j):
                Grid("green", coordinates_dict_with_pos[coordinate], coordinate)
