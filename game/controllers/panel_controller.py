import initvar
import load_images_sounds as lis
import menu_buttons

from game.controllers.move_tracker import MoveTracker


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
        for move_number, moves in MoveTracker.df_moves.items():
            if moves["white_move"] == "" and moves["black_move"] != "":
                move_number_rect = menu_buttons.MoveNumberRectangle.rectangle_dict.get(move_number)
                if move_number_rect and move_number_rect.text_is_visible:
                    placeholder_text = my_font.render("\u2014", True, initvar.MOVE_TEXT_COLOR_ON_PANE)
                    surface.blit(
                        placeholder_text,
                        (initvar.MOVES_PANE_WHITE_X + initvar.MOVE_PILL_TEXT_PADDING_X, move_number_rect.y),
                    )
        for piece_move_rect in menu_buttons.PieceMoveRectangle.rectangle_list:
            if piece_move_rect.text_is_visible:
                move_notation_text = my_font.render(piece_move_rect.move_notation, True, initvar.MOVE_TEXT_COLOR_ON_PANE)
                surface.blit(move_notation_text, (piece_move_rect.x + initvar.MOVE_PILL_TEXT_PADDING_X, piece_move_rect.y))

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
            latest_move_number = len(MoveTracker.df_moves)
            latest_move = MoveTracker.df_moves[latest_move_number]
            # Creating move notation rectangles if they haven't been created before for the respective move
            # If the last move is not in the dictionary, then add it
            if latest_move_number not in menu_buttons.PieceMoveRectangle.rectangle_dict:
                menu_buttons.PieceMoveRectangle.rectangle_dict[latest_move_number] = {}
            if latest_move_number not in menu_buttons.MoveNumberRectangle.rectangle_dict:
                menu_buttons.MoveNumberRectangle.rectangle_dict[latest_move_number] = None
            if ((latest_move['white_move'] != '' or latest_move['black_move'] != '')
                    and menu_buttons.MoveNumberRectangle.rectangle_dict[latest_move_number] is None):
                menu_buttons.MoveNumberRectangle(
                    latest_move_number,
                    initvar.MOVES_PANE_MOVE_NUMBER_X,
                    initvar.MOVES_PANE_Y_BEGIN + initvar.LINE_SPACING * latest_move_number,
                    initvar.RECTANGLE_WIDTH,
                    initvar.RECTANGLE_HEIGHT,
                )
            # We want the menu_buttons.PieceMoveRectangle.rectangle_dict to correspond to the df_moves dataframe
            if latest_move['white_move'] != '' and 'white_move' not in menu_buttons.PieceMoveRectangle.rectangle_dict[latest_move_number]:
                # Create rectangle which will eventually be used to blit text on it
                # Parameters: Total number of moves in the game, the move itself, the color of the piece that moved, and position & size of rectangle
                menu_buttons.PieceMoveRectangle(latest_move_number, latest_move['white_move'], 'white_move', initvar.MOVES_PANE_WHITE_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*latest_move_number, initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                # Scroll down automatically when a move is made
                cls.scroll_to_latest_move(latest_move_number)
            if latest_move['black_move'] != '' and 'black_move' not in menu_buttons.PieceMoveRectangle.rectangle_dict[latest_move_number]:
                # Only create menu_buttons.PieceMoveRectangle when black moved last, don't create a new menu_buttons.MoveNumberRectangle
                menu_buttons.PieceMoveRectangle(latest_move_number, latest_move['black_move'], 'black_move', initvar.MOVES_PANE_BLACK_X, initvar.MOVES_PANE_Y_BEGIN+initvar.LINE_SPACING*latest_move_number, initvar.RECTANGLE_WIDTH, initvar.RECTANGLE_HEIGHT)
                cls.scroll_to_latest_move(latest_move_number)
            cls.draw_text_on_rects_in_moves_pane(lis.SCREEN, my_font)

    @staticmethod
    def remove_latest_move(color_move):
        menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move].move_notation = ""
        menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move].kill()
        del menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()][color_move]
        if color_move == "white_move" or not menu_buttons.PieceMoveRectangle.rectangle_dict[MoveTracker.move_counter()]:
            menu_number_rect = menu_buttons.MoveNumberRectangle.rectangle_dict[MoveTracker.move_counter()]
            if menu_number_rect is not None:
                menu_number_rect.text = ""
                menu_number_rect.kill()
                if menu_number_rect in menu_buttons.MoveNumberRectangle.rectangle_list:
                    menu_buttons.MoveNumberRectangle.rectangle_list.remove(menu_number_rect)
            menu_buttons.MoveNumberRectangle.rectangle_dict[MoveTracker.move_counter()] = None
