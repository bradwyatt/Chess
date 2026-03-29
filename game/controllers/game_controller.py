import ast
import logging

import board
import initvar
import menu_buttons
import play_objects
import placed_objects
import start_objects

from game.controllers.move_tracker import MoveTracker
from game.controllers.panel_controller import PanelController
from game.controllers.switch_modes import GridController, SwitchModesController
from game.controllers.text_controller import TextController
from game.io.positions import GameProperties

log = logging.getLogger("log_guy")


class EditModeController():
    @staticmethod
    def right_click_destroy(mousepos):
        if start_objects.Dragging.drag_piece_name:
            start_objects.Dragging.dragging_all_false()
            start_objects.Start.restart_start_positions()
            return
        start_objects.Dragging.dragging_all_false()
        start_objects.Start.restart_start_positions()
        placed_objects.remove_placed_object(mousepos)


class GameController():
    """
    How pieces are effected after a move has been formally made
    For example, after a white bishop finished its move, then the grids
    that are in the line of sight from the bishop have its respective variables
    """
    def __init__(self, flipped, whoseturn="white", variant_key=None):
        self.whoseturn = whoseturn
        self.variant_key = variant_key
        self.castling_enabled = variant_key != "chaos_setup"
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
        # Reuse the normal turn-refresh path so custom editor positions also
        # recalculate checks, pins, and castle legality for the side to move.
        self.switch_turn(self.whoseturn, undo=True)
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
                piece_coordinate_move_notation = ast.literal_eval(MoveTracker.df_prior_moves[MoveTracker.move_counter()]["black_move"])['move_notation']
                for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                    for black_piece in black_piece_list:
                        for piece_history in black_piece.coordinate_history.keys():
                            if MoveTracker.move_counter() == piece_history:
                                pieces_to_undo.append(black_piece)
            elif game_controller.whoseturn == "black":
                piece_coordinate_move_notation = ast.literal_eval(MoveTracker.df_prior_moves[MoveTracker.move_counter()]["white_move"])['move_notation']
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
                        if q.coordinate == ast.literal_eval(MoveTracker.df_prior_moves[MoveTracker.move_counter()]["black_move"])['after']:
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
                        if q.coordinate == ast.literal_eval(MoveTracker.df_prior_moves[MoveTracker.move_counter()]["white_move"])['after']:
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
        # Seed the first move row before any history/capture bookkeeping runs.
        # This also supports custom positions that intentionally start with Black to move.
        if piece.color == "white" or MoveTracker.move_counter() == 0:
            next_move = MoveTracker.move_counter()+1
            MoveTracker.df_moves[next_move] = {"white_move": "", "black_move": ""}
            MoveTracker.df_prior_moves[next_move] = {"white_move": "", "black_move": ""}
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
                    if rook.coordinate == 'a1' and piece.previous_coordinate == 'e1' and piece.coordinate == 'c1':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d1'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d1'].coordinate
                        board.Grid.grid_dict['d1'].occupied = True
                        rook.allowed_to_castle = False
                        special_abb = "O-O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'a1'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'd1'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h1' and piece.previous_coordinate == 'e1' and piece.coordinate == 'g1':
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
                    if rook.coordinate == 'a8' and piece.previous_coordinate == 'e8' and piece.coordinate == 'c8':
                        rook.coordinate_history[MoveTracker.move_counter()] = {}
                        rook.rect.topleft = board.Grid.grid_dict['d8'].rect.topleft
                        rook.coordinate = board.Grid.grid_dict['d8'].coordinate
                        board.Grid.grid_dict['d8'].occupied = True
                        special_abb = "O-O-O"
                        rook.coordinate_history[MoveTracker.move_counter()]['before'] = 'a8'
                        rook.coordinate_history[MoveTracker.move_counter()]['after'] = 'd8'
                        rook.coordinate_history[MoveTracker.move_counter()]['move_notation'] = 'O-O-O'
                    elif rook.coordinate == 'h8' and piece.previous_coordinate == 'e8' and piece.coordinate == 'g8':
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
    def game_status_check(game_controller, imported_game_status=False):
        if imported_game_status==False:
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
                TextController.check_checkmate_text = "Black is in check"
                check_abb, game_controller.result_abb = checkmate_check('black')
            elif game_controller.color_in_check == "white":
                TextController.check_checkmate_text = "White is in check"
                check_abb, game_controller.result_abb = checkmate_check('white')
            elif game_controller.color_in_check == "" and game_controller.whoseturn == "white":
                game_controller.result_abb = stalemate_check('white')
            elif game_controller.color_in_check == "" and game_controller.whoseturn == "black":
                game_controller.result_abb = stalemate_check('black')
            else:
                # No checks
                TextController.check_checkmate_text = ""
        elif imported_game_status=="1-0":
            TextController.check_checkmate_text = "White wins"
            check_abb, game_controller.result_abb = "#", "1-0"
        elif imported_game_status=="0-1":
            TextController.check_checkmate_text = "Black wins"
            check_abb, game_controller.result_abb = "#", "0-1"
        elif imported_game_status=="1/2-1/2":
            TextController.check_checkmate_text = "Draw"
            check_abb, game_controller.result_abb = "", "1/2-1/2"
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
            MoveTracker.df_moves[MoveTracker.move_counter()]["black_move"] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[MoveTracker.move_counter()]['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            MoveTracker.selected_move = (MoveTracker.move_counter(), "black_move")
            MoveTracker.df_prior_moves[MoveTracker.move_counter()]["black_move"] = str(prior_moves_dict)
        elif game_controller.whoseturn == "black":
            # Create new record to make room for new white move
            # move_counter will update to new length of dataframe
            if special_abb == "=Q":
                piece_in_funcs = promoted_queen
            else:
                piece_in_funcs = piece
            move_text = str(MoveTracker.move_counter()) + ". " + \
                  cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb) + " "
            MoveTracker.df_moves[MoveTracker.move_counter()]["white_move"] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            piece.coordinate_history[MoveTracker.move_counter()]['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            prior_moves_dict['move_notation'] = cls.move_translator(grid.occupied_piece, piece_in_funcs, captured_abb, special_abb, check_abb)
            MoveTracker.selected_move = (MoveTracker.move_counter(), "white_move")
            MoveTracker.df_prior_moves[MoveTracker.move_counter()]["white_move"] = str(prior_moves_dict)
        SwitchModesController.replayed_game(False, game_controller)
        log.info(move_text)
        if game_controller.result_abb != "*":
            log.info(game_controller.result_abb)
