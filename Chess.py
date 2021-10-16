# pylint: disable=E1101
"""
Chess created by Brad Wyatt
"""
import random
import sys
import os
import copy
import datetime
import logging
import logging.handlers
import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askopenfilename
import ast
import json
import pygame
import pandas as pd
import numpy as np
import PySimpleGUI as sg
import load_images_sounds as lis
import menu_buttons
import initvar
import board
import start_objects
import placed_objects
import play_objects
import replayed_objects

#############
# Logging
#############

today = datetime.datetime.today()
log = logging.getLogger("log_guy")
log.handlers = []
log.setLevel(logging.INFO)

# Handlers for logging errors
if not initvar.exe_mode:
    log_file_name = "{0}.log".format(today.strftime("%Y-%m-%d %H%M%S"))
    log_file = os.path.join(initvar.log_path, log_file_name)
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
    """
    Load positions of the pieces
    """
    open_file = None
    if reset:
        loaded_dict = {'white_pawn': ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
                       'white_bishop': ['c1', 'f1'], 'white_knight': ['b1', 'g1'],
                       'white_rook': ['a1', 'h1'], 'white_queen': ['d1'], 'white_king': ['e1'],
                       'black_pawn': ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
                       'black_bishop': ['c8', 'f8'], 'black_knight': ['b8', 'g8'],
                       'black_rook': ['a8', 'h8'], 'black_queen': ['d8'], 'black_king': ['e8']}
    else:
        request_file_name = askopenfilename(defaultextension=".json")
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

    log.info("Positioning Loaded Successfully")
    return

def get_dict_rect_positions():
    """
    Returns the tuples of each objects' positions within all classes
    """
    total_placed_list = {'white_pawn': placed_objects.PlacedPawn.white_pawn_list,
                         'white_bishop': placed_objects.PlacedBishop.white_bishop_list,
                         'white_knight': placed_objects.PlacedKnight.white_knight_list,
                         'white_rook': placed_objects.PlacedRook.white_rook_list,
                         'white_queen': placed_objects.PlacedQueen.white_queen_list,
                         'white_king': placed_objects.PlacedKing.white_king_list,
                         'black_pawn': placed_objects.PlacedPawn.black_pawn_list,
                         'black_bishop': placed_objects.PlacedBishop.black_bishop_list,
                         'black_knight': placed_objects.PlacedKnight.black_knight_list,
                         'black_rook': placed_objects.PlacedRook.black_rook_list,
                         'black_queen': placed_objects.PlacedQueen.black_queen_list,
                         'black_king': placed_objects.PlacedKing.black_king_list}
    get_coord_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_coord in item_list:
            item_list_in_name.append(item_coord.coordinate)
        get_coord_for_all_obj[item_key] = item_list_in_name
    # Tuple positions converted to string to be JSON-compatible
    all_obj_coord_json = json.dumps(get_coord_for_all_obj)
    return all_obj_coord_json

def pos_save_file():
    """
    Save positions of the pieces
    """
    try:
        save_file_prompt = asksaveasfilename(defaultextension=".json")
        save_file_name = open(save_file_prompt, "w")
        if save_file_name is not None:
            # Write the file to disk
            obj_locations = copy.deepcopy(get_dict_rect_positions())
            print(str(obj_locations))
            save_file_name.write(str(obj_locations))
            save_file_name.close()
            log.info("File Saved Successfully.")
        else:
            log.info("Error! Need king to save!")
    except IOError:
        log.info("Save File Error (IOError)")

def pos_lists_to_coord(pos_score_list):
    """
    When analyzing the board, the function returns the score
    for each of the squares
    """
    score_dict = {}
    coordinate_list = ['a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
                  'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
                  'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
                  'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
                  'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
                  'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
                  'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
                  'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1']
    for item_index in range(0,len(pos_score_list)):
        score_dict[coordinate_list[item_index]] = pos_score_list[item_index]
    return score_dict

class GameProperties():
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
    @classmethod
    def game_properties_popup(cls):
        layout = [
            [sg.Text('Please enter the information for the game below (all fields are optional)')],
            [sg.Text('Event', size=(9, 0)), sg.InputText(default_text=cls.Event)],
            [sg.Text('Site', size=(9, 0)), sg.InputText(default_text=cls.Site)],
            [sg.Text('Date', size=(9, 0)), sg.InputText(default_text=cls.Date)],
            [sg.Text('Round', size=(9, 0)), sg.InputText(default_text=cls.Round)],
            [sg.Text('White', size=(9, 0)), sg.InputText(default_text=cls.White)],
            [sg.Text('Black', size=(9, 0)), sg.InputText(default_text=cls.Black)],
            [sg.Text('Result', size=(9, 0)), sg.InputText(default_text=cls.Result)],
            [sg.Text('WhiteElo', size=(9, 0)), sg.InputText(default_text=cls.WhiteElo)],
            [sg.Text('BlackElo', size=(9, 0)), sg.InputText(default_text=cls.BlackElo)],
            [sg.Text('ECO', size=(9, 0)), sg.InputText(default_text=cls.ECO)],
            [sg.Text('TimeControl', size=(9, 0)), sg.InputText(default_text=cls.TimeControl)],
            [sg.Submit("Ok"), sg.Cancel("Cancel")]
        ]
        #Please enter the information for the game below. All fields are optional.
        window = sg.Window('Game Properties', layout, element_justification='center')
        event, values = window.read()
        window.close()
        if event == 'Cancel' or event is None:
            return
        cls.Event = values[0]
        cls.Site = values[1]
        cls.Date = values[2]
        cls.Round = values[3]
        cls.White = values[4]
        cls.Black = values[5]
        cls.Result = values[6]
        cls.WhiteElo = values[7]
        cls.BlackElo = values[8]
        cls.ECO = values[9]
        cls.TimeControl = values[10]

class PgnWriterAndLoader():
    @staticmethod
    def write_moves(df_moves, result_abb):
        try:
            df = df_moves.copy()
            save_file_prompt = asksaveasfilename(defaultextension=".pgn")
            save_file_name = open(save_file_prompt, "w")
            if save_file_name is not None:
                # Write the file to disk
                pgn_output = ""
                pgn_output += '[Event "' + GameProperties.Event + '"]\n'
                pgn_output += '[Site "' + GameProperties.Site + '"]\n'
                pgn_output += '[Date "' + GameProperties.Date + '"]\n'
                pgn_output += '[Round "' + GameProperties.Round + '"]\n'
                pgn_output += '[White "' + GameProperties.White + '"]\n'
                pgn_output += '[Black "' + GameProperties.Black + '"]\n'
                pgn_output += '[Result "' + GameProperties.Result + '"]\n'
                pgn_output += '[ECO "' + GameProperties.ECO + '"]\n'
                pgn_output += '[TimeControl "' + GameProperties.TimeControl + '"]\n'
                pgn_output += '[WhiteElo "' + GameProperties.WhiteElo + '"]\n'
                pgn_output += '[BlackElo "' + GameProperties.BlackElo + '"]\n\n'
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
    @staticmethod
    def pgn_load(play_edit_switch_button):
        open_file = None
        request_file_name = askopenfilename(defaultextension=".pgn")
        log.info("Loading " + os.path.basename(request_file_name))
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return None
        SwitchModesController.switch_mode(SwitchModesController.PLAY_MODE, play_edit_switch_button)
        game_controller = GameController(GridController.flipped)
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
            GameProperties.Event = parameters['Event'].replace('"', '')
        except KeyError:
            GameProperties.Event = ""
        try:
            GameProperties.Site = parameters['Site'].replace('"', '')
        except KeyError:
            GameProperties.Site = ""
        try:
            GameProperties.Date = parameters['Date'].replace('"', '')
        except KeyError:
            GameProperties.Date = ""
        try:
            GameProperties.Round = parameters['Round'].replace('"', '')
        except KeyError:
            GameProperties.Round = ""
        try:
            GameProperties.White = parameters['White'].replace('"', '')
        except KeyError:
            GameProperties.White = ""
        try:
            GameProperties.Black = parameters['Black'].replace('"', '')
        except KeyError:
            GameProperties.Black = ""
        try:
            GameProperties.Result = parameters['Result'].replace('"', '')
        except KeyError:
            GameProperties.Result = ""
        try:
            GameProperties.WhiteElo = parameters['WhiteElo'].replace('"', '')
        except KeyError:
            GameProperties.WhiteElo = ""
        try:
            GameProperties.BlackElo = parameters['BlackElo'].replace('"', '')
        except KeyError:
            GameProperties.BlackElo = ""
        try:
            GameProperties.ECO = parameters['ECO'].replace('"', '')
        except KeyError:
            GameProperties.ECO = ""
        try:
            GameProperties.TimeControl = parameters['TimeControl'].replace('"', '')
        except KeyError:
            GameProperties.TimeControl = "0"

        # Removes line breaks and formulates all elements into one element in the list
        chess_game = "".join(chess_game).split("  ")

        number_move_splits = "".join(chess_game).split()

        def determine_piece_list(piece_abb, whoseturn):
            piece_white_map_dict = {"N": play_objects.PlayKnight.white_knight_list,
                                    "B": play_objects.PlayBishop.white_bishop_list,
                                    "R": play_objects.PlayRook.white_rook_list,
                                    "Q": play_objects.PlayQueen.white_queen_list,
                                    "K": play_objects.PlayKing.white_king_list}
            piece_black_map_dict = {"N": play_objects.PlayKnight.black_knight_list,
                                    "B": play_objects.PlayBishop.black_bishop_list,
                                    "R": play_objects.PlayRook.black_rook_list,
                                    "Q": play_objects.PlayQueen.black_queen_list,
                                    "K": play_objects.PlayKing.black_king_list}
            if whoseturn == "white":
                if piece_abb not in piece_white_map_dict:
                    chosen_list = play_objects.PlayPawn.white_pawn_list
                else:
                    # Check other piece types (besides pawn)
                    chosen_list = piece_white_map_dict[piece_abb]
            if whoseturn == "black":
                if piece_abb not in piece_black_map_dict:
                    chosen_list = play_objects.PlayPawn.black_pawn_list
                else:
                    # Check other piece types (besides pawn)
                    chosen_list = piece_black_map_dict[piece_abb]
            return chosen_list

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
                piece_determined = eligible_pieces[0]
            elif(piece_list != play_objects.PlayPawn.white_pawn_list and piece_list != play_objects.PlayPawn.black_pawn_list):
                # Decide the logic of if there are at least 2 eligible pieces
                for piece in eligible_pieces:
                    if piece.coordinate[1] == move[1]:
                        piece_determined = piece
                    elif piece.coordinate[0] == move[1]:
                        piece_determined = piece
            else:
                # Pawns
                for piece in eligible_pieces:
                    if piece.coordinate[0] == move[0]:
                        piece_determined = piece
            return piece_determined

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
                    if game_controller.whoseturn == "white":
                        type_of_piece_list = play_objects.PlayKing.white_king_list
                        grid_coordinate = 'g1'
                    elif game_controller.whoseturn == "black":
                        type_of_piece_list = play_objects.PlayKing.black_king_list
                        grid_coordinate = 'g8'
                    piece = type_of_piece_list[0]
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = MoveController.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = MoveController.game_status_check(game_controller)
                    MoveController.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                elif move == "O-O-O":
                    if game_controller.whoseturn == "white":
                        type_of_piece_list = play_objects.PlayKing.white_king_list
                        grid_coordinate = 'c1'
                    elif game_controller.whoseturn == "black":
                        type_of_piece_list = play_objects.PlayKing.black_king_list
                        grid_coordinate = 'c8'
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = MoveController.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = MoveController.game_status_check(game_controller)
                    MoveController.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                elif move[-2:] == "=Q":
                    if game_controller.whoseturn == "white":
                        type_of_piece_list = play_objects.PlayPawn.white_pawn_list
                    elif game_controller.whoseturn == "black":
                        type_of_piece_list = play_objects.PlayPawn.black_pawn_list
                    grid_coordinate = move[-4:-2]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = MoveController.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = MoveController.game_status_check(game_controller)
                    MoveController.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                else:
                    # NORMAL MOVES
                    # Last 2 characters are always the coordinate of the grid besides special exceptions above
                    type_of_piece_list = determine_piece_list(move[0], game_controller.whoseturn)
                    if move[-1] == "+" or move[-1] == "#":
                        grid_coordinate = move[-3:-1]
                    else:
                        grid_coordinate = move[-2:]
                    piece = determine_piece(type_of_piece_list, move, grid_coordinate, game_controller)
                    prior_moves_dict, captured_abb, special_abb, promoted_queen = MoveController.make_move(board.Grid.grid_dict[grid_coordinate], piece, game_controller)
                    check_abb = MoveController.game_status_check(game_controller)
                    MoveController.record_move(game_controller, board.Grid.grid_dict[grid_coordinate], piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
                PanelController.draw_move_rects_on_moves_pane(pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, initvar.MOVE_NOTATION_FONT_SIZE))

        def prior_move_grid_update(current_coord):
            for play_obj_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for play_obj in play_obj_list:
                    if play_obj.coordinate == current_coord:
                        play_obj.prior_move_color = True
                        board.Grid.grid_dict[play_obj.previous_coordinate].prior_move_color = True
                        play_obj.no_highlight()
                        board.Grid.grid_dict[play_obj.previous_coordinate].no_highlight()
                    else:
                        play_obj.prior_move_color = False
                        play_obj.no_highlight()
        prior_move_grid_update(grid_coordinate)

        # This goes through all pieces available moves
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.spaces_available(game_controller)

        log.info("PGN Finished Loading")
        return game_controller

class EditModeController():
    @staticmethod
    def right_click_destroy(mousepos):
        start_objects.Dragging.dragging_all_false()
        start_objects.Start.restart_start_positions()
        placed_objects.remove_placed_object(mousepos)


class GridController():
    flipped = False
    @staticmethod
    def flip_grids():
        letters = 'abcdefgh'
        numbers = '12345678'
        if not GridController.flipped:
            for grid in board.Grid.grid_list:
                mirror_grid_coordinate = ""
                for l in letters:
                    if l == grid.coordinate[0]:
                        mirror_grid_coordinate += letters[-(letters.index(l)+1)]
                for n in numbers:
                    if n == grid.coordinate[1]:
                        mirror_grid_coordinate += numbers[-(numbers.index(n)+1)]
                grid.rect.topleft = board.Grid.grid_dict[mirror_grid_coordinate].initial_rect_top_left
            GridController.flipped = True
        else:
            for grid in board.Grid.grid_list:
                grid.rect.topleft = grid.initial_rect_top_left
            GridController.flipped = False
        TextController.flip_board()
    @staticmethod
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
        grid.occupied = False
        grid.occupied_piece = ""
        grid.occupied_piece_color = ""
    @classmethod
    def update_grid_occupied_detection(cls):
        for grid in board.Grid.grid_list:
            if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                cls.grid_occupied_by_piece(grid)
    @staticmethod
    def prior_move_color(grid_coordinate, prior_move_piece):
        for grid in board.Grid.grid_list:
            if grid.coordinate == grid_coordinate:
                grid.prior_move_color = True
            else:
                grid.prior_move_color = False
            grid.no_highlight()
        if not SwitchModesController.REPLAYED:
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
    @staticmethod
    def piece_on_grid(grid_coordinate):
        piece_on_grid_var = None
        if not SwitchModesController.REPLAYED:
            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if grid_coordinate == piece.coordinate:
                        piece_on_grid_var = piece
        else:
            for piece_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    if grid_coordinate == piece.coordinate:
                        piece_on_grid_var = piece
        return piece_on_grid_var
    @classmethod
    def update_prior_move_color(cls, whoseturn=None):
        if MoveTracker.move_counter() == 0:
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
                        if move_num == MoveTracker.move_counter():
                            cls.prior_move_color(piece.coordinate_history[move_num]['before'], piece)
        elif whoseturn == "black":
            for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                for piece in piece_list:
                    for move_num in piece.coordinate_history:
                        if move_num == MoveTracker.move_counter():
                            cls.prior_move_color(piece.coordinate_history[move_num]['before'], piece)
        else:
            # Replayed use case
            for grid in board.Grid.grid_list:
                grid.prior_move_color = False
                grid.no_highlight()
            for piece_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    piece.prior_move_color = False
                    piece.prior_move_update()

class SwitchModesController():
    EDIT_MODE, PLAY_MODE = 0, 1
    GAME_MODE = EDIT_MODE
    REPLAYED = False
    @classmethod
    def switch_mode(cls, game_mode, play_edit_switch_button):
        if game_mode == cls.EDIT_MODE:
            log.info("\nEditing Mode Activated\n")
            cls.GAME_MODE = cls.EDIT_MODE
            play_edit_switch_button.image = play_edit_switch_button.game_mode_button(cls.GAME_MODE)
            TextController.check_checkmate_text = ""
        elif game_mode == cls.PLAY_MODE:
            log.info("Play Mode Activated\n")
            cls.GAME_MODE = cls.PLAY_MODE
            play_edit_switch_button.image = play_edit_switch_button.game_mode_button(cls.GAME_MODE)
            cls.placed_to_play(placed_objects.PlacedPawn.white_pawn_list, play_objects.PlayPawn, "white")
            cls.placed_to_play(placed_objects.PlacedBishop.white_bishop_list, play_objects.PlayBishop, "white")
            cls.placed_to_play(placed_objects.PlacedKnight.white_knight_list, play_objects.PlayKnight, "white")
            cls.placed_to_play(placed_objects.PlacedRook.white_rook_list, play_objects.PlayRook, "white")
            cls.placed_to_play(placed_objects.PlacedQueen.white_queen_list, play_objects.PlayQueen, "white")
            cls.placed_to_play(placed_objects.PlacedKing.white_king_list, play_objects.PlayKing, "white")
            cls.placed_to_play(placed_objects.PlacedPawn.black_pawn_list, play_objects.PlayPawn, "black")
            cls.placed_to_play(placed_objects.PlacedBishop.black_bishop_list, play_objects.PlayBishop, "black")
            cls.placed_to_play(placed_objects.PlacedKnight.black_knight_list, play_objects.PlayKnight, "black")
            cls.placed_to_play(placed_objects.PlacedRook.black_rook_list, play_objects.PlayRook, "black")
            cls.placed_to_play(placed_objects.PlacedQueen.black_queen_list, play_objects.PlayQueen, "black")
            cls.placed_to_play(placed_objects.PlacedKing.black_king_list, play_objects.PlayKing, "black")
            MoveTracker.restart()
    @staticmethod
    def placed_to_play(placed_list, class_obj, color):
        # Play pieces spawn where their placed piece correspondents are located
        for placed_obj in placed_list:
            class_obj(placed_obj.coordinate, color)
    @staticmethod
    def play_to_replayed(play_list, class_obj, color):
        # Play pieces spawn where their placed piece correspondents are located
        for play_obj in play_list:
            if play_obj.coordinate is not None:
                class_obj(color, play_obj.coordinate_history, coord=play_obj.coordinate)
            elif play_obj.coordinate is None:
                class_obj(color, play_obj.coordinate_history,
                          captured_move_number_and_coordinate=play_obj.captured_move_number_and_coordinate,
                          out_of_bounds_x_y=play_obj.rect.topleft)
    @classmethod
    def rewind_moves(cls, start_beginning=False):
        first_move = cls.list_of_moves_backwards(MoveTracker.df_prior_moves)[-1]
        list_of_moves_backwards = cls.list_of_moves_backwards(MoveTracker.df_prior_moves)[:-1]
        if start_beginning:
            list_of_moves_backwards.append(first_move)
        # list_of_moves_backwards list is ordered in descending order to the selected move
        for move_dict in list_of_moves_backwards:
            for replayed_obj_list in replayed_objects.Piece_Lists_Shortcut.all_pieces():
                for replayed_obj in replayed_obj_list:
                    for piece_history in replayed_obj.coordinate_history:
                        if piece_history in dict(move_dict):
                            if replayed_obj.coordinate_history[piece_history] == ast.literal_eval(move_dict[piece_history]):
                                replayed_obj.coordinate = ast.literal_eval(move_dict[piece_history])['before']
                                GridController.prior_move_color(replayed_obj.coordinate, replayed_obj)
                                if ast.literal_eval(move_dict[piece_history])['move_notation'] == "O-O":
                                    if replayed_obj.color == "white":
                                        GridController.piece_on_grid('f1').coordinate = 'h1'
                                    elif replayed_obj.color == "black":
                                        GridController.piece_on_grid('f8').coordinate = 'h8'
                                elif ast.literal_eval(move_dict[piece_history])['move_notation'] == "O-O-O":
                                    if replayed_obj.color == "white":
                                        GridController.piece_on_grid('d1').coordinate = 'a1'
                                    elif replayed_obj.color == "black":
                                        GridController.piece_on_grid('d8').coordinate = 'a8'
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
                                                if piece.coordinate == ast.literal_eval(MoveTracker.df_prior_moves.loc[piece_history, "white_move"])['after']:
                                                    piece.kill()
                                                    replayed_objects.ReplayedQueen.white_queen_list.remove(piece)
                                    elif replayed_obj.color == "black":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.black_pieces():
                                            for piece in replayed_objects.ReplayedQueen.black_queen_list:
                                                if piece.coordinate == ast.literal_eval(MoveTracker.df_prior_moves.loc[piece_history, "black_move"])['after']:
                                                    piece.kill()
                                                    replayed_objects.ReplayedQueen.black_queen_list.remove(piece)
        # -1 in the list refers to the highlighted move in the pane
        # Retrieve the grids from the piece that we are replaying, and get the grid from the previous move to that one
        prior_move_grid_and_piece_highlight_dict = cls.list_of_moves_backwards(MoveTracker.df_prior_moves)[-1]
        old_grid_coordinate_before = ast.literal_eval(list(prior_move_grid_and_piece_highlight_dict.values())[0])['before']
        old_grid_coordinate_after = ast.literal_eval(list(prior_move_grid_and_piece_highlight_dict.values())[0])['after']
        old_piece = GridController.piece_on_grid(old_grid_coordinate_after)
        GridController.prior_move_color(old_grid_coordinate_before, old_piece)
    @classmethod
    def replayed_game(cls, replayed, game_controller, start_beginning=False):
        cls.REPLAYED = replayed
        if cls.REPLAYED:
            replayed_objects.remove_all_replayed()
            cls.play_to_replayed(play_objects.PlayPawn.white_pawn_list, replayed_objects.ReplayedPawn, "white")
            cls.play_to_replayed(play_objects.PlayBishop.white_bishop_list, replayed_objects.ReplayedBishop, "white")
            cls.play_to_replayed(play_objects.PlayKnight.white_knight_list, replayed_objects.ReplayedKnight, "white")
            cls.play_to_replayed(play_objects.PlayRook.white_rook_list, replayed_objects.ReplayedRook, "white")
            cls.play_to_replayed(play_objects.PlayQueen.white_queen_list, replayed_objects.ReplayedQueen, "white")
            cls.play_to_replayed(play_objects.PlayKing.white_king_list, replayed_objects.ReplayedKing, "white")
            cls.play_to_replayed(play_objects.PlayPawn.black_pawn_list, replayed_objects.ReplayedPawn, "black")
            cls.play_to_replayed(play_objects.PlayBishop.black_bishop_list, replayed_objects.ReplayedBishop, "black")
            cls.play_to_replayed(play_objects.PlayKnight.black_knight_list, replayed_objects.ReplayedKnight, "black")
            cls.play_to_replayed(play_objects.PlayRook.black_rook_list, replayed_objects.ReplayedRook, "black")
            cls.play_to_replayed(play_objects.PlayQueen.black_queen_list, replayed_objects.ReplayedQueen, "black")
            cls.play_to_replayed(play_objects.PlayKing.black_king_list, replayed_objects.ReplayedKing, "black")
            cls.rewind_moves(start_beginning)
        else:
            replayed_objects.remove_all_replayed()
            GridController.update_prior_move_color(game_controller.whoseturn)
    @staticmethod
    def list_of_moves_backwards(df_prior_moves):
        moves_backwards_list = []
        limit_moves = MoveTracker.selected_move[0]
        limit_color = MoveTracker.selected_move[1]
        for move_num in range(MoveTracker.move_counter(), limit_moves-1, -1):
            moves_backwards_dict = {}
            if limit_color == 'black_move' and move_num == limit_moves:
                # Selected move is black, so ignore the white move on that same move number and break
                moves_backwards_dict[move_num] = df_prior_moves.loc[move_num, 'black_move']
                moves_backwards_list.append(moves_backwards_dict)
                break
            if df_prior_moves.loc[move_num, 'black_move'] == '':
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
class MoveTracker():
    df_moves = pd.DataFrame(columns=["white_move", "black_move"])
    df_moves.index = np.arange(1, len(df_moves)+1)
    df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
    df_prior_moves.index = np.arange(1, len(df_prior_moves)+1)
    move_counter = lambda : len(MoveTracker.df_moves)
    selected_move = (0, "")
    @classmethod
    def restart(cls):
        cls.df_moves = pd.DataFrame(columns=["white_move", "black_move"])
        cls.df_moves.index = np.arange(1, len(cls.df_moves)+1)
        cls.df_prior_moves = pd.DataFrame(columns=["white_move", "black_move"])
        cls.df_prior_moves.index = np.arange(1, len(cls.df_prior_moves)+1)
        cls.selected_move = (0, "")
    @classmethod
    def undo_move_in_dfs(cls, undo_color):
        if undo_color == "black":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if MoveTracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[cls.move_counter()]
            cls.selected_move = (cls.move_counter(), "white_move")
            cls.df_moves.loc[cls.move_counter(), "black_move"] = ''
            cls.df_prior_moves.loc[cls.move_counter(), "black_move"] = ''
        elif undo_color == "white":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if MoveTracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[cls.move_counter()]
            cls.selected_move = (cls.move_counter()-1, "black_move")
            cls.df_moves = MoveTracker.df_moves.iloc[:-1]
            cls.df_prior_moves = cls.df_prior_moves.iloc[:-1]
class CpuController():
    """
    Playing against the CPU
    Coordinates on the board have different score values depending on the piece
    """
    cpu_mode = True
    cpu_color = "black"
    enemy_color = "white"
    total_possible_moves = []
    white_pawn_pos_score_dict = pos_lists_to_coord(initvar.WHITE_PAWN_POS_SCORE)
    black_pawn_pos_score_dict = pos_lists_to_coord(initvar.WHITE_PAWN_POS_SCORE[::-1])
    white_knight_pos_score_dict = pos_lists_to_coord(initvar.WHITE_KNIGHT_POS_SCORE)
    black_knight_pos_score_dict = pos_lists_to_coord(initvar.WHITE_KNIGHT_POS_SCORE[::-1])
    white_bishop_pos_score_dict = pos_lists_to_coord(initvar.WHITE_BISHOP_POS_SCORE)
    black_bishop_pos_score_dict = pos_lists_to_coord(initvar.WHITE_BISHOP_POS_SCORE[::-1])
    white_king_pos_score_dict = pos_lists_to_coord(initvar.WHITE_KING_POS_SCORE)
    black_king_pos_score_dict = pos_lists_to_coord(initvar.WHITE_KING_POS_SCORE[::-1])
    white_rook_pos_score_dict = pos_lists_to_coord([0]*64)
    black_rook_pos_score_dict = pos_lists_to_coord([0]*64)
    white_queen_pos_score_dict = pos_lists_to_coord([0]*64)
    black_queen_pos_score_dict = pos_lists_to_coord([0]*64)
    @classmethod
    def cpu_mode_toggle(cls):
        if not cls.cpu_mode:
            cls.cpu_mode = True
        elif cls.cpu_mode:
            cls.cpu_mode = False
    @classmethod
    def analyze_board(cls, grid, piece_to_move, piece_color):
        white_score = 0
        black_score = 0
        for white_piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
            for white_piece in white_piece_list:
                if not white_piece.taken_off_board:
                    if white_piece in play_objects.PlayPawn.white_pawn_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_pawn_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_pawn_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['pawn']
                    elif white_piece in play_objects.PlayKnight.white_knight_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_knight_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_knight_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['knight']
                    elif white_piece in play_objects.PlayBishop.white_bishop_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_bishop_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_bishop_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['bishop']
                    elif white_piece in play_objects.PlayKing.white_king_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_king_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_king_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['king']
                    elif white_piece in play_objects.PlayRook.white_rook_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_rook_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_rook_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['rook']
                    elif white_piece in play_objects.PlayQueen.white_queen_list:
                        if piece_to_move == white_piece:
                            white_score += cls.white_queen_pos_score_dict[grid.coordinate]
                        else:
                            white_score += cls.white_queen_pos_score_dict[white_piece.coordinate]
                        white_score += initvar.piece_values_dict['queen']
        for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
            for black_piece in black_piece_list:
                if not black_piece.taken_off_board:
                    if black_piece in play_objects.PlayPawn.black_pawn_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_pawn_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_pawn_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['pawn']
                    elif black_piece in play_objects.PlayKnight.black_knight_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_knight_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_knight_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['knight']
                    elif black_piece in play_objects.PlayBishop.black_bishop_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_bishop_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_bishop_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['bishop']
                    elif black_piece in play_objects.PlayKing.black_king_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_king_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_king_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['king']
                    elif black_piece in play_objects.PlayRook.black_rook_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_rook_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_rook_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['rook']
                    elif black_piece in play_objects.PlayQueen.black_queen_list:
                        if piece_to_move == black_piece:
                            black_score += cls.black_queen_pos_score_dict[grid.coordinate]
                        else:
                            black_score += cls.black_queen_pos_score_dict[black_piece.coordinate]
                        black_score += initvar.piece_values_dict['queen']
        if piece_color == "white":
            total_score = white_score
        elif piece_color == "black":
            total_score = black_score
        return total_score
    @classmethod
    def total_possible_moves_update(cls):
        cls.total_possible_moves = []
        for grid in board.Grid.grid_list:
            # grid is the future move
            if grid.coords_of_available_pieces[cls.cpu_color]:
                for original_grid_coord_of_piece_to_move in grid.coords_of_available_pieces[cls.cpu_color]:
                    for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                        for piece in piece_list:
                            if original_grid_coord_of_piece_to_move == piece.coordinate:
                                piece_to_move = piece
                    cls.total_possible_moves.append((grid, piece_to_move))
    @classmethod
    def random_move(cls):
        return random.choice(cls.total_possible_moves)
    @classmethod
    def choose_move(cls):
        move_score_list = []
        random.seed(4)
        random.shuffle(cls.total_possible_moves)
        for possible_move in cls.total_possible_moves:
            grid = possible_move[0]
            piece_to_move = possible_move[1]
            move_score = cls.analyze_board(grid, piece_to_move, cls.cpu_color)
            if grid.occupied and not grid.coords_of_attacking_pieces[cls.enemy_color]:
                # No other attack pieces
                move_score += play_objects.Piece_Lists_Shortcut.piece_on_coord(grid.coordinate).score
            elif grid.occupied and grid.coords_of_attacking_pieces[cls.enemy_color]:
                # Trade only when other piece is higher value
                move_score = play_objects.Piece_Lists_Shortcut.piece_on_coord(grid.coordinate).score - piece_to_move.score
            if cls.cpu_color == "black":
                if piece_to_move in play_objects.PlayKing.black_king_list:
                    # Incentivize Castling
                    if piece_to_move.king_side_castle_ability and grid.coordinate == 'g8':
                        move_score += 0.5
                    elif piece_to_move.queen_side_castle_ability and grid.coordinate == 'c8':
                        move_score += 0.5
                    elif piece_to_move.castled:
                        pass
                    else:
                        # If king move not a castle move, don't do it early on
                        move_score -= 0.5
                elif piece_to_move in play_objects.PlayRook.black_rook_list:
                    # Disincentivize rook from moving before castling
                    if piece_to_move.allowed_to_castle:
                        move_score -= 0.5
                    elif not piece_to_move.allowed_to_castle:
                        pass
                """
                if len(board.Grid.grid_dict[grid.coordinate].coords_of_attacking_pieces['white']) > 0 \
                    and len(board.Grid.grid_dict[grid.coordinate].coords_of_protecting_pieces['black']) <= 1:
                        # Moving to a square being attacked by white and 0 protection
                        move_score -= piece_to_move.score
                elif len(board.Grid.grid_dict[grid.coordinate].coords_of_attacking_pieces['white']) > 0 \
                    and len(board.Grid.grid_dict[grid.coordinate].coords_of_protecting_pieces['black']) > 1:
                        # Moving to a square being attacked by white but you have some protection
                    lowest_attacker_score = []
                    for attacking_grid in board.Grid.grid_dict[grid.coordinate].coords_of_attacking_pieces['white']:
                        attacker_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(attacking_grid)
                        if attacker_piece not in play_objects.PlayKing.white_king_list:
                            if attacker_piece.score <= piece_to_move.score:
                                lowest_attacker_score.append(attacker_piece.score-piece_to_move.score)
                            else: 
                                lowest_attacker_score.append(0)
                        else:
                            lowest_attacker_score.append(0)
                    move_score += min(lowest_attacker_score)
                if len(board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces['white']) > 0 \
                    and len(board.Grid.grid_dict[grid.coordinate].coords_of_attacking_pieces['white']) == 0:
                        # Available space without an attacking piece
                        if piece_to_move not in play_objects.PlayKing.black_king_list:
                            move_score += piece_to_move.score
                        else:
                            pass
                elif len(board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces['white']) > 0 \
                    and len(board.Grid.grid_dict[piece_to_move.coordinate].coords_of_protecting_pieces['black']) > 1:
                        # Current piece being attacked and is being protected
                    lowest_attacker_score = []
                    for attacking_grid in board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces['white']:
                        attacker_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(attacking_grid)
                        if attacker_piece not in play_objects.PlayKing.white_king_list:
                            if attacker_piece.score <= piece_to_move.score:
                                lowest_attacker_score.append(piece_to_move.score-attacker_piece.score)
                            else:
                                lowest_attacker_score.append(0)
                        else:
                            lowest_attacker_score.append(0)
                    move_score += max(lowest_attacker_score)
            elif CpuController.cpu_color == "white":
                if piece_to_move in play_objects.PlayKing.white_king_list:
                    # Incentivize Castling
                    if piece_to_move.king_side_castle_ability == True and grid.coordinate == 'g1':
                        move_score += 0.5
                    elif piece_to_move.queen_side_castle_ability == True and grid.coordinate == 'c1':
                        move_score += 0.5
                    else:
                        # If king move not a castle move, don't do it early on
                        move_score -= 0.5
                elif piece_to_move in play_objects.PlayRook.white_rook_list:
                    # Disincentivize rook from moving before castling
                    if piece_to_move.allowed_to_castle == True:
                        move_score -= 0.5
                if len(board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces['black']) > 0 \
                    and len(board.Grid.grid_dict[piece_to_move.coordinate].coords_of_protecting_pieces['white']) == 0:
                        if len(grid.coords_of_protecting_pieces['white']) > 0:
                            move_score += piece_to_move.score
                """
            move_score_list.append(move_score)
        max_move = max(move_score_list)
        index_of_max_moves = move_score_list.index(max_move)
        return cls.total_possible_moves[index_of_max_moves]

class GameController():
    """
    How pieces are effected after a move has been formally made
    For example, after a white bishop finished its move, then the grids
    that are in the line of sight from the bishop have its respective variables
    """
    def __init__(self, flipped, whoseturn="white"):
        self.whoseturn = whoseturn
        self.color_in_check = ""
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        self.black_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.white_captured_x = initvar.BLACKANDWHITE_CAPTURED_X
        self.captured_pieces_flip(flipped)
        self.result_abb = "*"
    def captured_pieces_flip(self, flipped):
        if not flipped:
            self.white_captured_y = initvar.WHITE_CAPTURED_Y
            self.black_captured_y = initvar.BLACK_CAPTURED_Y
        else:
            self.white_captured_y = initvar.BLACK_CAPTURED_Y
            self.black_captured_y = initvar.WHITE_CAPTURED_Y
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if piece.taken_off_board:
                    if piece.color == "white":
                        piece.rect.topleft = piece.rect.topleft[0], self.white_captured_y
                    elif piece.color == "black":
                        piece.rect.topleft = piece.rect.topleft[0], self.black_captured_y
    def refresh_objects(self):
        GridController.update_grid_occupied_detection()
        self.projected_white_update()
        self.projected_black_update()
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.spaces_available(self)
        GridController.update_grid_occupied_detection()
        for grid in board.Grid.grid_list:
            grid.no_highlight()
    def __del__(self):
        """
        GameController can get deleted when going to Edit Mode
        Remove Check and Checkmate Text
        Destroy all play objects and remove them from list
        Reset all the grids
        """
        TextController.remove_check_checkmate_text()
        # Kill all Objects within their Class lists/dicts
        for spr_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for obj in spr_list:
                obj.kill()
        for spr_list in [menu_buttons.MoveNumberRectangle.rectangle_list, menu_buttons.PieceMoveRectangle.rectangle_list]:
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
        SwitchModesController.replayed_game(False, self)
        # Reset Moves Panel
        menu_buttons.MoveNumberRectangle.rectangle_list = []
        menu_buttons.PieceMoveRectangle.rectangle_list = []
        menu_buttons.MoveNumberRectangle.rectangle_dict = {}
        menu_buttons.PieceMoveRectangle.rectangle_dict = {}
        menu_buttons.PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
    def switch_turn(self, color_turn, undo=False):
        """
        Change turn
        If it was in check, it is no longer in check, and no more check piece
        Reset the grid variables about attacking pieces, available pieces
        Pieces that were labeled as attacking in grids, now become protecting
        since the turn switched
        Reset pinned pieces
        
        Checks if it is white move. If so, remove black check.
        Project black moves.
        If the grid white king is on has attacking pieces, then it is in check
        If double check then disable pieces from moving
        """
        self.whoseturn = color_turn
        self.check_attacking_coordinates = []
        self.attacker_piece = ""
        # No highlights and ensuring that attacking squares (used by diagonal pieces) are set to 0
        for grid in board.Grid.grid_list:
            grid.no_highlight()
            grid.coords_of_protecting_pieces['white'] = grid.coords_of_attacking_pieces['white']
            grid.coords_of_protecting_pieces['black'] = grid.coords_of_attacking_pieces['black']
            grid.coords_of_attacking_pieces['white'] = []
            grid.coords_of_attacking_pieces['black'] = []
            grid.coords_of_available_pieces['white'] = []
            grid.coords_of_available_pieces['black'] = []
        GridController.update_grid_occupied_detection()
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                piece.pinned = False
                piece.disable = False
        if self.whoseturn == "white":
            if not undo:
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
            GridController.update_grid_occupied_detection()
        elif self.whoseturn == "black":
            if not undo:
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
            GridController.update_grid_occupied_detection()
    def projected_white_update(self):
        """
        Project white pieces attacking movements
        """
        for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
            for piece in piece_list:
                piece.projected(self)
    def projected_black_update(self):
        """
        Project black pieces attacking movements
        """
        for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
            for piece in piece_list:
                piece.projected(self)
    @staticmethod
    def pinned_piece(pinned_piece_coordinate, pin_attacking_coordinates, color):
        """
        Iterates through all pieces to find the one that matches
        the coordinate with the pin
        """
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if board.Grid.grid_dict[pinned_piece_coordinate].coordinate == piece.coordinate \
                and piece.color == color:
                    piece.pinned_restrict(pin_attacking_coordinates)
    def king_in_check(self, attacker_piece, check_attacking_coordinates, color):
        """
        This function is called when projected from piece hits king
        For example, if white bishop checks black king, 
        the white bishop's projected function calls king_in_check function
        
        This is an instance method because GameController keeps track of the 
        color of who is in check, the coordinates of the attacking coordinates,
        and the piece that is attacking
        """
        self.color_in_check = color
        self.check_attacking_coordinates = check_attacking_coordinates
        self.attacker_piece = attacker_piece

class TextController():
    """
    Handle all text objects in this class
    """
    universal_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, initvar.UNIVERSAL_FONT_SIZE)
    move_notation_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, initvar.MOVE_NOTATION_FONT_SIZE)
    coor_A_text = universal_font.render("a", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_B_text = universal_font.render("b", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_C_text = universal_font.render("c", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_D_text = universal_font.render("d", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_E_text = universal_font.render("e", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_F_text = universal_font.render("f", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_G_text = universal_font.render("g", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_H_text = universal_font.render("h", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_1_text = universal_font.render("1", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_2_text = universal_font.render("2", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_3_text = universal_font.render("3", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_4_text = universal_font.render("4", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_5_text = universal_font.render("5", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_6_text = universal_font.render("6", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_7_text = universal_font.render("7", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_8_text = universal_font.render("8", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_letter_text_list = [coor_A_text, coor_B_text, coor_C_text, coor_D_text, coor_E_text, coor_F_text, coor_G_text, coor_H_text]
    coor_number_text_list = [coor_8_text, coor_7_text, coor_6_text, coor_5_text, coor_4_text, coor_3_text, coor_2_text, coor_1_text]
    check_checkmate_text = ""
    @classmethod
    def remove_check_checkmate_text(cls):
        """
        Not in check or checkmate, or resetting the game
        """
        cls.check_checkmate_text = ""
    @classmethod
    def flip_board(cls):
        """
        Coordinate texts flip when the board flips
        """
        cls.coor_letter_text_list.reverse()
        cls.coor_number_text_list.reverse()
        
class MoveController():
    """
    Select piece on board, make the move, complete the move, 
    check the game status (stalemate, checkmate, check), record the move
    (use move_translator for converting move to notation). 
    Ability to undo move
    """
    @staticmethod
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
        def get_prefix(piece, piece_name, captured_abb, special_abb):
            """
            Detecting when there is another piece of same color that 
            can attack the same position
            In order to get the prefix, we call out the positioning of piece
            When there is another of the same piece
            """
            prefix_characters = ""
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
                        prefix_characters += piece.previous_coordinate[0]
                        prefix = prefix_characters
                    elif piece.previous_coordinate[0] in letter_coords and piece.previous_coordinate[1] not in number_coords:
                        prefix_characters += piece.previous_coordinate[1]
                        prefix = prefix_characters
                    if((piece_name == "pawn" and captured_abb == "x") or (special_abb == "=Q" and captured_abb == "x")):
                        prefix_characters += piece.previous_coordinate[0]
                    prefix = prefix_characters
            return prefix
        if piece.color == "white":
            prefix = get_prefix(piece, piece_name, captured_abb, special_abb)
        elif piece.color == "black":
            prefix = get_prefix(piece, piece_name, captured_abb, special_abb)
        if special_abb == "":
            recorded_move = piece_abb + prefix + captured_abb + piece.coordinate[0] + piece.coordinate[1] + check_abb
        elif special_abb == "O-O":
            recorded_move = special_abb + check_abb
        elif special_abb == "O-O-O":
            recorded_move = special_abb + check_abb
        elif special_abb == "=Q":
            recorded_move = prefix + captured_abb + piece.coordinate[0] + piece.coordinate[1] + special_abb + check_abb
        return recorded_move
    @staticmethod
    def select_piece_unselect_all_others(piece_coord, game_controller):
        clicked_piece = None
        # Selecting and unselecting white pieces
        if game_controller.whoseturn == "white":
            for piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                for piece in piece_list:
                    # Selects piece
                    if (piece.coordinate == piece_coord and not piece.select and not SwitchModesController.REPLAYED):
                        clicked_piece = piece
                    else:
                        # Unselects piece
                        piece.no_highlight()
                        for grid in board.Grid.grid_list:
                            grid.no_highlight()
        # Selecting and unselecting black pieces
        elif game_controller.whoseturn == "black":
            for piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for piece in piece_list:
                    if (piece.coordinate == piece_coord and not piece.select and not SwitchModesController.REPLAYED):
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
    @classmethod
    def undo_move(cls, game_controller):
        SwitchModesController.replayed_game(False, game_controller)
        pieces_to_undo = []
        # Using pieces_to_undo as a list for castling
        if MoveTracker.move_counter() >= 1:
            # Finding the latest piece to undo
            if game_controller.whoseturn == "white":
                piece_coordinate_move_notation = ast.literal_eval(MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "black_move"])['move_notation']
                for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                    for black_piece in black_piece_list:
                        for piece_history in black_piece.coordinate_history.keys():
                            if MoveTracker.move_counter() == piece_history:
                                pieces_to_undo.append(black_piece)
            elif game_controller.whoseturn == "black":
                piece_coordinate_move_notation = ast.literal_eval(MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "white_move"])['move_notation']
                for white_piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                    for white_piece in white_piece_list:
                        for piece_history in white_piece.coordinate_history.keys():
                            if MoveTracker.move_counter() == piece_history:
                                pieces_to_undo.append(white_piece)
            if 'x' in piece_coordinate_move_notation:
                # Detect pieces that have been taken
                if pieces_to_undo[0].color == "black":
                    for white_piece_list in play_objects.Piece_Lists_Shortcut.white_pieces():
                        for white_piece in white_piece_list:
                            if white_piece.taken_off_board:
                                if white_piece.captured_move_number_and_coordinate['move_number'] == MoveTracker.move_counter():
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
                            if black_piece.taken_off_board:
                                if black_piece.captured_move_number_and_coordinate['move_number'] == MoveTracker.move_counter():
                                    black_piece.taken_off_board = False
                                    black_piece.coordinate = black_piece.captured_move_number_and_coordinate['coordinate']
                                    black_piece.rect.topleft = board.Grid.grid_dict[black_piece.coordinate].rect.topleft
                                    game_controller.black_captured_x -= initvar.BLACKANDWHITE_INCREMENTAL_X
                                    if 'ep_grid_after_coord' in black_piece.captured_move_number_and_coordinate:
                                        board.Grid.grid_dict[black_piece.captured_move_number_and_coordinate['ep_grid_after_coord']].en_passant_skipover = True
                                    black_piece.captured_move_number_and_coordinate = None
            if game_controller.whoseturn == "white":
                for piece_to_undo in pieces_to_undo:
                    piece_to_undo.coordinate = piece_to_undo.coordinate_history[MoveTracker.move_counter()]['before']
                    piece_to_undo.rect.topleft = board.Grid.grid_dict[piece_to_undo.coordinate].rect.topleft
                    del piece_to_undo.coordinate_history[MoveTracker.move_counter()]
                    GridController.grid_occupied_by_piece(board.Grid.grid_dict[piece_to_undo.coordinate])
                if 'O-O' in piece_coordinate_move_notation or 'O-O-O' in piece_coordinate_move_notation:
                    for black_king in play_objects.PlayKing.black_king_list:
                        if black_king in pieces_to_undo:
                            black_king.castled = False
                    for black_rook in play_objects.PlayRook.black_rook_list:
                        if black_rook in pieces_to_undo:
                            black_rook.allowed_to_castle = True
                if "=Q" in piece_coordinate_move_notation:
                    for q in play_objects.PlayQueen.black_queen_list:
                        if q.coordinate == ast.literal_eval(MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "black_move"])['after']:
                            queen = q
                    queen.kill()
                    play_objects.PlayQueen.black_queen_list.remove(queen)
                if pieces_to_undo[0] in play_objects.PlayPawn.black_pawn_list:
                    pieces_to_undo[0].taken_off_board = False
                PanelController.remove_latest_move('black_move')
                MoveTracker.undo_move_in_dfs("black")
                PanelController.scroll_to_latest_move(MoveTracker.move_counter())
                game_controller.switch_turn("black", undo=True)
                GridController.update_prior_move_color("black")
                cls.game_status_check(game_controller)
                log.info("Back to (" + str(len(MoveTracker.df_moves)) + ".) " + "Black undo turn " + str(piece_to_undo) + " going back to " + str(piece_to_undo.coordinate))
            elif game_controller.whoseturn == "black":
                for piece_to_undo in pieces_to_undo:
                    piece_to_undo.coordinate = piece_to_undo.coordinate_history[MoveTracker.move_counter()]['before']
                    piece_to_undo.rect.topleft = board.Grid.grid_dict[piece_to_undo.coordinate].rect.topleft
                    del piece_to_undo.coordinate_history[MoveTracker.move_counter()]
                    GridController.grid_occupied_by_piece(board.Grid.grid_dict[piece_to_undo.coordinate])
                if 'O-O' in piece_coordinate_move_notation or 'O-O-O' in piece_coordinate_move_notation:
                    for white_king in play_objects.PlayKing.white_king_list:
                        if white_king in pieces_to_undo:
                            white_king.castled = False
                    for white_rook in play_objects.PlayRook.white_rook_list:
                        if white_rook in pieces_to_undo:
                            white_rook.allowed_to_castle = True
                if "=Q" in piece_coordinate_move_notation:
                    for q in play_objects.PlayQueen.white_queen_list:
                        if q.coordinate == ast.literal_eval(MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "white_move"])['after']:
                            queen = q
                    queen.kill()
                    play_objects.PlayQueen.white_queen_list.remove(queen)
                if pieces_to_undo[0] in play_objects.PlayPawn.white_pawn_list:
                    pieces_to_undo[0].taken_off_board = False
                PanelController.remove_latest_move('white_move')
                MoveTracker.undo_move_in_dfs("white")
                PanelController.scroll_to_latest_move(MoveTracker.move_counter())
                game_controller.switch_turn("white", undo=True)
                GridController.update_prior_move_color("white")
                cls.game_status_check(game_controller)
                log.info("Back to (" + str(len(MoveTracker.df_moves)) + ".) " + "White undo turn " + str(piece_to_undo) + " going back to " + str(piece_to_undo.coordinate))
    @classmethod
    def complete_move(cls, new_coord, game_controller):
        for grid in board.Grid.grid_list:
            for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
                for piece in piece_list:
                    # Reset the prior move color variable from all pieces
                    piece.prior_move_color = False
                    # If piece is allowed to move to another grid coordinate and piece is also selected
                    if (grid.coordinate == new_coord \
                        and ((piece.coordinate in grid.coords_of_available_pieces['white'] and piece.color == "white") \
                             or (piece.coordinate in grid.coords_of_available_pieces['black'] and piece.color == "black")) \
                                 and piece.select):
                        prior_moves_dict, captured_abb, special_abb, promoted_queen = cls.make_move(grid, piece, game_controller)
                        check_abb = cls.game_status_check(game_controller)
                        cls.record_move(game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen)
    @staticmethod
    def make_move(grid, piece, game_controller):
        # Default captured_abb for function to be empty string
        captured_abb = ""
        # Castle, pawn promotion
        special_abb = ""
        # White win, draw, black win
        game_controller.result_abb = "*"
        promoted_queen = None
        prior_moves_dict = {}
        # Update df_moves dictionary with a new record for the new move (when white's turn)
        if piece.color == "white":
            next_move = MoveTracker.move_counter()+1
            MoveTracker.df_moves.loc[next_move] = ["", ""]
            MoveTracker.df_prior_moves.loc[next_move] = ["", ""]
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
                            piece_captured.captured(game_controller.black_captured_x, game_controller.black_captured_y, MoveTracker.move_counter())
                            game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                        elif piece_captured.color == "white":
                            piece_captured.captured(game_controller.white_captured_x, game_controller.white_captured_y, MoveTracker.move_counter())
                            game_controller.white_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                        # Captured_abb used for move notation
                        captured_abb = "x"
        # En Passant Capture
        if grid.en_passant_skipover:
            if piece in play_objects.PlayPawn.white_pawn_list:
                for black_pawn in play_objects.PlayPawn.black_pawn_list:
                    # Must include taken_off_board bool or else you get NoneType error
                    if not black_pawn.taken_off_board:
                        if black_pawn.coordinate[0] == grid.coordinate[0] and \
                        int(black_pawn.coordinate[1]) == 5:
                            black_pawn.captured(game_controller.black_captured_x, game_controller.black_captured_y, MoveTracker.move_counter(), grid.coordinate)
                            game_controller.black_captured_x += initvar.BLACKANDWHITE_INCREMENTAL_X
                            captured_abb = "x"
            elif piece in play_objects.PlayPawn.black_pawn_list:
                for white_pawn in play_objects.PlayPawn.white_pawn_list:
                    # Must include taken_off_board bool or else you get NoneType error
                    if not white_pawn.taken_off_board:
                        if white_pawn.coordinate[0] == grid.coordinate[0] and \
                        int(white_pawn.coordinate[1]) == 4:
                            white_pawn.captured(game_controller.white_captured_x, game_controller.white_captured_y, MoveTracker.move_counter(), grid.coordinate)
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
                piece.coordinate_history[MoveTracker.move_counter()] = {'before':piece.previous_coordinate}
                prior_moves_dict['before'] = piece.previous_coordinate
                chosen_prior_grid = old_grid
                
        # Moving piece, removing piece and grid highlights, changing Turn
        piece.rect.topleft = grid.rect.topleft
        piece.coordinate = grid.coordinate
        piece.coordinate_history[MoveTracker.move_counter()]['after'] = piece.coordinate
        prior_moves_dict['after'] = piece.coordinate
        grid.occupied = True
        
        GridController.prior_move_color(chosen_prior_grid.coordinate, piece)

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
                piece.captured(game_controller.white_captured_x, game_controller.white_captured_y, MoveTracker.move_counter())
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
                piece.captured(game_controller.black_captured_x, game_controller.black_captured_y, MoveTracker.move_counter())
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
                if rook.allowed_to_castle:
                    if rook.coordinate == 'a1' and piece.coordinate == 'c1':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d1'].coordinate
                        board.Grid.grid_dict['d1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'a1'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'd1'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h1' and piece.coordinate == 'g1':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['f1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f1'].coordinate
                        board.Grid.grid_dict['f1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'h1'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'f1'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O'
        elif piece in play_objects.PlayKing.black_king_list:
            piece.castled = True
            for rook in play_objects.PlayRook.black_rook_list:
                if rook.allowed_to_castle:
                    if rook.coordinate == 'a8' and piece.coordinate == 'c8':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d8'].coordinate
                        board.Grid.grid_dict['d8'].occupied = True
                        special_abb = "O-O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'a8'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'd8'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h8' and piece.coordinate == 'g8':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['f8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['f8'].coordinate
                        board.Grid.grid_dict['f8'].occupied = True
                        special_abb = "O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'h8'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'f8'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O'
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
        GridController.update_grid_occupied_detection()
        # Switch turns
        if game_controller.whoseturn == "white":
            game_controller.switch_turn("black")
        elif game_controller.whoseturn == "black":
            game_controller.switch_turn("white")
            
        return prior_moves_dict, captured_abb, special_abb, promoted_queen
    @staticmethod
    def game_status_check(game_controller):
        check_abb = ""
        def stalemate_check(whoseturn):
            for subgrid in board.Grid.grid_list:
                if len(subgrid.coords_of_available_pieces[whoseturn]) > 0:
                    # No check, no checkmate, no stalemate
                    TextController.check_checkmate_text = ""
                    return "*"
            TextController.check_checkmate_text = "Stalemate"
            return "1/2-1/2"
        def checkmate_check(whoseturn):
            for subgrid in board.Grid.grid_list:
                if len(subgrid.coords_of_available_pieces[whoseturn]) > 0:
                    # If able to detect that a grid can be available, that means it's NOT checkmate
                    return "+", "*"
            if whoseturn == 'black':
                TextController.check_checkmate_text = "White wins"
                game_result = "#", "1-0"
            elif whoseturn == 'white':
                TextController.check_checkmate_text = "Black wins"
                game_result = "#", "0-1"
            return game_result
        if game_controller.color_in_check == "black":
            TextController.check_checkmate_text = "Black King checked"
            check_abb, game_controller.result_abb = checkmate_check('black')
        elif game_controller.color_in_check == "white":
            TextController.check_checkmate_text = "White King checked"
            check_abb, game_controller.result_abb = checkmate_check('white')
        elif game_controller.color_in_check == "" and game_controller.whoseturn == "white":
            game_controller.result_abb = stalemate_check('white')
        elif game_controller.color_in_check == "" and game_controller.whoseturn == "black":
            game_controller.result_abb = stalemate_check('black')
        else:
            # No checks
            TextController.check_checkmate_text = ""
        for grid in board.Grid.grid_list:
            grid.no_highlight()
        GameProperties.Result = game_controller.result_abb
        return check_abb
    @classmethod
    def record_move(cls, game_controller, grid, piece, prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen=None):
        if game_controller.whoseturn == "white":
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
            move_text = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb) + " "
            MoveTracker.df_moves.loc[MoveTracker.move_counter(), "black_move"] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[MoveTracker.move_counter()]['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            MoveTracker.selected_move = (MoveTracker.move_counter(), "black_move")
            MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "black_move"] = str(prior_moves_dict)
        elif game_controller.whoseturn == "black":
            # Create new record to make room for new white move
            # move_counter will update to new length of dataframe
            if special_abb == "=Q":
                piece_in_funcs = promoted_queen
            else:
                piece_in_funcs = piece
            move_text = str(MoveTracker.move_counter()) + ". " + \
                  cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb) + " "
            MoveTracker.df_moves.loc[MoveTracker.move_counter(), "white_move"] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[MoveTracker.move_counter()]['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            MoveTracker.selected_move = (MoveTracker.move_counter(), "white_move")
            MoveTracker.df_prior_moves.loc[MoveTracker.move_counter(), "white_move"] = str(prior_moves_dict)
        SwitchModesController.replayed_game(False, game_controller)
        log.info(move_text)
        if game_controller.result_abb != "*":
            log.info(game_controller.result_abb)

class PanelController:
    """
    After a move is made, create a new instance of the Move number rectangle,
    and the piece move rectangle
    Then position text on those rectangles
    When the amount of moves exceeds the parameter, scroll to the latest move
    """
    @staticmethod
    def draw_text_on_rects_in_moves_pane(surface, my_font):
        for move_num_rect in menu_buttons.MoveNumberRectangle.rectangle_list:
            if move_num_rect.text_is_visible:
                # Only draw the text if the rectangle is below the top of the pane
                move_num_text = my_font.render(move_num_rect.text, True, initvar.MOVE_TEXT_COLOR_ON_PANE)
                surface.blit(move_num_text, (move_num_rect.x, move_num_rect.y))
        for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
            if piece_move_rect.text_is_visible:
                move_notation_text = my_font.render(piece_move_rect.move_notation, True, initvar.MOVE_TEXT_COLOR_ON_PANE)
                surface.blit(move_notation_text, (piece_move_rect.x, piece_move_rect.y))
    @staticmethod
    def scroll_to_latest_move(latest_move_number):
        if latest_move_number >= initvar.MOVES_PANE_MAX_MOVES:
            menu_buttons.PanelRectangles.scroll_range[0] = latest_move_number - (initvar.MOVES_PANE_MAX_MOVES-1)
            menu_buttons.PanelRectangles.scroll_range[1] = latest_move_number
            for move_num_rect in menu_buttons.MoveNumberRectangle.rectangle_list:
                move_num_rect.update_Y()
            for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
                piece_move_rect.update_Y()
    @staticmethod
    def scroll_to_first_move():
        menu_buttons.PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
        for move_num_rect in menu_buttons.MoveNumberRectangle.rectangle_list:
            move_num_rect.update_Y()
        for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
            piece_move_rect.update_Y()
    @staticmethod
    def update_scroll_range(unit_change):
        # unit_change refers to how many moves up/down to go
        # unit_change = -1 means scrolling up one unit, unit_change = 1 means scrolling down one unit
        menu_buttons.PanelRectangles.scroll_range[0] += unit_change
        menu_buttons.PanelRectangles.scroll_range[1] += unit_change
        for move_num_rect in menu_buttons.MoveNumberRectangle.rectangle_list:
            move_num_rect.update_Y()
        for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
            piece_move_rect.update_Y()
    @classmethod
    def draw_move_rects_on_moves_pane(cls, my_font):
        if len(MoveTracker.df_moves) >= 1:
            # Creating move notation rectangles if they haven't been created before for the respective move
            # If the last move is not in the dictionary, then add it
            if len(MoveTracker.df_moves) not in menu_buttons.PieceMoveRectangle.rectangle_dict:
                menu_buttons.PieceMoveRectangle.rectangle_dict[len(MoveTracker.df_moves)] = {}
                menu_buttons.MoveNumberRectangle.rectangle_dict[len(MoveTracker.df_moves)] = []
            # We want the menu_buttons.PieceMoveRectangle.rectangle_dict to correspond to the df_moves dataframe
            if MoveTracker.df_moves.loc[len(MoveTracker.df_moves), 'white_move'] != '' and 'white_move' not in menu_buttons.PieceMoveRectangle.rectangle_dict[len(MoveTracker.df_moves)]:
                # Create new move number rectangle since white made a move
                menu_buttons.MoveNumberRectangle(len(MoveTracker.df_moves), initvar.MOVES_PANE_MOVE_NUMBER_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(MoveTracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                # Create rectangle which will eventually be used to blit text on it
                # Parameters: Total number of moves in the game, the move itself, the color of the piece that moved, and position & size of rectangle
                menu_buttons.PieceMoveRectangle(len(MoveTracker.df_moves), MoveTracker.df_moves.loc[len(MoveTracker.df_moves), 'white_move'], 'white_move', initvar.MOVES_PANE_WHITE_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(MoveTracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                # Scroll down automatically when a move is made
                cls.scroll_to_latest_move(len(MoveTracker.df_moves))
            if MoveTracker.df_moves.loc[len(MoveTracker.df_moves), 'black_move'] != '' and 'black_move' not in menu_buttons.PieceMoveRectangle.rectangle_dict[len(MoveTracker.df_moves)]:
                # Only create menu_buttons.PieceMoveRectangle when black moved last, don't create a new menu_buttons.MoveNumberRectangle
                menu_buttons.PieceMoveRectangle(len(MoveTracker.df_moves), MoveTracker.df_moves.loc[len(MoveTracker.df_moves), 'black_move'], 'black_move', initvar.MOVES_PANE_BLACK_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*len(MoveTracker.df_moves), initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)        
                cls.scroll_to_latest_move(len(MoveTracker.df_moves))
            cls.draw_text_on_rects_in_moves_pane(lis.SCREEN, my_font)
    @staticmethod
    def remove_latest_move(color_move):
        menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move].move_notation = ""
        menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move].kill()
        del menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move]
        if color_move == "white_move":
            menu_buttons.MoveNumberRectangle.rectangle_dict[MoveTracker.move_counter()].text = ""
            menu_buttons.MoveNumberRectangle.rectangle_dict[MoveTracker.move_counter()].kill()

def main():
    try:
        # Tk box for when saving and loading
        # Must include this so the TK window doesn't stay in the background
        root = tk.Tk()
        root.withdraw()
        
        running, debug = 0, 1
        state = running
        debug_message = 0
        
        clock = pygame.time.Clock()
        
        play_edit_switch_button = menu_buttons.PlayEditSwitchButton(initvar.PLAY_EDIT_SWITCH_BUTTON_TOPLEFT)
        flip_board_button = menu_buttons.FlipBoardButton(initvar.FLIP_BOARD_BUTTON_TOPLEFT)
        cpu_button = menu_buttons.CPUButton(initvar.CPU_BUTTON_TOPLEFT, CpuController.cpu_mode)
        game_properties_button = menu_buttons.GamePropertiesButton(initvar.GAME_PROPERTIES_BUTTON_TOPLEFT)
        pos_load_file_button = menu_buttons.PosLoadFileButton(initvar.POS_LOAD_FILE_BUTTON_TOPLEFT)
        pos_save_file_button = menu_buttons.PosSaveFileButton(initvar.POS_SAVE_FILE_BUTTON_TOPLEFT)
        pgn_load_file_button = menu_buttons.PGNLoadFileButton(initvar.PGN_LOAD_FILE_BUTTON_TOPLEFT)
        pgn_save_file_button = menu_buttons.PGNSaveFileButton(initvar.PGN_SAVE_FILE_BUTTON_TOPLEFT)
        load_file_placeholder = menu_buttons.LoadFilePlaceholder(initvar.LOAD_FILE_PLACEHOLDER_TOPLEFT)
        save_file_placeholder = menu_buttons.SaveFilePlaceholder(initvar.SAVE_FILE_PLACEHOLDER_TOPLEFT)
        reset_board_button = menu_buttons.ResetBoardButton(initvar.RESET_BOARD_BUTTON_TOPLEFT)
        clear_button = menu_buttons.ClearButton(initvar.CLEAR_BUTTON_TOPLEFT)
        scroll_up_button = menu_buttons.ScrollUpButton(initvar.SCROLL_UP_BUTTON_TOPLEFT)
        scroll_down_button = menu_buttons.ScrollDownButton(initvar.SCROLL_DOWN_BUTTON_TOPLEFT)
        beginning_move_button = menu_buttons.BeginningMoveButton(initvar.BEGINNING_MOVE_BUTTON_TOPLEFT)
        prev_move_button = menu_buttons.PrevMoveButton(initvar.PREV_MOVE_BUTTON_TOPLEFT)
        next_move_button = menu_buttons.NextMoveButton(initvar.NEXT_MOVE_BUTTON_TOPLEFT)
        last_move_button = menu_buttons.LastMoveButton(initvar.LAST_MOVE_BUTTON_TOPLEFT)
        undo_move_button = menu_buttons.UndoMoveButton(initvar.UNDO_MOVE_BUTTON_TOPLEFT)
        # Window
        gameicon = pygame.image.load("Sprites/chessico.png")
        pygame.display.set_icon(gameicon)
        pygame.display.set_caption('Chess')
        # Load the starting positions of chessboard first
        pos_load_file(reset=True)
        mouse_coord = ""
        def mouse_coordinate(mousepos):
            mouse_coord = ""
            for grid in board.Grid.grid_list:
                if grid.rect.collidepoint(mousepos):
                    mouse_coord = grid.coordinate
                    return mouse_coord
            return mouse_coord
        while True:
            clock.tick(60)
            mousepos = pygame.mouse.get_pos()
            mouse_coord = mouse_coordinate(mousepos)
            if state == running: # Initiate room
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    # If user wants to debug
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            debug_message = 1
                            state = debug
                    if save_file_placeholder.rect.collidepoint(mousepos):
                        save_file_placeholder.hover = True
                    else:
                        save_file_placeholder.hover = False
                    if load_file_placeholder.rect.collidepoint(mousepos):
                        load_file_placeholder.hover = True
                    else:
                        load_file_placeholder.hover = False
                    # Menu, inanimate buttons at top, and on right side of game board
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] \
                        and (mousepos[0] > board.X_GRID_END or mousepos[1] < initvar.Y_GRID_START \
                             or mousepos[0] < initvar.X_GRID_START or mousepos[1] > board.Y_GRID_END):
                        #%% Left click buttons
                        if scroll_up_button.rect.collidepoint(mousepos) and menu_buttons.PanelRectangles.scroll_range[0] > 1: # Scroll up
                            if scroll_up_button.activate:    
                                PanelController.update_scroll_range(-1)
                        if scroll_down_button.rect.collidepoint(mousepos) and len(menu_buttons.MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and menu_buttons.PanelRectangles.scroll_range[1] < len(menu_buttons.MoveNumberRectangle.rectangle_list): # Scroll down
                            if scroll_down_button.activate:  
                                PanelController.update_scroll_range(1)
                        if pgn_load_file_button.rect.collidepoint(mousepos) and pgn_load_file_button.clickable:
                            if CpuController.cpu_mode:
                                CpuController.cpu_mode_toggle()
                                cpu_button.toggle(CpuController.cpu_mode)
                            game_controller = PgnWriterAndLoader.pgn_load(play_edit_switch_button)
                            for grid in board.Grid.grid_list:
                                grid.no_highlight()
                            GridController.update_grid_occupied_detection()
                        if pgn_save_file_button.rect.collidepoint(mousepos) and pgn_save_file_button.clickable:
                            GameProperties.game_properties_popup()
                            PgnWriterAndLoader.write_moves(MoveTracker.df_moves, game_controller.result_abb)
                        if flip_board_button.rect.collidepoint(mousepos):
                            GridController.flip_grids()
                            if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                                game_controller.captured_pieces_flip(GridController.flipped)
                        if undo_move_button.rect.collidepoint(mousepos) and undo_move_button.clickable:
                            if CpuController.cpu_mode:
                                CpuController.cpu_mode_toggle()
                                cpu_button.toggle(CpuController.cpu_mode)
                            MoveController.undo_move(game_controller)
                        if cpu_button.rect.collidepoint(mousepos) and cpu_button.clickable:
                            CpuController.cpu_mode_toggle()
                            cpu_button.toggle(CpuController.cpu_mode)
                        if beginning_move_button.rect.collidepoint(mousepos) and beginning_move_button.clickable:
                            MoveTracker.selected_move = 1, "white_move"
                            SwitchModesController.replayed_game(True, game_controller, True)
                            GridController.update_prior_move_color()
                            MoveTracker.selected_move = (0, "black_move")
                            PanelController.scroll_to_first_move()
                        if prev_move_button.rect.collidepoint(mousepos) and prev_move_button.clickable:
                            if MoveTracker.selected_move == (0, "black_move"):
                                pass
                            elif MoveTracker.selected_move == (1, "white_move"):
                                SwitchModesController.replayed_game(True, game_controller, True)
                                GridController.update_prior_move_color()
                                MoveTracker.selected_move = (0, "black_move")
                            elif MoveTracker.selected_move[1] == "black_move":
                                MoveTracker.selected_move = MoveTracker.selected_move[0], "white_move"
                                SwitchModesController.replayed_game(True, game_controller)
                            else:
                                MoveTracker.selected_move = MoveTracker.selected_move[0]-1, "black_move"
                                if MoveTracker.selected_move[0] < menu_buttons.PanelRectangles.scroll_range[0] and menu_buttons.PanelRectangles.scroll_range[0] >= 1:
                                    PanelController.update_scroll_range(-1)
                                SwitchModesController.replayed_game(True, game_controller)
                        if next_move_button.rect.collidepoint(mousepos) and next_move_button.clickable:
                            if MoveTracker.selected_move[0] != MoveTracker.move_counter():
                                # When selected move is not at the last move number
                                if MoveTracker.selected_move[1] == "black_move":
                                    # When selected move is not at last move number and we are at black move
                                    MoveTracker.selected_move = MoveTracker.selected_move[0]+1, "white_move"
                                    if MoveTracker.selected_move[0] > menu_buttons.PanelRectangles.scroll_range[1] and menu_buttons.PanelRectangles.scroll_range[1] < MoveTracker.move_counter():
                                        PanelController.update_scroll_range(1)
                                    if MoveTracker.selected_move[0] == MoveTracker.move_counter() and \
                                    MoveTracker.df_moves.loc[MoveTracker.move_counter(), "black_move"] == "":
                                            # Went to last move number and there is no black move yet
                                        SwitchModesController.replayed_game(False, game_controller)
                                    else:
                                        SwitchModesController.replayed_game(True, game_controller)
                                elif MoveTracker.selected_move[1] == "white_move":
                                    # When selected move is not at last move number and we are at white move
                                    MoveTracker.selected_move = MoveTracker.selected_move[0], "black_move"
                                    SwitchModesController.replayed_game(True, game_controller)
                            elif MoveTracker.selected_move[0] == MoveTracker.move_counter() \
                            and MoveTracker.df_moves.loc[MoveTracker.move_counter(), "black_move"] != "" \
                            and MoveTracker.selected_move[1] == "white_move":
                                # We are at last move (and black has not moved yet)
                                MoveTracker.selected_move = MoveTracker.selected_move[0], "black_move"
                                SwitchModesController.replayed_game(False, game_controller)
                            else:
                                # Last move 
                                SwitchModesController.replayed_game(False, game_controller)
                        if last_move_button.rect.collidepoint(mousepos) and last_move_button.clickable:
                            if MoveTracker.df_moves.loc[MoveTracker.move_counter(), "black_move"] == "":
                                MoveTracker.selected_move = MoveTracker.move_counter(), "white_move"
                            else:
                                MoveTracker.selected_move = MoveTracker.move_counter(), "black_move"
                            PanelController.scroll_to_latest_move(MoveTracker.move_counter())
                            SwitchModesController.replayed_game(False, game_controller)
                        # When clicking on a move on the right pane, it is your selected move
                        for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
                            if piece_move_rect.rect.collidepoint(mousepos) and piece_move_rect.text_is_visible:
                                MoveTracker.selected_move = (piece_move_rect.move_number, piece_move_rect.move_color)
                                if MoveTracker.selected_move[0] == MoveTracker.move_counter():
                                    if MoveTracker.df_moves.loc[MoveTracker.move_counter(), "black_move"] != "" \
                                    and piece_move_rect.move_color == "white_move":
                                        SwitchModesController.replayed_game(True, game_controller)
                                    else:
                                        SwitchModesController.replayed_game(False, game_controller)
                                else:
                                    SwitchModesController.replayed_game(True, game_controller)
                        # Editing mode only
                        if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                            #BUTTONS
                            if pos_save_file_button.rect.collidepoint(mousepos) and pos_save_file_button.clickable:
                                pos_save_file()
                            if pos_load_file_button.rect.collidepoint(mousepos) and pos_load_file_button.clickable:
                                pos_load_file()
                            if reset_board_button.rect.collidepoint(mousepos) and reset_board_button.clickable:
                                pos_load_file(reset=True)
                            if game_properties_button.rect.collidepoint(mousepos) and game_properties_button.clickable:
                                GameProperties.game_properties_popup()
                            # DRAG OBJECTS
                            # Goes through each of the types of pieces
                            # If start object is clicked on, then enable drag, blank box changes images to the original piece so it looks better
                            for piece_name in start_objects.Start.start_dict:
                                if start_objects.Start.start_dict.get(piece_name).rect.collidepoint(mousepos):
                                    start_objects.Dragging.start_drag(piece_name)
                    #################
                    # LEFT CLICK (PRESSED DOWN)
                    #################

                    # Mouse click on the board
                    elif (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and
                          initvar.X_GRID_START < mousepos[0] < board.X_GRID_END and
                          initvar.Y_GRID_START < mousepos[1] < board.Y_GRID_END): 
                        # Drag piece to board (initialize placed piece)
                        start_objects.Dragging.dragging_to_placed_no_dups(mouse_coord)
                        if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                            # Moves piece
                            MoveController.complete_move(mouse_coord, game_controller)
                            # Selects piece
                            MoveController.select_piece_unselect_all_others(mouse_coord, game_controller)
                            if CpuController.cpu_mode and game_controller.whoseturn == CpuController.cpu_color:
                                CpuController.total_possible_moves_update()
                                if CpuController.total_possible_moves:
                                    cpu_move = CpuController.choose_move()
                                    cpu_grid = cpu_move[0]
                                    cpu_piece = cpu_move[1]
                                    cpu_piece.select = True
                                    MoveController.complete_move(cpu_grid.coordinate, game_controller)    
                    if event.type == pygame.MOUSEBUTTONDOWN and (event.button == 4 or event.button == 5):
                        #scroll wheel
                        if event.button == 4: # Scroll up
                            if menu_buttons.PanelRectangles.scroll_range[0] > 1:
                                if scroll_up_button.activate:
                                    PanelController.update_scroll_range(-1)
                        if event.button == 5: # Scroll down
                            if len(menu_buttons.MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and menu_buttons.PanelRectangles.scroll_range[1] < len(menu_buttons.MoveNumberRectangle.rectangle_list):
                                if scroll_down_button.activate:
                                    PanelController.update_scroll_range(1)
                    if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                        # Right click on obj, destroy
                        if(event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]):
                            EditModeController.right_click_destroy(mousepos)
                    if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                        #################
                        # PLAY BUTTON
                        #################
                        if play_edit_switch_button.rect.collidepoint(mousepos) and SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE: 
                            # Makes clicking play again unclickable    
                            SwitchModesController.switch_mode(SwitchModesController.PLAY_MODE, play_edit_switch_button)
                            game_controller = GameController(GridController.flipped)
                            game_controller.refresh_objects()

                        #################
                        # LEFT CLICK (RELEASE) STOP BUTTON
                        #################
                        elif play_edit_switch_button.rect.collidepoint(mousepos) and SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                            SwitchModesController.switch_mode(SwitchModesController.EDIT_MODE, play_edit_switch_button)
                            del game_controller
                        if clear_button.rect.collidepoint(mousepos):
                            if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE: #Editing mode
                                start_objects.Start.restart_start_positions()
                                # REMOVE ALL SPRITES
                                placed_objects.remove_all_placed()
                    
                    # MIDDLE MOUSE DEBUGGER
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                        pass
                ##################
                # ALL EDIT ACTIONS
                ##################
                # Start piece is dragging according to where the mouse is
                if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                    # Constant loop
                    start_objects.Dragging.update_drag_piece_and_all_start_pieces_positions(mousepos)
                ##################
                # IN-GAME ACTIONS
                ##################
                #FOR DEBUGGING PURPOSES, PUT TEST CODE BELOW
                
                # Set background
                lis.SCREEN.blit(lis.GAME_BACKGROUND, (0, 0))
                # Individual sprites update
                flip_board_button.draw(lis.SCREEN)
                save_file_placeholder.draw(lis.SCREEN)
                pos_save_file_button.draw(lis.SCREEN, SwitchModesController.GAME_MODE, save_file_placeholder.hover)
                pgn_save_file_button.draw(lis.SCREEN, SwitchModesController.GAME_MODE, save_file_placeholder.hover)
                load_file_placeholder.draw(lis.SCREEN)
                pos_load_file_button.draw(lis.SCREEN, SwitchModesController.GAME_MODE, load_file_placeholder.hover)
                pgn_load_file_button.draw(lis.SCREEN, SwitchModesController.GAME_MODE, load_file_placeholder.hover)
                cpu_button.draw(lis.SCREEN, SwitchModesController.GAME_MODE)
                # Group sprites update
                menu_buttons.GAME_MODE_SPRITES.draw(lis.SCREEN)
                board.GRID_SPRITES.draw(lis.SCREEN)
                GridController.update_grid_occupied_detection()
                start_objects.START_SPRITES.update(SwitchModesController.GAME_MODE)
                menu_buttons.PLAY_PANEL_SPRITES.update(SwitchModesController.GAME_MODE)
                lis.SCREEN.blit(lis.MOVE_BG_IMAGE, (initvar.MOVE_BG_IMAGE_X,initvar.MOVE_BG_IMAGE_Y))
                if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE: #Only draw placed sprites in editing mode
                    start_objects.START_SPRITES.draw(lis.SCREEN)
                    placed_objects.PLACED_SPRITES.update()
                    placed_objects.PLACED_SPRITES.draw(lis.SCREEN)
                elif SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE: #Only draw play sprites in play mode
                    flip_board_button.draw(lis.SCREEN)
                    if not SwitchModesController.REPLAYED:
                        play_objects.PLAY_SPRITES.update()
                        play_objects.PLAY_SPRITES.draw(lis.SCREEN)
                    else:
                        replayed_objects.REPLAYED_SPRITES.update()
                        replayed_objects.REPLAYED_SPRITES.draw(lis.SCREEN)
                    menu_buttons.PLAY_PANEL_SPRITES.draw(lis.SCREEN)
                    # When the piece is selected on the right pane, fill the rectangle corresponding to the move
                    for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
                        if piece_move_rect.move_number == MoveTracker.selected_move[0] and piece_move_rect.move_color == MoveTracker.selected_move[1]:
                            piece_move_rect.draw(lis.SCREEN)
                    PanelController.draw_move_rects_on_moves_pane(TextController.move_notation_font)
                    # Update objects that aren't in a sprite group
                    scroll_up_button.draw(lis.SCREEN)
                    scroll_down_button.draw(lis.SCREEN, len(MoveTracker.df_moves))
                render_text = lambda x: TextController.universal_font.render(x, 1, initvar.UNIVERSAL_TEXT_COLOR)
                # Board Coordinates Drawing
                for text in range(0,len(TextController.coor_letter_text_list)):
                    lis.SCREEN.blit(TextController.coor_letter_text_list[text], (initvar.X_GRID_START+board.X_GRID_WIDTH/3+(board.X_GRID_WIDTH*text), initvar.Y_GRID_START-(board.Y_GRID_HEIGHT*0.75)))
                    lis.SCREEN.blit(TextController.coor_letter_text_list[text], (initvar.X_GRID_START+board.X_GRID_WIDTH/3+(board.X_GRID_WIDTH*text), board.Y_GRID_END+(board.Y_GRID_HEIGHT*0.25)))
                for text in range(0,len(TextController.coor_number_text_list)):
                    lis.SCREEN.blit(TextController.coor_number_text_list[text], (initvar.X_GRID_START-board.X_GRID_WIDTH/2, initvar.Y_GRID_START+board.Y_GRID_HEIGHT/4+(board.Y_GRID_HEIGHT*text)))
                    lis.SCREEN.blit(TextController.coor_number_text_list[text], (board.X_GRID_END+board.X_GRID_WIDTH/3, initvar.Y_GRID_START+board.Y_GRID_HEIGHT/4+(board.Y_GRID_HEIGHT*text)))
                if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                    check_checkmate_text_render = TextController.universal_font.render(TextController.check_checkmate_text, 1, initvar.UNIVERSAL_TEXT_COLOR)
                    if GridController.flipped:
                        if game_controller.whoseturn == "white" and game_controller.result_abb == "*":
                            whose_turn_text = TextController.universal_font.render("White's move", 1, initvar.UNIVERSAL_TEXT_COLOR)
                            lis.SCREEN.blit(whose_turn_text, initvar.BLACK_MOVE_X_Y)
                        elif game_controller.whoseturn == "black" and game_controller.result_abb == "*":
                            whose_turn_text = TextController.universal_font.render("Black's move", 1, initvar.UNIVERSAL_TEXT_COLOR)
                            lis.SCREEN.blit(whose_turn_text, initvar.WHITE_MOVE_X_Y)
                    else:
                        if game_controller.whoseturn == "white" and game_controller.result_abb == "*":
                            whose_turn_text = TextController.universal_font.render("White's move", 1, initvar.UNIVERSAL_TEXT_COLOR)
                            lis.SCREEN.blit(whose_turn_text, initvar.WHITE_MOVE_X_Y)
                        elif game_controller.whoseturn == "black" and game_controller.result_abb == "*":
                            whose_turn_text = TextController.universal_font.render("Black's move", 1, initvar.UNIVERSAL_TEXT_COLOR)
                            lis.SCREEN.blit(whose_turn_text, initvar.BLACK_MOVE_X_Y)
                    lis.SCREEN.blit(check_checkmate_text_render, initvar.CHECK_CHECKMATE_X_Y)
                if GridController.flipped:
                    if GameProperties.WhiteElo != "":
                        lis.SCREEN.blit(render_text(GameProperties.White + " (" + GameProperties.WhiteElo + ")"), initvar.BLACK_X_Y)
                    else:
                        lis.SCREEN.blit(render_text(GameProperties.White), initvar.BLACK_X_Y)
                    if GameProperties.BlackElo != "":
                        lis.SCREEN.blit(render_text(GameProperties.Black + " (" + GameProperties.BlackElo + ")"), initvar.WHITE_X_Y)
                    else:
                        lis.SCREEN.blit(render_text(GameProperties.Black), initvar.WHITE_X_Y)
                else:
                    if GameProperties.WhiteElo != "":
                        lis.SCREEN.blit(render_text(GameProperties.White + " (" + GameProperties.WhiteElo + ")"), initvar.WHITE_X_Y)
                    else:
                        lis.SCREEN.blit(render_text(GameProperties.White), initvar.WHITE_X_Y)
                    if GameProperties.BlackElo != "":
                        lis.SCREEN.blit(render_text(GameProperties.Black + " (" + GameProperties.BlackElo + ")"), initvar.BLACK_X_Y)
                    else:
                        lis.SCREEN.blit(render_text(GameProperties.Black), initvar.BLACK_X_Y)
                pygame.display.update()
            elif state == debug:
                if debug_message == 1:
                    log.info("Entering debug mode")
                    debug_message = 0
                    log.info("Use breakpoint here")
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            state = running
                            log.info("back to Running")
    except SystemExit:
        pass
    except:
        log.exception("Error out of main")
if __name__ == "__main__":
    main()
