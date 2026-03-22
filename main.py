# pylint: disable=E1101
"""
Chess created by Brad Wyatt
"""
import random
import sys
import os
import copy
import datetime
import asyncio
import logging
import logging.handlers
import ast
import json
import pygame
import initvar

if sys.platform != "emscripten":
    import tkinter as tk
    from tkinter.filedialog import asksaveasfilename, askopenfilename
else:
    tk = None
    asksaveasfilename = None
    askopenfilename = None

import load_images_sounds as lis
import menu_buttons
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
    os.makedirs(initvar.log_path, exist_ok=True)
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
# Submodule imports (re-exported for backward compatibility)
#############

from game.controllers.move_tracker import MoveTracker
from game.controllers.text_controller import TextController
from game.controllers.cpu_controller import CpuController
from game.controllers.panel_controller import PanelController
from game.controllers.switch_modes import SwitchModesController, GridController
from game.controllers.game_controller import EditModeController, GameController, MoveController
from game.io.positions import (
    native_file_dialogs_available, itch_mode_blocked,
    pos_load_file, get_dict_rect_positions, pos_save_file, pos_lists_to_coord,
    GameProperties,
)
from game.io.pgn import PgnWriterAndLoader

async def main():
    import asyncio
    import logging
    import load_images_sounds as lis
    pygame = lis.pygame
    log = logging.getLogger("log_guy")
    try:
        running, debug = 0, 1
        state = running
        debug_message = 0
        app_running = True

        clock = pygame.time.Clock()

        play_edit_switch_button = menu_buttons.PlayEditSwitchButton(initvar.PLAY_EDIT_SWITCH_BUTTON_TOPLEFT)
        flip_board_button = menu_buttons.FlipBoardButton(initvar.FLIP_BOARD_BUTTON_TOPLEFT)
        cpu_button = menu_buttons.CPUButton(initvar.CPU_BUTTON_TOPLEFT, CpuController.cpu_mode)
        game_properties_button = None
        pos_load_file_button = None
        pos_save_file_button = None
        pgn_load_file_button = None
        pgn_save_file_button = None
        load_file_placeholder = None
        save_file_placeholder = None
        if not initvar.ITCH_MODE:
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
        gameicon = pygame.image.load("sprites/chessico.png")
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
        while app_running:
            clock.tick(60)
            mousepos = pygame.mouse.get_pos()
            mouse_coord = mouse_coordinate(mousepos)
            if state == running: # Initiate room
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        app_running = False
                        break
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            app_running = False
                            break
                    # If user wants to debug
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            debug_message = 1
                            state = debug
                    if not initvar.ITCH_MODE:
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
                        if pgn_load_file_button and pgn_load_file_button.rect.collidepoint(mousepos) and pgn_load_file_button.clickable:
                            if CpuController.cpu_mode:
                                CpuController.cpu_mode_toggle()
                                cpu_button.toggle(CpuController.cpu_mode)
                            game_controller = PgnWriterAndLoader.pgn_load(play_edit_switch_button)
                            for grid in board.Grid.grid_list:
                                grid.no_highlight()
                            GridController.update_grid_occupied_detection()
                        if pgn_save_file_button and pgn_save_file_button.rect.collidepoint(mousepos) and pgn_save_file_button.clickable:
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
                                    MoveTracker.df_moves[MoveTracker.move_counter()]["black_move"] == "":
                                            # Went to last move number and there is no black move yet
                                        SwitchModesController.replayed_game(False, game_controller)
                                    else:
                                        SwitchModesController.replayed_game(True, game_controller)
                                elif MoveTracker.selected_move[1] == "white_move":
                                    # When selected move is not at last move number and we are at white move
                                    MoveTracker.selected_move = MoveTracker.selected_move[0], "black_move"
                                    SwitchModesController.replayed_game(True, game_controller)
                            elif MoveTracker.selected_move[0] == MoveTracker.move_counter() \
                            and MoveTracker.df_moves[MoveTracker.move_counter()]["black_move"] != "" \
                            and MoveTracker.selected_move[1] == "white_move":
                                # We are at last move (and black has not moved yet)
                                MoveTracker.selected_move = MoveTracker.selected_move[0], "black_move"
                                SwitchModesController.replayed_game(False, game_controller)
                            else:
                                # Last move
                                SwitchModesController.replayed_game(False, game_controller)
                        if last_move_button.rect.collidepoint(mousepos) and last_move_button.clickable:
                            if MoveTracker.df_moves[MoveTracker.move_counter()]["black_move"] == "":
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
                                    if MoveTracker.df_moves[MoveTracker.move_counter()]["black_move"] != "" \
                                    and piece_move_rect.move_color == "white_move":
                                        SwitchModesController.replayed_game(True, game_controller)
                                    else:
                                        SwitchModesController.replayed_game(False, game_controller)
                                else:
                                    SwitchModesController.replayed_game(True, game_controller)
                        # Editing mode only
                        if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                            #BUTTONS
                            if pos_save_file_button and pos_save_file_button.rect.collidepoint(mousepos) and pos_save_file_button.clickable:
                                pos_save_file()
                            if pos_load_file_button and pos_load_file_button.rect.collidepoint(mousepos) and pos_load_file_button.clickable:
                                pos_load_file()
                            if reset_board_button.rect.collidepoint(mousepos) and reset_board_button.clickable:
                                pos_load_file(reset=True)
                            if game_properties_button and game_properties_button.rect.collidepoint(mousepos) and game_properties_button.clickable:
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

                    #%% Middle Mouse Debugger
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[1]:
                        print(board.Grid.grid_dict[mouse_coord].coords_of_protecting_pieces)
                if not app_running:
                    continue
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
                #%% Test code below for debugging purposes

                # Set background
                lis.SCREEN.blit(lis.GAME_BACKGROUND, (0, 0))
                # Individual sprites update
                flip_board_button.draw(lis.SCREEN)
                if not initvar.ITCH_MODE:
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
                        app_running = False
                        break
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            state = running
                            log.info("back to Running")
                if not app_running:
                    continue
            await asyncio.sleep(0)
    except:
        log.exception("Error out of main")
    finally:
        pygame.quit()
        lis.destroy_root()

if __name__ == "__main__":
    asyncio.run(main())
