"""
Chess created by Brad Wyatt

Features To-Do (short-term):
Menu objects are still invisible yet can be clickable

Clean Code Ideas:
Re-examine sprite groups
Edit_Mode_Controller to handle all the clicking event functions
Panel classes in separate file (instead of menu_buttons)
Getting rid of import *
Splitting groups of statements that were for after clicking into functions and methods within class
Feedback

Features To-Do (long-term):
Customized Turns for black and white (in these cases, substitute first move with "" ?)
Choose piece for Promotion
Sounds
If no king then don't start game
Themes
Grid using color rather than sprite
AI
"""
import board
import start_objects
import placed_objects
import play_objects
import replayed_objects
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
from tkinter import ttk  
import ast
import pygame
import datetime
import logging
import logging.handlers
import pandas as pd
import numpy as np
import initvar
import PySimpleGUI as sg


#############
# Logging
#############

today = datetime.datetime.today()
log = logging.getLogger("log_guy")
log.handlers = []
log.setLevel(logging.INFO)

# Handlers for logging errors
if initvar.exe_mode == False:
    log_file_name = "{0}.log".format(today.strftime("%Y-%m-%d %H%M%S"))
    log_file = os.path.join("C:/Users/Brad/Documents/GitHub/Chess-WORK-IN-PROGRESS-/logs/", log_file_name)
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

def pos_load_file(reset=False):
    open_file = None
    if reset == True:
        loaded_dict = {'white_pawn': ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
                       'white_bishop': ['c1', 'f1'], 'white_knight': ['b1', 'g1'],
                       'white_rook': ['a1', 'h1'], 'white_queen': ['d1'], 'white_king': ['e1'],
                       'black_pawn': ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
                       'black_bishop': ['c8', 'f8'], 'black_knight': ['b8', 'g8'],
                       'black_rook': ['a8', 'h8'], 'black_queen': ['d8'], 'black_king': ['e8'],
                       'RGB': Preferences.colorkey}
    else:
        request_file_name = askopenfilename(defaultextension=".lvl")
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return
        loaded_file = open_file.read()
        loaded_dict = ast.literal_eval(loaded_file)
    
    for obj_list in play_objects.Piece_Lists_Shortcut.all_pieces():
        for obj in obj_list:
            obj.destroy()
    if open_file:
        open_file.close()
    
    log.info("Removing sprites and loading piece positions...")
    
    # Removes all placed lists
    placed_objects.remove_all_placed()
    
    for white_pawn_pos in loaded_dict['white_pawn']:
        placed_objects.PlacedPawn(white_pawn_pos, "white")
    for white_bishop_pos in loaded_dict['white_bishop']:
        placed_objects.PlacedBishop(white_bishop_pos, "white")
    for white_knight_pos in loaded_dict['white_knight']:
        placed_objects.PlacedKnight(white_knight_pos, "white")
    for white_rook_pos in loaded_dict['white_rook']:
        placed_objects.PlacedRook(white_rook_pos, "white")
    for white_queen_pos in loaded_dict['white_queen']:
        placed_objects.PlacedQueen(white_queen_pos, "white")
    for white_king_pos in loaded_dict['white_king']:
        placed_objects.PlacedKing(white_king_pos, "white")
    for black_pawn_pos in loaded_dict['black_pawn']:
        placed_objects.PlacedPawn(black_pawn_pos, "black")
    for black_bishop_pos in loaded_dict['black_bishop']:
        placed_objects.PlacedBishop(black_bishop_pos, "black")
    for black_knight_pos in loaded_dict['black_knight']:
        placed_objects.PlacedKnight(black_knight_pos, "black")
    for black_rook_pos in loaded_dict['black_rook']:
        placed_objects.PlacedRook(black_rook_pos, "black")
    for black_queen_pos in loaded_dict['black_queen']:
        placed_objects.PlacedQueen(black_queen_pos, "black")
    for black_king_pos in loaded_dict['black_king']:
        placed_objects.PlacedKing(black_king_pos, "black")
    Preferences.colorkey = loaded_dict['RGB']
    
    log.info("Positioning Loaded Successfully")
    return

            
# Returns the tuples of each objects' positions within all classes
def get_dict_rect_positions():
    total_placed_list = {'white_pawn': placed_objects.PlacedPawn.white_pawn_list, 'white_bishop': placed_objects.PlacedBishop.white_bishop_list, 
                         'white_knight': placed_objects.PlacedKnight.white_knight_list, 'white_rook': placed_objects.PlacedRook.white_rook_list,
                         'white_queen': placed_objects.PlacedQueen.white_queen_list, 'white_king': placed_objects.PlacedKing.white_king_list,
                         'black_pawn': placed_objects.PlacedPawn.black_pawn_list, 'black_bishop': placed_objects.PlacedBishop.black_bishop_list,
                         'black_knight': placed_objects.PlacedKnight.black_knight_list, 'black_rook': placed_objects.PlacedRook.black_rook_list,
                         'black_queen': placed_objects.PlacedQueen.black_queen_list, 'black_king': placed_objects.PlacedKing.black_king_list}
    get_coord_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_coord in item_list:
            item_list_in_name.append(item_coord.coordinate)
        get_coord_for_all_obj[item_key] = item_list_in_name
    return get_coord_for_all_obj

def pos_save_file():
    try:
        # default extension is optional, here will add .txt if missing
        save_file_prompt = asksaveasfilename(defaultextension=".lvl")
        save_file_name = open(save_file_prompt, "w")
        if save_file_name is not None:
            # Write the file to disk
            obj_locations = copy.deepcopy(get_dict_rect_positions())
            obj_locations['RGB'] = Preferences.colorkey
            save_file_name.write(str(obj_locations))
            save_file_name.close()
            log.info("File Saved Successfully.")
        else:
            log.info("Error! Need king to save!")
    except IOError:
        log.info("Save File Error (IOError)")

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

class Preferences():
    colorkey = initvar.COLORKEY_RGB
    Event = ""
    Site = ""
    Date = ""
    Round = ""
    White = ""
    Black = ""
    Result = ""
    WhiteElo = ""
    BlackElo = ""
    ECO = ""
    TimeControl = "0"
    def get_color():
        color = askcolor()
        return [color[0][0], color[0][1], color[0][2]]
    def game_properties_popup():
        layout = [
            [sg.Text('Please enter the information for the game below (all fields are optional)')],
            [sg.Text('Event', size=(9, 0)), sg.InputText(default_text=Preferences.Event)],
            [sg.Text('Site', size=(9, 0)), sg.InputText(default_text=Preferences.Site)],
            [sg.Text('Date', size=(9, 0)), sg.InputText(default_text=Preferences.Date)],
            [sg.Text('Round', size=(9, 0)), sg.InputText(default_text=Preferences.Round)],
            [sg.Text('White', size=(9, 0)), sg.InputText(default_text=Preferences.White)],
            [sg.Text('Black', size=(9, 0)), sg.InputText(default_text=Preferences.Black)],
            [sg.Text('Result', size=(9, 0)), sg.InputText(default_text=Preferences.Result)],
            [sg.Text('WhiteElo', size=(9, 0)), sg.InputText(default_text=Preferences.WhiteElo)],
            [sg.Text('BlackElo', size=(9, 0)), sg.InputText(default_text=Preferences.BlackElo)],
            [sg.Text('ECO', size=(9, 0)), sg.InputText(default_text=Preferences.ECO)],
            [sg.Text('TimeControl', size=(9, 0)), sg.InputText(default_text=Preferences.TimeControl)],
            [sg.Submit("Ok"), sg.Cancel("Cancel")]
        ]
        #Please enter the information for the game below. All fields are optional.
        window = sg.Window('Game Properties', layout, element_justification='center')
        event, values = window.read()
        window.close()
        if event == 'Cancel' or event == None:
            return
        else:
            Preferences.Event = values[0]
            Preferences.Site = values[1]
            Preferences.Date = values[2]
            Preferences.Round = values[3]
            Preferences.White = values[4]
            Preferences.Black = values[5]
            Preferences.Result = values[6]
            Preferences.WhiteElo = values[7]
            Preferences.BlackElo = values[8]
            Preferences.ECO = values[9]
            Preferences.TimeControl = values[10]

class PGN_Writer_and_Loader():
    def write_moves(df_moves, result_abb):
        try:
            df = df_moves.copy()
            save_file_prompt = asksaveasfilename(defaultextension=".pgn")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                pgn_output = ""
                pgn_output += '[Event "' + Preferences.Event + '"]\n'
                pgn_output += '[Site "' + Preferences.Site + '"]\n'
                pgn_output += '[Date "' + Preferences.Date + '"]\n'
                pgn_output += '[Round "' + Preferences.Round + '"]\n'
                pgn_output += '[White "' + Preferences.White + '"]\n'
                pgn_output += '[Black "' + Preferences.Black + '"]\n'
                pgn_output += '[Result "' + Preferences.Result + '"]\n'
                pgn_output += '[ECO "' + Preferences.ECO + '"]\n'
                pgn_output += '[TimeControl "' + Preferences.TimeControl + '"]\n'
                pgn_output += '[WhiteElo "' + Preferences.WhiteElo + '"]\n'
                pgn_output += '[BlackElo "' + Preferences.BlackElo + '"]\n\n'
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
            log.info("Save File Error (IOError)")
    def pgn_load(PLAY_EDIT_SWITCH_BUTTON):
        open_file = None
        request_file_name = askopenfilename(defaultextension=".pgn")
        log.info("Loading " + os.path.basename(request_file_name))
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return
        Switch_Modes_Controller.switch_mode(Switch_Modes_Controller.PLAY_MODE, PLAY_EDIT_SWITCH_BUTTON)
        game_controller = Game_Controller(Grid_Controller.flipped)
        game_controller.refresh_objects()
        
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
            Preferences.Event = parameters['Event'].replace('"', '')
        except KeyError:
            Preferences.Event = ""
        try:
            Preferences.Site = parameters['Site'].replace('"', '')
        except KeyError:
            Preferences.Site = ""
        try:
            Preferences.Date = parameters['Date'].replace('"', '')
        except KeyError:
            Preferences.Date = ""
        try:
            Preferences.Round = parameters['Round'].replace('"', '')
        except KeyError:
            Preferences.Round = ""
        try:
            Preferences.White = parameters['White'].replace('"', '')
        except KeyError:
            Preferences.White = ""
        try:
            Preferences.Black = parameters['Black'].replace('"', '')
        except KeyError:
            Preferences.Black = ""
        try:
            Preferences.Result = parameters['Result'].replace('"', '')
        except KeyError:
            Preferences.Result = ""
        try:
            Preferences.WhiteElo = parameters['WhiteElo'].replace('"', '')
        except KeyError:
            Preferences.WhiteElo = ""
        try:
            Preferences.BlackElo = parameters['BlackElo'].replace('"', '')
        except KeyError:
            Preferences.BlackElo = ""
        try:
            Preferences.ECO = parameters['ECO'].replace('"', '')
        except KeyError:
            Preferences.ECO = ""
        try:
            Preferences.TimeControl = parameters['TimeControl'].replace('"', '')
        except KeyError:
            Preferences.TimeControl = "0"
        
        # Removes line breaks and formulates all elements into one element in the list
        chess_game = "".join(chess_game).split("  ")
        
        number_move_splits = "".join(chess_game).split()
        
        def determine_piece_list(piece_abb, whoseturn):
            if whoseturn == "white":
                if piece_abb == "N":
                    return play_objects.PlayKnight.white_knight_list
                elif piece_abb == "B":
                    return play_objects.PlayBishop.white_bishop_list
                elif piece_abb == "R":
                    return play_objects.PlayRook.white_rook_list
                elif piece_abb == "Q":
                    return play_objects.PlayQueen.white_queen_list
                elif piece_abb == "K":
                    return play_objects.PlayKing.white_king_list
                else:
                    return play_objects.PlayPawn.white_pawn_list
            elif whoseturn == "black":
                if piece_abb == "N":
                    return play_objects.PlayKnight.black_knight_list
                elif piece_abb == "B":
                    return play_objects.PlayBishop.black_bishop_list
                elif piece_abb == "R":
                    return play_objects.PlayRook.black_rook_list
                elif piece_abb == "Q":
                    return play_objects.PlayQueen.black_queen_list
                elif piece_abb == "K":
                    return play_objects.PlayKing.black_king_list
                else:
                    return play_objects.PlayPawn.black_pawn_list
                
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
            elif(piece_list != play_objects.PlayPawn.white_pawn_list and piece_list != play_objects.PlayPawn.black_pawn_list):
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
                        type_of_piece_list = play_objects.PlayKing.white_king_list
                        grid_coordinate = 'g1'
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = play_objects.PlayKing.black_king_list
                        grid_coordinate = 'g8'
                    piece = type_of_piece_list[0]
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = Move_Controller.game_status_check(game_controller)
                    Move_Controller.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                elif move == "O-O-O":
                    if game_controller.WHOSETURN == "white":
                        type_of_piece_list = play_objects.PlayKing.white_king_list
                        grid_coordinate = 'c1'
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = play_objects.PlayKing.black_king_list
                        grid_coordinate = 'c8'
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = Move_Controller.game_status_check(game_controller)
                    Move_Controller.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                elif move[-2:] == "=Q":
                    if game_controller.WHOSETURN == "white":
                        type_of_piece_list = play_objects.PlayPawn.white_pawn_list
                    elif game_controller.WHOSETURN == "black":
                        type_of_piece_list = play_objects.PlayPawn.black_pawn_list
                    grid_coordinate = move[-4:-2]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = Move_Controller.game_status_check(game_controller)
                    Move_Controller.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)                    
                else:
                    # NORMAL MOVES
                    # Last 2 characters are always the coordinate of the grid besides special exceptions above
                    type_of_piece_list = determine_piece_list(move[0], game_controller.WHOSETURN)
                    if move[-1] == "+" or move[-1] == "#":
                        grid_coordinate = move[-3:-1]
                    else:
                        grid_coordinate = move[-2:]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = Move_Controller.game_status_check(game_controller)                    
                    Move_Controller.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)                    
                Panel_Controller.draw_move_rects_on_moves_pane(pygame.font.SysFont('Arial', 16), game_controller)
                
        def prior_move_off(current_coord):
            for play_obj_list in play_objects.Piece_Lists_Shortcut.all_pieces():
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
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.spaces_available(game_controller)
            
        log.info("PGN Finished Loading")
        return game_controller

class Edit_Mode_Controller():
    def right_click_destroy(MOUSEPOS):
        start_objects.Dragging.dragging_all_false()
        start_objects.Start.restart_start_positions()
        placed_objects.remove_placed_object(MOUSEPOS)


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
    def grid_occupied_by_piece(grid):
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if grid.rect.topleft == piece.rect.topleft:
                    grid.occupied = True
                    if piece.color == "white":
                        grid.occupied_piece_color = "white"
                    elif piece.color == "black":
                        grid.occupied_piece_color = "black"
                    if(piece in play_objects.PlayPawn.white_pawn_list or piece in play_objects.PlayPawn.black_pawn_list):
                        grid.occupied_piece = "pawn"
                    elif(piece in play_objects.PlayBishop.white_bishop_list or piece in play_objects.PlayBishop.black_bishop_list):
                        grid.occupied_piece = "bishop"
                    elif(piece in play_objects.PlayKnight.white_knight_list or piece in play_objects.PlayKnight.black_knight_list):
                        grid.occupied_piece = "knight"
                    elif(piece in play_objects.PlayRook.white_rook_list or piece in play_objects.PlayRook.black_rook_list):
                        grid.occupied_piece = "rook"
                    elif(piece in play_objects.PlayQueen.white_queen_list or piece in play_objects.PlayQueen.black_queen_list):
                        grid.occupied_piece = "queen"
                    elif(piece in play_objects.PlayKing.white_king_list or piece in play_objects.PlayKing.black_king_list):
                        grid.occupied_piece = "king"
                    return
        else:
            grid.occupied = False
            grid.occupied_piece = ""
            grid.occupied_piece_color = ""
    def update_grid_occupied_detection():
        for grid in board.Grid.grid_list:
            if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE:
                Grid_Controller.grid_occupied_by_piece(grid)
    def prior_move_color(grid_coordinate, prior_move_piece):
        for grid in board.Grid.grid_list:
            if grid.coordinate == grid_coordinate:
                grid.prior_move_color = True
            else:
                grid.prior_move_color = False
            grid.no_highlight()
        if Switch_Modes_Controller.REPLAYED == False:
            # Updating prior move sprites for play objects
            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if piece == prior_move_piece:
                        piece.prior_move_color = True
                    else:
                        piece.prior_move_color = False
                    piece.no_highlight()
        else:
            # Updating prior move sprites for replayed objects
            for piece_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if piece == prior_move_piece:
                        piece.prior_move_color = True
                    else:
                        piece.prior_move_color = False
                    piece.prior_move_update()
            #print("Does piece have red color? " + str(prior_move_piece.prior_move_color))
    def piece_on_grid(grid_coordinate):
        if Switch_Modes_Controller.REPLAYED == False:
            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if grid_coordinate == piece.coordinate:
                        return piece
        else:
            for piece_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if grid_coordinate == piece.coordinate:
                        return piece
    def update_prior_move_color(whoseturn=None):
        if Move_Tracker.move_counter() == 0:
            for grid in board.Grid.grid_list:
                grid.prior_move_color = False
                grid.no_highlight()
            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    piece.prior_move_color = False
                    piece.no_highlight()
        if whoseturn == "white":
            for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for piece in piece_list:
                    for move_num in piece.coordinate_history:
                        if move_num == Move_Tracker.move_counter():
                            Grid_Controller.prior_move_color(piece.coordinate_history[move_num]['before'], piece)
        elif whoseturn == "black":
            for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                for piece in piece_list:
                    for move_num in piece.coordinate_history:
                        if move_num == Move_Tracker.move_counter():
                            Grid_Controller.prior_move_color(piece.coordinate_history[move_num]['before'], piece)
        else:
            # Replayed use case
            for grid in board.Grid.grid_list:
                grid.prior_move_color = False
                grid.no_highlight()
            for piece_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    piece.prior_move_color = False
                    piece.prior_move_update()
        

class Switch_Modes_Controller():
    EDIT_MODE, PLAY_MODE = 0, 1
    GAME_MODE = EDIT_MODE
    REPLAYED = False
    def switch_mode(game_mode, PLAY_EDIT_SWITCH_BUTTON):
        if game_mode == Switch_Modes_Controller.EDIT_MODE:
            log.info("\nEditing Mode Activated\n")
            Switch_Modes_Controller.GAME_MODE = Switch_Modes_Controller.EDIT_MODE
            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(Switch_Modes_Controller.GAME_MODE)
            Text_Controller.check_checkmate_text = ""
        elif game_mode == Switch_Modes_Controller.PLAY_MODE:
            log.info("Play Mode Activated\n")
            Switch_Modes_Controller.GAME_MODE = Switch_Modes_Controller.PLAY_MODE
            PLAY_EDIT_SWITCH_BUTTON.image = PLAY_EDIT_SWITCH_BUTTON.game_mode_button(Switch_Modes_Controller.GAME_MODE)
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedPawn.white_pawn_list, play_objects.PlayPawn, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedBishop.white_bishop_list, play_objects.PlayBishop, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedKnight.white_knight_list, play_objects.PlayKnight, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedRook.white_rook_list, play_objects.PlayRook, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedQueen.white_queen_list, play_objects.PlayQueen, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedKing.white_king_list, play_objects.PlayKing, "white")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedPawn.black_pawn_list, play_objects.PlayPawn, "black")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedBishop.black_bishop_list, play_objects.PlayBishop, "black")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedKnight.black_knight_list, play_objects.PlayKnight, "black")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedRook.black_rook_list, play_objects.PlayRook, "black")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedQueen.black_queen_list, play_objects.PlayQueen, "black")
            Switch_Modes_Controller.placed_to_play(placed_objects.PlacedKing.black_king_list, play_objects.PlayKing, "black")
            Move_Tracker.restart()
    def placed_to_play(placed_list, class_obj, color):
        # Play pieces spawn where their placed piece correspondents are located
        for placed_obj in placed_list:
            class_obj(placed_obj.coordinate, color)
    def play_to_replayed(play_list, class_obj, color):
        # Play pieces spawn where their placed piece correspondents are located
        for play_obj in play_list:
            if play_obj.coordinate is not None:
                class_obj(color, play_obj.coordinate_history, coord=play_obj.coordinate)
            elif play_obj.coordinate is None:
                class_obj(color, play_obj.coordinate_history, 
                          captured_move_number_and_coordinate=play_obj.captured_move_number_and_coordinate, 
                          out_of_bounds_x_y=play_obj.rect.topleft)
    def rewind_moves(start_beginning=False):
        first_move = Switch_Modes_Controller.list_of_moves_backwards(Move_Tracker.df_prior_moves)[-1]
        list_of_moves_backwards = Switch_Modes_Controller.list_of_moves_backwards(Move_Tracker.df_prior_moves)[:-1]
        if start_beginning == True:
            list_of_moves_backwards.append(first_move)
        # list_of_moves_backwards list is ordered in descending order to the selected move
        for move_dict in list_of_moves_backwards:
            for replayed_obj_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for replayed_obj in replayed_obj_list:
                    for piece_history in replayed_obj.coordinate_history:
                        if piece_history in dict(move_dict):
                            if replayed_obj.coordinate_history[piece_history] == ast.literal_eval(move_dict[piece_history]):
                                replayed_obj.coordinate = ast.literal_eval(move_dict[piece_history])['before']
                                Grid_Controller.prior_move_color(replayed_obj.coordinate, replayed_obj)
                                if ast.literal_eval(move_dict[piece_history])['move_notation'] == "O-O":
                                    if replayed_obj.color == "white":
                                        Grid_Controller.piece_on_grid('f1').coordinate = 'h1'
                                    elif replayed_obj.color == "black":
                                        Grid_Controller.piece_on_grid('f8').coordinate = 'h8'
                                elif ast.literal_eval(move_dict[piece_history])['move_notation'] == "O-O-O":
                                    if replayed_obj.color == "white":
                                        Grid_Controller.piece_on_grid('d1').coordinate = 'a1'
                                    elif replayed_obj.color == "black":
                                        Grid_Controller.piece_on_grid('d8').coordinate = 'a8'
                                if "x" in ast.literal_eval(move_dict[piece_history])['move_notation']:
                                    if replayed_obj.color == "white":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.black_pieces():
                                            for piece in piece_list:
                                                if piece.captured_move_number_and_coordinate:
                                                    if piece.captured_move_number_and_coordinate['move_number'] == piece_history:
                                                        if 'ep_grid_after_coord' in piece.captured_move_number_and_coordinate:
                                                            # En Passant exception
                                                            piece.coordinate = piece.captured_move_number_and_coordinate['ep_grid_after_coord'][0] + str(int(piece.captured_move_number_and_coordinate['ep_grid_after_coord'][1])-1)
                                                        else:
                                                            piece.coordinate = ast.literal_eval(move_dict[piece_history])['after']
                                    elif replayed_obj.color == "black":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.white_pieces():
                                            for piece in piece_list:
                                                if piece.captured_move_number_and_coordinate:
                                                    if piece.captured_move_number_and_coordinate['move_number'] == piece_history:
                                                        if 'ep_grid_after_coord' in piece.captured_move_number_and_coordinate:
                                                            # En Passant exception
                                                            piece.coordinate = piece.captured_move_number_and_coordinate['ep_grid_after_coord'][0] + str(int(piece.captured_move_number_and_coordinate['ep_grid_after_coord'][1])+1)
                                                        else:
                                                            piece.coordinate = ast.literal_eval(move_dict[piece_history])['after']
                                if "=Q" in ast.literal_eval(move_dict[piece_history])['move_notation']:
                                    if replayed_obj.color == "white":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.white_pieces():
                                            for piece in replayed_objects.ReplayedQueen.white_queen_list:
                                                if piece.coordinate == eval(Move_Tracker.df_prior_moves.loc[piece_history, "white_move"])['after']:
                                                    piece.kill()
                                                    replayed_objects.ReplayedQueen.white_queen_list.remove(piece)
                                    elif replayed_obj.color == "black":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.black_pieces():
                                            for piece in replayed_objects.ReplayedQueen.black_queen_list:
                                                if piece.coordinate == eval(Move_Tracker.df_prior_moves.loc[piece_history, "black_move"])['after']:
                                                    piece.kill()
                                                    replayed_objects.ReplayedQueen.black_queen_list.remove(piece)
        # -1 in the list refers to the highlighted move in the pane
        # Retrieve the grids from the piece that we are replaying, and get the grid from the previous move to that one
        prior_move_grid_and_piece_highlight_dict = Switch_Modes_Controller.list_of_moves_backwards(Move_Tracker.df_prior_moves)[-1]
        old_grid_coordinate_before = ast.literal_eval(list(prior_move_grid_and_piece_highlight_dict.values())[0])['before']
        old_grid_coordinate_after = ast.literal_eval(list(prior_move_grid_and_piece_highlight_dict.values())[0])['after']
        old_piece = Grid_Controller.piece_on_grid(old_grid_coordinate_after)
        Grid_Controller.prior_move_color(old_grid_coordinate_before, old_piece)
    def replayed_game(replayed, game_controller, start_beginning=False):
        Switch_Modes_Controller.REPLAYED = replayed
        if Switch_Modes_Controller.REPLAYED == True:
            replayed_objects.remove_all_replayed()
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayPawn.white_pawn_list, replayed_objects.ReplayedPawn, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayBishop.white_bishop_list, replayed_objects.ReplayedBishop, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayKnight.white_knight_list, replayed_objects.ReplayedKnight, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayRook.white_rook_list, replayed_objects.ReplayedRook, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayQueen.white_queen_list, replayed_objects.ReplayedQueen, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayKing.white_king_list, replayed_objects.ReplayedKing, "white")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayPawn.black_pawn_list, replayed_objects.ReplayedPawn, "black")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayBishop.black_bishop_list, replayed_objects.ReplayedBishop, "black")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayKnight.black_knight_list, replayed_objects.ReplayedKnight, "black")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayRook.black_rook_list, replayed_objects.ReplayedRook, "black")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayQueen.black_queen_list, replayed_objects.ReplayedQueen, "black")
            Switch_Modes_Controller.play_to_replayed(play_objects.PlayKing.black_king_list, replayed_objects.ReplayedKing, "black")
            Switch_Modes_Controller.rewind_moves(start_beginning)
        else:
            replayed_objects.remove_all_replayed()
            Grid_Controller.update_prior_move_color(game_controller.WHOSETURN)
    def list_of_moves_backwards(df_prior_moves):
        moves_backwards_list = []
        limit_moves = Move_Tracker.selected_move[0]
        limit_color = Move_Tracker.selected_move[1]
        for move_num in range(Move_Tracker.move_counter(), limit_moves-1, -1):
            moves_backwards_dict = {}
            if limit_color == 'black_move' and move_num == limit_moves:
                # Selected move is black, so ignore the white move on that same move number and break 
                moves_backwards_dict[move_num] = df_prior_moves.loc[move_num, 'black_move']
                moves_backwards_list.append(moves_backwards_dict)
                break
            elif df_prior_moves.loc[move_num, 'black_move'] == '':
                # Current move has no black move yet, so ignore adding that to list
                pass
            else:
                moves_backwards_dict[move_num] = df_prior_moves.loc[move_num, 'black_move']
                moves_backwards_list.append(moves_backwards_dict)
                moves_backwards_dict = {}
            moves_backwards_dict[move_num] = df_prior_moves.loc[move_num, 'white_move']
            moves_backwards_list.append(moves_backwards_dict)
        # When select a move on pane, we take back the move right after that
        return moves_backwards_list
        

class Move_Tracker():
    df_moves = pd.DataFrame(columns=["white_move", "black_move"])
    df_moves.index = np.arange(1, len(df_moves)+1)
    df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
    df_prior_moves.index = np.arange(1, len(df_prior_moves)+1)
    move_counter = lambda : len(Move_Tracker.df_moves)
    selected_move = (0, "")
    def restart():
        Move_Tracker.df_moves = pd.DataFrame(columns=["white_move", "black_move"])
        Move_Tracker.df_moves.index = np.arange(1, len(Move_Tracker.df_moves)+1)
        Move_Tracker.df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
        Move_Tracker.df_prior_moves.index = np.arange(1, len(Move_Tracker.df_prior_moves)+1)
        #%% The below 1 line may need to be deleted
        Move_Tracker.move_counter = lambda : len(Move_Tracker.df_moves) 
        Move_Tracker.selected_move = (0, "")
    def undo_move_in_dfs(undo_color):
        if undo_color == "black":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if Move_Tracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[Move_Tracker.move_counter()]
            Move_Tracker.selected_move = (Move_Tracker.move_counter(), "white_move")
            Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] = ''
            Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "black_move"] = ''
            
        elif undo_color == "white":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if Move_Tracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[Move_Tracker.move_counter()]
            Move_Tracker.selected_move = (Move_Tracker.move_counter()-1, "black_move")
            Move_Tracker.df_moves = Move_Tracker.df_moves.iloc[:-1]
            Move_Tracker.df_prior_moves = Move_Tracker.df_prior_moves.iloc[:-1]


class Game_Controller():
    def __init__(self, flipped, whoseturn="white"):
        self.WHOSETURN = whoseturn
        self.color_in_check = ""
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.black_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.white_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.captured_pieces_flip(flipped)
        self.result_abb = "*"
    def captured_pieces_flip(self, flipped):
        if flipped == False:
            self.white_captured_y = initvar.WHITE_CAPTURED_Y
            self.black_captured_y = initvar.BLACK_CAPTURED_Y
        else:
            self.white_captured_y = initvar.BLACK_CAPTURED_Y
            self.black_captured_y = initvar.WHITE_CAPTURED_Y
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if piece.taken_off_board == True:
                    if piece.color == "white":
                        piece.rect.topleft = piece.rect.topleft[0], self.white_captured_y
                    elif piece.color == "black":
                        piece.rect.topleft = piece.rect.topleft[0], self.black_captured_y
    def refresh_objects(self):
        Grid_Controller.update_grid_occupied_detection()
        self.projected_white_update()
        self.projected_black_update()
        
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.spaces_available(self)
        Grid_Controller.update_grid_occupied_detection()
        for grid in board.Grid.grid_list:
            grid.no_highlight()
            
    def __del__(self):
        Text_Controller.reset()
        # Kill all Objects within their Class lists/dicts
        for spr_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for obj in spr_list:
                obj.kill()
        for spr_list in [MoveNumberRectangle.rectangle_list, PieceMoveRectangle.rectangle_list]:
            for obj in spr_list:
                obj.kill()
        play_objects.PlayPawn.white_pawn_list = []
        play_objects.PlayBishop.white_bishop_list = []
        play_objects.PlayKnight.white_knight_list = []
        play_objects.PlayRook.white_rook_list = []
        play_objects.PlayQueen.white_queen_list = []
        play_objects.PlayKing.white_king_list = []
        play_objects.PlayPawn.black_pawn_list = []
        play_objects.PlayBishop.black_bishop_list = []
        play_objects.PlayKnight.black_knight_list = []
        play_objects.PlayRook.black_rook_list = []
        play_objects.PlayQueen.black_queen_list = []
        play_objects.PlayKing.black_king_list = []
        for grid in board.Grid.grid_list:
            grid.reset_play_interaction_vars()
        Switch_Modes_Controller.replayed_game(False, self)
        # Reset Moves Panel
        MoveNumberRectangle.rectangle_list = []
        PieceMoveRectangle.rectangle_list = []
        MoveNumberRectangle.rectangle_dict = {}
        PieceMoveRectangle.rectangle_dict = {}
        PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
    def switch_turn(self, color_turn, undo=False):
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
        Grid_Controller.update_grid_occupied_detection()
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.pinned = False
                piece.disable = False
        if self.WHOSETURN == "white":
            if undo == False:
                # Since black just moved, there are no check attacking pieces from white
                if self.color_in_check == "black":
                    self.color_in_check = ""
            self.projected_black_update()
            # If white king is not in check, reset color_in_check, else white in check
            for white_king in play_objects.PlayKing.white_king_list:
                if board.Grid.grid_dict[white_king.coordinate].coords_of_attacking_pieces['black'] == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "white"
                    # Disable pieces if their king is in double-check
                    if len(board.Grid.grid_dict[white_king.coordinate].coords_of_attacking_pieces['black']) > 1:
                        for piece_list in [play_objects.PlayPawn.white_pawn_list, play_objects.PlayBishop.white_bishop_list, 
                                           play_objects.PlayKnight.white_knight_list, play_objects.PlayRook.white_rook_list, 
                                           play_objects.PlayQueen.white_queen_list]:
                            for piece in piece_list:
                                piece.disable = True
            for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                for sub_piece in piece_list:
                    sub_piece.spaces_available(self)
            Grid_Controller.update_grid_occupied_detection()
        elif self.WHOSETURN == "black":
            if undo == False:
                # Since black just moved, there are no check attacking pieces from white
                if self.color_in_check == "white":
                    self.color_in_check = ""
                # Project squares for white and black pieces
            self.projected_white_update()
            
            # If black king is not in check, reset color_in_check, else black in check
            for black_king in play_objects.PlayKing.black_king_list:
                if board.Grid.grid_dict[black_king.coordinate].coords_of_attacking_pieces['white'] == []:
                    self.color_in_check = ""
                else:
                    self.color_in_check = "black"
                    # Disable pieces if their king is in double-check
                    if len(board.Grid.grid_dict[black_king.coordinate].coords_of_attacking_pieces['white']) > 1:
                        for piece_list in [play_objects.PlayPawn.black_pawn_list, play_objects.PlayBishop.black_bishop_list, 
                                           play_objects.PlayKnight.black_knight_list, play_objects.PlayRook.black_rook_list, 
                                           play_objects.PlayQueen.black_queen_list]:
                            for piece in piece_list:
                                piece.disable = True
            for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for sub_piece in piece_list:
                    sub_piece.spaces_available(self)
            Grid_Controller.update_grid_occupied_detection()
    def projected_white_update(self):
        # Project pieces attacking movements starting now
        for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
            for piece in piece_list:
                piece.projected(self)
    def projected_black_update(self):
        # Project pieces attacking movements starting now
        for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
            for piece in piece_list:
                piece.projected(self)
    def pinned_piece(self, pinned_piece_coordinate, pin_attacking_coordinates, color):
        # Iterates through all pieces to find the one that matches
        # the coordinate with the pin
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
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
    def select_piece_unselect_all_others(mousepos, game_controller):
        clicked_piece = None
        # Selecting and unselecting white pieces
        if game_controller.WHOSETURN == "white":
            for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                for piece in piece_list:
                    # Selects piece
                    if (piece.rect.collidepoint(mousepos) and piece.select == False and Switch_Modes_Controller.REPLAYED == False):
                        clicked_piece = piece
                    else:
                        # Unselects piece
                        piece.no_highlight()
                        for grid in board.Grid.grid_list:
                            grid.no_highlight()
        # Selecting and unselecting black pieces
        elif game_controller.WHOSETURN == "black":
            for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for piece in piece_list:
                    if (piece.rect.collidepoint(mousepos) and piece.select == False and Switch_Modes_Controller.REPLAYED == False):
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
    def undo_move(game_controller):
        Switch_Modes_Controller.replayed_game(False, game_controller)
        pieces_to_undo = []
        # Using pieces_to_undo as a list for castling
        if Move_Tracker.move_counter() >= 1:
            # Finding the latest piece to undo
            if game_controller.WHOSETURN == "white":
                piece_coordinate_move_notation = eval(Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "black_move"])['move_notation']
                for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                    for black_piece in black_piece_list:
                        for piece_history in black_piece.coordinate_history.keys():
                            if Move_Tracker.move_counter() == piece_history:
                                pieces_to_undo.append(black_piece)
            elif game_controller.WHOSETURN == "black":
                piece_coordinate_move_notation = eval(Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "white_move"])['move_notation']
                for white_piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                    for white_piece in white_piece_list:
                        for piece_history in white_piece.coordinate_history.keys():
                            if Move_Tracker.move_counter() == piece_history:
                                pieces_to_undo.append(white_piece)
            if 'x' in piece_coordinate_move_notation:
                # Detect pieces that have been taken
                if pieces_to_undo[0].color == "black":
                    for white_piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                        for white_piece in white_piece_list:
                            if white_piece.taken_off_board == True:
                                if white_piece.captured_move_number_and_coordinate['move_number'] == Move_Tracker.move_counter():
                                    white_piece.taken_off_board = False
                                    white_piece.coordinate = white_piece.captured_move_number_and_coordinate['coordinate']
                                    white_piece.rect.topleft = board.Grid.grid_dict[white_piece.coordinate].rect.topleft
                                    game_controller.white_captured_x -= initvar.BLACKANDWHITE_INCREMENTAL_X
                                    if 'ep_grid_after_coord' in white_piece.captured_move_number_and_coordinate:
                                        board.Grid.grid_dict[white_piece.captured_move_number_and_coordinate['ep_grid_after_coord']].en_passant_skipover = True
                                    white_piece.captured_move_number_and_coordinate = None
                elif pieces_to_undo[0].color == "white":
                    for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                        for black_piece in black_piece_list:
                            if black_piece.taken_off_board == True:
                                if black_piece.captured_move_number_and_coordinate['move_number'] == Move_Tracker.move_counter():
                                    black_piece.taken_off_board = False
                                    black_piece.coordinate = black_piece.captured_move_number_and_coordinate['coordinate']
                                    black_piece.rect.topleft = board.Grid.grid_dict[black_piece.coordinate].rect.topleft
                                    game_controller.black_captured_x -= initvar.BLACKANDWHITE_INCREMENTAL_X
                                    if 'ep_grid_after_coord' in black_piece.captured_move_number_and_coordinate:
                                        board.Grid.grid_dict[black_piece.captured_move_number_and_coordinate['ep_grid_after_coord']].en_passant_skipover = True
                                    black_piece.captured_move_number_and_coordinate = None
            if game_controller.WHOSETURN == "white":
                for piece_to_undo in pieces_to_undo:
                    piece_to_undo.coordinate = piece_to_undo.coordinate_history[Move_Tracker.move_counter()]['before']
                    piece_to_undo.rect.topleft = board.Grid.grid_dict[piece_to_undo.coordinate].rect.topleft
                    del piece_to_undo.coordinate_history[Move_Tracker.move_counter()]
                    Grid_Controller.grid_occupied_by_piece(board.Grid.grid_dict[piece_to_undo.coordinate])
                if 'O-O' or 'O-O-O' in piece_coordinate_move_notation:
                    for black_king in play_objects.PlayKing.black_king_list:
                        if black_king in pieces_to_undo:
                            black_king.castled = False
                    for black_rook in play_objects.PlayRook.black_rook_list:
                        if black_rook in pieces_to_undo:
                            black_rook.allowed_to_castle = True
                if "=Q" in piece_coordinate_move_notation:
                    for q in play_objects.PlayQueen.black_queen_list:
                        if q.coordinate == eval(Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "black_move"])['after']:
                            queen = q
                    queen.kill()
                    play_objects.PlayQueen.black_queen_list.remove(queen)
                if pieces_to_undo[0] in play_objects.PlayPawn.black_pawn_list:
                    pieces_to_undo[0].taken_off_board = False
                PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]['black_move'].move_notation = ""
                PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]['black_move'].kill()
                del PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]['black_move']
                Move_Tracker.undo_move_in_dfs("black")
                Panel_Controller.scroll_to_latest_move(Move_Tracker.move_counter())
                game_controller.switch_turn("black", undo=True)
                Grid_Controller.update_prior_move_color("black")
                Move_Controller.game_status_check(game_controller)
                log.info("Back to (" + str(len(Move_Tracker.df_moves)) + ".) " + "Black undo turn " + str(piece_to_undo) + " going back to " + str(piece_to_undo.coordinate))
            elif game_controller.WHOSETURN == "black":
                for piece_to_undo in pieces_to_undo:
                    piece_to_undo.coordinate = piece_to_undo.coordinate_history[Move_Tracker.move_counter()]['before']
                    piece_to_undo.rect.topleft = board.Grid.grid_dict[piece_to_undo.coordinate].rect.topleft
                    del piece_to_undo.coordinate_history[Move_Tracker.move_counter()]
                    Grid_Controller.grid_occupied_by_piece(board.Grid.grid_dict[piece_to_undo.coordinate])
                if 'O-O' or 'O-O-O' in piece_coordinate_move_notation:
                    for white_king in play_objects.PlayKing.white_king_list:
                        if white_king in pieces_to_undo:
                            white_king.castled = False
                    for white_rook in play_objects.PlayRook.white_rook_list:
                        if white_rook in pieces_to_undo:
                            white_rook.allowed_to_castle = True
                if "=Q" in piece_coordinate_move_notation:
                    for q in play_objects.PlayQueen.white_queen_list:
                        if q.coordinate == eval(Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "white_move"])['after']:
                            queen = q
                    queen.kill()
                    play_objects.PlayQueen.white_queen_list.remove(queen)
                if pieces_to_undo[0] in play_objects.PlayPawn.white_pawn_list:
                    pieces_to_undo[0].taken_off_board = False
                PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]['white_move'].move_notation = ""
                PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]['white_move'].kill()
                del PieceMoveRectangle.rectangle_dict[Move_Tracker.move_counter()]
                MoveNumberRectangle.rectangle_dict[Move_Tracker.move_counter()].text = ""
                MoveNumberRectangle.rectangle_dict[Move_Tracker.move_counter()].kill()
                Move_Tracker.undo_move_in_dfs("white")
                Panel_Controller.scroll_to_latest_move(Move_Tracker.move_counter())
                game_controller.switch_turn("white", undo=True)
                Grid_Controller.update_prior_move_color("white")
                Move_Controller.game_status_check(game_controller)
                log.info("Back to (" + str(len(Move_Tracker.df_moves)) + ".) " + "White undo turn " + str(piece_to_undo) + " going back to " + str(piece_to_undo.coordinate))
            #print("game_controller df: \n" + str(Move_Tracker.df_moves))
    def make_move(grid, piece, game_controller):
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
        # Update df_moves dictionary with a new record for the new move (when white's turn)
        if piece.color == "white":
            next_move = Move_Tracker.move_counter()+1
            Move_Tracker.df_moves.loc[next_move] = ["", ""]
            Move_Tracker.df_prior_moves.loc[next_move] = ["", ""]
        # Taking a piece by checking if available grid is opposite color of piece
        # And iterating through all pieces to check if coordinates of that grid
        # are the same as any of the pieces
        if((piece.color == "white" and grid.occupied_piece_color == "black") or
            (piece.color == "black" and grid.occupied_piece_color == "white")):
            for piece_captured_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece_captured in piece_captured_list:
                    # Moving captured piece off the board
                    if piece_captured.coordinate == grid.coordinate:
                        if piece_captured.color == "black":
                            piece_captured.captured(game_controller.black_captured_x, game_controller.black_captured_y, Move_Tracker.move_counter())
                            game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                        elif piece_captured.color == "white":
                            piece_captured.captured(game_controller.white_captured_x, game_controller.white_captured_y, Move_Tracker.move_counter())
                            game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                        # Captured_abb used for move notation
                        captured_abb = "x"
        # En Passant Capture
        if grid.en_passant_skipover == True:
            if piece in play_objects.PlayPawn.white_pawn_list:
                for black_pawn in play_objects.PlayPawn.black_pawn_list:
                    # Must include taken_off_board bool or else you get NoneType error
                    if black_pawn.taken_off_board == False:
                        if black_pawn.coordinate[0] == grid.coordinate[0] and \
                            int(black_pawn.coordinate[1]) == 5:
                                black_pawn.captured(game_controller.black_captured_x, game_controller.black_captured_y, Move_Tracker.move_counter(), grid.coordinate)
                                game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                                captured_abb = "x"
            elif piece in play_objects.PlayPawn.black_pawn_list:
                for white_pawn in play_objects.PlayPawn.white_pawn_list:
                    # Must include taken_off_board bool or else you get NoneType error
                    if white_pawn.taken_off_board == False:
                        if white_pawn.coordinate[0] == grid.coordinate[0] and \
                            int(white_pawn.coordinate[1]) == 4:
                                white_pawn.captured(game_controller.white_captured_x, game_controller.white_captured_y, Move_Tracker.move_counter(), grid.coordinate)
                                game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                                captured_abb = "x"
                            
        # Reset en passant skipover for all squares
        for sub_grid in board.Grid.grid_list:
            sub_grid.en_passant_skipover = False
        
        chosen_prior_grid = None
        # Grid is no longer occupied by a piece
        for old_grid in board.Grid.grid_list:
            if old_grid.coordinate == piece.coordinate:
                old_grid.occupied = False
                piece.previous_coordinate = old_grid.coordinate
                piece.coordinate_history[Move_Tracker.move_counter()] = {'before':piece.previous_coordinate}
                prior_moves_dict['before'] = piece.previous_coordinate
                chosen_prior_grid = old_grid
                
        # Moving piece, removing piece and grid highlights, changing Turn
        piece.rect.topleft = grid.rect.topleft
        piece.coordinate = grid.coordinate
        piece.coordinate_history[Move_Tracker.move_counter()]['after'] = piece.coordinate
        prior_moves_dict['after'] = piece.coordinate
        grid.occupied = True
        
        Grid_Controller.prior_move_color(chosen_prior_grid.coordinate, piece)

        #########
        # RULES AFTER MOVE
        #########
        
        # Enpassant Rule and Promotion Rule for Pawns
        if piece in play_objects.PlayPawn.white_pawn_list:
            if int(piece.coordinate[1]) == 8:
                special_abb = "=Q"
                promoted_queen = play_objects.PlayQueen(piece.coordinate, "white")
                promoted_queen.previous_coordinate = piece.previous_coordinate
                # Take white pawn off the board
                piece.captured(game_controller.white_captured_x, game_controller.white_captured_y, Move_Tracker.move_counter())
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
        elif piece in play_objects.PlayPawn.black_pawn_list:
            if int(piece.coordinate[1]) == 1:
                special_abb = "=Q"
                promoted_queen = play_objects.PlayQueen(piece.coordinate, "black")
                promoted_queen.previous_coordinate = piece.previous_coordinate
                # Take black pawn off the board
                piece.captured(game_controller.black_captured_x, game_controller.black_captured_y, Move_Tracker.move_counter())
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
        if piece in play_objects.PlayKing.white_king_list:
            piece.castled = True
            for rook in play_objects.PlayRook.white_rook_list:
                if rook.allowed_to_castle == True:
                    if rook.coordinate == 'a1' and piece.coordinate == 'c1':
                        rook.coordinate_history[Move_Tracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d1'].coordinate
                        board.Grid.grid_dict['d1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O-O"
                        rook.coordinate_history[Move_Tracker.move_counter()]['before'] = 'a1'
                        rook.coordinate_history[Move_Tracker.move_counter()]['after'] = 'd1'
                        rook.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h1' and piece.coordinate == 'g1':
                        rook.coordinate_history[Move_Tracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['f1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f1'].coordinate
                        board.Grid.grid_dict['f1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O"
                        rook.coordinate_history[Move_Tracker.move_counter()]['before'] = 'h1'
                        rook.coordinate_history[Move_Tracker.move_counter()]['after'] = 'f1'
                        rook.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = 'O-O'
        elif piece in play_objects.PlayKing.black_king_list:
            piece.castled = True
            for rook in play_objects.PlayRook.black_rook_list:
                if rook.allowed_to_castle == True:
                    if rook.coordinate == 'a8' and piece.coordinate == 'c8':
                        rook.coordinate_history[Move_Tracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d8'].coordinate
                        board.Grid.grid_dict['d8'].occupied = True
                        special_abb = "O-O-O"
                        rook.coordinate_history[Move_Tracker.move_counter()]['before'] = 'a8'
                        rook.coordinate_history[Move_Tracker.move_counter()]['after'] = 'd8'
                        rook.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h8' and piece.coordinate == 'g8':
                        rook.coordinate_history[Move_Tracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['f8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f8'].coordinate
                        board.Grid.grid_dict['f8'].occupied = True
                        special_abb = "O-O"
                        rook.coordinate_history[Move_Tracker.move_counter()]['before'] = 'h8'
                        rook.coordinate_history[Move_Tracker.move_counter()]['after'] = 'f8'
                        rook.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = 'O-O'
        elif piece in play_objects.PlayRook.white_rook_list or piece in play_objects.PlayRook.black_rook_list:
            piece.allowed_to_castle = False
            if piece.previous_coordinate == 'h1':
                play_objects.PlayKing.white_king_list[0].king_side_castle_ability = False
            if piece.previous_coordinate == 'a1':
                play_objects.PlayKing.white_king_list[0].queen_side_castle_ability = False
            if piece.previous_coordinate == 'h8':
                play_objects.PlayKing.black_king_list[0].king_side_castle_ability = False
            if piece.previous_coordinate == 'a8':
                play_objects.PlayKing.black_king_list[0].queen_side_castle_ability = False
        # Update all grids to reflect the coordinates of the pieces
        Grid_Controller.update_grid_occupied_detection()
        # Switch turns
        if(game_controller.WHOSETURN == "white"):
            game_controller.switch_turn("black")
        elif(game_controller.WHOSETURN == "black"):
            game_controller.switch_turn("white")
            
        return prior_moves_dict, captured_abb, special_abb, promoted_queen
    
    def game_status_check(game_controller):
        check_abb = ""
        def stalemate_check(game_controller, whoseturn):
            for subgrid in board.Grid.grid_list:
                if len(subgrid.coords_of_available_pieces[whoseturn]) > 0:
                    # No check, no checkmate, no stalemate
                    Text_Controller.check_checkmate_text = ""
                    return "*"
            Text_Controller.check_checkmate_text = "Stalemate"
            return "1/2-1/2"
        def checkmate_check(game_controller, whoseturn):
            for subgrid in board.Grid.grid_list:
                if len(subgrid.coords_of_available_pieces[whoseturn]) > 0:
                    # If able to detect that a grid can be available, that means it's NOT checkmate
                    return "+", "*"
            if whoseturn == 'black':
                Text_Controller.check_checkmate_text = "White wins"
                return "#", "1-0"
            elif whoseturn == 'white':
                Text_Controller.check_checkmate_text = "Black wins"
                return "#", "0-1"
        if game_controller.color_in_check == "black":
            Text_Controller.check_checkmate_text = "Black King checked"
            check_abb, game_controller.result_abb = checkmate_check(game_controller, 'black')
        elif game_controller.color_in_check == "white":
            Text_Controller.check_checkmate_text = "White King checked"
            check_abb, game_controller.result_abb = checkmate_check(game_controller, 'white')
        elif game_controller.color_in_check == "" and game_controller.WHOSETURN == "white":
            game_controller.result_abb = stalemate_check(game_controller, 'white')
        elif game_controller.color_in_check == "" and game_controller.WHOSETURN == "black":
            game_controller.result_abb = stalemate_check(game_controller, 'black')
        else:
            # No checks
            Text_Controller.check_checkmate_text = ""
        for grid in board.Grid.grid_list:
            grid.no_highlight()
        Preferences.Result = game_controller.result_abb
        return check_abb
    def record_move(game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen=None):
        if(game_controller.WHOSETURN == "white"):
            # Log the move
            # Record the move in the df_moves dataframe
            # Record the move in that piece's history
            # Record the move in the prior_moves_history then add that to prior_move_history dataframe
            # Automatically make the move the selected move (thus highlighting in right panel)
            if special_abb == "=Q":
                piece_in_funcs = promoted_queen
            else:
                piece_in_funcs = piece
                # When the piece became promoted to a Queen
            move_text = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb) + " "
            Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            Move_Tracker.selected_move = (Move_Tracker.move_counter(), "black_move")
            Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "black_move"] = str(prior_moves_dict)
        elif(game_controller.WHOSETURN == "black"):
            # Create new record to make room for new white move
            # move_counter will update to new length of dataframe
            if special_abb == "=Q":
                piece_in_funcs = promoted_queen
            else:
                piece_in_funcs = piece
            move_text = str(Move_Tracker.move_counter()) + ". " + \
                  Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb) + " "
            Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "white_move"] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[Move_Tracker.move_counter()]['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = Move_Controller.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            Move_Tracker.selected_move = (Move_Tracker.move_counter(), "white_move")
            Move_Tracker.df_prior_moves.loc[Move_Tracker.move_counter(), "white_move"] = str(prior_moves_dict)
        Switch_Modes_Controller.replayed_game(False, game_controller)
        log.info(move_text)
        if game_controller.result_abb != "*":
            log.info(game_controller.result_abb)
        
        return

class Panel_Controller:
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
        if latest_move_number >= initvar.MOVES_PANE_MAX_MOVES:
            PanelRectangles.scroll_range[0] = latest_move_number - (initvar.MOVES_PANE_MAX_MOVES-1)
            PanelRectangles.scroll_range[1] = latest_move_number
            for move_num_rect in MoveNumberRectangle.rectangle_list:
                move_num_rect.update_Y()
            for piece_move_rect in PieceMoveRectangle.rectangle_list:
                piece_move_rect.update_Y()

    def scroll_to_first_move():
        PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
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
        if len(Move_Tracker.df_moves) >= 1:
            # Creating move notation rectangles if they haven't been created before for the respective move
            # If the last move is not in the dictionary, then add it
            if len(Move_Tracker.df_moves) not in PieceMoveRectangle.rectangle_dict:
                PieceMoveRectangle.rectangle_dict[len(Move_Tracker.df_moves)] = {}
                MoveNumberRectangle.rectangle_dict[len(Move_Tracker.df_moves)] = []
            # We want the PieceMoveRectangle.rectangle_dict to correspond to the df_moves dataframe
            if Move_Tracker.df_moves.loc[len(Move_Tracker.df_moves), 'white_move'] != '' and 'white_move' not in PieceMoveRectangle.rectangle_dict[len(Move_Tracker.df_moves)]:
                # Create new move number rectangle since white made a move
                MoveNumberRectangle(len(Move_Tracker.df_moves), initvar.MOVES_PANE_MOVE_NUMBER_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(Move_Tracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                # Create rectangle which will eventually be used to blit text on it
                # Parameters: Total number of moves in the game, the move itself, the color of the piece that moved, and position & size of rectangle
                PieceMoveRectangle(len(Move_Tracker.df_moves), Move_Tracker.df_moves.loc[len(Move_Tracker.df_moves), 'white_move'], 'white_move', initvar.MOVES_PANE_WHITE_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(Move_Tracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                # Scroll down automatically when a move is made
                Panel_Controller.scroll_to_latest_move(len(Move_Tracker.df_moves))
            if Move_Tracker.df_moves.loc[len(Move_Tracker.df_moves), 'black_move'] != '' and 'black_move' not in PieceMoveRectangle.rectangle_dict[len(Move_Tracker.df_moves)]:
                # Only create PieceMoveRectangle when black moved last, don't create a new MoveNumberRectangle
                PieceMoveRectangle(len(Move_Tracker.df_moves), Move_Tracker.df_moves.loc[len(Move_Tracker.df_moves), 'black_move'], 'black_move', initvar.MOVES_PANE_BLACK_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(Move_Tracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)        
                Panel_Controller.scroll_to_latest_move(len(Move_Tracker.df_moves))
            Panel_Controller.draw_text_on_rects_in_moves_pane(SCREEN, my_font)

def main():
    try:
        #Tk box for color
        root = tk.Tk()
        root.withdraw()
        #Global variables
        MENUON = 1
        
        RUNNING, DEBUG = 0, 1
        state = RUNNING
        debug_message = 0
        
        GAME_MODE_SPRITES = pygame.sprite.Group()
        CLOCK = pygame.time.Clock()
        
        #Fonts
        arial_font = pygame.font.SysFont('Arial', 24)
        move_notation_font = pygame.font.SysFont('Arial', 16)
        
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
        BEGINNING_MOVE_BUTTON = BeginningMoveButton(initvar.BEGINNING_MOVE_BUTTON_TOPLEFT)
        PREV_MOVE_BUTTON = PrevMoveButton(initvar.PREV_MOVE_BUTTON_TOPLEFT)
        NEXT_MOVE_BUTTON = NextMoveButton(initvar.NEXT_MOVE_BUTTON_TOPLEFT)
        LAST_MOVE_BUTTON = LastMoveButton(initvar.LAST_MOVE_BUTTON_TOPLEFT)
        UNDO_MOVE_BUTTON = UndoMoveButton(initvar.UNDO_MOVE_BUTTON_TOPLEFT)
        
        #Backgrounds
        INFO_SCREEN = pygame.image.load("Sprites/infoscreen.bmp").convert()
        INFO_SCREEN = pygame.transform.scale(INFO_SCREEN, (initvar.SCREEN_WIDTH, initvar.SCREEN_HEIGHT))
        #window
        gameicon = pygame.image.load("Sprites/chessico.png")
        pygame.display.set_icon(gameicon)
        pygame.display.set_caption('Chess')

                        
        # Load the starting positions of chessboard first
        pos_load_file(reset=True)
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
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and MOUSEPOS[0] > initvar.X_GRID_END:
                        #%% Left click buttons
                        if SCROLL_UP_BUTTON.rect.collidepoint(MOUSEPOS) and PanelRectangles.scroll_range[0] > 1: # Scroll up
                            if SCROLL_UP_BUTTON.activate == True:    
                                Panel_Controller.update_scroll_range(-1)
                        if SCROLL_DOWN_BUTTON.rect.collidepoint(MOUSEPOS) and len(MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and PanelRectangles.scroll_range[1] < len(MoveNumberRectangle.rectangle_list): # Scroll down
                            if SCROLL_DOWN_BUTTON.activate == True:  
                                Panel_Controller.update_scroll_range(1)
                        if PGN_LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS) and PGN_LOAD_FILE_BUTTON.clickable == True:
                            game_controller = PGN_Writer_and_Loader.pgn_load(PLAY_EDIT_SWITCH_BUTTON)
                            for grid in board.Grid.grid_list:
                                grid.no_highlight()
                            Grid_Controller.update_grid_occupied_detection()
                        if PGN_SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS) and PGN_SAVE_FILE_BUTTON.clickable == True:
                            Preferences.game_properties_popup()
                            PGN_Writer_and_Loader.write_moves(Move_Tracker.df_moves, game_controller.result_abb)
                        if FLIP_BOARD_BUTTON.rect.collidepoint(MOUSEPOS):
                            Grid_Controller.flip_grids()
                            if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE:
                                game_controller.captured_pieces_flip(Grid_Controller.flipped)
                        if UNDO_MOVE_BUTTON.rect.collidepoint(MOUSEPOS) and UNDO_MOVE_BUTTON.clickable == True:
                            Move_Controller.undo_move(game_controller)
                        if BEGINNING_MOVE_BUTTON.rect.collidepoint(MOUSEPOS) and BEGINNING_MOVE_BUTTON.clickable == True:
                            Move_Tracker.selected_move = 1, "white_move"
                            Switch_Modes_Controller.replayed_game(True, game_controller, True)
                            Grid_Controller.update_prior_move_color()
                            Move_Tracker.selected_move = (0, "black_move")
                            Panel_Controller.scroll_to_first_move()
                        if PREV_MOVE_BUTTON.rect.collidepoint(MOUSEPOS) and PREV_MOVE_BUTTON.clickable == True:
                            if Move_Tracker.selected_move == (0, "black_move"):
                                pass
                            elif Move_Tracker.selected_move == (1, "white_move"):
                                Switch_Modes_Controller.replayed_game(True, game_controller, True)
                                Grid_Controller.update_prior_move_color()
                                Move_Tracker.selected_move = (0, "black_move")
                            elif Move_Tracker.selected_move[1] == "black_move":
                                Move_Tracker.selected_move = Move_Tracker.selected_move[0], "white_move"
                                Switch_Modes_Controller.replayed_game(True, game_controller)
                            else:
                                Move_Tracker.selected_move = Move_Tracker.selected_move[0]-1, "black_move"
                                if Move_Tracker.selected_move[0] < PanelRectangles.scroll_range[0] and PanelRectangles.scroll_range[0] >= 1:
                                    Panel_Controller.update_scroll_range(-1)
                                Switch_Modes_Controller.replayed_game(True, game_controller)
                        if NEXT_MOVE_BUTTON.rect.collidepoint(MOUSEPOS) and NEXT_MOVE_BUTTON.clickable == True:
                            if Move_Tracker.selected_move[0] != Move_Tracker.move_counter():
                                # When selected move is not at the last move number
                                if Move_Tracker.selected_move[1] == "black_move":
                                    # When selected move is not at last move number and we are at black move
                                    Move_Tracker.selected_move = Move_Tracker.selected_move[0]+1, "white_move"
                                    if Move_Tracker.selected_move[0] > PanelRectangles.scroll_range[1] and PanelRectangles.scroll_range[1] < Move_Tracker.move_counter():
                                        Panel_Controller.update_scroll_range(1)
                                    if Move_Tracker.selected_move[0] == Move_Tracker.move_counter() and \
                                        Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] == "":
                                            # Went to last move number and there is no black move yet
                                            Switch_Modes_Controller.replayed_game(False, game_controller)
                                    else:
                                        Switch_Modes_Controller.replayed_game(True, game_controller)
                                elif Move_Tracker.selected_move[1] == "white_move":
                                    # When selected move is not at last move number and we are at white move
                                    Move_Tracker.selected_move = Move_Tracker.selected_move[0], "black_move"
                                    Switch_Modes_Controller.replayed_game(True, game_controller)
                            elif Move_Tracker.selected_move[0] == Move_Tracker.move_counter() \
                                and Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] != "" \
                                    and Move_Tracker.selected_move[1] == "white_move":
                                        # We are at last move (and black has not moved yet)
                                        Move_Tracker.selected_move = Move_Tracker.selected_move[0], "black_move"
                                        Switch_Modes_Controller.replayed_game(False, game_controller)
                            else:
                                # Last move 
                                Switch_Modes_Controller.replayed_game(False, game_controller)
                        if LAST_MOVE_BUTTON.rect.collidepoint(MOUSEPOS) and LAST_MOVE_BUTTON.clickable == True:
                            if Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] == "":
                                Move_Tracker.selected_move = Move_Tracker.move_counter(), "white_move"
                            else:
                                Move_Tracker.selected_move = Move_Tracker.move_counter(), "black_move"
                            Panel_Controller.scroll_to_latest_move(Move_Tracker.move_counter())
                            Switch_Modes_Controller.replayed_game(False, game_controller)
                        # When clicking on a move on the right pane, it is your selected move
                        for piece_move_rect in PieceMoveRectangle.rectangle_list:
                            if piece_move_rect.rect.collidepoint(MOUSEPOS) and piece_move_rect.text_is_visible:
                                Move_Tracker.selected_move = (piece_move_rect.move_number, piece_move_rect.move_color)
                                if Move_Tracker.selected_move[0] == Move_Tracker.move_counter():
                                    if Move_Tracker.df_moves.loc[Move_Tracker.move_counter(), "black_move"] != "" \
                                        and piece_move_rect.move_color == "white_move":
                                            Switch_Modes_Controller.replayed_game(True, game_controller)
                                    else:
                                        Switch_Modes_Controller.replayed_game(False, game_controller)
                                else:
                                    Switch_Modes_Controller.replayed_game(True, game_controller)
                        # Editing mode only
                        if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE:
                            #BUTTONS
                            if COLOR_BUTTON.rect.collidepoint(MOUSEPOS):
                                Preferences.colorkey = Preferences.get_color()
                            if POS_SAVE_FILE_BUTTON.rect.collidepoint(MOUSEPOS) and POS_SAVE_FILE_BUTTON.clickable == True:
                                pos_save_file()
                            if POS_LOAD_FILE_BUTTON.rect.collidepoint(MOUSEPOS) and POS_LOAD_FILE_BUTTON.clickable == True:
                                pos_load_file()
                            if RESET_BOARD_BUTTON.rect.collidepoint(MOUSEPOS) and RESET_BOARD_BUTTON.clickable == True:
                                pos_load_file(reset=True)
                            if GAME_PROPERTIES_BUTTON.rect.collidepoint(MOUSEPOS) and GAME_PROPERTIES_BUTTON.clickable == True:
                                Preferences.game_properties_popup()
                                

                            # DRAG OBJECTS
                            # Goes through each of the types of pieces
                            # If start object is clicked on, then enable drag, blank box changes images to the original piece so it looks better
                            for piece_name in start_objects.Start.start_dict.keys():
                                if start_objects.Start.start_dict.get(piece_name).rect.collidepoint(MOUSEPOS):
                                    start_objects.Dragging.start_drag(piece_name)
                    #################
                    # LEFT CLICK (PRESSED DOWN)
                    #################
                    
                    # Mouse click on the board
                    elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                          MOUSEPOS[0] > initvar.X_GRID_START and MOUSEPOS[0] < initvar.X_GRID_END and
                          MOUSEPOS[1] > initvar.Y_GRID_START and MOUSEPOS[1] < initvar.Y_GRID_END): 
                        # Drag piece to board (initialize placed piece)
                        start_objects.Dragging.dragging_to_placed_no_dups(MOUSE_COORD)
                        if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE:
                            # Moves piece
                            def update_pieces_and_board():
                                for grid in board.Grid.grid_list:
                                    for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                                        for piece in piece_list:
                                            # Reset the prior move color variable from all pieces
                                            piece.prior_move_color = False
                                            # If piece is allowed to move to another grid coordinate and piece is also selected
                                            if (grid.rect.collidepoint(MOUSEPOS) \
                                                and ((piece.coordinate in grid.coords_of_available_pieces['white'] and piece.color == "white") \
                                                     or (piece.coordinate in grid.coords_of_available_pieces['black'] and piece.color == "black")) \
                                                         and piece.select==True):
                                                prior_moves_dict, captured_abb, special_abb, promoted_queen = Move_Controller.make_move(grid, piece, game_controller)
                                                check_abb = Move_Controller.game_status_check(game_controller)
                                                Move_Controller.record_move(game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                            update_pieces_and_board()
                            # Selects piece
                            Move_Controller.select_piece_unselect_all_others(MOUSEPOS, game_controller)
    
                    if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                        #scroll wheel
                        if event.button == 4: # Scroll up
                            if PanelRectangles.scroll_range[0] > 1:
                                if SCROLL_UP_BUTTON.activate == True:
                                    Panel_Controller.update_scroll_range(-1)
                        if event.button == 5: # Scroll down
                            if len(MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and PanelRectangles.scroll_range[1] < len(MoveNumberRectangle.rectangle_list):
                                if SCROLL_DOWN_BUTTON.activate == True:  
                                    Panel_Controller.update_scroll_range(1)
                    if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE:
                        # Right click on obj, destroy
                        if(event.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):   
                            Edit_Mode_Controller.right_click_destroy(MOUSEPOS)
                    
                    if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                        #################
                        # PLAY BUTTON
                        #################
                        if PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE: 
                            # Makes clicking play again unclickable    
                            Switch_Modes_Controller.switch_mode(Switch_Modes_Controller.PLAY_MODE, PLAY_EDIT_SWITCH_BUTTON)
                            game_controller = Game_Controller(Grid_Controller.flipped)
                            game_controller.refresh_objects()

                        #################
                        # LEFT CLICK (RELEASE) STOP BUTTON
                        #################
                        elif PLAY_EDIT_SWITCH_BUTTON.rect.collidepoint(MOUSEPOS) and Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE:
                            Switch_Modes_Controller.switch_mode(Switch_Modes_Controller.EDIT_MODE, PLAY_EDIT_SWITCH_BUTTON)
                            del game_controller
                        if INFO_BUTTON.rect.collidepoint(MOUSEPOS):
                            pass
                            #MENUON = 2
                        if CLEAR_BUTTON.rect.collidepoint(MOUSEPOS):
                            if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE: #Editing mode
                                start_objects.Start.restart_start_positions()
                                # REMOVE ALL SPRITES
                                placed_objects.remove_all_placed()
                    
                    # MIDDLE MOUSE DEBUGGER
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                    #%% Middle mouse debugger
                        def test_piece():
                            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                                for piece in piece_list:
                                    if piece.rect.collidepoint(MOUSEPOS):
                                        print("piece dict: " + str(piece.__dict__))
                        def test_grid_str():
                            for grid in board.Grid.grid_list:
                                if grid.rect.collidepoint(MOUSEPOS):
                                    log.info("Coordinate: " + str(grid.coordinate) \
                                           + ", White Pieces Attacking: " + str(grid.coords_of_attacking_pieces['white']) \
                                           + ", Black Pieces Attacking: " + str(grid.coords_of_attacking_pieces['black']) \
                                               + ", grid variable: " + str(grid.highlighted) \
                                                   + ", White Pieces Available: " + str(grid.coords_of_available_pieces['white']) \
                                                       + ", Black Pieces Available: " + str(grid.coords_of_available_pieces['black']))
                        test_grid_str()
                        #test_piece()
                                
                ##################
                # ALL EDIT ACTIONS
                ##################
                # Start piece is dragging according to where the mouse is
                if Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE:
                    # Constant loop
                    start_objects.Dragging.update_drag_piece_and_all_start_pieces_positions(MOUSEPOS)
            
                ##################
                # IN-GAME ACTIONS
                ##################
                #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
                
                #Update all sprites
                SCREEN.fill(Preferences.colorkey)
                
                FLIP_BOARD_BUTTON.draw(SCREEN)
                GAME_MODE_SPRITES.draw(SCREEN)
                board.GRID_SPRITES.draw(SCREEN)
                Grid_Controller.update_grid_occupied_detection()
                start_objects.START_SPRITES.update(Switch_Modes_Controller.GAME_MODE)
                PLAY_PANEL_SPRITES.update(Switch_Modes_Controller.GAME_MODE)
                
                SCREEN.blit(initvar.MOVE_BG_IMAGE, (initvar.MOVE_BG_IMAGE_HEIGHT,initvar.MOVE_BG_IMAGE_WIDTH))
                if(Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.EDIT_MODE): #Only draw placed sprites in editing mode
                    start_objects.START_SPRITES.draw(SCREEN)
                    placed_objects.PLACED_SPRITES.update()
                    placed_objects.PLACED_SPRITES.draw(SCREEN)
                elif(Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE): #Only draw play sprites in play mode
                    FLIP_BOARD_BUTTON.draw(SCREEN)
                    if Switch_Modes_Controller.REPLAYED == False:
                        play_objects.PLAY_SPRITES.update()
                        play_objects.PLAY_SPRITES.draw(SCREEN)
                    else:
                        replayed_objects.REPLAYED_SPRITES.update()
                        replayed_objects.REPLAYED_SPRITES.draw(SCREEN)
                    PLAY_PANEL_SPRITES.draw(SCREEN)
                    
                    # When the piece is selected on the right pane, fill the rectangle corresponding to the move
                    for piece_move_rect in PieceMoveRectangle.rectangle_list:
                        if piece_move_rect.move_number == Move_Tracker.selected_move[0] and piece_move_rect.move_color == Move_Tracker.selected_move[1]:
                            piece_move_rect.draw(SCREEN)
                    Panel_Controller.draw_move_rects_on_moves_pane(move_notation_font, game_controller)
                    # Update objects that aren't in a sprite group
                    SCROLL_UP_BUTTON.draw(SCREEN)
                    SCROLL_DOWN_BUTTON.draw(SCREEN, len(Move_Tracker.df_moves))
                render_text = lambda x: arial_font.render(x, 1, (0, 0, 0)) 
                # Board Coordinates Drawing
                for text in range(0,len(Text_Controller.coor_letter_text_list)):
                    SCREEN.blit(Text_Controller.coor_letter_text_list[text], (initvar.X_GRID_START+initvar.X_GRID_WIDTH/3+(initvar.X_GRID_WIDTH*text), initvar.Y_GRID_START-(initvar.Y_GRID_HEIGHT*0.75)))
                    SCREEN.blit(Text_Controller.coor_letter_text_list[text], (initvar.X_GRID_START+initvar.X_GRID_WIDTH/3+(initvar.X_GRID_WIDTH*text), initvar.Y_GRID_END+(initvar.Y_GRID_HEIGHT*0.25)))
                for text in range(0,len(Text_Controller.coor_number_text_list)):
                    SCREEN.blit(Text_Controller.coor_number_text_list[text], (initvar.X_GRID_START-initvar.X_GRID_WIDTH/2, initvar.Y_GRID_START+initvar.Y_GRID_HEIGHT/4+(initvar.Y_GRID_HEIGHT*text)))
                    SCREEN.blit(Text_Controller.coor_number_text_list[text], (initvar.X_GRID_END+initvar.X_GRID_WIDTH/3, initvar.Y_GRID_START+initvar.Y_GRID_HEIGHT/4+(initvar.Y_GRID_HEIGHT*text)))
                if(Switch_Modes_Controller.GAME_MODE == Switch_Modes_Controller.PLAY_MODE):
                    check_checkmate_text_render = arial_font.render(Text_Controller.check_checkmate_text, 1, (0, 0, 0))
                    if Grid_Controller.flipped == True:
                        if game_controller.WHOSETURN == "white" and game_controller.result_abb == "*":
                            whose_turn_text = arial_font.render("White's move", 1, (0, 0, 0))
                            SCREEN.blit(whose_turn_text, initvar.BLACK_MOVE_X_Y)
                        elif game_controller.WHOSETURN == "black" and game_controller.result_abb == "*":
                            whose_turn_text = arial_font.render("Black's move", 1, (0, 0, 0))
                            SCREEN.blit(whose_turn_text, initvar.WHITE_MOVE_X_Y)
                    else:
                        if game_controller.WHOSETURN == "white" and game_controller.result_abb == "*":
                            whose_turn_text = arial_font.render("White's move", 1, (0, 0, 0))
                            SCREEN.blit(whose_turn_text, initvar.WHITE_MOVE_X_Y)
                        elif game_controller.WHOSETURN == "black" and game_controller.result_abb == "*":
                            whose_turn_text = arial_font.render("Black's move", 1, (0, 0, 0))
                            SCREEN.blit(whose_turn_text, initvar.BLACK_MOVE_X_Y)
                    SCREEN.blit(check_checkmate_text_render, initvar.CHECK_CHECKMATE_X_Y)
                if Grid_Controller.flipped == True:
                    if Preferences.WhiteElo != "":
                        SCREEN.blit(render_text(Preferences.White + " (" + Preferences.WhiteElo + ")"), initvar.BLACK_X_Y)
                    else:
                        SCREEN.blit(render_text(Preferences.White), initvar.BLACK_X_Y)
                    if Preferences.BlackElo != "":
                        SCREEN.blit(render_text(Preferences.Black + " (" + Preferences.BlackElo + ")"), initvar.WHITE_X_Y)
                    else:
                        SCREEN.blit(render_text(Preferences.Black), initvar.WHITE_X_Y)
                else:
                    if Preferences.WhiteElo != "":
                        SCREEN.blit(render_text(Preferences.White + " (" + Preferences.WhiteElo + ")"), initvar.WHITE_X_Y)
                    else:
                        SCREEN.blit(render_text(Preferences.White), initvar.WHITE_X_Y)
                    if Preferences.BlackElo != "":
                        SCREEN.blit(render_text(Preferences.Black + " (" + Preferences.BlackElo + ")"), initvar.BLACK_X_Y)
                    else:
                        SCREEN.blit(render_text(Preferences.Black), initvar.BLACK_X_Y)
                pygame.display.update()
                #print("MEOW 1123 " + today.strftime("%Y-%m-%d %H%M%S"))
            elif state == DEBUG:
                if debug_message == 1:
                    log.info("Entering debug mode")
                    debug_message = 0
                    #%% Testing (space)
                    print(str(Move_Tracker.selected_move))
                    #print(str(Move_Tracker.df_moves))
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