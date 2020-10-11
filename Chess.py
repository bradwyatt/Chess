"""
Chess created by Brad Wyatt
Python 3

Testing:
spaces_available for pawn: when king is in check, you can take a protector piece (bad)

Features To-Do (short-term):
Where taken pieces go
Restart button
If no king then don't start game

Features To-Do (long-term):
Create function where given coordinates, return X, Y of square (for loaded_file func)
Save positions rather than restarting when pressing stop button
Recording moves on right side (each move has a dictionary of dictionaries of where pieces are)
PGN format?
Customized Turns for black and white
Choose piece for Promotion
"""
from start_objects import *
from placed_objects import *
from load_images_sounds import *
from menu_buttons import *
import random
import sys
import os
import copy
import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter.filedialog import *
from ast import *
import pygame
from pygame.constants import RLEACCEL
from pygame.locals import (KEYDOWN, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_LEFT,
                           K_RIGHT, QUIT, K_ESCAPE)
import datetime

#Grouping Images and Sounds
STARTPOS = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
             'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
             'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
             'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}


START_SPRITES = pygame.sprite.Group()

def snap_to_grid(pos, x_range, y_range):
    best_num_X, best_num_Y = x_range[0], y_range[0] #So Y doesn't go above the menu
    for x in range(x_range[0], x_range[1], x_range[2]):
        if pos[0]-x <= 48 and pos[0]-x >= 0:
            best_num_X = x
    for y in range(y_range[0], y_range[1], y_range[2]):
        if pos[1]-y <= 48 and pos[1]-y >= 0:
            best_num_Y = y
    best_grid_snap = (best_num_X, best_num_Y)
    return best_grid_snap
             
def remove_placed_object(PLACED_SPRITES, mousepos):
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
    return PLACED_SPRITES


def restart_start_objects(START):
    START.white_pawn.rect.topleft = STARTPOS['white_pawn']
    START.white_bishop.rect.topleft = STARTPOS['white_bishop']
    START.white_knight.rect.topleft = STARTPOS['white_knight']
    START.white_rook.rect.topleft = STARTPOS['white_rook']
    START.white_queen.rect.topleft = STARTPOS['white_queen']
    START.white_king.rect.topleft = STARTPOS['white_king']
    START.black_pawn.rect.topleft = STARTPOS['black_pawn']
    START.black_bishop.rect.topleft = STARTPOS['black_bishop']
    START.black_knight.rect.topleft = STARTPOS['black_knight']
    START.black_rook.rect.topleft = STARTPOS['black_rook']
    START.black_queen.rect.topleft = STARTPOS['black_queen']
    START.black_king.rect.topleft = STARTPOS['black_king']
    return START

def get_color():
    color = askcolor()
    return [color[0][0], color[0][1], color[0][2]]

def load_file(PLACED_SPRITES, colorkey, reset=False):
    open_file = None
    if reset == True:
        loaded_dict = {'white_pawn': [(48, 384), (96, 384), (144, 384), (192, 384), (240, 384), (288, 384), (336, 384), (384, 384)],
                       'white_bishop': [(288, 432), (144, 432)], 'white_knight': [(336, 432), (96, 432)],
                       'white_rook': [(384, 432), (48, 432)], 'white_queen': [(192, 432)], 'white_king': [(240, 432)],
                       'black_pawn': [(48, 144), (96, 144), (144, 144), (192, 144), (240, 144), (288, 144), (336, 144), (384, 144)],
                       'black_bishop': [(144, 96), (288, 96)], 'black_knight': [(336, 96), (96, 96)],
                       'black_rook': [(384, 96), (48, 96)], 'black_queen': [(192, 96)], 'black_king': [(240, 96)],
                       'RGB': colorkey}
    else:
        request_file_name = askopenfilename(defaultextension=".lvl")
        open_file = open(request_file_name, "r")
        loaded_file = open_file.read()
        loaded_dict = literal_eval(loaded_file)
            
    for play_white_pawn in PlayPawn.white_pawn_list:
        play_white_pawn.destroy()
    for play_white_bishop in PlayBishop.white_bishop_list:
        play_white_bishop.destroy()
    for play_white_knight in PlayKnight.white_knight_list:
        play_white_knight.destroy()
    for play_white_rook in PlayRook.white_rook_list:
        play_white_rook.destroy()
    for play_white_queen in PlayQueen.white_queen_list:
        play_white_queen.destroy()
    for play_white_king in PlayKing.white_king_list:
        play_white_king.destroy()
    for play_black_pawn in PlayPawn.black_pawn_list:
        play_black_pawn.destroy()
    for play_black_bishop in PlayBishop.black_bishop_list:
        play_black_bishop.destroy()
    for play_black_knight in PlayKnight.black_knight_list:
        play_black_knight.destroy()
    for play_black_rook in PlayRook.black_rook_list:
        play_black_rook.destroy()
    for play_black_queen in PlayQueen.black_queen_list:
        play_black_queen.destroy()
    for play_black_king in PlayKing.black_king_list:
        play_black_king.destroy()
    if open_file:
        open_file.close()
    
    # Removes all placed lists
    remove_all_placed()
    
    print("Removed all sprites. Now creating lists for loaded level.")
    
    for white_pawn_pos in loaded_dict['white_pawn']:
        PlacedPawn(white_pawn_pos, PLACED_SPRITES, "white")
    for white_bishop_pos in loaded_dict['white_bishop']:
        PlacedBishop(white_bishop_pos, PLACED_SPRITES, "white")
    for white_knight_pos in loaded_dict['white_knight']:
        PlacedKnight(white_knight_pos, PLACED_SPRITES, "white")
    for white_rook_pos in loaded_dict['white_rook']:
        PlacedRook(white_rook_pos, PLACED_SPRITES, "white")
    for white_queen_pos in loaded_dict['white_queen']:
        PlacedQueen(white_queen_pos, PLACED_SPRITES, "white")
    for white_king_pos in loaded_dict['white_king']:
        PlacedKing(white_king_pos, PLACED_SPRITES, "white")
    for black_pawn_pos in loaded_dict['black_pawn']:
        PlacedPawn(black_pawn_pos, PLACED_SPRITES, "black")
    for black_bishop_pos in loaded_dict['black_bishop']:
        PlacedBishop(black_bishop_pos, PLACED_SPRITES, "black")
    for black_knight_pos in loaded_dict['black_knight']:
        PlacedKnight(black_knight_pos, PLACED_SPRITES, "black")
    for black_rook_pos in loaded_dict['black_rook']:
        PlacedRook(black_rook_pos, PLACED_SPRITES, "black")
    for black_queen_pos in loaded_dict['black_queen']:
        PlacedQueen(black_queen_pos, PLACED_SPRITES, "black")
    for black_king_pos in loaded_dict['black_king']:
        PlacedKing(black_king_pos, PLACED_SPRITES, "black")
    colorkey = loaded_dict['RGB']
    
    print("File Loaded")
    return PLACED_SPRITES, colorkey

def save_file(colorkey):
    try:
        # default extension is optional, here will add .txt if missing
        save_file_prompt = asksaveasfilename(defaultextension=".lvl")
        save_file_name = open(save_file_prompt, "w")
        if save_file_name is not None:
            # Write the file to disk
            obj_locations = copy.deepcopy(get_dict_rect_positions())
            obj_locations['RGB'] = colorkey
            save_file_name.write(str(obj_locations))
            save_file_name.close()
            print("File Saved Successfully.")
        else:
            print("Error! Need king to save!")
    except IOError:
        print("Save File Error, please restart game and try again.")

def quit():
    print('Thanks for playing')
    sys.exit()

#############
# PLAY PIECES
#############

class ChessPiece:
    def __init__(self, pos, PLAY_SPRITES, image, col):
        PLAY_SPRITES.add(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.color = col
        COLOR_POSSIBILITIES = ["white", "black"]
        OTHER_COLOR_INDEX = (COLOR_POSSIBILITIES.index(self.color)+1)%2
        self.enemy_color = COLOR_POSSIBILITIES[OTHER_COLOR_INDEX]
        self.select = False
        self.pinned = False
        self.disable = False
        self.taken_off_board = False
        self.coordinate = self.get_coordinate()
        self.previous_coordinate = self.get_coordinate()
    def get_coordinate(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                return grid.coordinate
    def pinned_restrict(self, pin_attacking_coordinates):
        self.pinned = True
        self.pin_attacking_coordinates = pin_attacking_coordinates

class PlayPawn(ChessPiece, pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_PAWN"]
            PlayPawn.white_pawn_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
            PlayPawn.black_pawn_list.append(self)
        super().__init__(pos, PLAY_SPRITES, self.image, col)
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def captured(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = 200, 600
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_PAWN_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_PAWN_HIGHLIGHTED"]
            self.select = True
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_PAWN"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_PAWN"]
            self.select = False
    def projected(self, game_controller):
        if self.taken_off_board != True:
            self.proj_attacking_coordinates = [self.coordinate]
            if(self.color == "white"):
                for grid in Grid.grid_list:
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            print("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            print("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            elif(self.color == "black"):
                for grid in Grid.grid_list:
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            print("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            print("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            def pawn_movement():
                if self.color == "white":
                    movement = 1
                    initial_space = 2
                    hop_space = 4
                elif self.color == "black":
                    movement = -1
                    initial_space = 7
                    hop_space = 5
                for grid in Grid.grid_list:
                    # Move one space up
                    if (grid.coordinate[0] == self.coordinate[0] and \
                        grid.coordinate[1] == self.coordinate[1]+movement): 
                        if grid.occupied == False:
                            if game_controller.color_in_check == self.color:
                                if self.pinned == True:
                                    self.disable = True
                                    return
                                elif grid.coordinate in game_controller.check_attacking_coordinates:
                                    grid.highlight()
                            elif self.pinned == False:
                                grid.highlight()
                    # Move two spaces up
                    if (self.coordinate[1] == initial_space and grid.coordinate[0] == self.coordinate[0] and \
                        grid.coordinate[1] == hop_space and grid.occupied == False):
                        # If space before hop space is occupied by a piece
                        if Grid.grid_dict["".join(map(str, (grid.coordinate[0], hop_space-movement)))].occupied == False:
                            if grid.occupied == False:
                                if game_controller.color_in_check == self.color:
                                    if self.pinned == True:
                                        self.disable = True
                                        return
                                    elif grid.coordinate in game_controller.check_attacking_coordinates:
                                        grid.highlight()
                                elif self.pinned == False:
                                    grid.highlight()
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and grid.coordinate[1] == self.coordinate[1]+movement and \
                    grid.occupied_piece_color == self.enemy_color):
                        # No check and no pin is moving as normal
                        if self.pinned == False and game_controller.color_in_check != self.color:
                            grid.highlight()
                        # When checked then only able to take the attacker piece in reach
                        elif game_controller.color_in_check == self.color:
                            if grid.coordinate == game_controller.check_attacking_coordinates[0]:
                                grid.highlight()
                        # If attacker is causing pin
                        elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                            grid.highlight()
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and grid.coordinate[1] == self.coordinate[1]+movement and \
                    grid.occupied_piece_color == self.enemy_color):
                        # No check and no pin is moving as normal
                        if self.pinned == False and game_controller.color_in_check != self.color:
                            grid.highlight()
                        # When checked then only able to take the attacker piece in reach
                        elif game_controller.color_in_check == self.color:
                            if grid.coordinate == game_controller.check_attacking_coordinates[0]:
                                grid.highlight()
                        # If attacker is causing pin
                        elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                            grid.highlight()
                    # En Passant
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and grid.coordinate[1] == self.coordinate[1]+movement and \
                    grid.en_passant_skipover == True):
                        if self.pinned == False:
                            grid.highlight()
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and grid.coordinate[1] == self.coordinate[1]+movement and \
                    grid.en_passant_skipover == True):
                        if self.pinned == False:
                            grid.highlight()
            pawn_movement()
 
class PlayKnight(ChessPiece, pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
            PlayKnight.white_knight_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
            PlayKnight.black_knight_list.append(self)
        super().__init__(pos, PLAY_SPRITES, self.image, col)
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            self.proj_attacking_coordinates = [self.coordinate]
            def knight_proj_direction(x, y):
                for grid in Grid.grid_list:
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and grid.coordinate[1] == self.coordinate[1]+y:
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            print("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("knight", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            knight_proj_direction(-1, -2)
            knight_proj_direction(-1, 2)
            knight_proj_direction(1, -2)
            knight_proj_direction(1, 2)
            knight_proj_direction(-2, -1)
            knight_proj_direction(-2, 1)
            knight_proj_direction(2, -1)
            knight_proj_direction(2, 1)
    def captured(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = 400, 600
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_KNIGHT_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_KNIGHT_HIGHLIGHTED"]
            self.select = True
    def spaces_available(self, game_controller):
        # A knight can't legally move when it is pinned in chess
        if(self.taken_off_board != True and self.disable == False and self.pinned == False):
            def knight_move_direction(x, y):
                for grid in Grid.grid_list:
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and grid.coordinate[1] == self.coordinate[1]+y \
                        and (grid.occupied == 0 or grid.occupied_piece_color != self.color):
                            if game_controller.color_in_check == self.color:
                                if grid.coordinate in game_controller.check_attacking_coordinates:
                                    grid.highlight()
                                else:
                                    return
                            grid.highlight()
            knight_move_direction(-1, -2)
            knight_move_direction(-1, 2)
            knight_move_direction(1, -2)
            knight_move_direction(1, 2)
            knight_move_direction(-2, -1)
            knight_move_direction(-2, 1)
            knight_move_direction(2, -1)
            knight_move_direction(2, 1)
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_KNIGHT"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_KNIGHT"]
            self.select = False

def bishop_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the bishop and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        for grid in Grid.grid_list:
            if(ord(grid.coordinate[0]) == ord(piece.coordinate[0])+(x*i) and grid.coordinate[1] == piece.coordinate[1]+(y*i)):
                # Incrementing the count for allowable grids that this piece moves
                proj_attacking_coordinates.append(grid.coordinate) 
                # If King is already in check and it's iterating to next occupied grid space
                if(pieces_in_way == 1 and king_count == 1):
                    game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                    return
                # Passing this piece's coordinate to this grid
                if pinned_piece_coord is None:
                    grid.attack_count_increment(piece.color, piece.coordinate)
                # Counting pieces and Ignoring pieces that are past the king
                if(grid.occupied == 1 and king_count < 1): 
                    pieces_in_way += 1
                    if(grid.occupied_piece == "king" and grid.occupied_piece_color == piece.enemy_color):
                        king_count += 1
                    else:
                        # If there's already no pin
                        if pinned_piece_coord is None:
                            pinned_piece_coord = grid.coordinate
                        # 2 pieces without a king
                        else:
                            return
                # 2 Pieces in way, includes 1 king
                if(pieces_in_way == 2 and king_count == 1): 
                    print("King is pinned on coordinate " + str(grid.coordinate))
                    game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
                    return
                # 1 Piece in way which is King
                # This is check, we will iterate one more time to cover the next square king is not allowed to go to
                elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
                    print("Check for coordinate " + str(grid.coordinate))
                    # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
                    # Corner case where king is on the edge of the board
                    if((grid.coordinate[0] == 'a' and x == -1) or (grid.coordinate[0] == 'h' and x == 1) or \
                       (grid.coordinate[1] == 8 and y == 1) or (grid.coordinate[1] == 1 and y == -1)):
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        return

def bishop_direction_spaces_available(bishop, game_controller, x, y):
    for i in range(1,8):
        for grid in Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(bishop.coordinate[0])+(x*i) \
                   and grid.coordinate[1] == bishop.coordinate[1]+(y*i):
                # If no enemy piece on grid
                if grid.occupied == 0:
                    # If current king not in check and this piece is not pinned
                    if(game_controller.color_in_check != bishop.color and bishop.pinned == False):
                        grid.highlight()
                    # If current king is in check
                    elif game_controller.color_in_check == bishop.color:
                        # Disable piece if it is pinned and checked from another enemy piece
                        if bishop.pinned == True:
                            bishop.disable = True
                            return
                        # Block path of enemy bishop, rook, or queen 
                        # You cannot have multiple spaces in one direction when blocking so return
                        elif grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                            and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                                 or game_controller.attacker_piece == "queen"):
                            grid.highlight()
                            return
                        # The only grid available is the attacker piece when pawn or knight
                        elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                            and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                            grid.highlight()
                            return
                    # If pinned and the grid is within the attacking coordinates restraint
                    # Includes grid.coordinate != self.coordinate so that staying at same coordinate doesn't count as move
                    elif(bishop.pinned == True and grid.coordinate in bishop.pin_attacking_coordinates \
                         and grid.occupied_piece != 'king' and grid.coordinate != bishop.coordinate):
                            grid.highlight()
                    else:
                        # When all the above conditions aren't met, then the bishop can't move further
                        return
                # If enemy piece on grid
                elif grid.occupied == 1 and grid.occupied_piece_color == bishop.enemy_color:
                    # Check_Attacking_Coordinates only exists when there is check
                    if game_controller.color_in_check == bishop.color:
                        if grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                            and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                                 or game_controller.attacker_piece == "queen"):
                            grid.highlight()
                        elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                            and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                            grid.highlight()
                    # If pinned and grid is within the attacking coordinates restraint
                    elif(bishop.pinned == True and grid.occupied_piece != 'king'):
                        if grid.coordinate in bishop.pin_attacking_coordinates:
                            # If not in check from another piece
                            if not game_controller.check_attacking_coordinates:
                                grid.highlight()
                                # No return since there are more than one possibility when between king and attacker piece
                    else:
                        # In all other cases where no check and no pin
                        grid.highlight()
                    # Will always return function on square with enemy piece
                    return
                # If same color piece in the way
                elif grid.occupied == 1 and grid.occupied_piece_color == bishop.color:
                    # Will always return function on square with friendly piece
                    return

class PlayBishop(ChessPiece, pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
            PlayBishop.white_bishop_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
            PlayBishop.black_bishop_list.append(self)
        super().__init__(pos, PLAY_SPRITES, self.image, col)
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            bishop_projected("bishop", self, game_controller, -1, -1) #southwest
            bishop_projected("bishop", self, game_controller, -1, 1) #northwest
            bishop_projected("bishop", self, game_controller, 1, -1) #southeast
            bishop_projected("bishop", self, game_controller, 1, 1) #northeast
    def captured(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = 300, 600
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_BISHOP_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_BISHOP_HIGHLIGHTED"]
            self.select = True
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            bishop_direction_spaces_available(self, game_controller, -1, -1) #southwest
            bishop_direction_spaces_available(self, game_controller, -1, 1) #northwest
            bishop_direction_spaces_available(self, game_controller, 1, -1) #southeast
            bishop_direction_spaces_available(self, game_controller, 1, 1) #northeast
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_BISHOP"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_BISHOP"]
            self.select = False

def rook_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the rook and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        for grid in Grid.grid_list:
            if(ord(grid.coordinate[0]) == ord(piece.coordinate[0])+(x*i) \
               and grid.coordinate[1] == piece.coordinate[1]+(y*i)):
                # Incrementing the count for allowable grids that this piece moves
                proj_attacking_coordinates.append(grid.coordinate)
                # If King is already in check and it's iterating to next occupied grid space
                if(pieces_in_way == 1 and king_count == 1):
                    game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                    return
                # Passing this piece's coordinate to this grid
                if pinned_piece_coord is None:
                    grid.attack_count_increment(piece.color, piece.coordinate)
                # Counting pieces and Ignoring pieces that are past the king
                if(grid.occupied == 1 and king_count < 1): 
                    pieces_in_way += 1
                    if(grid.occupied_piece == "king" and grid.occupied_piece_color == piece.enemy_color):
                        king_count += 1
                    else:
                        # If there's already no pin
                        if pinned_piece_coord is None:
                            pinned_piece_coord = grid.coordinate
                        # 2 pieces without a king
                        else:
                            return
                # 2 Pieces in way, includes 1 king
                if(pieces_in_way == 2 and king_count == 1): #2 Pieces in way, includes 1 king
                    print("King is pinned on coordinate " + str(grid.coordinate))
                    game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
                    return
                # 1 Piece in way which is King
                # This is check, we will iterate one more time to cover the next square king is not allowed to go to
                elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
                    print("Check for coordinate " + str(grid.coordinate))
                    # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
                    if((grid.coordinate[0] == 'a' and y == 0) or (grid.coordinate[0] == 'h' and y == 0) or \
                       (grid.coordinate[1] == 1 and x == 0) or (grid.coordinate[1] == 8 and x == 0)):
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        return
    return

def rook_direction_spaces_available(rook, game_controller, x, y):
    for i in range(1,8):
        for grid in Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(rook.coordinate[0])+(x*i) and grid.coordinate[1] == rook.coordinate[1]+(y*i):
                # If no enemy piece on grid
                if grid.occupied == 0:
                    # If current king not in check and this piece is not pinned
                    if(game_controller.color_in_check != rook.color and rook.pinned == False):
                        grid.highlight()
                    # If current king is in check
                    elif game_controller.color_in_check == rook.color:
                        # Disable piece if it is pinned and checked from another enemy piece
                        if rook.pinned == True:
                            rook.disable = True
                            return
                        # Block path of enemy bishop, rook, or queen 
                        # You cannot have multiple spaces in one direction when blocking so return
                        elif grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                            and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                                 or game_controller.attacker_piece == "queen"):
                            grid.highlight()
                            return
                        # The only grid available is the attacker piece when pawn or knight
                        elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                            and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                            grid.highlight()
                            return
                    # If pinned and grid is within the attacking coordinates restraint
                    elif(rook.pinned == True and grid.coordinate in rook.pin_attacking_coordinates \
                         and grid.occupied_piece != 'king' and grid.coordinate != rook.coordinate):
                        grid.highlight() 
                    else:
                        # When all the above conditions aren't met, then the bishop can't move further
                        return
                # If enemy piece on grid
                elif grid.occupied == 1 and grid.occupied_piece_color == rook.enemy_color:
                    # Check_Attacking_Coordinates only exists when there is check
                    if game_controller.color_in_check == rook.color:
                        # Block path of enemy bishop, rook, or queen 
                        # You cannot have multiple spaces in one direction when blocking so return
                        if grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                            and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                                 or game_controller.attacker_piece == "queen"):
                            grid.highlight()
                        # The only grid available is the attacker piece when pawn or knight
                        elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                            and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                            grid.highlight()
                    # If pinned and grid is within the attacking coordinates restraint
                    elif(rook.pinned == True and grid.coordinate in rook.pin_attacking_coordinates \
                         and grid.occupied_piece != 'king'):
                        grid.highlight()      
                    else:
                        # In all other cases where no check and no pin
                        grid.highlight()
                    return
                # If same color piece in the way
                elif grid.occupied == 1 and grid.occupied_piece_color == rook.color:
                    return

class PlayRook(ChessPiece, pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
            PlayRook.white_rook_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
            PlayRook.black_rook_list.append(self)
        super().__init__(pos, PLAY_SPRITES, self.image, col)
        self.allowed_to_castle = True
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def captured(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = 550, 600
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            rook_projected("rook", self, game_controller, -1, 0) #west
            rook_projected("rook", self, game_controller, 1, 0) #east
            rook_projected("rook", self, game_controller, 0, 1) #north
            rook_projected("rook", self, game_controller, 0, -1) #south
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK_HIGHLIGHTED"]
        self.select = True
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            rook_direction_spaces_available(self, game_controller, -1, 0) #west
            rook_direction_spaces_available(self, game_controller, 1, 0) #east
            rook_direction_spaces_available(self, game_controller, 0, 1) #north
            rook_direction_spaces_available(self, game_controller, 0, -1) #south
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
        self.select = False

class PlayQueen(ChessPiece, pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
            PlayQueen.white_queen_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
            PlayQueen.black_queen_list.append(self)
        super().__init__(pos, PLAY_SPRITES, self.image, col)
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def captured(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = 650, 600
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            bishop_projected("queen", self, game_controller, -1, -1) #southwest
            bishop_projected("queen", self, game_controller, -1, 1) #northwest
            bishop_projected("queen", self, game_controller, 1, -1) #southeast
            bishop_projected("queen", self, game_controller, 1, 1) #northeast
            rook_projected("rook", self, game_controller, -1, 0) #west
            rook_projected("rook", self, game_controller, 1, 0) #east
            rook_projected("rook", self, game_controller, 0, 1) #north
            rook_projected("rook", self, game_controller, 0, -1) #south
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_QUEEN_HIGHLIGHTED"]
            if(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_QUEEN_HIGHLIGHTED"]
            self.select = True
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            bishop_direction_spaces_available(self, game_controller, -1, -1) #southwest
            bishop_direction_spaces_available(self, game_controller, -1, 1) #northwest
            bishop_direction_spaces_available(self, game_controller, 1, -1) #southeast
            bishop_direction_spaces_available(self, game_controller, 1, 1) #northeast
            rook_direction_spaces_available(self, game_controller, -1, 0) #west
            rook_direction_spaces_available(self, game_controller, 1, 0) #east
            rook_direction_spaces_available(self, game_controller, 0, 1) #north
            rook_direction_spaces_available(self, game_controller, 0, -1) #south
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_QUEEN"]
            if(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_QUEEN"]
            self.select = False

class PlayKing(ChessPiece, pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, pos, PLAY_SPRITES, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_KING"]
            PlayKing.white_king_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_KING"]
            PlayKing.black_king_list.append(self)
        self.left_castle_ability = False
        self.right_castle_ability = False
        self.castled = False
        super().__init__(pos, PLAY_SPRITES, self.image, col)
    def update(self):
        for grid in Grid.grid_list:
            if self.rect.colliderect(grid):
                self.coordinate = grid.coordinate
    def castle_check(self, game_controller):
        if(self.castled == False and game_controller.color_in_check != self.color):
            if self.color == "white":
                for white_rook in PlayRook.white_rook_list:
                    if white_rook.allowed_to_castle == True:
                        if(white_rook.coordinate == ['a', 1]):
                            if(Grid.grid_dict['b1'].occupied == 0 and Grid.grid_dict['c1'].occupied == 0 and Grid.grid_dict['d1'].occupied == 0 \
                               and len(Grid.grid_dict['b1'].num_of_black_pieces_attacking) == 0 and len(Grid.grid_dict['c1'].num_of_black_pieces_attacking) == 0 \
                               and len(Grid.grid_dict['d1'].num_of_black_pieces_attacking) == 0):
                                self.left_castle_ability = True
                            else:
                                self.left_castle_ability = False
                        if(white_rook.coordinate == ['h', 1]):
                            if(Grid.grid_dict['f1'].occupied == 0 and Grid.grid_dict['g1'].occupied == 0 \
                               and len(Grid.grid_dict['f1'].num_of_black_pieces_attacking) == 0 and len(Grid.grid_dict['g1'].num_of_black_pieces_attacking) == 0):
                                self.right_castle_ability = True
                            else:
                                self.right_castle_ability = False
            elif self.color == "black":
                for black_rook in PlayRook.black_rook_list:
                    if black_rook.allowed_to_castle == True:
                        if(black_rook.coordinate == ['a', 8]):
                            if(Grid.grid_dict['b8'].occupied == 0 and Grid.grid_dict['c8'].occupied == 0 and Grid.grid_dict['d8'].occupied == 0 \
                               and len(Grid.grid_dict['b8'].num_of_white_pieces_attacking) == 0 and len(Grid.grid_dict['c8'].num_of_white_pieces_attacking) == 0 \
                               and len(Grid.grid_dict['d8'].num_of_white_pieces_attacking) == 0):
                                self.left_castle_ability = True
                            else:
                                self.left_castle_ability = False
                        if(black_rook.coordinate == ['h', 8]):
                            if(Grid.grid_dict['f8'].occupied == 0 and Grid.grid_dict['g8'].occupied == 0 \
                               and len(Grid.grid_dict['f8'].num_of_white_pieces_attacking) == 0 and len(Grid.grid_dict['g8'].num_of_white_pieces_attacking) == 0):
                                self.right_castle_ability = True
                            else:
                                self.right_castle_ability = False
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KING_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KING_HIGHLIGHTED"]
        self.select = 1
    def projected(self, game_controller):
        if self.taken_off_board == False:
            for grid in Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1] and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.right_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1] and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.left_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
    def spaces_available(self, game_controller):
        if((self.color == "white" and self.coordinate == ['e', 1]) or (self.color == "black" and self.coordinate == ['e', 8])):
            self.castle_check(game_controller)
        for grid in Grid.grid_list:
            # Direct Enemy Threat refers to how many opposing color pieces are attacking square
            if self.color == "white":
                direct_enemy_threat = len(grid.num_of_black_pieces_attacking) > 0
            elif self.color == "black":
                direct_enemy_threat = len(grid.num_of_white_pieces_attacking) > 0
            # Projected Enemy Threat refers to threatening squares past the king
            projected_enemy_threat = grid.coordinate in game_controller.check_attacking_coordinates
            # If square does not have same color piece on it
            # If square is not directly threatened by opposing piece
            # If square is not in enemy piece projection OR if enemy piece in reach to be take-able
            if(grid.occupied_piece_color != self.color and direct_enemy_threat == False and \
               (projected_enemy_threat == False or grid.occupied_piece_color == self.enemy_color)):
                # King can have only one move in all directions
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and grid.coordinate[1] == self.coordinate[1]+1:
                    grid.highlight()
                # Castle
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and grid.coordinate[1] == self.coordinate[1] and \
                    self.right_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8) and \
                    self.castled == False):
                        grid.highlight()
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and grid.coordinate[1] == self.coordinate[1] and \
                    self.left_castle_ability == 1 and (self.coordinate[1] == 1 or self.coordinate[1]==8) and \
                    self.castled == False):
                        grid.highlight()
    def no_highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KING"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KING"]
        self.select = 0

class PlayEditSwitchButton(pygame.sprite.Sprite):
    def __init__(self, pos, GAME_MODE_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PLAY_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        GAME_MODE_SPRITES.add(self)
    def game_mode_button(self, game_mode):
        if game_mode == 0:
            self.image = IMAGES["SPR_PLAY_BUTTON"]
        elif game_mode == 1:
            self.image = IMAGES["SPR_STOP_BUTTON"]
        return self.image
    
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
        Grid.grid_dict["".join(map(str, (coordinate)))] = self
        self.num_of_white_pieces_attacking = []
        self.num_of_black_pieces_attacking = []
        self.en_passant_skipover = False
    def reset_board(self):
        self.no_highlight()
        self.num_of_white_pieces_attacking = []
        self.num_of_black_pieces_attacking = []
    def attack_count_reset(self):
        self.num_of_white_pieces_attacking = []
        self.num_of_black_pieces_attacking = []
    def remove_count_remove(self, coordinate):
        self.num_of_white_pieces_attacking.remove(coordinate)
        self.num_of_black_pieces_attacking.remove(coordinate)
    def attack_count_increment(self, color, attack_coord):
        if color == "white":
            self.num_of_white_pieces_attacking.append(attack_coord)
        elif color == "black":
            self.num_of_black_pieces_attacking.append(attack_coord)
    def update(self, game_controller):
        if game_controller.game_mode == game_controller.PLAY_MODE:
            def grid_occupied_by_piece():
                for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                   PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                   PlayQueen.white_queen_list, PlayKing.white_king_list,
                                   PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                                   PlayKnight.black_knight_list, PlayRook.black_rook_list,
                                   PlayQueen.black_queen_list, PlayKing.black_king_list]:
                    for piece in piece_list:
                        if self.rect.topleft == piece.rect.topleft:
                            self.occupied = True
                            if piece.color == "white":
                                self.occupied_piece_color = "white"
                            elif piece.color == "black":
                                self.occupied_piece_color = "black"
                            if(piece in PlayPawn.white_pawn_list or piece in PlayPawn.black_pawn_list):
                                self.occupied_piece = "pawn"
                            elif(piece in PlayBishop.white_bishop_list or piece in PlayBishop.black_bishop_list):
                                self.occupied_piece = "bishop"
                            elif(piece in PlayKnight.white_knight_list or piece in PlayKnight.black_knight_list):
                                self.occupied_piece = "knight"
                            elif(piece in PlayRook.white_rook_list or piece in PlayRook.black_rook_list):
                                self.occupied_piece = "rook"
                            elif(piece in PlayQueen.white_queen_list or piece in PlayQueen.black_queen_list):
                                self.occupied_piece = "queen"
                            elif(piece in PlayKing.white_king_list or piece in PlayKing.black_king_list):
                                self.occupied_piece = "king"
                            return
                else:
                    self.occupied = False
                    self.occupied_piece = ""
                    self.occupied_piece_color = ""
            grid_occupied_by_piece()
    def highlight(self):
        self.image = IMAGES["SPR_HIGHLIGHT"]
        self.highlighted = True
    def no_highlight(self):
        if(self.color == "green"):
            self.image = IMAGES["SPR_GREEN_GRID"]
        elif(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_GRID"]
        self.highlighted = False
    
class Dragging():
    def __init__(self):
        self.white_pawn = False
        self.white_bishop = False
        self.white_knight = False
        self.white_rook = False
        self.white_queen = False
        self.white_king = False
        self.black_pawn = False
        self.black_bishop = False
        self.black_knight = False
        self.black_rook = False
        self.black_queen = False
        self.black_king = False
    def dragging_all_false(self):
        self.white_pawn = False
        self.white_bishop = False
        self.white_knight = False
        self.white_rook = False
        self.white_queen = False
        self.white_king = False
        self.black_pawn = False
        self.black_bishop = False
        self.black_knight = False
        self.black_rook = False
        self.black_queen = False
        self.black_king = False
        
class Start():
    def __init__(self):
        self.blank_box = StartBlankBox()
        START_SPRITES.add(self.blank_box)
        self.white_pawn = StartPawn("white")
        START_SPRITES.add(self.white_pawn)
        self.white_bishop = StartBishop("white")
        START_SPRITES.add(self.white_bishop)
        self.white_knight = StartKnight("white")
        START_SPRITES.add(self.white_knight)        
        self.white_rook = StartRook("white")
        START_SPRITES.add(self.white_rook)        
        self.white_queen = StartQueen("white")
        START_SPRITES.add(self.white_queen)        
        self.white_king = StartKing("white")
        START_SPRITES.add(self.white_king)        
        self.black_pawn = StartPawn("black")
        START_SPRITES.add(self.black_pawn)
        self.black_bishop = StartBishop("black")
        START_SPRITES.add(self.black_bishop)
        self.black_knight = StartKnight("black")
        START_SPRITES.add(self.black_knight)        
        self.black_rook = StartRook("black")
        START_SPRITES.add(self.black_rook)        
        self.black_queen = StartQueen("black")
        START_SPRITES.add(self.black_queen)        
        self.black_king = StartKing("black")
        START_SPRITES.add(self.black_king)            
            
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'white_pawn': PlacedPawn.white_pawn_list, 'white_bishop': PlacedBishop.white_bishop_list, 
                         'white_knight': PlacedKnight.white_knight_list, 'white_rook': PlacedRook.white_rook_list,
                         'white_queen': PlacedQueen.white_queen_list, 'white_king': PlacedKing.white_king_list,
                         'black_pawn': PlacedPawn.black_pawn_list, 'black_bishop': PlacedBishop.black_bishop_list,
                         'black_knight': PlacedKnight.black_knight_list, 'black_rook': PlacedRook.black_rook_list,
                         'black_queen': PlacedQueen.black_queen_list, 'black_king': PlacedKing.black_king_list}
    get_rect_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_rect in item_list:
            item_list_in_name.append(item_rect.rect.topleft)
        get_rect_for_all_obj[item_key] = item_list_in_name
    return get_rect_for_all_obj

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

class Game_Controller():
    def __init__(self):
        self.WHOSETURN = "white"
        self.color_in_check = ""
        self.EDIT_MODE, self.PLAY_MODE = 0, 1
        self.game_mode = self.EDIT_MODE
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.check_checkmate_text = ""
    def reset_board(self):
        self.WHOSETURN = "white"
        self.color_in_check = ""
        self.game_mode = self.EDIT_MODE
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.check_checkmate_text = ""
        for spr_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                 PlayKnight.white_knight_list, PlayRook.white_rook_list,
                 PlayQueen.white_queen_list, PlayKing.white_king_list, 
                 PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                 PlayKnight.black_knight_list, PlayRook.black_rook_list,
                 PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for obj in spr_list:
                obj.kill()
        PlayPawn.white_pawn_list = []
        PlayBishop.white_bishop_list = []
        PlayKnight.white_knight_list = []
        PlayRook.white_rook_list = []
        PlayQueen.white_queen_list = []
        PlayKing.white_king_list = []
        PlayPawn.black_pawn_list = []
        PlayBishop.black_bishop_list = []
        PlayKnight.black_knight_list = []
        PlayRook.black_rook_list = []
        PlayQueen.black_queen_list = []
        PlayKing.black_king_list = []
        for grid in Grid.grid_list:
            grid.reset_board()
            grid.attack_count_reset()
    def switch_turn(self, color_turn):
        self.WHOSETURN = color_turn
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        # No highlights and ensuring that attacking squares (used by diagonal pieces) are set to 0
        for grid in Grid.grid_list:
            grid.no_highlight()
            grid.num_of_white_pieces_attacking = []
            grid.num_of_black_pieces_attacking = []
        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                           PlayQueen.white_queen_list, PlayKing.white_king_list,
                           PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                           PlayKnight.black_knight_list, PlayRook.black_rook_list,
                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for piece in piece_list:
                piece.pinned = False
                piece.disable = False
        if self.WHOSETURN == "white":
            # Since black just moved, there are no check attacking pieces from white
            if self.color_in_check == "black":
                self.color_in_check = ""
            self.projected_black_update()
            self.projected_white_update()
            # If white king is not in check, reset color_in_check, else white in check
            for white_king in PlayKing.white_king_list:
                if Grid.grid_dict["".join(map(str, (white_king.coordinate)))].num_of_black_pieces_attacking == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "white"
                    # Disable pieces if their king is in double-check
                    if len(Grid.grid_dict["".join(map(str, (white_king.coordinate)))].num_of_black_pieces_attacking) > 1:
                        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                           PlayQueen.white_queen_list]:
                            for piece in piece_list:
                                piece.disable = True
        elif self.WHOSETURN == "black":
            # Since black just moved, there are no check attacking pieces from white
            if self.color_in_check == "white":
                self.color_in_check = ""
            # Project squares for white and black pieces
            self.projected_white_update()
            self.projected_black_update()
            # If black king is not in check, reset color_in_check, else black in check
            for black_king in PlayKing.black_king_list:
                if Grid.grid_dict["".join(map(str, (black_king.coordinate)))].num_of_white_pieces_attacking == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "black"
                    # Disable pieces if their king is in double-check
                    if len(Grid.grid_dict["".join(map(str, (black_king.coordinate)))].num_of_white_pieces_attacking) > 1:
                        for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                           PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                           PlayQueen.black_queen_list]:
                            for piece in piece_list:
                                piece.disable = True
    def projected_white_update(self):
        # Project pieces attacking movements starting now
        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                           PlayKnight.white_knight_list, PlayRook.white_rook_list,
                           PlayQueen.white_queen_list, PlayKing.white_king_list]:
            for piece in piece_list:
                piece.projected(self)
    def projected_black_update(self):
        # Project pieces attacking movements starting now
        for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                           PlayKnight.black_knight_list, PlayRook.black_rook_list,
                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for piece in piece_list:
                piece.projected(self)
    def pinned_piece(self, pinned_piece_coordinate, pin_attacking_coordinates, color):
        # Iterates through all pieces to find the one that matches
        # the coordinate with the pin
        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                           PlayQueen.white_queen_list, PlayKing.white_king_list,
                           PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                           PlayKnight.black_knight_list, PlayRook.black_rook_list,
                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for piece in piece_list:
                if Grid.grid_dict["".join(map(str, (pinned_piece_coordinate)))].coordinate == piece.coordinate \
                    and piece.color == color:
                    piece.pinned_restrict(pin_attacking_coordinates)
    def king_in_check(self, attacker_piece, check_piece_coordinate, check_attacking_coordinates, color):
        self.color_in_check = color
        self.check_attacking_coordinates = check_attacking_coordinates
        self.attacker_piece = attacker_piece
                            
def main():    
    #Tk box for color
    root = tk.Tk()
    root.withdraw()
    #Global variables
    MENUON = 1
    
    #################
    # USER CAN SET BELOW PARAMETERS
    #################
    COLORKEY = [160, 160, 160]
    X_GRID_START = 48 # First board coordinate for X
    X_GRID_WIDTH = 48 # How many pixels X is separated by
    Y_GRID_START = 96 # First board coordinate for Y
    Y_GRID_HEIGHT = 48 # How many pixels Y is separated by
    
    #################
    #################
    X_GRID_END = X_GRID_START+(X_GRID_WIDTH*8)
    Y_GRID_END = Y_GRID_START+(Y_GRID_HEIGHT*8)
    XGRIDRANGE = [X_GRID_START, X_GRID_END, X_GRID_WIDTH] #1st num: begin 2nd: end 3rd: step
    YGRIDRANGE = [Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT] #1st num: begin 2nd: end 3rd: step
    
    RUNNING, DEBUG = 0, 1
    state = RUNNING
    debug_message = 0
    
    game_controller = Game_Controller()
    
    GAME_MODE_SPRITES = pygame.sprite.Group()
    GRID_SPRITES = pygame.sprite.Group()
    PLACED_SPRITES = pygame.sprite.Group()
    PLAY_SPRITES = pygame.sprite.Group()
    CLOCK = pygame.time.Clock()
    
    #Fonts
    arial_font = pygame.font.SysFont('Arial', 24)

    #Start (Menu) Objects
    START = Start()
    #DRAGGING Variables
    DRAGGING = Dragging()
    
    PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), GAME_MODE_SPRITES)

    CLEAR_BUTTON = ClearButton((SCREEN_WIDTH-115, 10))
    START_SPRITES.add(CLEAR_BUTTON)
    INFO_BUTTON = InfoButton((SCREEN_WIDTH-320, 10))
    START_SPRITES.add(INFO_BUTTON)
    RESTART_BUTTON = RestartButton((SCREEN_WIDTH-175, 10), PLAY_SPRITES)
    COLOR_BUTTON = ColorButton((SCREEN_WIDTH-195, 10))
    START_SPRITES.add(COLOR_BUTTON)
    SAVE_FILE_BUTTON = SaveFileButton((SCREEN_WIDTH-230, 10))
    START_SPRITES.add(SAVE_FILE_BUTTON)
    LOAD_FILE_BUTTON = LoadFileButton((SCREEN_WIDTH-265, 10))
    START_SPRITES.add(LOAD_FILE_BUTTON)
    #Backgrounds
    INFO_SCREEN = pygame.image.load("Sprites/infoscreen.bmp").convert()
    INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (SCREEN_WIDTH, SCREEN_HEIGHT))
    #window
    gameicon = pygame.image.load("Sprites/chessico.png")
    pygame.display.set_icon(gameicon)
    pygame.display.set_caption('Chess')
    #fonts
    coor_A_text = arial_font.render("a", 1, (0, 0, 0))
    coor_B_text = arial_font.render("b", 1, (0, 0, 0))
    coor_C_text = arial_font.render("c", 1, (0, 0, 0))
    coor_D_text = arial_font.render("d", 1, (0, 0, 0))
    coor_E_text = arial_font.render("e", 1, (0, 0, 0))
    coor_F_text = arial_font.render("f", 1, (0, 0, 0))
    coor_G_text = arial_font.render("g", 1, (0, 0, 0))
    coor_H_text = arial_font.render("h", 1, (0, 0, 0))
    coor_1_text = arial_font.render("1", 1, (0, 0, 0))
    coor_2_text = arial_font.render("2", 1, (0, 0, 0))
    coor_3_text = arial_font.render("3", 1, (0, 0, 0))
    coor_4_text= arial_font.render("4", 1, (0, 0, 0))
    coor_5_text = arial_font.render("5", 1, (0, 0, 0))
    coor_6_text = arial_font.render("6", 1, (0, 0, 0))
    coor_7_text= arial_font.render("7", 1, (0, 0, 0))
    coor_8_text = arial_font.render("8", 1, (0, 0, 0))
    
    # Creates grid setting coordinate as list with first element being letter and second being number
    for x in range(X_GRID_START, X_GRID_END, X_GRID_WIDTH): 
        for y in range(Y_GRID_START, Y_GRID_END, Y_GRID_HEIGHT): 
            grid_pos = x, y
            grid_coordinate = [chr(int((x-X_GRID_START)/X_GRID_WIDTH)+97), int((Y_GRID_END-y)/Y_GRID_HEIGHT)]
            grid = Grid(GRID_SPRITES, grid_pos, grid_coordinate)
    for grid in Grid.grid_list:
        for i in range(ord("a"), ord("h"), 2):
            for j in range(2, 9, 2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_WHITE_GRID"]
                    grid.color = "white"
        for i in range(ord("b"), ord("i"), 2):
            for j in range(1, 8, 2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_WHITE_GRID"]
                    grid.color = "white"
        for i in range(ord("a"), ord("h"), 2):
            for j in range(1, 8, 2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_GREEN_GRID"]
                    grid.color = "green"
        for i in range(ord("b"), ord("i"), 2):
            for j in range(2, 9, 2):
                if(ord(grid.coordinate[0]) == i and grid.coordinate[1] == j):
                    grid.image = IMAGES["SPR_GREEN_GRID"]
                    grid.color = "green"
                    
    # Load the starting positions of chessboard first
    load_file(PLACED_SPRITES, COLORKEY, reset=True)
        
    while True:
        CLOCK.tick(60)
        MOUSEPOS = pygame.mouse.get_pos()
        if state == RUNNING and MENUON == 1: # Initiate room
            #Start Objects
            START.white_pawn.rect.topleft = STARTPOS['white_pawn']
            START.white_bishop.rect.topleft = STARTPOS['white_bishop']
            START.white_knight.rect.topleft = STARTPOS['white_knight']
            START.white_rook.rect.topleft = STARTPOS['white_rook']
            START.white_queen.rect.topleft = STARTPOS['white_queen']
            START.white_king.rect.topleft = STARTPOS['white_king']
            START.black_pawn.rect.topleft = STARTPOS['black_pawn']
            START.black_bishop.rect.topleft = STARTPOS['black_bishop']
            START.black_knight.rect.topleft = STARTPOS['black_knight']
            START.black_rook.rect.topleft = STARTPOS['black_rook']
            START.black_queen.rect.topleft = STARTPOS['black_queen']
            START.black_king.rect.topleft = STARTPOS['black_king']
            
    
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        MENUON = 1 #Getting out of menus
                # If user wants to debug
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        debug_message = 1
                        state = DEBUG
                #DRAG (only for menu and inanimate buttons at top)
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[0] > X_GRID_END:
                    if game_controller.game_mode == game_controller.EDIT_MODE: #Checks if in Editing Mode
                        #BUTTONS
                        if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                            COLORKEY = get_color()
                        if SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            save_file(COLORKEY)
                        if LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PLACED_SPRITES, COLORKEY = load_file(PLACED_SPRITES, COLORKEY)
                        # DRAG OBJECTS
                        if START.white_pawn.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_pawn = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_pawn.rect.topleft)
                        elif START.white_bishop.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_bishop = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_bishop.rect.topleft)
                        elif START.white_knight.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_knight = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_knight.rect.topleft)
                        elif START.white_rook.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_rook = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_rook.rect.topleft)
                        elif START.white_queen.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_queen = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_queen.rect.topleft)
                        elif START.white_king.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.white_king = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.white_king.rect.topleft)
                        elif START.black_pawn.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_pawn = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_pawn.rect.topleft)                    
                        elif START.black_bishop.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_bishop = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_bishop.rect.topleft)
                        elif START.black_knight.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_knight = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_knight.rect.topleft)
                        elif START.black_rook.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_rook = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_rook.rect.topleft)
                        elif START.black_queen.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_queen = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_queen.rect.topleft)
                        elif START.black_king.rect.collidepoint(MOUSEPOS):
                            DRAGGING.dragging_all_false()
                            START = restart_start_objects(START)
                            DRAGGING.black_king = True
                            START.blank_box.flip_start_sprite(DRAGGING, START.black_king.rect.topleft)
                            
                #################
                # LEFT CLICK (PRESSED DOWN)
                #################
                
                # Placed object placed on location of mouse release
                elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                      MOUSEPOS[0] > X_GRID_START and MOUSEPOS[0] < X_GRID_END and
                      MOUSEPOS[1] > Y_GRID_START and MOUSEPOS[1] < Y_GRID_END): 
                    def dragging_to_placed_no_dups():
                        for piece_list in [PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list, 
                                           PlacedKnight.white_knight_list, PlacedRook.white_rook_list, 
                                           PlacedQueen.white_queen_list, PlacedKing.white_king_list,
                                           PlacedPawn.black_pawn_list, PlacedBishop.black_bishop_list, 
                                           PlacedKnight.black_knight_list, PlacedRook.black_rook_list, 
                                           PlacedQueen.black_queen_list, PlacedKing.black_king_list]:
                            # If there is already a piece on grid then don't create new Placed object
                            for piece in piece_list:
                                if piece.rect.topleft == snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE):
                                    return
                        if DRAGGING.white_pawn:
                            for grid in Grid.grid_list:
                                if grid.rect.topleft == snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE):
                                    if grid.coordinate[1] != 1 and grid.coordinate[1] != 8:
                                        PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                                    else:
                                        print("You are not allowed to place a pawn on rank " + str(grid.coordinate[1]))
                        elif DRAGGING.white_bishop:
                            PlacedBishop(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                        elif DRAGGING.white_knight:
                            PlacedKnight(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                        elif DRAGGING.white_rook:
                            PlacedRook(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                        elif DRAGGING.white_queen:
                            PlacedQueen(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                        elif DRAGGING.white_king:
                            if not PlacedKing.white_king_list:
                                PlacedKing(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                            else:
                                print("You can only have one white king.")
                        elif DRAGGING.black_pawn:
                            for grid in Grid.grid_list:
                                if grid.rect.topleft == snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE):
                                    if grid.coordinate[1] != 1 and grid.coordinate[1] != 8:
                                        PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                                    else:
                                        print("You are not allowed to place a pawn on rank " + str(grid.coordinate[1]))
                        elif DRAGGING.black_bishop:
                            PlacedBishop(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                        elif DRAGGING.black_knight:
                            PlacedKnight(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                        elif DRAGGING.black_rook:
                            PlacedRook(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                        elif DRAGGING.black_queen:
                            PlacedQueen(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                        elif DRAGGING.black_king:
                            if not PlacedKing.black_king_list:
                                PlacedKing(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                            else:
                                print("You can only have one black king.")
                        
                    dragging_to_placed_no_dups()
                                
                    # Moves piece
                    def move_piece_on_grid():
                        for grid in Grid.grid_list:
                            for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                               PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                               PlayQueen.white_queen_list, PlayKing.white_king_list,
                                               PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                               PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                               PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                for piece in piece_list:
                                    if (grid.rect.collidepoint(MOUSEPOS) and grid.highlighted==True and piece.select==True):
                                        # Taking a piece by checking if highlighted grid is opposite color of piece
                                        # And iterating through all pieces to check if coordinates of that grid
                                        # are the same as any of the pieces
                                        if((piece.color == "white" and grid.occupied_piece_color == "black") or
                                            (piece.color == "black" and grid.occupied_piece_color == "white")):
                                            for piece_captured_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                                                        PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                                                        PlayQueen.white_queen_list, PlayKing.white_king_list,
                                                                        PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                                                        PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                                                        PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                                for piece_captured in piece_captured_list:
                                                    if piece_captured.coordinate == grid.coordinate:
                                                        piece_captured.captured()
                                        # En Passant Capture
                                        if grid.en_passant_skipover == True:
                                            if piece in PlayPawn.white_pawn_list:
                                                for black_pawn in PlayPawn.black_pawn_list:
                                                    # Must include taken_off_board bool or else you get NoneType error
                                                    if black_pawn.taken_off_board == False:
                                                        if black_pawn.coordinate[0] == grid.coordinate[0] and \
                                                            black_pawn.coordinate[1] == 5:
                                                                black_pawn.captured()
                                            elif piece in PlayPawn.black_pawn_list:
                                                for white_pawn in PlayPawn.white_pawn_list:
                                                    # Must include taken_off_board bool or else you get NoneType error
                                                    if white_pawn.taken_off_board == False:
                                                        if white_pawn.coordinate[0] == grid.coordinate[0] and \
                                                            white_pawn.coordinate[1] == 4:
                                                                white_pawn.captured()
                                                            
                                        # Reset en passant skipover for all squares
                                        for sub_grid in Grid.grid_list:
                                            sub_grid.en_passant_skipover = False
                                            
                                        # Grid is no longer occupied by a piece
                                        for old_grid in Grid.grid_list:
                                            if old_grid.coordinate == piece.coordinate:
                                                old_grid.occupied = False
                                                piece.previous_coordinate = old_grid.coordinate
                                                
                                        # Moving piece, removing piece and grid highlights, changing Turn
                                        piece.rect.topleft = grid.rect.topleft
                                        piece.coordinate = grid.coordinate
                                        grid.occupied = True
                                        piece.no_highlight()
                                        
                                        #########
                                        # RULES AFTER MOVE
                                        #########
                                        
                                        # Enpassant Rule and Promotion Rule for Pawns
                                        if piece in PlayPawn.white_pawn_list:
                                            if piece.coordinate[1] == 8:
                                                PlayQueen(piece.rect.topleft, PLAY_SPRITES, "white")
                                                # Take white pawn off the board
                                                piece.captured()
                                            # Detects that pawn was just moved
                                            elif piece.coordinate[1] == 4 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                                                piece.previous_coordinate[1] == 2:
                                                for sub_grid in Grid.grid_list:
                                                    if sub_grid.coordinate[0] == piece.coordinate[0] and sub_grid.coordinate[1] == piece.coordinate[1]-1:
                                                        sub_grid.en_passant_skipover = True
                                                    else:
                                                        sub_grid.en_passant_skipover = False
                                            else:
                                                grid.en_passant_skipover = False
                                        elif piece in PlayPawn.black_pawn_list:
                                            if piece.coordinate[1] == 1:
                                                PlayQueen(piece.rect.topleft, PLAY_SPRITES, "black")
                                                # Take white pawn off the board
                                                piece.captured()
                                            # Detects that pawn was just moved
                                            elif piece.coordinate[1] == 5 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                                                piece.previous_coordinate[1] == 7:
                                                for sub_grid in Grid.grid_list:
                                                    if sub_grid.coordinate[0] == piece.coordinate[0] and sub_grid.coordinate[1] == piece.coordinate[1]+1:
                                                        sub_grid.en_passant_skipover = True
                                                    else:
                                                        sub_grid.en_passant_skipover = False
                                            else:
                                                grid.en_passant_skipover = False
                                        
                                        # Strips king's ability to castle again after moving once
                                        if piece in PlayKing.white_king_list:
                                            piece.castled = True
                                            for rook in PlayRook.white_rook_list:
                                                if rook.allowed_to_castle == True:
                                                    if rook.coordinate == ['a', 1] and piece.coordinate == ['c', 1]:
                                                        rook.rect.topleft = Grid.grid_dict['d1'].rect.topleft
                                                        rook.coordinate = Grid.grid_dict['d1'].coordinate
                                                        Grid.grid_dict['d1'].occupied = True
                                                        rook.allowed_to_castle = False
                                                    elif rook.coordinate == ['h', 1] and piece.coordinate == ['g', 1]:
                                                        rook.rect.topleft = Grid.grid_dict['f1'].rect.topleft
                                                        rook.coordinate = Grid.grid_dict['f1'].coordinate
                                                        Grid.grid_dict['f1'].occupied = True
                                                        rook.allowed_to_castle = False
                                        elif piece in PlayKing.black_king_list:
                                            piece.castled = True
                                            for rook in PlayRook.black_rook_list:
                                                if rook.allowed_to_castle == True:
                                                    if rook.coordinate == ['a', 8] and piece.coordinate == ['c', 8]:
                                                        rook.rect.topleft = Grid.grid_dict['d8'].rect.topleft
                                                        rook.coordinate = Grid.grid_dict['d8'].coordinate
                                                        Grid.grid_dict['d8'].occupied = True
                                                    elif rook.coordinate == ['h', 8] and piece.coordinate == ['g', 8]:
                                                        rook.rect.topleft = Grid.grid_dict['f8'].rect.topleft
                                                        rook.coordinate = Grid.grid_dict['f8'].coordinate
                                                        Grid.grid_dict['f8'].occupied = True
                                        elif piece in PlayRook.white_rook_list or PlayRook.black_rook_list:
                                            piece.allowed_to_castle = False
                                        # Update all grids to reflect the coordinates of the pieces
                                        GRID_SPRITES.update(game_controller)
                                        # Switch turns
                                        if(game_controller.WHOSETURN == "white"):
                                            print("\n BLACK TURN \n")
                                            game_controller.switch_turn("black")
                                        elif(game_controller.WHOSETURN == "black"):
                                            print("\n WHITE TURN \n")
                                            game_controller.switch_turn("white")
                                        if game_controller.color_in_check == "black":
                                            game_controller.check_checkmate_text = "Black King checked"
                                            for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                                               PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                                               PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                                for piece in piece_list:
                                                    piece.spaces_available(game_controller)
                                            def checkmate_check(game_controller):
                                                for subgrid in Grid.grid_list:
                                                    if subgrid.highlighted == True:
                                                        return
                                                game_controller.check_checkmate_text = "White wins"
                                            checkmate_check(game_controller)
                                        elif game_controller.color_in_check == "white":
                                            game_controller.check_checkmate_text = "White King checked"
                                            for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                                               PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                                               PlayQueen.white_queen_list, PlayKing.white_king_list]:
                                                for piece in piece_list:
                                                    piece.spaces_available(game_controller)
                                            def checkmate_check(game_controller):
                                                for subgrid in Grid.grid_list:
                                                    if subgrid.highlighted == True:
                                                        return
                                                game_controller.check_checkmate_text = "Black wins"
                                            checkmate_check(game_controller)
                                        else:
                                            # No checks
                                            game_controller.check_checkmate_text = ""
                                        return
                    move_piece_on_grid()

                    clicked_piece = None
                    # Selecting and unselecting white pieces
                    if game_controller.WHOSETURN == "white":
                        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                           PlayQueen.white_queen_list, PlayKing.white_king_list]:
                            for piece in piece_list:
                                # Selects piece
                                if (piece.rect.collidepoint(MOUSEPOS) and piece.select == False):
                                    clicked_piece = piece
                                else:
                                    # Unselects piece
                                    piece.no_highlight()
                                    for grid in Grid.grid_list:
                                        grid.no_highlight()
                    # Selecting and unselecting black pieces
                    elif game_controller.WHOSETURN == "black":
                        for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                           PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
                            for piece in piece_list:
                                if (piece.rect.collidepoint(MOUSEPOS) and piece.select == False):
                                    clicked_piece = piece
                                else:
                                    piece.no_highlight()
                                    for grid in Grid.grid_list:
                                        grid.no_highlight()
                    # Just do this last, since we know only one piece will be selected
                    if clicked_piece is not None:
                        clicked_piece.highlight()
                        clicked_piece.spaces_available(game_controller)
                        clicked_piece = None

                #################
                # CLICK (RELEASE)
                ################# 
                
                if game_controller.game_mode == game_controller.EDIT_MODE:
                    # Right click on obj, destroy
                    if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                        DRAGGING.dragging_all_false()
                        START = restart_start_objects(START)
                        PLACED_SPRITES = remove_placed_object(PLACED_SPRITES, MOUSEPOS)
                
                if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                    #################
                    # PLAY BUTTON
                    #################
                    if PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_controller.game_mode == game_controller.EDIT_MODE: 
                        # Makes clicking play again unclickable    
                        game_controller.game_mode = game_controller.PLAY_MODE
                        PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_controller.game_mode)
                        print("Play Mode Activated")
    
                        for placed_white_pawn in PlacedPawn.white_pawn_list:
                            PlayPawn(placed_white_pawn.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_bishop in PlacedBishop.white_bishop_list:
                            PlayBishop(placed_white_bishop.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_knight in PlacedKnight.white_knight_list:
                            PlayKnight(placed_white_knight.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_rook in PlacedRook.white_rook_list:
                            PlayRook(placed_white_rook.rect.topleft, PLAY_SPRITES, "white")
                        for placed_white_queen in PlacedQueen.white_queen_list:
                            PlayQueen(placed_white_queen.rect.topleft, PLAY_SPRITES, "white")    
                        for placed_white_king in PlacedKing.white_king_list:
                            PlayKing(placed_white_king.rect.topleft, PLAY_SPRITES, "white")
                        for placed_black_pawn in PlacedPawn.black_pawn_list:
                            PlayPawn(placed_black_pawn.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_bishop in PlacedBishop.black_bishop_list:
                            PlayBishop(placed_black_bishop.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_knight in PlacedKnight.black_knight_list:
                            PlayKnight(placed_black_knight.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_rook in PlacedRook.black_rook_list:
                            PlayRook(placed_black_rook.rect.topleft, PLAY_SPRITES, "black")
                        for placed_black_queen in PlacedQueen.black_queen_list:
                            PlayQueen(placed_black_queen.rect.topleft, PLAY_SPRITES, "black")    
                        for placed_black_king in PlacedKing.black_king_list:
                            PlayKing(placed_black_king.rect.topleft, PLAY_SPRITES, "black")
                        game_controller.WHOSETURN = "white"
                        GRID_SPRITES.update(game_controller)
                        game_controller.projected_white_update()
                        game_controller.projected_black_update()
                    #################
                    # LEFT CLICK (RELEASE) STOP BUTTON
                    #################
                    elif PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_controller.game_mode == game_controller.PLAY_MODE:
                        print("Editing Mode Activated")
                        game_controller.game_mode = game_controller.EDIT_MODE
                        PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_controller.game_mode)
                        game_controller.reset_board()
                    if RESTART_BUTTON.rect.collidepoint(MOUSEPOS):
                        pass
                    if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                        MENUON = 2
                    if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                        if game_controller.game_mode == game_controller.EDIT_MODE: #Editing mode
                            START = restart_start_objects(START)
                            # REMOVE ALL SPRITES
                            remove_all_placed()
                # MIDDLE MOUSE DEBUGGER
                if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                    for grid in Grid.grid_list:
                        if grid.rect.collidepoint(MOUSEPOS):
                            print("Coordinate: " + str(grid.coordinate) \
                                   + ", White Pieces Attacking: " + str(grid.num_of_white_pieces_attacking) \
                                   + ", Black Pieces Attacking: " + str(grid.num_of_black_pieces_attacking) \
                                   + ", Grid occupied? " + str(grid.en_passant_skipover))
                            
            ##################
            # ALL EDIT ACTIONS
            ##################
            # Replace start sprite with blank box in top menu
            if game_controller.game_mode == game_controller.EDIT_MODE:
                if DRAGGING.white_pawn:
                    START.blank_box.rect.topleft = STARTPOS['white_pawn'] # Replaces in Menu
                    START.white_pawn.rect.topleft = (MOUSEPOS[0]-(START.white_pawn.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_pawn.image.get_height()/2))
                else:
                    START.white_pawn.rect.topleft = STARTPOS['white_pawn']
                if DRAGGING.white_bishop:
                    START.blank_box.rect.topleft = STARTPOS['white_bishop'] # Replaces in Menu
                    START.white_bishop.rect.topleft = (MOUSEPOS[0]-(START.white_bishop.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_bishop.image.get_height()/2))
                else:
                    START.white_bishop.rect.topleft = STARTPOS['white_bishop']
                if DRAGGING.white_knight:
                    START.blank_box.rect.topleft = STARTPOS['white_knight'] # Replaces in Menu
                    START.white_knight.rect.topleft = (MOUSEPOS[0]-(START.white_knight.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_knight.image.get_height()/2))
                else:
                    START.white_knight.rect.topleft = STARTPOS['white_knight']    
                if DRAGGING.white_rook:
                    START.blank_box.rect.topleft = STARTPOS['white_rook'] # Replaces in Menu
                    START.white_rook.rect.topleft = (MOUSEPOS[0]-(START.white_rook.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_rook.image.get_height()/2))
                else:
                    START.white_rook.rect.topleft = STARTPOS['white_rook']                       
                if DRAGGING.white_queen:
                    START.blank_box.rect.topleft = STARTPOS['white_queen'] # Replaces in Menu
                    START.white_queen.rect.topleft = (MOUSEPOS[0]-(START.white_queen.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_queen.image.get_height()/2))
                else:
                    START.white_queen.rect.topleft = STARTPOS['white_queen']                            
                if DRAGGING.white_king:
                    START.blank_box.rect.topleft = STARTPOS['white_king'] # Replaces in Menu
                    START.white_king.rect.topleft = (MOUSEPOS[0]-(START.white_king.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.white_king.image.get_height()/2))
                else:
                    START.white_king.rect.topleft = STARTPOS['white_king']                     
                if DRAGGING.black_pawn:
                    START.blank_box.rect.topleft = STARTPOS['black_pawn'] # Replaces in Menu
                    START.black_pawn.rect.topleft = (MOUSEPOS[0]-(START.black_pawn.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_pawn.image.get_height()/2))
                else:
                    START.black_pawn.rect.topleft = STARTPOS['black_pawn']
                if DRAGGING.black_bishop:
                    START.blank_box.rect.topleft = STARTPOS['black_bishop'] # Replaces in Menu
                    START.black_bishop.rect.topleft = (MOUSEPOS[0]-(START.black_bishop.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_bishop.image.get_height()/2))
                else:
                    START.black_bishop.rect.topleft = STARTPOS['black_bishop']
                if DRAGGING.black_knight:
                    START.blank_box.rect.topleft = STARTPOS['black_knight'] # Replaces in Menu
                    START.black_knight.rect.topleft = (MOUSEPOS[0]-(START.black_knight.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_knight.image.get_height()/2))
                else:
                    START.black_knight.rect.topleft = STARTPOS['black_knight']    
                if DRAGGING.black_rook:
                    START.blank_box.rect.topleft = STARTPOS['black_rook'] # Replaces in Menu
                    START.black_rook.rect.topleft = (MOUSEPOS[0]-(START.black_rook.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_rook.image.get_height()/2))
                else:
                    START.black_rook.rect.topleft = STARTPOS['black_rook']                       
                if DRAGGING.black_queen:
                    START.blank_box.rect.topleft = STARTPOS['black_queen'] # Replaces in Menu
                    START.black_queen.rect.topleft = (MOUSEPOS[0]-(START.black_queen.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_queen.image.get_height()/2))
                else:
                    START.black_queen.rect.topleft = STARTPOS['black_queen']                            
                if DRAGGING.black_king:
                    START.blank_box.rect.topleft = STARTPOS['black_king'] # Replaces in Menu
                    START.black_king.rect.topleft = (MOUSEPOS[0]-(START.black_king.image.get_width()/2),
                                                   MOUSEPOS[1]-(START.black_king.image.get_height()/2))
                else:
                    START.black_king.rect.topleft = STARTPOS['black_king']                        
        
            ##################
            # IN-GAME ACTIONS
            ##################
            if game_controller.game_mode == game_controller.PLAY_MODE:
                pass
            #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
            
            #Update all sprites
            #START_SPRITES.update()
            PLACED_SPRITES.update(Grid.grid_list)
            PLAY_SPRITES.update()
            SCREEN.fill(COLORKEY)
            GAME_MODE_SPRITES.draw(SCREEN)
            GRID_SPRITES.draw(SCREEN)
            GRID_SPRITES.update(game_controller)
            if(game_controller.game_mode == game_controller.EDIT_MODE): #Only draw placed sprites in editing mode
                START_SPRITES.draw(SCREEN)
                PLACED_SPRITES.draw(SCREEN)    
            elif(game_controller.game_mode == game_controller.PLAY_MODE): #Only draw play sprites in play mode
                PLAY_SPRITES.draw(SCREEN)
            # Board Coordinates Drawing
            coor_letter_text_list = [coor_A_text, coor_B_text, coor_C_text, coor_D_text, coor_E_text, coor_F_text, coor_G_text, coor_H_text]
            for text in range(0,len(coor_letter_text_list)):
                SCREEN.blit(coor_letter_text_list[text], (X_GRID_START+X_GRID_WIDTH/3+(X_GRID_WIDTH*text), Y_GRID_START-(Y_GRID_HEIGHT*0.75)))
                SCREEN.blit(coor_letter_text_list[text], (X_GRID_START+X_GRID_WIDTH/3+(X_GRID_WIDTH*text), Y_GRID_END+(Y_GRID_HEIGHT*0.25)))
            coor_number_text_list = [coor_8_text, coor_7_text, coor_6_text, coor_5_text, coor_4_text, coor_3_text, coor_2_text, coor_1_text]
            for text in range(0,len(coor_number_text_list)):
                SCREEN.blit(coor_number_text_list[text], (X_GRID_START-X_GRID_WIDTH/2, Y_GRID_START+Y_GRID_HEIGHT/4+(Y_GRID_HEIGHT*text)))
                SCREEN.blit(coor_number_text_list[text], (X_GRID_END+X_GRID_WIDTH/3, Y_GRID_START+Y_GRID_HEIGHT/4+(Y_GRID_HEIGHT*text)))
            if(game_controller.game_mode == game_controller.PLAY_MODE):
                check_checkmate_text_render = arial_font.render(game_controller.check_checkmate_text, 1, (0, 0, 0))
                if game_controller.WHOSETURN == "white":
                    whose_turn_text = arial_font.render("White's move to turn", 1, (0, 0, 0))
                elif game_controller.WHOSETURN == "black":
                    whose_turn_text = arial_font.render("Black's move to turn", 1, (0, 0, 0))
                SCREEN.blit(whose_turn_text, (X_GRID_END+X_GRID_WIDTH, SCREEN_HEIGHT/2))
                SCREEN.blit(check_checkmate_text_render, (X_GRID_END+X_GRID_WIDTH, 200))
            pygame.display.update()
        elif state == DEBUG:
            if debug_message == 1:
                print("Entering debug mode")
                debug_message = 0
                # USE BREAKPOINT HERE
                print("Use breakpoint here")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        state = RUNNING
                        print("back to Running")
if __name__ == "__main__":
    main()