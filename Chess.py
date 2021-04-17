"""
Chess created by Brad Wyatt
Python 3
Credits:
Scroll bar for moves based on https://www.reddit.com/r/pygame/comments/94czzs/text_boxes_with_scrollbars_and_changing_buttons/
PLEASE do new console after each time exiting the program

Round 2 Thoughts:
Replace the scroll bar logic with the following. Create a list of SelectedMoveRectangle(s) from parent class. Self.text should be the move. The text blitted to the screen should take from the rectangle with the same X. When scrolling, the rectangle Y will change, and when it's out of boundary of 19 moves then be invisible and unclickable.
Prior move color
Play back one move
Undo move
Highlight move (that we're on, or examining) on the right side. I will probably want to get move number on left side and white move, and then black move several spaces from the end of the width. Will need to work on body_text Text_Controller stuff
Pause mode- The board has the Placed pieces, and you can go back and forward in your analysis. But you can't bring in new pieces
I'd really like to get rid of hardcoding values, like pos_load_file for resetting board
Sounds
Making sure that we are doing promotion correctly
Perhaps using a direction arrow (like babaschess) to determine which piece could take the other piece. This could get confusing when flipping board though
                                                                                                         
Testing (these are all in logs or PGN_Incorrect_Notation folder):
Found a bug in castling there's a screenshot of it. This was before figuring out how to do moves, so ignore until you find again
Found a bug with two queens having a spot available and then move notation didnt specify which one
Ne2 illegal

Features To-Do (short-term):
Instead of using rect to place pieces on the grid, use coordinates (this will help when we flip the board too)
Save states (IS THIS REALLY NEEDED?), be able to undo and redo moves
Previous move highlighted different color
Record moves correctly (keep in mind which direction the other piece is coming from)
If no king then don't start game

Buttons to Implement:
Previous Move
Next Move
Beginning of Game
Latest move
Game Properties (use Babaschess for model)
Flip Board

Features To-Do (long-term):
Create function where given coordinates, return X, Y of square (for loaded_file func)
Save positions rather than restarting when pressing stop button
Customized Turns for black and white
Choose piece for Promotion

Already Solved? :
Notation moves for moves past 10
"""
from start_objects import *
from placed_objects import *
from load_images_sounds import *
from menu_buttons import *
import random
import re
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
import logging
import logging.handlers
import pandas as pd
import numpy as np

#############
# Logging
#############

today = datetime.datetime.today()
log_file_name = "{0}.log".format(today.strftime("%Y-%m-%d %H%M%S"))
log_file = os.path.join("C:/Users/Brad/Documents/GitHub/Chess-WORK-IN-PROGRESS-/logs/", log_file_name)

log = logging.getLogger("log_guy")
log.handlers = []
log.setLevel(logging.INFO)

# Handlers for logging errors
file_handler = logging.FileHandler(log_file)
log_file_formatter = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
file_handler.setFormatter(log_file_formatter)
file_handler.setLevel(logging.DEBUG)
log.addHandler(file_handler)

console_handler = logging.StreamHandler()
log_console_handler = logging.Formatter("%(message)s")
console_handler.setFormatter(log_console_handler)
console_handler.setLevel(logging.DEBUG)
log.addHandler(console_handler)

#############
# Functions and Grouping
#############

#Grouping Images and Sounds
STARTPOS = {'white_pawn': (480, 390), 'white_bishop':(480, 340), 'white_knight':(480, 290),
             'white_rook':(480, 240), 'white_queen':(480, 190), 'white_king':(480, 140),
             'black_pawn': (540, 390), 'black_bishop':(540, 340), 'black_knight':(540, 290),
             'black_rook':(540, 240), 'black_queen':(540, 190), 'black_king':(540, 140)}

move_bg_image = pygame.image.load('Sprites/move_bg.png')
START_SPRITES = pygame.sprite.Group()
RECTANGLE_SPRITES = pygame.sprite.Group()


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

def pos_load_file(PLACED_SPRITES, colorkey, reset=False):
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
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return PLACED_SPRITES, colorkey
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
    
    log.info("Removed all sprites. Now creating lists for loaded level.")
    
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
    
    log.info("Positioning Loaded Successfully")
    return PLACED_SPRITES, colorkey

def pos_save_file(colorkey):
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
            log.info("File Saved Successfully.")
        else:
            log.info("Error! Need king to save!")
    except IOError:
        log.info("Save File Error, please restart game and try again.")

def quit():
    log.info('Thanks for playing')
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
        self.coordinate_history = {}
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
    def captured(self, x, y):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = x, y
    def promoted(self):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = -100, -100
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
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            elif(self.color == "black"):
                for grid in Grid.grid_list:
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
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
                        int(grid.coordinate[1]) == int(self.coordinate[1])+movement): 
                        if grid.occupied == False:
                            if game_controller.color_in_check == self.color:
                                if self.pinned == True:
                                    self.disable = True
                                    return
                                elif grid.coordinate in game_controller.check_attacking_coordinates:
                                    grid.highlight()
                            elif self.pinned == False:
                                grid.highlight()
                            elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                                grid.highlight()
                    # Move two spaces up
                    if (int(self.coordinate[1]) == initial_space and grid.coordinate[0] == self.coordinate[0] and \
                        int(grid.coordinate[1]) == hop_space and grid.occupied == False):
                        # If space before hop space is occupied by a piece
                        if Grid.grid_dict[grid.coordinate[0] + str(hop_space-movement)].occupied == False:
                            if grid.occupied == False:
                                if game_controller.color_in_check == self.color:
                                    if self.pinned == True:
                                        self.disable = True
                                        return
                                    elif grid.coordinate in game_controller.check_attacking_coordinates:
                                        grid.highlight()
                                elif self.pinned == False:
                                    grid.highlight()
                                elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                                    grid.highlight()
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
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
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
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
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
                    grid.en_passant_skipover == True):
                        if self.pinned == False:
                            grid.highlight()
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
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
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and int(grid.coordinate[1]) == int(self.coordinate[1])+y:
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("knight", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            knight_proj_direction(-1, -2)
            knight_proj_direction(-1, 2)
            knight_proj_direction(1, -2)
            knight_proj_direction(1, 2)
            knight_proj_direction(-2, -1)
            knight_proj_direction(-2, 1)
            knight_proj_direction(2, -1)
            knight_proj_direction(2, 1)
    def captured(self, x, y):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = x, y
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
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and int(grid.coordinate[1]) == int(self.coordinate[1])+y \
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
            if(ord(grid.coordinate[0]) == ord(piece.coordinate[0])+(x*i) and int(grid.coordinate[1]) == int(piece.coordinate[1])+(y*i)):
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
                    #log.info("King is pinned on coordinate " + str(grid.coordinate))
                    game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
                    return
                # 1 Piece in way which is King
                # This is check, we will iterate one more time to cover the next square king is not allowed to go to
                elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
                    #log.info("Check for coordinate " + str(grid.coordinate))
                    # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
                    # Corner case where king is on the edge of the board
                    if((grid.coordinate[0] == 'a' and x == -1) or (grid.coordinate[0] == 'h' and x == 1) or \
                       (int(grid.coordinate[1]) == 8 and y == 1) or (int(grid.coordinate[1]) == 1 and y == -1)):
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        return

def bishop_direction_spaces_available(bishop, game_controller, x, y):
    for i in range(1,8):
        for grid in Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(bishop.coordinate[0])+(x*i) \
                   and int(grid.coordinate[1]) == int(bishop.coordinate[1])+(y*i):
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
    def captured(self, x, y):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = x, y
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
               and int(grid.coordinate[1]) == int(piece.coordinate[1])+(y*i)):
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
                    #log.info("King is pinned on coordinate " + str(grid.coordinate))
                    game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
                    return
                # 1 Piece in way which is King
                # This is check, we will iterate one more time to cover the next square king is not allowed to go to
                elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
                    #log.info("Check for coordinate " + str(grid.coordinate))
                    # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
                    if((grid.coordinate[0] == 'a' and y == 0) or (grid.coordinate[0] == 'h' and y == 0) or \
                       (int(grid.coordinate[1]) == 1 and x == 0) or (int(grid.coordinate[1]) == 8 and x == 0)):
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        return
    return

def rook_direction_spaces_available(rook, game_controller, x, y):
    for i in range(1,8):
        for grid in Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(rook.coordinate[0])+(x*i) and int(grid.coordinate[1]) == int(rook.coordinate[1])+(y*i):
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
    def captured(self, x, y):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = x, y
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
    def captured(self, x, y):
        self.taken_off_board = True
        self.coordinate = None
        self.rect.topleft = x, y
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
                        if(white_rook.coordinate == 'a1'):
                            if(Grid.grid_dict['b1'].occupied == 0 and Grid.grid_dict['c1'].occupied == 0 and Grid.grid_dict['d1'].occupied == 0 \
                               and len(Grid.grid_dict['b1'].list_of_black_pieces_attacking) == 0 and len(Grid.grid_dict['c1'].list_of_black_pieces_attacking) == 0 \
                               and len(Grid.grid_dict['d1'].list_of_black_pieces_attacking) == 0):
                                self.left_castle_ability = True
                            else:
                                self.left_castle_ability = False
                        if(white_rook.coordinate == 'h1'):
                            if(Grid.grid_dict['f1'].occupied == 0 and Grid.grid_dict['g1'].occupied == 0 \
                               and len(Grid.grid_dict['f1'].list_of_black_pieces_attacking) == 0 and len(Grid.grid_dict['g1'].list_of_black_pieces_attacking) == 0):
                                self.right_castle_ability = True
                            else:
                                self.right_castle_ability = False
            elif self.color == "black":
                for black_rook in PlayRook.black_rook_list:
                    if black_rook.allowed_to_castle == True:
                        if(black_rook.coordinate == 'a8'):
                            if(Grid.grid_dict['b8'].occupied == 0 and Grid.grid_dict['c8'].occupied == 0 and Grid.grid_dict['d8'].occupied == 0 \
                               and len(Grid.grid_dict['b8'].list_of_white_pieces_attacking) == 0 and len(Grid.grid_dict['c8'].list_of_white_pieces_attacking) == 0 \
                               and len(Grid.grid_dict['d8'].list_of_white_pieces_attacking) == 0):
                                self.left_castle_ability = True
                            else:
                                self.left_castle_ability = False
                        if(black_rook.coordinate == 'h8'):
                            if(Grid.grid_dict['f8'].occupied == 0 and Grid.grid_dict['g8'].occupied == 0 \
                               and len(Grid.grid_dict['f8'].list_of_white_pieces_attacking) == 0 and len(Grid.grid_dict['g8'].list_of_white_pieces_attacking) == 0):
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
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.right_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.left_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
    def spaces_available(self, game_controller):
        if((self.color == "white" and self.coordinate == 'e1') or (self.color == "black" and self.coordinate == 'e8')):
            self.castle_check(game_controller)
        for grid in Grid.grid_list:
            # Direct Enemy Threat refers to how many opposing color pieces are attacking square
            if self.color == "white":
                direct_enemy_threat = len(grid.list_of_black_pieces_attacking) > 0
            elif self.color == "black":
                direct_enemy_threat = len(grid.list_of_white_pieces_attacking) > 0
            # Projected Enemy Threat refers to threatening squares past the king
            projected_enemy_threat = grid.coordinate in game_controller.check_attacking_coordinates
            # If square does not have same color piece on it
            # If square is not directly threatened by opposing piece
            # If square is not in enemy piece projection OR if enemy piece in reach to be take-able
            if(grid.occupied_piece_color != self.color and direct_enemy_threat == False and \
               (projected_enemy_threat == False or grid.occupied_piece_color == self.enemy_color)):
                # King can have only one move in all directions
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.highlight()
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight()
                # Castle
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    self.right_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8) and \
                    self.castled == False):
                        grid.highlight()
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    self.left_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8) and \
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
        Grid.grid_dict[self.coordinate] = self
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
        self.en_passant_skipover = False
        self.prior_move_color = False
    def reset_board(self):
        self.no_highlight()
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
    def attack_count_reset(self):
        self.list_of_white_pieces_attacking = []
        self.list_of_black_pieces_attacking = []
    def remove_count_remove(self, coordinate):
        self.list_of_white_pieces_attacking.remove(coordinate)
        self.list_of_black_pieces_attacking.remove(coordinate)
    def attack_count_increment(self, color, attack_coord):
        if color == "white":
            self.list_of_white_pieces_attacking.append(attack_coord)
        elif color == "black":
            self.list_of_black_pieces_attacking.append(attack_coord)
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
        if(self.prior_move_color == True):
            self.image = IMAGES["SPR_PRIOR_MOVE_GRID"]
        elif(self.color == "green"):
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
    def drag_piece(self, piece):
        self.dragging_all_false()
        if piece == "white_pawn":
            self.white_pawn = True
        elif piece == "white_bishop":
            self.white_bishop = True
        elif piece == "white_knight":
            self.white_knight = True
        elif piece == "white_rook":
            self.white_rook = True
        elif piece == "white_queen":
            self.white_queen = True
        elif piece == "white_king":
            self.white_king = True
        elif piece == "black_pawn":
            self.black_pawn = True
        elif piece == "black_bishop":
            self.black_bishop = True
        elif piece == "black_knight":
            self.black_knight = True
        elif piece == "black_rook":
            self.black_rook = True
        elif piece == "black_queen":
            self.black_queen = True
        elif piece == "black_king":
            self.black_king = True
        
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
    
class PGN_Writer():
    def __init__(self):
        self.Event = ""
        self.Site = ""
        self.Date = ""
        self.Round = ""
        self.White = ""
        self.Black = ""
        self.Result = ""
        self.WhiteElo = ""
        self.BlackElo = ""
        self.ECO = ""
    def write_moves(self, df_moves, result_abb):
        try:
            df = df_moves.copy()
            save_file_prompt = asksaveasfilename(defaultextension=".pgn")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                pgn_output = ""
                pgn_output += '[Event "' + self.Event + '"]\n'
                pgn_output += '[Site "' + self.Site + '"]\n'
                pgn_output += '[Date "' + self.Date + '"]\n'
                pgn_output += '[Round "' + self.Round + '"]\n'
                pgn_output += '[White "' + self.White + '"]\n'
                pgn_output += '[Black "' + self.Black + '"]\n'
                pgn_output += '[Result "' + self.Result + '"]\n'
                pgn_output += '[ECO "' + self.ECO + '"]\n'
                pgn_output += '[BlackElo "' + self.BlackElo + '"]\n\n'
                for i in df.index:
                    # If black hasn't moved then shorten the pgn output so it doesn't give two spaces
                    if str(df.loc[i, 'black_move']) == "":
                        pgn_output += str(i) + ". " + str(df.loc[i, 'white_move']) + " "
                    else:
                        pgn_output += str(i) + ". " + str(df.loc[i, 'white_move']) + " " + str(df.loc[i, 'black_move']) + " "
                pgn_output += result_abb
                save_file_name.write(pgn_output)
                save_file_name.close()
                log.info("File Saved Successfully.")
            else:
                log.info("Error! Need king to save!")
        except IOError:
            log.info("Save File Error, please restart game and try again.")

class Game_Controller():
    def __init__(self):
        self.WHOSETURN = "white"
        self.color_in_check = ""
        self.EDIT_MODE, self.PLAY_MODE = 0, 1
        self.game_mode = self.EDIT_MODE
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.black_captured_x = 50
        self.white_captured_x = 50
        self.move_counter = 1
        self.df_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_moves.index = np.arange(1, len(self.df_moves)+1) # Index at 1 rather than 0 because chess starts that way
        self.df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_prior_moves.index = np.arange(1, len(self.df_prior_moves)+1)
        self.result_abb = "*"
    def reset_board(self):
        self.WHOSETURN = "white"
        self.color_in_check = ""
        self.game_mode = self.EDIT_MODE
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.black_captured_x = 50
        self.white_captured_x = 50
        self.move_counter = 1
        self.df_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_moves.index = np.arange(1, len(self.df_moves)+1) # Index at 1 rather than 0 because chess starts that way
        self.df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_prior_moves.index = np.arange(1, len(self.df_prior_moves)+1)
        self.result_abb = "*"
        Text_Controller.check_checkmate_text = ""
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
            grid.list_of_white_pieces_attacking = []
            grid.list_of_black_pieces_attacking = []
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
                if Grid.grid_dict[white_king.coordinate].list_of_black_pieces_attacking == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "white"
                    # Disable pieces if their king is in double-check
                    if len(Grid.grid_dict[white_king.coordinate].list_of_black_pieces_attacking) > 1:
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
                if Grid.grid_dict[black_king.coordinate].list_of_white_pieces_attacking == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "black"
                    # Disable pieces if their king is in double-check
                    if len(Grid.grid_dict[black_king.coordinate].list_of_white_pieces_attacking) > 1:
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
                if Grid.grid_dict[pinned_piece_coordinate].coordinate == piece.coordinate \
                    and piece.color == color:
                    piece.pinned_restrict(pin_attacking_coordinates)
    def king_in_check(self, attacker_piece, check_piece_coordinate, check_attacking_coordinates, color):
        self.color_in_check = color
        self.check_attacking_coordinates = check_attacking_coordinates
        self.attacker_piece = attacker_piece


class Text_Controller():
    check_checkmate_text = ""
    body_text = ""
    max_moves_that_fits_pane = 19
    # Example Games
    """
    body_text = "1. e4 c6 2. c4 d5 3. exd5 cxd5 4. cxd5 Nf6 5. Nc3 Nxd5 6. d4 Nc6 7. Nf3 e6 8. Bd3 Be7 \
        9. O-O O-O 10. Re1 Bf6 11. Be4 Nce7 12. a3 Rb8 13. h4 b6 14. Qd3 g6 15. h5 Bb7 16. Bh6 Re8 \
        17. Rac1 Nxc3 18. bxc3 Bxe4 19. Rxe4 Nf5 20. Bf4 Rc8 21. hxg6 hxg6 22. Be5 Bxe5 \
        23. Nxe5 Qg5 24. Rd1 Kg7 25. Qf3 Rh8 "
    body_text = "1.e4 c5 2.Nf3 d6 3.Bb5+ Nc6 4.O-O Bd7 5.Re1 Nf6 6.c3 a6 7.Ba4 b5 8.Bc2 e5 9.h3 Be7 10.d4 O-O 11.d5 Na5 12.Nbd2 g6 13.b4 Nb7 14.a4 Qc7 15.Nf1 Nh5 16.Bh6 Ng7 17.Ng3 f6 18.Qd2 Rfc8 19.Ra2 a5 20.Rea1 axb4 21.cxb4 bxa4 22.Bxa4 Bxa4 23.Rxa4 Rxa4 24.Rxa4 cxb4 25.Rxb4 Nc5 26.Be3 Qd7 27.Rc4 Rb8 28.Bxc5 dxc5 29.Nf1 Ne8 30.Qc2 Qb5 31.N3d2 Qb2 32.Qa4 Kf7 33.Rc2 Qb4 34.Qd7 Nd6 35.Ne3 Kf8 36.Kh2 Rd8 37.Qg4 Qd4 38.Nec4 f5 39.Qe2 Nxe4 40.Nxe4 Qxe4 41.Qxe4 fxe4 42.Rd2 Bg5 43.Rd1 Rb8 44.Kg1 Rb4 45.Nxe5 c4 46.Nc6 Rb2 47.Nd4 c3 48.Re1 c2 49.Nxc2 Rxc2 50.Rxe4 Rd2 51.g3 Be7 52.Rf4+ Kg7 53.Kg2 Bc5 54.h4 Rxd5 55.Rc4 Kf6 56.Rc2 Kf5 57.Ra2 Bb4 58.Rb2 Bc3 59.Rc2 Rd3 60.Kf1 Bd4 61.Kg2 Rb3 62.Rc7 h6 63.Rf7+ Ke6 64.Rf4 Bb6 65.Rf8 Rb2 66.Rf3 g5 67.hxg5 hxg5 68.Rf8 Bc5 69.Rf3 Ra2 70.Kg1 Ra7 71.Kg2 Ke5 72.Kh3 Ra4 73.Kg2 Ra2 74.Rf7 Ke4 75.Rf3 Bd4 76.Rf8 Kd3 77.Rf5 Ke4 78.Rxg5 Rxf2+ 79.Kh3 Rf8 80.Rg4+ Ke3 81.Rf4 Rg8 82.Rg4 Bg7 83.Kg2 Kd3 84.Rg6 Ke4 85.Rg5 Kd4 86.Kg1 Kd3 87.Kg2 Ke4 88.Rg4+ Kf5 89.Rf4+ Kg5 90.Kf3 Ra8 91.Rg4+ Kf6 92.Rf4+ Ke6 93.Kg2 Be5 94.Rf3 Rh8 95.Kg1 Kd5 96.Kg2 Ke4 97.Rb3 Rc8 98.Kh3 Rc2 99.Kg4 Rg2 100.Ra3 Rg1 101.Rb3 Bd6 102.Rc3 Kd4 103.Rb3 Bc5 104.Rf3 Bb4 "
    """
    scroll = 0
    def latest_scroll(body_text, scroll):
        if body_text == "":
            return 0
        else:
            final_move = int(re.findall(re.compile(r'\d{1,3}\.'), body_text)[-1].replace(".",""))
            # 19 moves at a time
            return final_move-Text_Controller.max_moves_that_fits_pane

def draw_text(surface, text, color, rectangle, scroll, my_font):
    y = rectangle[1]
    line_spacing = 2
    line_text_black = ""

    # get the height of the font
    font_height = my_font.size("Tg")[1]
    while text:
        
        # determine if the row of text will be outside our area
        if y + font_height > rectangle[1] + rectangle[3]:
            break
        
        # determine maximum width of line purely based on the starting move digits on white's turn
        
        for i in range(1, len(text)):
            if bool(re.findall(re.compile(r'\d{3}\.'), text[i:i+4])) == True:
                break
            elif bool(re.findall(re.compile(r'\d{2}\.'), text[i:i+3])) == True:
                if(text[i-1].isdigit()):
                    continue
                else:
                    break
            elif bool(re.findall(re.compile(r'\d\.'), text[i:i+2])) == True:
                if(text[i-1].isdigit()):
                    continue
                else:
                    break

        if scroll > 0:
            scroll -= 1
        else:
            # render the line and blit it to the surface
            line_text_list = text[:i].split()
            if len(line_text_list) == 3:
                # Move number, space, white move, calculated space, black move
                line_text_white = line_text_list[0] + " " + line_text_list[1] + " "
                line_text_black = line_text_list[2]
            else:
                # Move number, space, white move
                line_text_white = text[:i]
            line_text_white_split = line_text_white.split()
            if line_text_white_split:
                # If the move number is only a single digit (ie "5.") then include a space at the beginning so that the rest of moves can align
                if len(line_text_white_split[0]) == 2:
                    line_text_white = "  " + line_text_white_split[0] + " " + line_text_white_split[1]
                else:
                    line_text_white = line_text_white_split[0] + " " + line_text_white_split[1]
            image_white = my_font.render(line_text_white, True, color)
            
            surface.blit(image_white, (rectangle[0], y))
            if line_text_black:
                image_black = my_font.render(line_text_black, True, color)
                surface.blit(image_black, (rectangle[0]+100, y))
                # Move to next line
                y += font_height + line_spacing
                # Reset line text black since we moved to next line (and white is now to move)
                line_text_black = ""

        # remove the text we just blitted
        text = text[i:]
        
    return text
                
#draw the text window at coordinates x,y
def draw_moves(my_font, body_text, scroll, game_controller):
    SCREEN.blit(move_bg_image, (675,70))
    spacing_length = 21
    if len(game_controller.df_moves) >= 1:
        # White was latest move
        #print("SCROLL: " + str(scroll))
        
        # Creating move notation rectangles if they haven't been created before for the respective move
        # If the last move is not in the dictionary, then add it
        if len(game_controller.df_moves) not in SelectedMoveRectangle.rectangle_dict:
            SelectedMoveRectangle.rectangle_dict[len(game_controller.df_moves)] = []
        # If last move is in dictionary but has no white move, and rectangle_dict key for that move is length 0
        if game_controller.df_moves.loc[len(game_controller.df_moves), 'white_move'] != '' and len(SelectedMoveRectangle.rectangle_dict[len(game_controller.df_moves)]) == 0:
            SelectedMoveRectangle(len(game_controller.df_moves), SCREEN_WIDTH-206, 89+spacing_length*len(game_controller.df_moves), 20, 56, RECTANGLE_SPRITES)
        # If last move is in dictionary but has no black move, and rectangle_dict key for that move is length 1
        if game_controller.df_moves.loc[len(game_controller.df_moves), 'black_move'] != '' and len(SelectedMoveRectangle.rectangle_dict[len(game_controller.df_moves)]) == 1:
            SelectedMoveRectangle(len(game_controller.df_moves), SCREEN_WIDTH-127, 89+spacing_length*len(game_controller.df_moves), 20, 56, RECTANGLE_SPRITES)
        test_text = my_font.render("yayyyyy", True, [255,255,255])
        SCREEN.blit(test_text, (SCREEN_WIDTH-210, 89+spacing_length*len(game_controller.df_moves)))
    #draw the floating header
    #text = my_font.render(header_text, True, [255,255,255])
    #SCREEN.blit(text, [100, 20])

    #draw the main text
    draw_text(SCREEN, body_text, [255,255,255], [SCREEN_WIDTH-225, 110, 200, 400], scroll, my_font)



def main():
    try:
        #Tk box for color
        root = tk.Tk()
        root.withdraw()
        #Global variables
        MENUON = 1
        Text_Controller.scroll = Text_Controller.latest_scroll(Text_Controller.body_text, Text_Controller.scroll)
        #header_text = "This is the header text which will not scroll"
        
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
        move_notation_font = pygame.font.SysFont('Arial', 16)
    
        #Start (Menu) Objects
        START = Start()
        #DRAGGING Variables
        DRAGGING = Dragging()
        
        PGN_WRITER = PGN_Writer()
        
        PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton((SCREEN_WIDTH-50, 8), GAME_MODE_SPRITES)
        FLIP_BOARD_BUTTON = FlipBoardButton((SCREEN_WIDTH-480, 10))
        START_SPRITES.add(FLIP_BOARD_BUTTON)
        GAME_PROPERTIES_BUTTON = GamePropertiesButton((SCREEN_WIDTH-430, 10))
        START_SPRITES.add(GAME_PROPERTIES_BUTTON)
        INFO_BUTTON = InfoButton((SCREEN_WIDTH-360, 10))
        START_SPRITES.add(INFO_BUTTON)
        POS_LOAD_FILE_BUTTON = PosLoadFileButton((SCREEN_WIDTH-305, 10))
        START_SPRITES.add(POS_LOAD_FILE_BUTTON)
        POS_SAVE_FILE_BUTTON = PosSaveFileButton((SCREEN_WIDTH-270, 10))
        START_SPRITES.add(POS_SAVE_FILE_BUTTON)
        PGN_LOAD_FILE_BUTTON = PGNLoadFileButton((SCREEN_WIDTH-50, 100))
        PGN_SAVE_FILE_BUTTON = PGNSaveFileButton((SCREEN_WIDTH-50, 60))
        COLOR_BUTTON = ColorButton((SCREEN_WIDTH-235, 10))
        START_SPRITES.add(COLOR_BUTTON)
        RESET_BOARD_BUTTON = ResetBoardButton((SCREEN_WIDTH-190, 10))
        START_SPRITES.add(RESET_BOARD_BUTTON)
        CLEAR_BUTTON = ClearButton((SCREEN_WIDTH-115, 10))
        START_SPRITES.add(CLEAR_BUTTON)
        SCROLL_UP_BUTTON = ScrollUpButton((686, 80))
        SCROLL_DOWN_BUTTON = ScrollDownButton((686, 510))
        GAME_MODE_SPRITES.add(SCROLL_DOWN_BUTTON)
        BEGINNING_MOVE_BUTTON = BeginningMoveButton((SCREEN_WIDTH-235, 545), PLAY_SPRITES)
        PREV_MOVE_BUTTON = PrevMoveButton((SCREEN_WIDTH-195, 545), PLAY_SPRITES)
        NEXT_MOVE_BUTTON = NextMoveButton((SCREEN_WIDTH-155, 545), PLAY_SPRITES)
        LAST_MOVE_BUTTON = LastMoveButton((SCREEN_WIDTH-115, 545), PLAY_SPRITES)
        
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
                grid_coordinate_as_list_element = [chr(int((x-X_GRID_START)/X_GRID_WIDTH)+97), int((Y_GRID_END-y)/Y_GRID_HEIGHT)]
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
                        
        # Load the starting positions of chessboard first
        pos_load_file(PLACED_SPRITES, COLORKEY, reset=True)
            
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
                    # Menu, inanimate buttons at top, and on right side of game board
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[0] > X_GRID_END:
                        if SCROLL_UP_BUTTON.rect.collidepoint(MOUSEPOS): # Scroll up
                            if Text_Controller.scroll > 0:
                                Text_Controller.scroll -= 1
                        if SCROLL_DOWN_BUTTON.rect.collidepoint(MOUSEPOS): # Scroll down
                            if game_controller.move_counter > Text_Controller.max_moves_that_fits_pane:
                                if game_controller.move_counter - Text_Controller.scroll > Text_Controller.max_moves_that_fits_pane + 1 \
                                    and game_controller.WHOSETURN == "white":
                                        Text_Controller.scroll += 1
                                elif game_controller.move_counter - Text_Controller.scroll > Text_Controller.max_moves_that_fits_pane \
                                    and game_controller.WHOSETURN == "black":
                                        Text_Controller.scroll += 1
                        if PGN_LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            pass
                        if PGN_SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PGN_WRITER.write_moves(game_controller.df_moves, game_controller.result_abb)
                        # Editing mode only
                        if game_controller.game_mode == game_controller.EDIT_MODE:
                            #BUTTONS
                            if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                                COLORKEY = get_color()
                            if POS_SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                                pos_save_file(COLORKEY)
                            if POS_LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                                PLACED_SPRITES, COLORKEY = pos_load_file(PLACED_SPRITES, COLORKEY)
                            if RESET_BOARD_BUTTON.rect.collidepoint(MOUSEPOS):
                                PLACED_SPRITES, COLORKEY = pos_load_file(PLACED_SPRITES, COLORKEY, reset=True)
                            
                            list_of_start_objs = {"white_pawn": START.white_pawn, 
                                             "white_bishop": START.white_bishop, 
                                             "white_knight": START.white_knight,
                                             "white_rook": START.white_rook, 
                                             "white_queen": START.white_queen, 
                                             "white_king": START.white_king,
                                             "black_pawn": START.black_pawn, 
                                             "black_bishop": START.black_bishop, 
                                             "black_knight": START.black_knight,
                                             "black_rook": START.black_rook, 
                                             "black_queen": START.black_queen, 
                                             "black_king": START.black_king}
                            # DRAG OBJECTS
                            # Goes through each of the types of pieces
                            # If start object is clicked on, then enable drag, blank box changes images to the original piece so it looks better
                            for piece_name in list_of_start_objs.keys():
                                if list_of_start_objs.get(piece_name).rect.collidepoint(MOUSEPOS):
                                    START = restart_start_objects(START)
                                    DRAGGING.drag_piece(piece_name)
                                    START.blank_box.flip_start_sprite(DRAGGING, list_of_start_objs.get(piece_name).rect.topleft)
                                
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
                            # Created Placed objects at the snapped grid location of the piece that's being dragged
                            if DRAGGING.white_pawn:
                                for grid in Grid.grid_list:
                                    if grid.rect.topleft == snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE):
                                        if int(grid.coordinate[1]) != 1 and int(grid.coordinate[1]) != 8:
                                            PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "white")
                                        else:
                                            log.info("You are not allowed to place a pawn on rank " + grid.coordinate[1])
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
                                    log.info("You can only have one white king.")
                            elif DRAGGING.black_pawn:
                                for grid in Grid.grid_list:
                                    if grid.rect.topleft == snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE):
                                        if int(grid.coordinate[1]) != 1 and int(grid.coordinate[1]) != 8:
                                            PlacedPawn(snap_to_grid(MOUSEPOS, XGRIDRANGE, YGRIDRANGE), PLACED_SPRITES, "black")
                                        else:
                                            log.info("You are not allowed to place a pawn on rank " + grid.coordinate[1])
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
                                    log.info("You can only have one black king.")
                            
                        dragging_to_placed_no_dups()
                        
                        def move_translator(piece_name, piece, captured_abb, special_abb="", check_abb=""):
                            piece_abb = ""
                            if piece_name == "knight":
                                piece_abb = "N"
                            elif piece_name == "bishop":
                                piece_abb = "B"
                            elif piece_name == "rook":
                                piece_abb = "R"
                            elif piece_name == "queen":
                                piece_abb = "Q"
                            elif piece_name == "king":
                                piece_abb = "K"
                            def prefix_func(piece, piece_name, captured_abb, special_abb):
                                # Detecting when there is another piece of same color that 
                                # can attack the same position
                                # In order to get the prefix, we call out the positioning of piece
                                # When there is another of the same piece
                                prefix = ""
                                for grid in Grid.grid_list:
                                    if piece.color == "white":
                                        list_of_attack_pieces = grid.list_of_white_pieces_attacking
                                    elif piece.color == "black":
                                        list_of_attack_pieces = grid.list_of_black_pieces_attacking
                                    # If piece (that just moved) coordinate is same as grid coordinate
                                    if grid.coordinate == piece.coordinate:
                                        # Going through list of other same color attackers (of new grid coordinate)
                                        same_piece_list = []
                                        for attacker_grid in list_of_attack_pieces:
                                            # Pawn is only piece that can enter space without attacking it
                                            if(Grid.grid_dict[attacker_grid].occupied_piece == piece_name \
                                                and piece_name != "pawn" and special_abb != "=Q"):
                                                same_piece_list.append(attacker_grid)
                                        #log.info("SAME PIECE LIST " + str(same_piece_list))
                                        letter_coords = [coords_from_same_piece[0] for coords_from_same_piece in same_piece_list] 
                                        number_coords = [coords_from_same_piece[1] for coords_from_same_piece in same_piece_list] 
                                        #log.info("LETTER COORDS " + str(letter_coords))
                                        #log.info("NUMBER COORDS " + str(number_coords))
                                        #log.info("previous coord " + str(piece.previous_coordinate))
                                        if piece.previous_coordinate[0] in letter_coords and piece.previous_coordinate[1] in number_coords:
                                            prefix = piece.previous_coordinate[0] + piece.previous_coordinate[1]
                                            return prefix
                                        elif piece.previous_coordinate[0] not in letter_coords and piece.previous_coordinate[1] in number_coords:
                                            prefix += piece.previous_coordinate[0]
                                            return prefix
                                        elif piece.previous_coordinate[0] in letter_coords and piece.previous_coordinate[1] not in number_coords:
                                            prefix += piece.previous_coordinate[1]
                                            return prefix
                                        if((piece_name == "pawn" and captured_abb == "x") or (special_abb == "=Q" and captured_abb == "x")):
                                            prefix += piece.previous_coordinate[0]
                                        return prefix
                            if piece.color == "white":
                                prefix = prefix_func(piece, piece_name, captured_abb, special_abb)
                            elif piece.color == "black":
                                prefix = prefix_func(piece, piece_name, captured_abb, special_abb)
                            #recorded_move = piece.color + prefix + " " + piece_name + " from " + str(piece.previous_coordinate) + " to " + str(piece.coordinate)
                            if special_abb == "":
                                recorded_move = piece_abb + prefix + captured_abb + piece.coordinate[0] + piece.coordinate[1] + check_abb
                            elif special_abb == "O-O":
                                recorded_move = special_abb + check_abb
                            elif special_abb == "O-O-O":
                                recorded_move = special_abb + check_abb
                            elif special_abb == "=Q":
                                recorded_move = prefix + captured_abb + piece.coordinate[0] + piece.coordinate[1] + special_abb + check_abb
                            return recorded_move
                                    
                        # Moves piece
                        def move_piece_on_grid(black_captured_y=525, white_captured_y=15, incremental_x=40):
                            # Default captured_abb for function to be empty string
                            captured_abb = ""
                            # Castle, pawn promotion
                            special_abb = ""
                            # Check or checkmate
                            check_abb = ""
                            # White win, draw, black win
                            game_controller.result_abb = "*"
                            prior_moves_dict = {}
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
                                                        # Moving captured piece off the board
                                                        if piece_captured.coordinate == grid.coordinate:
                                                            if piece_captured.color == "black":
                                                                piece_captured.captured(game_controller.black_captured_x, black_captured_y)
                                                                game_controller.black_captured_x += incremental_x
                                                            elif piece_captured.color == "white":
                                                                piece_captured.captured(game_controller.white_captured_x, white_captured_y)
                                                                game_controller.white_captured_x += incremental_x
                                                            # Captured_abb used for move notation
                                                            captured_abb = "x"
                                            # En Passant Capture
                                            if grid.en_passant_skipover == True:
                                                if piece in PlayPawn.white_pawn_list:
                                                    for black_pawn in PlayPawn.black_pawn_list:
                                                        # Must include taken_off_board bool or else you get NoneType error
                                                        if black_pawn.taken_off_board == False:
                                                            if black_pawn.coordinate[0] == grid.coordinate[0] and \
                                                                int(black_pawn.coordinate[1]) == 5:
                                                                    black_pawn.captured(game_controller.black_captured_x, black_captured_y)
                                                                    captured_abb = "x"
                                                elif piece in PlayPawn.black_pawn_list:
                                                    for white_pawn in PlayPawn.white_pawn_list:
                                                        # Must include taken_off_board bool or else you get NoneType error
                                                        if white_pawn.taken_off_board == False:
                                                            if white_pawn.coordinate[0] == grid.coordinate[0] and \
                                                                int(white_pawn.coordinate[1]) == 4:
                                                                    white_pawn.captured(game_controller.white_captured_x, white_captured_y)
                                                                    captured_abb = "x"
                                                                
                                            # Reset en passant skipover for all squares
                                            for sub_grid in Grid.grid_list:
                                                sub_grid.en_passant_skipover = False
                                                
                                            # Grid is no longer occupied by a piece
                                            for old_grid in Grid.grid_list:
                                                if old_grid.coordinate == piece.coordinate:
                                                    old_grid.occupied = False
                                                    piece.previous_coordinate = old_grid.coordinate
                                                    piece.coordinate_history[game_controller.move_counter] = {'before':piece.previous_coordinate}
                                                    prior_moves_dict['before'] = piece.previous_coordinate
                                                    old_grid.prior_move_color = True
                                                    
                                            # Moving piece, removing piece and grid highlights, changing Turn
                                            piece.rect.topleft = grid.rect.topleft
                                            piece.coordinate = grid.coordinate
                                            piece.coordinate_history[game_controller.move_counter]['after'] = piece.coordinate
                                            prior_moves_dict['after'] = piece.coordinate
                                            grid.occupied = True
                                            piece.no_highlight()
                                            
                                            #########
                                            # RULES AFTER MOVE
                                            #########
                                            
                                            # Enpassant Rule and Promotion Rule for Pawns
                                            if piece in PlayPawn.white_pawn_list:
                                                if int(piece.coordinate[1]) == 8:
                                                    special_abb = "=Q"
                                                    promoted_queen = PlayQueen(piece.rect.topleft, PLAY_SPRITES, "white")
                                                    promoted_queen.previous_coordinate = piece.previous_coordinate
                                                    # Take white pawn off the board
                                                    piece.promoted()
                                                # Detects that pawn was just moved
                                                elif int(piece.coordinate[1]) == 4 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                                                    int(piece.previous_coordinate[1]) == 2:
                                                    for sub_grid in Grid.grid_list:
                                                        if sub_grid.coordinate[0] == piece.coordinate[0] and int(sub_grid.coordinate[1]) == int(piece.coordinate[1])-1:
                                                            sub_grid.en_passant_skipover = True
                                                        else:
                                                            sub_grid.en_passant_skipover = False
                                                else:
                                                    grid.en_passant_skipover = False
                                            elif piece in PlayPawn.black_pawn_list:
                                                if int(piece.coordinate[1]) == 1:
                                                    special_abb = "=Q"
                                                    promoted_queen = PlayQueen(piece.rect.topleft, PLAY_SPRITES, "black")
                                                    promoted_queen.previous_coordinate = piece.previous_coordinate
                                                    # Take black pawn off the board
                                                    piece.promoted()
                                                # Detects that pawn was just moved
                                                elif int(piece.coordinate[1]) == 5 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                                                    int(piece.previous_coordinate[1]) == 7:
                                                    for sub_grid in Grid.grid_list:
                                                        if sub_grid.coordinate[0] == piece.coordinate[0] and int(sub_grid.coordinate[1]) == int(piece.coordinate[1])+1:
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
                                                        if rook.coordinate == 'a1' and piece.coordinate == 'c1':
                                                            rook.rect.topleft = Grid.grid_dict['d1'].rect.topleft
                                                            rook.coordinate = Grid.grid_dict['d1'].coordinate
                                                            Grid.grid_dict['d1'].occupied = True
                                                            rook.allowed_to_castle = False
                                                            special_abb = "O-O-O"
                                                        elif rook.coordinate == 'h1' and piece.coordinate == 'g1':
                                                            rook.rect.topleft = Grid.grid_dict['f1'].rect.topleft
                                                            rook.coordinate = Grid.grid_dict['f1'].coordinate
                                                            Grid.grid_dict['f1'].occupied = True
                                                            rook.allowed_to_castle = False
                                                            special_abb = "O-O"
                                            elif piece in PlayKing.black_king_list:
                                                piece.castled = True
                                                for rook in PlayRook.black_rook_list:
                                                    if rook.allowed_to_castle == True:
                                                        if rook.coordinate == 'a8' and piece.coordinate == 'c8':
                                                            rook.rect.topleft = Grid.grid_dict['d8'].rect.topleft
                                                            rook.coordinate = Grid.grid_dict['d8'].coordinate
                                                            Grid.grid_dict['d8'].occupied = True
                                                            special_abb = "O-O-O"
                                                        elif rook.coordinate == 'h8' and piece.coordinate == 'g8':
                                                            rook.rect.topleft = Grid.grid_dict['f8'].rect.topleft
                                                            rook.coordinate = Grid.grid_dict['f8'].coordinate
                                                            Grid.grid_dict['f8'].occupied = True
                                                            special_abb = "O-O"
                                            elif piece in PlayRook.white_rook_list or PlayRook.black_rook_list:
                                                piece.allowed_to_castle = False
                                            # Update all grids to reflect the coordinates of the pieces
                                            GRID_SPRITES.update(game_controller)
                                            # Switch turns
                                            if(game_controller.WHOSETURN == "white"):
                                                game_controller.switch_turn("black")
                                            elif(game_controller.WHOSETURN == "black"):
                                                game_controller.switch_turn("white")
                                                game_controller.move_counter += 1
                                            if game_controller.color_in_check == "black":
                                                Text_Controller.check_checkmate_text = "Black King checked"
                                                for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                                                   PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                                                   PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                                    for sub_piece in piece_list:
                                                        sub_piece.spaces_available(game_controller)
                                                def checkmate_check(game_controller):
                                                    for subgrid in Grid.grid_list:
                                                        if subgrid.highlighted == True:
                                                            # If able to detect that a grid can be highlighted, that means it's NOT checkmate
                                                            return "+", "*"
                                                    Text_Controller.check_checkmate_text = "White wins"
                                                    return "#", "1-0"
                                                check_abb, game_controller.result_abb = checkmate_check(game_controller)
                                            elif game_controller.color_in_check == "white":
                                                Text_Controller.check_checkmate_text = "White King checked"
                                                for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                                                   PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                                                   PlayQueen.white_queen_list, PlayKing.white_king_list]:
                                                    for sub_piece in piece_list:
                                                        sub_piece.spaces_available(game_controller)
                                                def checkmate_check(game_controller):
                                                    for subgrid in Grid.grid_list:
                                                        if subgrid.highlighted == True:
                                                            # If able to detect that a grid can be highlighted, that means it's NOT checkmate
                                                            return "+", "*"
                                                    Text_Controller.check_checkmate_text = "Black wins"
                                                    return "#", "0-1"
                                                check_abb, game_controller.result_abb = checkmate_check(game_controller)
                                            elif game_controller.color_in_check == "" and game_controller.WHOSETURN == "white":
                                                for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                                                   PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                                                   PlayQueen.white_queen_list, PlayKing.white_king_list]:
                                                    for sub_piece in piece_list:
                                                        sub_piece.spaces_available(game_controller)
                                                def stalemate_check(game_controller):
                                                    for subgrid in Grid.grid_list:
                                                        if subgrid.highlighted == True:
                                                            # No check, no checkmate, no stalemate
                                                            Text_Controller.check_checkmate_text = ""
                                                            return "*"
                                                    Text_Controller.check_checkmate_text = "Stalemate"
                                                    return "1/2-1/2"
                                                game_controller.result_abb = stalemate_check(game_controller)
                                            elif game_controller.color_in_check == "" and game_controller.WHOSETURN == "black":
                                                for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                                                   PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                                                   PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                                    for sub_piece in piece_list:
                                                        sub_piece.spaces_available(game_controller)
                                                def stalemate_check(game_controller):
                                                    for subgrid in Grid.grid_list:
                                                        if subgrid.highlighted == True:
                                                            # No check, no checkmate, no stalemate
                                                            Text_Controller.check_checkmate_text = ""
                                                            return "*"
                                                    Text_Controller.check_checkmate_text = "Stalemate"
                                                    return "1/2-1/2"
                                                game_controller.result_abb = stalemate_check(game_controller)
                                            else:
                                                # No checks
                                                Text_Controller.check_checkmate_text = ""
                                            if(game_controller.WHOSETURN == "white"):
                                                if special_abb == "=Q":
                                                    # When the piece became promoted to a Queen
                                                    move_text = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb) + " "
                                                    game_controller.df_moves.loc[game_controller.move_counter-1, "black_move"] = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                                                    piece.coordinate_history[game_controller.move_counter-1]['move_notation'] = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                                                    prior_moves_dict['move_notation'] = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                                                else:
                                                    move_text = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb) + " "
                                                    game_controller.df_moves.loc[game_controller.move_counter-1, "black_move"] = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                                                    piece.coordinate_history[game_controller.move_counter-1]['move_notation'] = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                                                    prior_moves_dict['move_notation'] = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                                                game_controller.df_prior_moves.loc[game_controller.move_counter-1, "black_move"] = str(prior_moves_dict)
                                            elif(game_controller.WHOSETURN == "black"):
                                                if special_abb == "=Q":
                                                    move_text = str(game_controller.move_counter) + ". " + \
                                                          move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb) + " "
                                                    game_controller.df_moves.loc[game_controller.move_counter] = [move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb), '']
                                                    piece.coordinate_history[game_controller.move_counter]['move_notation'] = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                                                    prior_moves_dict['move_notation'] = move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                                                else:
                                                    move_text = str(game_controller.move_counter) + ". " + \
                                                          move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb) + " "
                                                    game_controller.df_moves.loc[game_controller.move_counter] = [move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb), '']
                                                    piece.coordinate_history[game_controller.move_counter]['move_notation'] = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                                                    prior_moves_dict['move_notation'] = move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                                                game_controller.df_prior_moves.loc[game_controller.move_counter, "white_move"] = str(prior_moves_dict)
                                            Text_Controller.body_text += move_text
                                            log.info(move_text)
                                            if game_controller.result_abb != "*":
                                                log.info(game_controller.result_abb)
                                            
                                            Text_Controller.scroll = Text_Controller.latest_scroll(Text_Controller.body_text, Text_Controller.scroll)
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
    
                    if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                        #scroll wheel
                        if event.button == 4: # Scroll up
                            if Text_Controller.scroll > 0:
                                Text_Controller.scroll -= 1
                        if event.button == 5: # Scroll down
                            if game_controller.move_counter > Text_Controller.max_moves_that_fits_pane:
                                if game_controller.move_counter - Text_Controller.scroll > Text_Controller.max_moves_that_fits_pane + 1 \
                                    and game_controller.WHOSETURN == "white":
                                    Text_Controller.scroll += 1
                                elif game_controller.move_counter - Text_Controller.scroll > Text_Controller.max_moves_that_fits_pane \
                                    and game_controller.WHOSETURN == "black":
                                    Text_Controller.scroll += 1
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
                            Text_Controller.body_text = ""
                            log.info("Play Mode Activated\n")
                            
                            def placed_to_play(placed_list, class_obj, sprite_group, color):
                                # Play pieces spawn where their placed piece correspondents are located
                                for placed_obj in placed_list:
                                    class_obj(placed_obj.rect.topleft, sprite_group, color)

                            placed_to_play(PlacedPawn.white_pawn_list, PlayPawn, PLAY_SPRITES, "white")
                            placed_to_play(PlacedBishop.white_bishop_list, PlayBishop, PLAY_SPRITES, "white")
                            placed_to_play(PlacedKnight.white_knight_list, PlayKnight, PLAY_SPRITES, "white")
                            placed_to_play(PlacedRook.white_rook_list, PlayRook, PLAY_SPRITES, "white")
                            placed_to_play(PlacedQueen.white_queen_list, PlayQueen, PLAY_SPRITES, "white")
                            placed_to_play(PlacedKing.white_king_list, PlayKing, PLAY_SPRITES, "white")
                            placed_to_play(PlacedPawn.black_pawn_list, PlayPawn, PLAY_SPRITES, "black")
                            placed_to_play(PlacedBishop.black_bishop_list, PlayBishop, PLAY_SPRITES, "black")
                            placed_to_play(PlacedKnight.black_knight_list, PlayKnight, PLAY_SPRITES, "black")
                            placed_to_play(PlacedRook.black_rook_list, PlayRook, PLAY_SPRITES, "black")
                            placed_to_play(PlacedQueen.black_queen_list, PlayQueen, PLAY_SPRITES, "black")
                            placed_to_play(PlacedKing.black_king_list, PlayKing, PLAY_SPRITES, "black")
                            
                            game_controller.WHOSETURN = "white"
                            GRID_SPRITES.update(game_controller)
                            game_controller.projected_white_update()
                            game_controller.projected_black_update()
                        #################
                        # LEFT CLICK (RELEASE) STOP BUTTON
                        #################
                        elif PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_controller.game_mode == game_controller.PLAY_MODE:
                            log.info("\nEditing Mode Activated\n")
                            game_controller.game_mode = game_controller.EDIT_MODE
                            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(game_controller.game_mode)
                            game_controller.reset_board()
                        # Undo move through PREV_MOVE_BUTTON
                        if PREV_MOVE_BUTTON.rect.collidepoint(MOUSEPOS):
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
                        for black_pawn in PlayPawn.black_pawn_list:
                            log.info(str(black_pawn.__dict__))
                        """
                        for grid in Grid.grid_list:
                            if grid.rect.collidepoint(MOUSEPOS):
                                log.info("Coordinate: " + str(grid.coordinate) \
                                       + ", White Pieces Attacking: " + str(grid.list_of_white_pieces_attacking) \
                                       + ", Black Pieces Attacking: " + str(grid.list_of_black_pieces_attacking) \
                                       + ", Grid occupied? " + str(grid.__dict__))
                        """
                                
                ##################
                # ALL EDIT ACTIONS
                ##################
                # Start piece is dragging according to where the mouse is
                if game_controller.game_mode == game_controller.EDIT_MODE:
                    def replace_start_sprite_with_black_box(dragging_obj, start_blank_box_var, start_obj_pos, start_obj, mouse_pos):
                        if dragging_obj:
                            start_blank_box_var.rect.topleft = start_obj_pos
                            start_obj.rect.topleft = (mouse_pos[0]-(start_obj.image.get_width()/2),
                                                      mouse_pos[1]-(start_obj.image.get_height()/2))
                        else:
                            start_obj.rect.topleft = start_obj_pos
                    replace_start_sprite_with_black_box(DRAGGING.white_pawn, START.blank_box, STARTPOS['white_pawn'], START.white_pawn, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.white_bishop, START.blank_box, STARTPOS['white_bishop'], START.white_bishop, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.white_knight, START.blank_box, STARTPOS['white_knight'], START.white_knight, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.white_rook, START.blank_box, STARTPOS['white_rook'], START.white_rook, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.white_queen, START.blank_box, STARTPOS['white_queen'], START.white_queen, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.white_king, START.blank_box, STARTPOS['white_king'], START.white_king, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_pawn, START.blank_box, STARTPOS['black_pawn'], START.black_pawn, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_bishop, START.blank_box, STARTPOS['black_bishop'], START.black_bishop, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_knight, START.blank_box, STARTPOS['black_knight'], START.black_knight, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_rook, START.blank_box, STARTPOS['black_rook'], START.black_rook, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_queen, START.blank_box, STARTPOS['black_queen'], START.black_queen, MOUSEPOS)
                    replace_start_sprite_with_black_box(DRAGGING.black_king, START.blank_box, STARTPOS['black_king'], START.black_king, MOUSEPOS)                      
            
                ##################
                # IN-GAME ACTIONS
                ##################
                if game_controller.game_mode == game_controller.PLAY_MODE:
                    pass
                #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
                
                #Update all sprites
                #START_SPRITES.update()
                PLACED_SPRITES.update(Grid.grid_list)
                #PLAY_SPRITES.update()
                SCREEN.fill(COLORKEY)
                
                draw_moves(move_notation_font, Text_Controller.body_text, Text_Controller.scroll, game_controller)
                
                GAME_MODE_SPRITES.draw(SCREEN)
                GRID_SPRITES.draw(SCREEN)
                GRID_SPRITES.update(game_controller)
                
                if(game_controller.game_mode == game_controller.EDIT_MODE): #Only draw placed sprites in editing mode
                    START_SPRITES.draw(SCREEN)
                    PLACED_SPRITES.draw(SCREEN)    
                elif(game_controller.game_mode == game_controller.PLAY_MODE): #Only draw play sprites in play mode
                    PLAY_SPRITES.draw(SCREEN)
                RECTANGLE_SPRITES.draw(SCREEN)
                # Update objects that aren't in a sprite group
                SCROLL_UP_BUTTON.update(Text_Controller.scroll)
                SCROLL_UP_BUTTON.draw(SCREEN)
                SCROLL_DOWN_BUTTON.update(game_controller.move_counter, game_controller.WHOSETURN, Text_Controller.max_moves_that_fits_pane, Text_Controller.scroll)
                SCROLL_DOWN_BUTTON.draw(SCREEN)
                PGN_LOAD_FILE_BUTTON.draw(SCREEN)
                PGN_SAVE_FILE_BUTTON.draw(SCREEN)
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
                    check_checkmate_text_render = arial_font.render(Text_Controller.check_checkmate_text, 1, (0, 0, 0))
                    if game_controller.WHOSETURN == "white":
                        whose_turn_text = arial_font.render("White's move", 1, (0, 0, 0))
                    elif game_controller.WHOSETURN == "black":
                        whose_turn_text = arial_font.render("Black's move", 1, (0, 0, 0))
                    SCREEN.blit(whose_turn_text, (X_GRID_END+X_GRID_WIDTH, SCREEN_HEIGHT/2))
                    SCREEN.blit(check_checkmate_text_render, (X_GRID_END+X_GRID_WIDTH, 200))
                pygame.display.update()
            elif state == DEBUG:
                if debug_message == 1:
                    log.info("Entering debug mode")
                    debug_message = 0
                    # USE BREAKPOINT HERE
                    print(str(game_controller.df_prior_moves))
                    log.info("Use breakpoint here")
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            state = RUNNING
                            log.info("back to Running")
    except SystemExit:
        pass
    except:
        log.exception("Error out of main")
if __name__ == "__main__":
    main()