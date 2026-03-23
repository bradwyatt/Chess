import random

import board
import initvar
import play_objects

from game.io.positions import pos_lists_to_coord


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
        color_score = {"white": 0, "black": 0}
        for piece_list in play_objects.Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if not piece.taken_off_board:
                    pos_dict = getattr(cls, f"{piece.color}_{piece.piece_type}_pos_score_dict")
                    coord = grid.coordinate if piece_to_move == piece else piece.coordinate
                    color_score[piece.color] += pos_dict[coord] + initvar.piece_values_dict[piece.piece_type]
        return color_score[piece_color]

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
        gridcoord_piece_score_list = []
        random.shuffle(cls.total_possible_moves)
        for possible_move in cls.total_possible_moves:
            grid = possible_move[0]
            piece_to_move = possible_move[1]
            move_score = cls.analyze_board(grid, piece_to_move, cls.cpu_color)
            if grid.occupied and not grid.coords_of_attacking_pieces[cls.enemy_color]:
                # Enemy piece is free to take without protection
                move_score += play_objects.Piece_Lists_Shortcut.piece_on_coord(grid.coordinate).score
            elif grid.occupied and grid.coords_of_attacking_pieces[cls.enemy_color]:
                # Trade only when enemy piece is higher value
                move_score += play_objects.Piece_Lists_Shortcut.piece_on_coord(grid.coordinate).score - piece_to_move.score
            elif not grid.occupied and grid.coords_of_attacking_pieces[cls.enemy_color] \
                and not grid.coords_of_protecting_pieces[cls.cpu_color]:
                # Moving to a square (not occupied) being attacked by enemy and 0 protection
                move_score -= piece_to_move.score
            elif not grid.occupied and grid.coords_of_attacking_pieces[cls.enemy_color] \
                and grid.coords_of_protecting_pieces[cls.cpu_color]:
                # Moving to a square (not occupied) being attacked by enemy but you have some protection
                # For each attacking piece, calculate what the score would be if enemy takes cpu piece
                # Enemy king can't attack because at least one of CPU's pieces are protecting it
                trade_score_list = []
                for attacking_grid in grid.coords_of_attacking_pieces[cls.enemy_color]:
                    attacker_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(attacking_grid)
                    if isinstance(attacker_piece, play_objects.PlayKing):
                        trade_score_list.append(0)
                    else:
                        trade_score_list.append(attacker_piece.score-piece_to_move.score)
                if min(trade_score_list) < 0:
                    # If there is one piece that has less value than piece_to_move, then move_score should decrease by that
                    move_score += min(trade_score_list)
                else:
                    pass
            if board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces[cls.enemy_color] \
                and board.Grid.grid_dict[piece_to_move.coordinate].coords_of_protecting_pieces[cls.cpu_color] \
                    and not isinstance(piece_to_move, play_objects.PlayKing):
                    # Current piece being attacked and is being protected
                    # Not including King from piece_to_move since it can't trade
                trade_score_list = []
                for attacking_grid in board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces[cls.enemy_color]:
                    attacker_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(attacking_grid)
                    if not isinstance(attacker_piece, play_objects.PlayKing):
                        if attacker_piece.score <= piece_to_move.score:
                            # If attacker piece is less valuable than piece to move, then append to trade_score_list
                            trade_score_list.append(piece_to_move.score-attacker_piece.score)
                        else:
                            trade_score_list.append(0)
                    else:
                        trade_score_list.append(0)
                move_score += max(trade_score_list)
            elif board.Grid.grid_dict[piece_to_move.coordinate].coords_of_attacking_pieces[cls.enemy_color] \
                and not board.Grid.grid_dict[piece_to_move.coordinate].coords_of_protecting_pieces[cls.cpu_color] \
                    and not isinstance(piece_to_move, play_objects.PlayKing):
                    # Current piece being attacked and is not protected
                    # Not including King from piece_to_move since it can't trade
                move_score += piece_to_move.score
            move_score_list.append(move_score)
            # gridcoord_piece_score_list for debugging purposes only
            # Gives the piece, the move, the score
            gridcoord_piece_score_list.append((possible_move[0].coordinate, possible_move[1], move_score))
        #print("Total Possible Moves: \n" + str(gridcoord_piece_score_list) + "\n")
        max_move = max(move_score_list)
        index_of_max_moves = move_score_list.index(max_move)
        return cls.total_possible_moves[index_of_max_moves]
