import ast
import logging

import board
import initvar
import placed_objects
import play_objects
import replayed_objects

from game.controllers.move_tracker import MoveTracker
from game.controllers.text_controller import TextController

log = logging.getLogger("log_guy")


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
            for color in ("white", "black"):
                for piece_type, placed_cls in placed_objects.PLACED_PIECE_CLASS.items():
                    placed_list = getattr(placed_cls, f"{color}_{piece_type}_list")
                    cls.placed_to_play(placed_list, play_objects.PLAY_PIECE_CLASS[piece_type], color)
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
                                                if piece.coordinate == ast.literal_eval(MoveTracker.df_prior_moves[piece_history]["white_move"])['after']:
                                                    piece.kill()
                                                    replayed_objects.ReplayedQueen.white_queen_list.remove(piece)
                                    elif replayed_obj.color == "black":
                                        for piece_list in replayed_objects.Piece_Lists_Shortcut.black_pieces():
                                            for piece in replayed_objects.ReplayedQueen.black_queen_list:
                                                if piece.coordinate == ast.literal_eval(MoveTracker.df_prior_moves[piece_history]["black_move"])['after']:
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
            for color in ("white", "black"):
                for piece_type, play_cls in play_objects.PLAY_PIECE_CLASS.items():
                    play_list = getattr(play_cls, f"{color}_{piece_type}_list")
                    cls.play_to_replayed(play_list, replayed_objects.REPLAYED_PIECE_CLASS[piece_type], color)
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
                moves_backwards_dict[move_num] = df_prior_moves[move_num]['black_move']
                moves_backwards_list.append(moves_backwards_dict)
                break
            if df_prior_moves[move_num]['black_move'] == '':
                # Current move has no black move yet, so ignore adding that to list
                pass
            else:
                moves_backwards_dict[move_num] = df_prior_moves[move_num]['black_move']
                moves_backwards_list.append(moves_backwards_dict)
                moves_backwards_dict = {}
            moves_backwards_dict[move_num] = df_prior_moves[move_num]['white_move']
            moves_backwards_list.append(moves_backwards_dict)
        # When select a move on pane, we take back the move right after that
        return moves_backwards_list
