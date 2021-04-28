"""
Chess created by Brad Wyatt

Features To-Do (short-term):
Undo move
Play back one move
Be able to click on a move in the pane to view it
--> One idea I had before was pause mode (mode between edit and play)
--> I think the right thing to do would take the df_prior_moves to get the move. The tricky part is differentiating this from Undo move (through a conditional variable checking within each class for example). And coloring prior_move_color appropriately.
Game Properties
Menu objects are still invisible yet clickable

Buttons to Implement:
Previous Move
Next Move
Beginning of Game
Latest move
Game Properties (use Babaschess for model)

Features To-Do (long-term):
Customized Turns for black and white
Choose piece for Promotion
Sounds
If no king then don't start game
Remove yellow highlight on grid

Testing/Code Improvements:
Getting rid of import *?
Splitting groups of statements that were for after clicking into functions and methods within classes
Feedback

Optional:
Perhaps using a direction arrow (like babaschess) to determine which piece could take the other piece. This could get confusing when flipping board though
AI
"""
import board
from start_objects import *
from placed_objects import *
from play_objects import *
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
import initvar

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
# Functions
#############
             
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
    START.white_pawn.rect.topleft = initvar.STARTPOS['white_pawn']
    START.white_bishop.rect.topleft = initvar.STARTPOS['white_bishop']
    START.white_knight.rect.topleft = initvar.STARTPOS['white_knight']
    START.white_rook.rect.topleft = initvar.STARTPOS['white_rook']
    START.white_queen.rect.topleft = initvar.STARTPOS['white_queen']
    START.white_king.rect.topleft = initvar.STARTPOS['white_king']
    START.black_pawn.rect.topleft = initvar.STARTPOS['black_pawn']
    START.black_bishop.rect.topleft = initvar.STARTPOS['black_bishop']
    START.black_knight.rect.topleft = initvar.STARTPOS['black_knight']
    START.black_rook.rect.topleft = initvar.STARTPOS['black_rook']
    START.black_queen.rect.topleft = initvar.STARTPOS['black_queen']
    START.black_king.rect.topleft = initvar.STARTPOS['black_king']
    return START

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

def get_color():
    color = askcolor()
    return [color[0][0], color[0][1], color[0][2]]

def pos_load_file(PLACED_SPRITES, colorkey, reset=False):
    open_file = None
    if reset == True:
        loaded_dict = {'white_pawn': ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
                       'white_bishop': ['c1', 'f1'], 'white_knight': ['b1', 'g1'],
                       'white_rook': ['a1', 'h1'], 'white_queen': ['d1'], 'white_king': ['e1'],
                       'black_pawn': ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
                       'black_bishop': ['c8', 'f8'], 'black_knight': ['b8', 'g8'],
                       'black_rook': ['a8', 'h8'], 'black_queen': ['d8'], 'black_king': ['e8'],
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

            
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'white_pawn': PlacedPawn.white_pawn_list, 'white_bishop': PlacedBishop.white_bishop_list, 
                         'white_knight': PlacedKnight.white_knight_list, 'white_rook': PlacedRook.white_rook_list,
                         'white_queen': PlacedQueen.white_queen_list, 'white_king': PlacedKing.white_king_list,
                         'black_pawn': PlacedPawn.black_pawn_list, 'black_bishop': PlacedBishop.black_bishop_list,
                         'black_knight': PlacedKnight.black_knight_list, 'black_rook': PlacedRook.black_rook_list,
                         'black_queen': PlacedQueen.black_queen_list, 'black_king': PlacedKing.black_king_list}
    get_coord_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_coord in item_list:
            item_list_in_name.append(item_coord.coordinate)
        get_coord_for_all_obj[item_key] = item_list_in_name
    return get_coord_for_all_obj

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
    
class Dragging():
    def __init__(self):
        self.dragging_all_false()
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
        self.start_obj_image_placeholder = StartObjImagePlaceholder()
        self.white_pawn = StartPawn("white")
        self.white_bishop = StartBishop("white")
        self.white_knight = StartKnight("white")        
        self.white_rook = StartRook("white")      
        self.white_queen = StartQueen("white")      
        self.white_king = StartKing("white")      
        self.black_pawn = StartPawn("black")
        self.black_bishop = StartBishop("black")
        self.black_knight = StartKnight("black")      
        self.black_rook = StartRook("black")      
        self.black_queen = StartQueen("black")      
        self.black_king = StartKing("black")
    
class PGN_Writer_and_Loader():
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
    def pgn_load(self, game_controller, PLAY_SPRITES, PLAY_EDIT_SWITCH_BUTTON):
        open_file = None
        request_file_name = askopenfilename(defaultextension=".pgn")
        log.info("Loading PGN...")
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return
        game_controller.switch_mode(game_controller.PLAY_MODE, PLAY_EDIT_SWITCH_BUTTON)
        game_controller.spawn_play_objects(PLAY_SPRITES)
        
        loaded_file = open_file.read()
        all_components_split = loaded_file.split("\n")
        parameters = {}
        chess_game = []
        for row in all_components_split:
            updated_row = row.replace('[', '').replace(']','')
            if '[' in row:
                # For the row that contains the parameters, only include the first item on the line and set as key
                parameters[updated_row.split(" ")[0]] = " ".join(updated_row.split(" ")[1:])
            else:
                if row != '':
                    # Skip any lines that have empty spaces, we are only getting the chess game moves
                    chess_game.append(row)
        try:
            self.Event = parameters['Event']
        except KeyError:
            self.Event = ""
        try:
            self.Site = parameters['Site']
        except KeyError:
            self.Site = ""
        try:
            self.Date = parameters['Date']
        except KeyError:
            self.Date = ""
        try:
            self.Round = parameters['Round']
        except KeyError:
            self.Round = ""
        try:
            self.White = parameters['White']
        except KeyError:
            self.White = ""
        try:
            self.Black = parameters['Black']
        except KeyError:
            self.Black = ""
        try:
            self.Result = parameters['Result']
        except KeyError:
            self.Result = ""
        try:
            self.WhiteElo = parameters['WhiteElo']
        except KeyError:
            self.WhiteElo = ""
        try:
            self.BlackElo = parameters['BlackElo']
        except KeyError:
            self.BlackElo = ""
        try:
            self.ECO = parameters['ECO']
        except KeyError:
            self.ECO = ""
        
        # Removes line breaks and formulates all elements into one element in the list
        chess_game = "".join(chess_game).split("  ")
        
        number_move_splits = "".join(chess_game).split()
        
        def determine_piece_list(piece_abb, whoseturn):
            if whoseturn == "white":
                if piece_abb == "N":
                    return PlayKnight.white_knight_list
                elif piece_abb == "B":
                    return PlayBishop.white_bishop_list
                elif piece_abb == "R":
                    return PlayRook.white_rook_list
                elif piece_abb == "Q":
                    return PlayQueen.white_queen_list
                elif piece_abb == "K":
                    return PlayKing.white_king_list
                else:
                    return PlayPawn.white_pawn_list
            elif whoseturn == "black":
                if piece_abb == "N":
                    return PlayKnight.black_knight_list
                elif piece_abb == "B":
                    return PlayBishop.black_bishop_list
                elif piece_abb == "R":
                    return PlayRook.black_rook_list
                elif piece_abb == "Q":
                    return PlayQueen.black_queen_list
                elif piece_abb == "K":
                    return PlayKing.black_king_list
                else:
                    return PlayPawn.black_pawn_list
                
        def determine_piece(piece_list, move, grid_coordinate, game_controller):
            eligible_pieces = []
            for piece in piece_list:
                if piece.coordinate is not None:
                    piece.spaces_available(game_controller)
                    if (piece.coordinate in board.Grid.grid_dict[grid_coordinate].coords_of_available_pieces['white'] \
                        or piece.coordinate in board.Grid.grid_dict[grid_coordinate].coords_of_available_pieces['black']):
                            eligible_pieces.append(piece)
            if len(eligible_pieces) == 1:
                # List only has one eligible piece
                return eligible_pieces[0]
            elif(piece_list != PlayPawn.white_pawn_list and piece_list != PlayPawn.black_pawn_list):
                # Decide the logic of if there are at least 2 eligible pieces
                for piece in eligible_pieces:
                    if piece.coordinate[1] == move[1]:
                        return piece
                    elif piece.coordinate[0] == move[1]:
                        return piece
            else:
                # Pawns
                for piece in eligible_pieces:
                    if piece.coordinate[0] == move[0]:
                        return piece
                    
        for row in number_move_splits:
            # Breakpoint for a specific move on PGN
            #if "14." in move:
            #    break
            if ("." in row) or ("*" in row) or ("0-1" in row) or ("1-0" in row) or ("1/2-1/2" in row):
                pass
            else:
                move = row
                # type_of_piece list in Nce2 would be "N"
                
                if move == "O-O":
                    if game_controller.WHOSETURN == "white":
                        type_of_piece_list = PlayKing.white_king_list
                        grid_coordinate = 'g1'
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = PlayKing.black_king_list
                        grid_coordinate = 'g8'
                    piece = type_of_piece_list[0]
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller, PLAY_SPRITES)
                    Move_Controller.game_status_check(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, promoted_queen)
                elif move == "O-O-O":
                    if game_controller.WHOSETURN == "white":
                        type_of_piece_list = PlayKing.white_king_list
                        grid_coordinate = 'c1'
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = PlayKing.black_king_list
                        grid_coordinate = 'c8'
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller, PLAY_SPRITES)
                    Move_Controller.game_status_check(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, promoted_queen)
                elif move[-2:] == "=Q":
                    if game_controller.WHOSETURN == "white":
                        type_of_piece_list = PlayPawn.white_pawn_list
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = PlayPawn.black_pawn_list
                    grid_coordinate = move[-4:-2]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller, PLAY_SPRITES)
                    Move_Controller.game_status_check(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, promoted_queen)
                else:
                    # NORMAL MOVES
                    # Last 2 characters are always the coordinate of the grid besides special exceptions above
                    type_of_piece_list = determine_piece_list(move[0], game_controller.WHOSETURN)
                    if move[-1] == "+" or move[-1] == "#":
                        grid_coordinate = move[-3:-1]
                    else:
                        grid_coordinate = move[-2:]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller, PLAY_SPRITES)
                    Move_Controller.game_status_check(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, promoted_queen)
                draw_move_rects_on_moves_pane(pygame.font.SysFont('Arial', 16), game_controller)
                
        def prior_move_off(current_coord):
            for play_obj_list in (PlayPawn.white_pawn_list, PlayBishop.white_bishop_list,
                                     PlayKnight.white_knight_list, PlayRook.white_rook_list,
                                     PlayQueen.white_queen_list, PlayKing.white_king_list,
                                     PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                                     PlayKnight.black_knight_list, PlayRook.black_rook_list,
                                     PlayQueen.black_queen_list, PlayKing.black_king_list):
                for play_obj in play_obj_list:
                    if play_obj.coordinate == grid_coordinate:
                        play_obj.prior_move_color = True
                        board.Grid.grid_dict[play_obj.previous_coordinate].prior_move_color = True
                        play_obj.no_highlight()
                        board.Grid.grid_dict[play_obj.previous_coordinate].no_highlight()
                    else:
                        play_obj.prior_move_color = False
                        play_obj.no_highlight()
            return
        prior_move_off(grid_coordinate)
        
        # This goes through all pieces available moves
        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                           PlayQueen.white_queen_list, PlayKing.white_king_list,
                           PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                           PlayKnight.black_knight_list, PlayRook.black_rook_list,
                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for piece in piece_list:
                piece.spaces_available(game_controller)
            
        log.info("PGN Finished Loading")
        return

class Grid_Controller():
    flipped = False
    def flip_grids():
        letters = 'abcdefgh'
        numbers = '12345678'
        if Grid_Controller.flipped == False:
            for grid in board.Grid.grid_list:
                mirror_grid_coordinate = ""
                for l in letters:
                    if l == grid.coordinate[0]:
                        mirror_grid_coordinate += letters[-(letters.index(l)+1)]
                for n in numbers:
                    if n == grid.coordinate[1]:
                        mirror_grid_coordinate += numbers[-(numbers.index(n)+1)]
                grid.rect.topleft = board.Grid.grid_dict[mirror_grid_coordinate].initial_rect_top_left
            Grid_Controller.flipped = True
        else:
            for grid in board.Grid.grid_list:
                grid.rect.topleft = grid.initial_rect_top_left
            Grid_Controller.flipped = False
        Text_Controller.flip_board()
                
    def update_grid(game_controller):
        for grid in board.Grid.grid_list:
            if game_controller.game_mode == game_controller.PLAY_MODE:
                def grid_occupied_by_piece():
                    for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                       PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                       PlayQueen.white_queen_list, PlayKing.white_king_list,
                                       PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                                       PlayKnight.black_knight_list, PlayRook.black_rook_list,
                                       PlayQueen.black_queen_list, PlayKing.black_king_list]:
                        for piece in piece_list:
                            if grid.rect.topleft == piece.rect.topleft:
                                grid.occupied = True
                                if piece.color == "white":
                                    grid.occupied_piece_color = "white"
                                elif piece.color == "black":
                                    grid.occupied_piece_color = "black"
                                if(piece in PlayPawn.white_pawn_list or piece in PlayPawn.black_pawn_list):
                                    grid.occupied_piece = "pawn"
                                elif(piece in PlayBishop.white_bishop_list or piece in PlayBishop.black_bishop_list):
                                    grid.occupied_piece = "bishop"
                                elif(piece in PlayKnight.white_knight_list or piece in PlayKnight.black_knight_list):
                                    grid.occupied_piece = "knight"
                                elif(piece in PlayRook.white_rook_list or piece in PlayRook.black_rook_list):
                                    grid.occupied_piece = "rook"
                                elif(piece in PlayQueen.white_queen_list or piece in PlayQueen.black_queen_list):
                                    grid.occupied_piece = "queen"
                                elif(piece in PlayKing.white_king_list or piece in PlayKing.black_king_list):
                                    grid.occupied_piece = "king"
                                return
                    else:
                        grid.occupied = False
                        grid.occupied_piece = ""
                        grid.occupied_piece_color = ""
                grid_occupied_by_piece()

class Game_Controller():
    def __init__(self):
        self.EDIT_MODE, self.PLAY_MODE = 0, 1
        self.game_mode = self.EDIT_MODE
        self.reset_initial_vars()
    def reset_initial_vars(self):
        self.WHOSETURN = "white"
        self.color_in_check = ""
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.black_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.white_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.move_counter = 1
        self.df_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_moves.index = np.arange(1, len(self.df_moves)+1) # Index at 1 rather than 0 because chess starts that way
        self.df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
        self.df_prior_moves.index = np.arange(1, len(self.df_prior_moves)+1)
        self.result_abb = "*"
        self.selected_move = [0, "", ""]
    def switch_mode(self, game_mode, PLAY_EDIT_SWITCH_BUTTON):
        if game_mode == self.EDIT_MODE:
            log.info("\nEditing Mode Activated\n")
            self.game_mode = self.EDIT_MODE
            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(self.game_mode)
            self.reset_board()
            Text_Controller.check_checkmate_text = ""
        elif game_mode == self.PLAY_MODE:
            log.info("Play Mode Activated\n")
            self.game_mode = self.PLAY_MODE
            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(self.game_mode)
    def spawn_play_objects(self, PLAY_SPRITES):
        def placed_to_play(placed_list, class_obj, sprite_group, color):
            # Play pieces spawn where their placed piece correspondents are located
            for placed_obj in placed_list:
                class_obj(placed_obj.coordinate, sprite_group, color)

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
        
        self.WHOSETURN = "white"
        Grid_Controller.update_grid(self)
        self.projected_white_update()
        self.projected_black_update()
        
        for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                           PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                           PlayQueen.white_queen_list, PlayKing.white_king_list,
                           PlayPawn.black_pawn_list, PlayBishop.black_bishop_list,
                           PlayKnight.black_knight_list, PlayRook.black_rook_list,
                           PlayQueen.black_queen_list, PlayKing.black_king_list]:
            for piece in piece_list:
                piece.spaces_available(self)
        for grid in board.Grid.grid_list:
            grid.no_highlight()
            
    def reset_board(self):
        self.game_mode = self.EDIT_MODE
        self.reset_initial_vars()
        Text_Controller.reset()
        # Kill all Objects within their Class lists/dicts
        for spr_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                 PlayKnight.white_knight_list, PlayRook.white_rook_list,
                 PlayQueen.white_queen_list, PlayKing.white_king_list, 
                 PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                 PlayKnight.black_knight_list, PlayRook.black_rook_list,
                 PlayQueen.black_queen_list, PlayKing.black_king_list,
                 MoveNumberRectangle.rectangle_list, PieceMoveRectangle.rectangle_list]:
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
        for grid in board.Grid.grid_list:
            grid.reset_board()
        # Reset Moves Panel
        MoveNumberRectangle.rectangle_list = []
        PieceMoveRectangle.rectangle_list = []
        MoveNumberRectangle.rectangle_dict = {}
        PieceMoveRectangle.rectangle_dict = {}
        PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
    def switch_turn(self, color_turn):
        self.WHOSETURN = color_turn
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        # No highlights and ensuring that attacking squares (used by diagonal pieces) are set to 0
        for grid in board.Grid.grid_list:
            grid.no_highlight()
            grid.coords_of_attacking_pieces['white'] = []
            grid.coords_of_attacking_pieces['black'] = []
            grid.coords_of_available_pieces['white'] = []
            grid.coords_of_available_pieces['black'] = []
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
                if board.Grid.grid_dict[white_king.coordinate].coords_of_attacking_pieces['black'] == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "white"
                    # Disable pieces if their king is in double-check
                    if len(board.Grid.grid_dict[white_king.coordinate].coords_of_attacking_pieces['black']) > 1:
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
                if board.Grid.grid_dict[black_king.coordinate].coords_of_attacking_pieces['white'] == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "black"
                    # Disable pieces if their king is in double-check
                    if len(board.Grid.grid_dict[black_king.coordinate].coords_of_attacking_pieces['white']) > 1:
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
                if board.Grid.grid_dict[pinned_piece_coordinate].coordinate == piece.coordinate \
                    and piece.color == color:
                    piece.pinned_restrict(pin_attacking_coordinates)
    def king_in_check(self, attacker_piece, check_piece_coordinate, check_attacking_coordinates, color):
        self.color_in_check = color
        self.check_attacking_coordinates = check_attacking_coordinates
        self.attacker_piece = attacker_piece


class Text_Controller():
    arial_font = pygame.font.SysFont('Arial', 24)
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
    coor_letter_text_list = [coor_A_text, coor_B_text, coor_C_text, coor_D_text, coor_E_text, coor_F_text, coor_G_text, coor_H_text]
    coor_number_text_list = [coor_8_text, coor_7_text, coor_6_text, coor_5_text, coor_4_text, coor_3_text, coor_2_text, coor_1_text]
    check_checkmate_text = ""
    
    def reset():
        Text_Controller.check_checkmate_text = ""
    def flip_board():
        Text_Controller.coor_letter_text_list.reverse()
        Text_Controller.coor_number_text_list.reverse()
        
class Move_Controller():
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
            for grid in board.Grid.grid_list:
                if piece.color == "white":
                    list_of_attack_pieces = grid.coords_of_attacking_pieces['white']
                elif piece.color == "black":
                    list_of_attack_pieces = grid.coords_of_attacking_pieces['black']
                # If piece (that just moved) coordinate is same as grid coordinate
                if grid.coordinate == piece.coordinate:
                    # Going through list of other same color attackers (of new grid coordinate)
                    same_piece_list = []
                    for attacker_grid in list_of_attack_pieces:
                        # Pawn is only piece that can enter space without attacking it
                        if(board.Grid.grid_dict[attacker_grid].occupied_piece == piece_name \
                            and piece_name != "pawn" and special_abb != "=Q"):
                            same_piece_list.append(attacker_grid)
                    letter_coords = [coords_from_same_piece[0] for coords_from_same_piece in same_piece_list] 
                    number_coords = [coords_from_same_piece[1] for coords_from_same_piece in same_piece_list] 
                    if(len(same_piece_list) > 0 and ((piece.previous_coordinate[0] not in letter_coords and piece.previous_coordinate[1] in number_coords) \
                        or (piece.previous_coordinate[0] not in letter_coords and piece.previous_coordinate[1] not in number_coords))):
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
    def make_move(grid, piece, game_controller, PLAY_SPRITES):
        # Default captured_abb for function to be empty string
        captured_abb = ""
        # Castle, pawn promotion
        special_abb = ""
        # Check or checkmate
        check_abb = ""
        # White win, draw, black win
        game_controller.result_abb = "*"
        promoted_queen = None
        prior_moves_dict = {}
        # Taking a piece by checking if available grid is opposite color of piece
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
                            piece_captured.captured(game_controller.black_captured_x, initvar.BLACK_CAPTURED_Y)
                            game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                        elif piece_captured.color == "white":
                            piece_captured.captured(game_controller.white_captured_x, initvar.WHITE_CAPTURED_Y)
                            game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
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
                                black_pawn.captured(game_controller.black_captured_x, initvar.BLACK_CAPTURED_Y)
                                game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                                captured_abb = "x"
            elif piece in PlayPawn.black_pawn_list:
                for white_pawn in PlayPawn.white_pawn_list:
                    # Must include taken_off_board bool or else you get NoneType error
                    if white_pawn.taken_off_board == False:
                        if white_pawn.coordinate[0] == grid.coordinate[0] and \
                            int(white_pawn.coordinate[1]) == 4:
                                white_pawn.captured(game_controller.white_captured_x, initvar.WHITE_CAPTURED_Y)
                                game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                                captured_abb = "x"
                            
        # Reset en passant skipover for all squares
        for sub_grid in board.Grid.grid_list:
            sub_grid.en_passant_skipover = False
            
        # Grid is no longer occupied by a piece
        for old_grid in board.Grid.grid_list:
            if old_grid.coordinate == piece.coordinate:
                old_grid.occupied = False
                piece.previous_coordinate = old_grid.coordinate
                piece.coordinate_history[game_controller.move_counter] = {'before':piece.previous_coordinate}
                prior_moves_dict['before'] = piece.previous_coordinate
                old_grid.prior_move_color = True
            else:
                old_grid.prior_move_color = False
                old_grid.no_highlight()
                
        # Moving piece, removing piece and grid highlights, changing Turn
        piece.rect.topleft = grid.rect.topleft
        piece.coordinate = grid.coordinate
        piece.coordinate_history[game_controller.move_counter]['after'] = piece.coordinate
        prior_moves_dict['after'] = piece.coordinate
        grid.occupied = True
        piece.prior_move_color = True
        piece.no_highlight()
        
        #########
        # RULES AFTER MOVE
        #########
        
        # Enpassant Rule and Promotion Rule for Pawns
        if piece in PlayPawn.white_pawn_list:
            if int(piece.coordinate[1]) == 8:
                special_abb = "=Q"
                promoted_queen = PlayQueen(piece.coordinate, PLAY_SPRITES, "white")
                promoted_queen.previous_coordinate = piece.previous_coordinate
                # Take white pawn off the board
                piece.captured(game_controller.white_captured_x, initvar.WHITE_CAPTURED_Y)
                game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
            # Detects that pawn was just moved
            elif int(piece.coordinate[1]) == 4 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                int(piece.previous_coordinate[1]) == 2:
                for sub_grid in board.Grid.grid_list:
                    if sub_grid.coordinate[0] == piece.coordinate[0] and int(sub_grid.coordinate[1]) == int(piece.coordinate[1])-1:
                        sub_grid.en_passant_skipover = True
                    else:
                        sub_grid.en_passant_skipover = False
            else:
                grid.en_passant_skipover = False
        elif piece in PlayPawn.black_pawn_list:
            if int(piece.coordinate[1]) == 1:
                special_abb = "=Q"
                promoted_queen = PlayQueen(piece.coordinate, PLAY_SPRITES, "black")
                promoted_queen.previous_coordinate = piece.previous_coordinate
                # Take black pawn off the board
                piece.captured(game_controller.black_captured_x, initvar.BLACK_CAPTURED_Y)
                game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
            # Detects that pawn was just moved
            elif int(piece.coordinate[1]) == 5 and piece.previous_coordinate[0] == piece.coordinate[0] and \
                int(piece.previous_coordinate[1]) == 7:
                for sub_grid in board.Grid.grid_list:
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
                        rook.rect.topleft = board.Grid.grid_dict['d1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d1'].coordinate
                        board.Grid.grid_dict['d1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O-O"
                    elif rook.coordinate == 'h1' and piece.coordinate == 'g1':
                        rook.rect.topleft = board.Grid.grid_dict['f1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f1'].coordinate
                        board.Grid.grid_dict['f1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O"
        elif piece in PlayKing.black_king_list:
            piece.castled = True
            for rook in PlayRook.black_rook_list:
                if rook.allowed_to_castle == True:
                    if rook.coordinate == 'a8' and piece.coordinate == 'c8':
                        rook.rect.topleft = board.Grid.grid_dict['d8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d8'].coordinate
                        board.Grid.grid_dict['d8'].occupied = True
                        special_abb = "O-O-O"
                    elif rook.coordinate == 'h8' and piece.coordinate == 'g8':
                        rook.rect.topleft = board.Grid.grid_dict['f8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f8'].coordinate
                        board.Grid.grid_dict['f8'].occupied = True
                        special_abb = "O-O"
        elif piece in PlayRook.white_rook_list or PlayRook.black_rook_list:
            piece.allowed_to_castle = False
        # Update all grids to reflect the coordinates of the pieces
        Grid_Controller.update_grid(game_controller)
        # Switch turns
        if(game_controller.WHOSETURN == "white"):
            game_controller.switch_turn("black")
        elif(game_controller.WHOSETURN == "black"):
            game_controller.switch_turn("white")
            game_controller.move_counter += 1
            
        return prior_moves_dict, captured_abb, special_abb, promoted_queen
    
    def game_status_check(game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, promoted_queen=None):
        check_abb = ""
        if game_controller.color_in_check == "black":
            Text_Controller.check_checkmate_text = "Black King checked"
            for piece_list in [PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                               PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                               PlayQueen.black_queen_list, PlayKing.black_king_list]:
                for sub_piece in piece_list:
                    sub_piece.spaces_available(game_controller)
            def checkmate_check(game_controller):
                for subgrid in board.Grid.grid_list:
                    if len(subgrid.coords_of_available_pieces['black']) > 0:
                        # If able to detect that a grid can be available, that means it's NOT checkmate
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
                for subgrid in board.Grid.grid_list:
                    if len(subgrid.coords_of_available_pieces['white']) > 0:
                        # If able to detect that a grid can be available, that means it's NOT checkmate
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
                for subgrid in board.Grid.grid_list:
                    if len(subgrid.coords_of_available_pieces['white']) > 0:
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
                for subgrid in board.Grid.grid_list:
                    if len(subgrid.coords_of_available_pieces['black']) > 0:
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
            # Log the move
            # Record the move in the df_moves dataframe
            # Record the move in that piece's history
            # Record the move in the prior_moves_history then add that to prior_move_history dataframe
            # Automatically make the move the selected move (thus highlighting in right panel)
            if special_abb == "=Q":
                # When the piece became promoted to a Queen
                move_text = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb) + " "
                game_controller.df_moves.loc[game_controller.move_counter-1, "black_move"] = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                piece.coordinate_history[game_controller.move_counter-1]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                game_controller.selected_move = [game_controller.move_counter-1, Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb), "black"]
            else:
                move_text = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb) + " "
                game_controller.df_moves.loc[game_controller.move_counter-1, "black_move"] = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                piece.coordinate_history[game_controller.move_counter-1]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                game_controller.selected_move = [game_controller.move_counter-1, Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb), "black"]
            game_controller.df_prior_moves.loc[game_controller.move_counter-1, "black_move"] = str(prior_moves_dict)
        elif(game_controller.WHOSETURN == "black"):
            if special_abb == "=Q":
                move_text = str(game_controller.move_counter) + ". " + \
                      Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb) + " "
                game_controller.df_moves.loc[game_controller.move_counter] = [Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb), '']
                piece.coordinate_history[game_controller.move_counter]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb)
                game_controller.selected_move = [game_controller.move_counter, Move_Controller.move_translator(grid.occupied_piece, promoted_queen, captured_abb, special_abb, check_abb), "white"]
            else:
                move_text = str(game_controller.move_counter) + ". " + \
                      Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb) + " "
                game_controller.df_moves.loc[game_controller.move_counter] = [Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb), '']
                piece.coordinate_history[game_controller.move_counter]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb)
                game_controller.selected_move = [game_controller.move_counter, Move_Controller.move_translator(grid.occupied_piece, piece, captured_abb, special_abb, check_abb), "white"]
            game_controller.df_prior_moves.loc[game_controller.move_counter, "white_move"] = str(prior_moves_dict)
        log.info(move_text)
        if game_controller.result_abb != "*":
            log.info(game_controller.result_abb)
        
        return

def draw_text_on_rects_in_moves_pane(surface, my_font):
    for move_num_rect in MoveNumberRectangle.rectangle_list:
        if move_num_rect.text_is_visible == True:
            # Only draw the text if the rectangle is below the top of the pane
            move_num_text = my_font.render(move_num_rect.text, True, initvar.TEXT_COLOR)
            surface.blit(move_num_text, (move_num_rect.x, move_num_rect.y))
    for piece_move_rect in PieceMoveRectangle.rectangle_list:
        if piece_move_rect.text_is_visible == True:
            move_notation_text = my_font.render(piece_move_rect.move_notation, True, initvar.TEXT_COLOR)
            surface.blit(move_notation_text, (piece_move_rect.x, piece_move_rect.y))

def scroll_to_latest_move(latest_move_number):
    if latest_move_number > initvar.MOVES_PANE_MAX_MOVES:
        PanelRectangles.scroll_range[0] = latest_move_number - (initvar.MOVES_PANE_MAX_MOVES-1)
        PanelRectangles.scroll_range[1] = latest_move_number
        for move_num_rect in MoveNumberRectangle.rectangle_list:
            move_num_rect.update_Y()
        for piece_move_rect in PieceMoveRectangle.rectangle_list:
            piece_move_rect.update_Y()
            
def update_scroll_range(unit_change):
    # unit_change refers to how many moves up/down to go
    # unit_change = -1 means scrolling up one unit, unit_change = 1 means scrolling down one unit
    PanelRectangles.scroll_range[0] += unit_change
    PanelRectangles.scroll_range[1] += unit_change
    for move_num_rect in MoveNumberRectangle.rectangle_list:
        move_num_rect.update_Y()
    for piece_move_rect in PieceMoveRectangle.rectangle_list:
        piece_move_rect.update_Y()

def draw_move_rects_on_moves_pane(my_font, game_controller):
    if len(game_controller.df_moves) >= 1:
        # Creating move notation rectangles if they haven't been created before for the respective move
        # If the last move is not in the dictionary, then add it
        if len(game_controller.df_moves) not in PieceMoveRectangle.rectangle_dict:
            PieceMoveRectangle.rectangle_dict[len(game_controller.df_moves)] = []
            MoveNumberRectangle.rectangle_dict[len(game_controller.df_moves)] = []
        # We want the PieceMoveRectangle.rectangle_dict to correspond to the df_moves dataframe
        if game_controller.df_moves.loc[len(game_controller.df_moves), 'white_move'] != '' and len(PieceMoveRectangle.rectangle_dict[len(game_controller.df_moves)]) == 0:
            # Create new move number rectangle since white made a move
            MoveNumberRectangle(len(game_controller.df_moves), initvar.MOVES_PANE_MOVE_NUMBER_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(game_controller.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
            # Create rectangle which will eventually be used to blit text on it
            # Parameters: Total number of moves in the game, the move itself, the color of the piece that moved, and position & size of rectangle
            PieceMoveRectangle(len(game_controller.df_moves), game_controller.df_moves.loc[len(game_controller.df_moves), 'white_move'], 'white', initvar.MOVES_PANE_WHITE_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(game_controller.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
            # Scroll down automatically when a move is made
            scroll_to_latest_move(len(game_controller.df_moves))
        if game_controller.df_moves.loc[len(game_controller.df_moves), 'black_move'] != '' and len(PieceMoveRectangle.rectangle_dict[len(game_controller.df_moves)]) == 1:
            # Only create PieceMoveRectangle when black moved last, don't create a new MoveNumberRectangle
            PieceMoveRectangle(len(game_controller.df_moves), game_controller.df_moves.loc[len(game_controller.df_moves), 'black_move'], 'black', initvar.MOVES_PANE_BLACK_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(game_controller.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)        
            scroll_to_latest_move(len(game_controller.df_moves))
        draw_text_on_rects_in_moves_pane(SCREEN, my_font)

def main():
    try:
        #Tk box for color
        root = tk.Tk()
        root.withdraw()
        #Global variables
        MENUON = 1
        
        COLORKEY = initvar.COLORKEY_RGB
        
        RUNNING, DEBUG = 0, 1
        state = RUNNING
        debug_message = 0
        
        game_controller = Game_Controller()
        
        GAME_MODE_SPRITES = pygame.sprite.Group()
        
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
        
        PGN_WRITER_AND_LOADER = PGN_Writer_and_Loader()
        
        PLAY_EDIT_SWITCH_BUTTON = PlayEditSwitchButton(initvar.PLAY_EDIT_SWITCH_BUTTON_TOPLEFT, GAME_MODE_SPRITES)
        FLIP_BOARD_BUTTON = FlipBoardButton(initvar.FLIP_BOARD_BUTTON_TOPLEFT)
        GAME_PROPERTIES_BUTTON = GamePropertiesButton(initvar.GAME_PROPERTIES_BUTTON_TOPLEFT)
        INFO_BUTTON = InfoButton(initvar.INFO_BUTTON_TOPLEFT)
        POS_LOAD_FILE_BUTTON = PosLoadFileButton(initvar.POS_LOAD_FILE_BUTTON_TOPLEFT)
        POS_SAVE_FILE_BUTTON = PosSaveFileButton(initvar.POS_SAVE_FILE_BUTTON_TOPLEFT)
        PGN_LOAD_FILE_BUTTON = PGNLoadFileButton(initvar.PGN_LOAD_FILE_BUTTON_TOPLEFT)
        PGN_SAVE_FILE_BUTTON = PGNSaveFileButton(initvar.PGN_SAVE_FILE_BUTTON_TOPLEFT)
        COLOR_BUTTON = ColorButton(initvar.COLOR_BUTTON_TOPLEFT)
        RESET_BOARD_BUTTON = ResetBoardButton(initvar.RESET_BOARD_BUTTON_TOPLEFT)
        CLEAR_BUTTON = ClearButton(initvar.CLEAR_BUTTON_TOPLEFT)
        SCROLL_UP_BUTTON = ScrollUpButton(initvar.SCROLL_UP_BUTTON_TOPLEFT)
        SCROLL_DOWN_BUTTON = ScrollDownButton(initvar.SCROLL_DOWN_BUTTON_TOPLEFT)
        GAME_MODE_SPRITES.add(SCROLL_DOWN_BUTTON)
        BEGINNING_MOVE_BUTTON = BeginningMoveButton(initvar.BEGINNING_MOVE_BUTTON_TOPLEFT, PLAY_SPRITES)
        PREV_MOVE_BUTTON = PrevMoveButton(initvar.PREV_MOVE_BUTTON_TOPLEFT, PLAY_SPRITES)
        NEXT_MOVE_BUTTON = NextMoveButton(initvar.NEXT_MOVE_BUTTON_TOPLEFT, PLAY_SPRITES)
        LAST_MOVE_BUTTON = LastMoveButton(initvar.LAST_MOVE_BUTTON_TOPLEFT, PLAY_SPRITES)
        
        #Backgrounds
        INFO_SCREEN = pygame.image.load("Sprites/infoscreen.bmp").convert()
        INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (initvar.SCREEN_WIDTH, initvar.SCREEN_HEIGHT))
        #window
        gameicon = pygame.image.load("Sprites/chessico.png")
        pygame.display.set_icon(gameicon)
        pygame.display.set_caption('Chess')

                        
        # Load the starting positions of chessboard first
        pos_load_file(PLACED_SPRITES, COLORKEY, reset=True)
        MOUSE_COORD = ""
        
        def mouse_coordinate(mousepos):
            mouse_coord = ""
            for grid in board.Grid.grid_list:
                if grid.rect.collidepoint(mousepos):
                    mouse_coord = grid.coordinate
                    return mouse_coord
            return mouse_coord
            
        while True:
            CLOCK.tick(60)
            MOUSEPOS = pygame.mouse.get_pos()
            MOUSE_COORD = mouse_coordinate(MOUSEPOS)
            if state == RUNNING and MENUON == 1: # Initiate room
                #Start Objects
                START.white_pawn.rect.topleft = initvar.STARTPOS['white_pawn']
                START.white_bishop.rect.topleft = initvar.STARTPOS['white_bishop']
                START.white_knight.rect.topleft = initvar.STARTPOS['white_knight']
                START.white_rook.rect.topleft = initvar.STARTPOS['white_rook']
                START.white_queen.rect.topleft = initvar.STARTPOS['white_queen']
                START.white_king.rect.topleft = initvar.STARTPOS['white_king']
                START.black_pawn.rect.topleft = initvar.STARTPOS['black_pawn']
                START.black_bishop.rect.topleft = initvar.STARTPOS['black_bishop']
                START.black_knight.rect.topleft = initvar.STARTPOS['black_knight']
                START.black_rook.rect.topleft = initvar.STARTPOS['black_rook']
                START.black_queen.rect.topleft = initvar.STARTPOS['black_queen']
                START.black_king.rect.topleft = initvar.STARTPOS['black_king']
                
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
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[0] > board.X_GRID_END:
                        if SCROLL_UP_BUTTON.rect.collidepoint(MOUSEPOS) and PanelRectangles.scroll_range[0] > 1: # Scroll up
                            update_scroll_range(-1)
                        if SCROLL_DOWN_BUTTON.rect.collidepoint(MOUSEPOS) and len(MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and PanelRectangles.scroll_range[1] < len(MoveNumberRectangle.rectangle_list): # Scroll down
                            update_scroll_range(1)
                        if PGN_LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PGN_WRITER_AND_LOADER.pgn_load(game_controller, PLAY_SPRITES, PLAY_EDIT_SWITCH_BUTTON)
                            for grid in board.Grid.grid_list:
                                grid.no_highlight()
                            Grid_Controller.update_grid(game_controller)
                        if PGN_SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS):
                            PGN_WRITER_AND_LOADER.write_moves(game_controller.df_moves, game_controller.result_abb)
                        if FLIP_BOARD_BUTTON.rect.collidepoint(MOUSEPOS):
                            Grid_Controller.flip_grids()
                        # When clicking on a move on the right pane, it is your selected move
                        for piece_move_rect in PieceMoveRectangle.rectangle_list:
                            if piece_move_rect.rect.collidepoint(MOUSEPOS) and piece_move_rect.text_is_visible:
                                game_controller.selected_move[0] = piece_move_rect.move_number
                                game_controller.selected_move[1] = piece_move_rect.move_notation
                                game_controller.selected_move[2] = piece_move_rect.move_color
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
                                    START.start_obj_image_placeholder.flip_start_sprite(DRAGGING, list_of_start_objs.get(piece_name).rect.topleft)
                                
                    #################
                    # LEFT CLICK (PRESSED DOWN)
                    #################
                    
                    # Placed object placed on location of mouse release
                    elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                          MOUSEPOS[0] > initvar.X_GRID_START and MOUSEPOS[0] < board.X_GRID_END and
                          MOUSEPOS[1] > initvar.Y_GRID_START and MOUSEPOS[1] < board.Y_GRID_END): 
                        def dragging_to_placed_no_dups():
                            for piece_list in [PlacedPawn.white_pawn_list, PlacedBishop.white_bishop_list, 
                                               PlacedKnight.white_knight_list, PlacedRook.white_rook_list, 
                                               PlacedQueen.white_queen_list, PlacedKing.white_king_list,
                                               PlacedPawn.black_pawn_list, PlacedBishop.black_bishop_list, 
                                               PlacedKnight.black_knight_list, PlacedRook.black_rook_list, 
                                               PlacedQueen.black_queen_list, PlacedKing.black_king_list]:
                                # If there is already a piece on grid then don't create new Placed object
                                for piece in piece_list:
                                    if piece.coordinate == MOUSE_COORD:
                                        return
                            # Created Placed objects at the snapped grid location of the piece that's being dragged
                            if DRAGGING.white_pawn:
                                if int(MOUSE_COORD[1]) != 1 and int(MOUSE_COORD[1]) != 8:
                                    PlacedPawn(MOUSE_COORD, PLACED_SPRITES, "white")
                                else:
                                    log.info("You are not allowed to place a pawn on rank " + MOUSE_COORD[1])
                            elif DRAGGING.white_bishop:
                                PlacedBishop(MOUSE_COORD, PLACED_SPRITES, "white")
                            elif DRAGGING.white_knight:
                                PlacedKnight(MOUSE_COORD, PLACED_SPRITES, "white")
                            elif DRAGGING.white_rook:
                                PlacedRook(MOUSE_COORD, PLACED_SPRITES, "white")
                            elif DRAGGING.white_queen:
                                PlacedQueen(MOUSE_COORD, PLACED_SPRITES, "white")
                            elif DRAGGING.white_king:
                                if not PlacedKing.white_king_list:
                                    PlacedKing(MOUSE_COORD, PLACED_SPRITES, "white")
                                else:
                                    log.info("You can only have one white king.")
                            elif DRAGGING.black_pawn:
                                if int(MOUSE_COORD[1]) != 1 and int(MOUSE_COORD[1]) != 8:
                                    PlacedPawn(MOUSE_COORD, PLACED_SPRITES, "black")
                                else:
                                    log.info("You are not allowed to place a pawn on rank " + MOUSE_COORD[1])
                            elif DRAGGING.black_bishop:
                                PlacedBishop(MOUSE_COORD, PLACED_SPRITES, "black")
                            elif DRAGGING.black_knight:
                                PlacedKnight(MOUSE_COORD, PLACED_SPRITES, "black")
                            elif DRAGGING.black_rook:
                                PlacedRook(MOUSE_COORD, PLACED_SPRITES, "black")
                            elif DRAGGING.black_queen:
                                PlacedQueen(MOUSE_COORD, PLACED_SPRITES, "black")
                            elif DRAGGING.black_king:
                                if not PlacedKing.black_king_list:
                                    PlacedKing(MOUSE_COORD, PLACED_SPRITES, "black")
                                else:
                                    log.info("You can only have one black king.")
            
                        dragging_to_placed_no_dups()
        
                        # Moves piece
                        def update_pieces_and_board():
                            for grid in board.Grid.grid_list:
                                for piece_list in [PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                                                   PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                                                   PlayQueen.white_queen_list, PlayKing.white_king_list,
                                                   PlayPawn.black_pawn_list, PlayBishop.black_bishop_list, 
                                                   PlayKnight.black_knight_list, PlayRook.black_rook_list, 
                                                   PlayQueen.black_queen_list, PlayKing.black_king_list]:
                                    for piece in piece_list:
                                        # Reset the prior move color variable from all pieces
                                        piece.prior_move_color = False
                                        if (grid.rect.collidepoint(MOUSEPOS) \
                                            and ((piece.coordinate in grid.coords_of_available_pieces['white'] and piece.color == "white") \
                                                 or (piece.coordinate in grid.coords_of_available_pieces['black'] and piece.color == "black")) \
                                                     and piece.select==True):
                                            prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(grid, piece, game_controller, PLAY_SPRITES)
                                            Move_Controller.game_status_check(game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, promoted_queen)
                        update_pieces_and_board()
    
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
                                        for grid in board.Grid.grid_list:
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
                                        for grid in board.Grid.grid_list:
                                            grid.no_highlight()
                        # Just do this last, since we know only one piece will be selected
                        if clicked_piece is not None:
                            clicked_piece.highlight()
                            clicked_piece.spaces_available(game_controller)
                            clicked_piece = None
    
                    if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                        #scroll wheel
                        if event.button == 4: # Scroll up
                            if PanelRectangles.scroll_range[0] > 1:
                                update_scroll_range(-1)
                        if event.button == 5: # Scroll down
                            if len(MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and PanelRectangles.scroll_range[1] < len(MoveNumberRectangle.rectangle_list):
                                update_scroll_range(1)
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
                            game_controller.switch_mode(game_controller.PLAY_MODE, PLAY_EDIT_SWITCH_BUTTON)
                            game_controller.spawn_play_objects(PLAY_SPRITES)

                        #################
                        # LEFT CLICK (RELEASE) STOP BUTTON
                        #################
                        elif PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and game_controller.game_mode == game_controller.PLAY_MODE:
                            game_controller.switch_mode(game_controller.EDIT_MODE, PLAY_EDIT_SWITCH_BUTTON)
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
                        for grid in board.Grid.grid_list:
                            if grid.rect.collidepoint(MOUSEPOS):
                                log.info("Coordinate: " + str(grid.coordinate) \
                                       + ", White Pieces Attacking: " + str(grid.coords_of_attacking_pieces['white']) \
                                       + ", Black Pieces Attacking: " + str(grid.coords_of_attacking_pieces['black']) \
                                           + ", grid variable: " + str(grid.highlighted) \
                                               + ", White Pieces Available: " + str(grid.coords_of_available_pieces['white']) \
                                                   + ", Black Pieces Available: " + str(grid.coords_of_available_pieces['black']))
                                
                ##################
                # ALL EDIT ACTIONS
                ##################
                # Start piece is dragging according to where the mouse is
                if game_controller.game_mode == game_controller.EDIT_MODE:
                    def drag_and_replace_start_obj_image(dragging_obj, start_substitute_image, start_obj_pos, start_obj, mouse_pos):
                        if dragging_obj:
                            start_substitute_image.rect.topleft = start_obj_pos
                            start_obj.rect.topleft = (mouse_pos[0]-(start_obj.image.get_width()/2),
                                                      mouse_pos[1]-(start_obj.image.get_height()/2))
                        else:
                            start_obj.rect.topleft = start_obj_pos
                    drag_and_replace_start_obj_image(DRAGGING.white_pawn, START.start_obj_image_placeholder, initvar.STARTPOS['white_pawn'], START.white_pawn, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.white_bishop, START.start_obj_image_placeholder, initvar.STARTPOS['white_bishop'], START.white_bishop, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.white_knight, START.start_obj_image_placeholder, initvar.STARTPOS['white_knight'], START.white_knight, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.white_rook, START.start_obj_image_placeholder, initvar.STARTPOS['white_rook'], START.white_rook, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.white_queen, START.start_obj_image_placeholder, initvar.STARTPOS['white_queen'], START.white_queen, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.white_king, START.start_obj_image_placeholder, initvar.STARTPOS['white_king'], START.white_king, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_pawn, START.start_obj_image_placeholder, initvar.STARTPOS['black_pawn'], START.black_pawn, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_bishop, START.start_obj_image_placeholder, initvar.STARTPOS['black_bishop'], START.black_bishop, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_knight, START.start_obj_image_placeholder, initvar.STARTPOS['black_knight'], START.black_knight, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_rook, START.start_obj_image_placeholder, initvar.STARTPOS['black_rook'], START.black_rook, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_queen, START.start_obj_image_placeholder, initvar.STARTPOS['black_queen'], START.black_queen, MOUSEPOS)
                    drag_and_replace_start_obj_image(DRAGGING.black_king, START.start_obj_image_placeholder, initvar.STARTPOS['black_king'], START.black_king, MOUSEPOS)                      
            
                ##################
                # IN-GAME ACTIONS
                ##################
                if game_controller.game_mode == game_controller.PLAY_MODE:
                    pass
                #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
                
                #Update all sprites
                SCREEN.fill(COLORKEY)
                
                FLIP_BOARD_BUTTON.draw(SCREEN)
                GAME_MODE_SPRITES.draw(SCREEN)
                board.GRID_SPRITES.draw(SCREEN)
                Grid_Controller.update_grid(game_controller)
                
                SCREEN.blit(initvar.MOVE_BG_IMAGE, (initvar.MOVE_BG_IMAGE_HEIGHT,initvar.MOVE_BG_IMAGE_WIDTH))
                if(game_controller.game_mode == game_controller.EDIT_MODE): #Only draw placed sprites in editing mode
                    initvar.START_SPRITES.draw(SCREEN)
                    PLACED_SPRITES.update()
                    PLACED_SPRITES.draw(SCREEN)    
                elif(game_controller.game_mode == game_controller.PLAY_MODE): #Only draw play sprites in play mode
                    FLIP_BOARD_BUTTON.draw(SCREEN)
                    PLAY_SPRITES.update()
                    PLAY_SPRITES.draw(SCREEN)
                    PGN_SAVE_FILE_BUTTON.draw(SCREEN)
                    
                # When the piece is selected on the right pane, fill the rectangle corresponding to the move
                for piece_move_rect in PieceMoveRectangle.rectangle_list:
                    if piece_move_rect.move_number == game_controller.selected_move[0] and piece_move_rect.move_notation == game_controller.selected_move[1]\
                        and piece_move_rect.move_color == game_controller.selected_move[2]:
                            piece_move_rect.draw(SCREEN)
                draw_move_rects_on_moves_pane(move_notation_font, game_controller)
                # Update objects that aren't in a sprite group
                SCROLL_UP_BUTTON.draw(SCREEN)
                SCROLL_DOWN_BUTTON.draw(SCREEN, len(game_controller.df_moves))
                # Board Coordinates Drawing
                for text in range(0,len(Text_Controller.coor_letter_text_list)):
                    SCREEN.blit(Text_Controller.coor_letter_text_list[text], (initvar.X_GRID_START+initvar.X_GRID_WIDTH/3+(initvar.X_GRID_WIDTH*text), initvar.Y_GRID_START-(initvar.Y_GRID_HEIGHT*0.75)))
                    SCREEN.blit(Text_Controller.coor_letter_text_list[text], (initvar.X_GRID_START+initvar.X_GRID_WIDTH/3+(initvar.X_GRID_WIDTH*text), board.Y_GRID_END+(initvar.Y_GRID_HEIGHT*0.25)))
                for text in range(0,len(Text_Controller.coor_number_text_list)):
                    SCREEN.blit(Text_Controller.coor_number_text_list[text], (initvar.X_GRID_START-initvar.X_GRID_WIDTH/2, initvar.Y_GRID_START+initvar.Y_GRID_HEIGHT/4+(initvar.Y_GRID_HEIGHT*text)))
                    SCREEN.blit(Text_Controller.coor_number_text_list[text], (board.X_GRID_END+initvar.X_GRID_WIDTH/3, initvar.Y_GRID_START+initvar.Y_GRID_HEIGHT/4+(initvar.Y_GRID_HEIGHT*text)))
                if(game_controller.game_mode == game_controller.PLAY_MODE):
                    check_checkmate_text_render = arial_font.render(Text_Controller.check_checkmate_text, 1, (0, 0, 0))
                    if game_controller.WHOSETURN == "white":
                        whose_turn_text = arial_font.render("White's move", 1, (0, 0, 0))
                    elif game_controller.WHOSETURN == "black":
                        whose_turn_text = arial_font.render("Black's move", 1, (0, 0, 0))
                    SCREEN.blit(whose_turn_text, (board.X_GRID_END+initvar.X_GRID_WIDTH, initvar.SCREEN_HEIGHT/2))
                    SCREEN.blit(check_checkmate_text_render, (board.X_GRID_END+initvar.X_GRID_WIDTH, 200))
                pygame.display.update()
            elif state == DEBUG:
                if debug_message == 1:
                    log.info("Entering debug mode")
                    debug_message = 0
                    # USE BREAKPOINT HERE
                    #print(str(MOUSE_COORD))
                    #print(str(game_controller.df_prior_moves))
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