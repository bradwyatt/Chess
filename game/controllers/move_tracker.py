import play_objects


class MoveTracker():
    df_moves = {}  # {move_num: {"white_move": "", "black_move": ""}}
    df_prior_moves = {}
    move_counter = lambda : len(MoveTracker.df_moves)
    selected_move = (0, "")

    @classmethod
    def restart(cls):
        cls.df_moves = {}
        cls.df_prior_moves = {}
        cls.selected_move = (0, "")

    @classmethod
    def undo_move_in_dfs(cls, undo_color):
        if undo_color == "black":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if MoveTracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[cls.move_counter()]
            cls.df_moves[cls.move_counter()]["black_move"] = ''
            cls.df_prior_moves[cls.move_counter()]["black_move"] = ''
            if cls.df_moves[cls.move_counter()]["white_move"] == '':
                del cls.df_moves[max(cls.df_moves)]
                del cls.df_prior_moves[max(cls.df_prior_moves)]
                cls.selected_move = (0, "black_move")
            else:
                cls.selected_move = (cls.move_counter(), "white_move")
        elif undo_color == "white":
            for black_piece_list in play_objects.Piece_Lists_Shortcut.black_pieces():
                for black_piece in black_piece_list:
                    if MoveTracker.move_counter() in black_piece.coordinate_history:
                        del black_piece.coordinate_history[cls.move_counter()]
            cls.selected_move = (cls.move_counter()-1, "black_move")
            del cls.df_moves[max(cls.df_moves)]
            del cls.df_prior_moves[max(cls.df_prior_moves)]
