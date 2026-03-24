import copy
import logging
import os
import sys
from pathlib import Path

import board
import initvar
import play_objects
import pygame

from game.controllers.game_controller import GameController, MoveController
from game.controllers.move_tracker import MoveTracker
from game.controllers.panel_controller import PanelController
from game.controllers.switch_modes import GridController, SwitchModesController
from game.io.positions import GameProperties, itch_mode_blocked, native_file_dialogs_available, pos_load_file

if sys.platform != "emscripten":
    from tkinter.filedialog import asksaveasfilename, askopenfilename
else:
    asksaveasfilename = None
    askopenfilename = None

log = logging.getLogger("log_guy")


class PgnWriterAndLoader():

    @staticmethod
    def write_moves(df_moves, result_abb):
        if not native_file_dialogs_available():
            itch_mode_blocked("Saving PGN")
            return
        try:
            df = copy.deepcopy(df_moves)
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
                for i in sorted(df.keys()):
                    # If black hasn't moved then shorten the pgn output so it doesn't give two spaces
                    if str(df[i]['black_move']) == "":
                        pgn_output += str(i) + ". " + str(df[i]['white_move']) + " "
                    else:
                        pgn_output += str(i) + ". " + str(df[i]['white_move']) + " " + str(df[i]['black_move']) + " "
                pgn_output += result_abb
                save_file_name.write(pgn_output)
                save_file_name.close()
                log.info("File Saved Successfully.")
            else:
                log.info("Error! Need king to save!")
        except IOError:
            log.info("Save File Error (IOError)")

    @staticmethod
    def _load_from_pgn_text(play_edit_switch_button, loaded_file):
        pos_load_file(reset=True)
        SwitchModesController.switch_mode(SwitchModesController.PLAY_MODE, play_edit_switch_button)
        game_controller = GameController(GridController.flipped)
        game_controller.refresh_objects()

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
                    chess_game.append(row + " ")
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
        # Also if the PGN has no space after the move number, then include a space for easier parsing
        chess_game = "".join(chess_game).split("  ")
        if chess_game[0][2] != " ":
            chess_game[0] = chess_game[0].replace(".", ". ")
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
            if ("." in row) or ("*" in row):
                pass
            else:
                move = row
                if ("0-1" in row) or ("1-0" in row) or ("1/2-1/2" in row):
                    MoveController.game_status_check(game_controller, imported_game_status=row)
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

        if MoveTracker.move_counter() >= 1:
            MoveTracker.selected_move = (1, "white_move")
            SwitchModesController.replayed_game(True, game_controller, True)
            GridController.update_prior_move_color()
            MoveTracker.selected_move = (0, "black_move")
            PanelController.scroll_to_first_move()

        log.info("PGN Finished Loading")
        return game_controller

    @staticmethod
    def pgn_load(play_edit_switch_button):
        if not native_file_dialogs_available():
            itch_mode_blocked("Loading PGN")
            return None
        request_file_name = askopenfilename(defaultextension=".pgn")
        log.info("Loading " + os.path.basename(request_file_name))
        try:
            with open(request_file_name, "r", encoding="utf-8") as open_file:
                return PgnWriterAndLoader._load_from_pgn_text(play_edit_switch_button, open_file.read())
        except FileNotFoundError:
            log.info("File not found")
            return None

    @staticmethod
    def pgn_load_from_path(play_edit_switch_button, pgn_path):
        resolved_path = Path(pgn_path)
        if not resolved_path.is_absolute():
            resolved_path = (initvar.BASE_DIR / resolved_path).resolve()
        log.info("Loading " + resolved_path.name)
        try:
            with open(resolved_path, "r", encoding="utf-8") as open_file:
                return PgnWriterAndLoader._load_from_pgn_text(play_edit_switch_button, open_file.read())
        except FileNotFoundError:
            log.info("File not found")
            return None
