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
import pygame.freetype
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
    pos_load_file, load_position_from_json, get_dict_rect_positions, pos_save_file, pos_lists_to_coord,
    GameProperties, POSITION_METADATA_DEFAULTS, load_position_from_dict,
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
        pending_cpu_move_at = None

        def cancel_pending_cpu_move():
            nonlocal pending_cpu_move_at
            pending_cpu_move_at = None

        def schedule_cpu_move():
            nonlocal pending_cpu_move_at
            pending_cpu_move_at = pygame.time.get_ticks() + initvar.CPU_MOVE_DELAY_MS

        def _sync_cpu_turn_after_mode_change():
            if SwitchModesController.GAME_MODE != SwitchModesController.PLAY_MODE:
                cancel_pending_cpu_move()
                return
            if not CpuController.cpu_mode or game_controller.result_abb != "*":
                cancel_pending_cpu_move()
                return
            if game_controller.whoseturn == CpuController.cpu_color:
                schedule_cpu_move()
            else:
                cancel_pending_cpu_move()

        def start_game(whoseturn=None):
            nonlocal game_controller
            cancel_pending_cpu_move()
            start_objects.Dragging.dragging_all_false()
            SwitchModesController.switch_mode(SwitchModesController.PLAY_MODE, play_edit_switch_button)
            if whoseturn is None:
                whoseturn = pending_start_whoseturn
            game_controller = GameController(
                GridController.flipped,
                whoseturn=whoseturn,
                variant_key=active_game_mode_key,
            )
            game_controller.refresh_objects()
            if CpuController.cpu_mode and game_controller.whoseturn == CpuController.cpu_color:
                schedule_cpu_move()

        def _normalize_game_mode_label(game_mode):
            normalized = str(game_mode).strip().lower().replace("-", " ").replace("_", " ")
            if normalized == "play as white vs cpu":
                return "Play as White vs CPU"
            if normalized == "play as black vs cpu":
                return "Play as Black vs CPU"
            return "Human vs Human"

        def _normalize_board_orientation_label(board_orientation):
            normalized = str(board_orientation).strip().lower().replace("-", " ").replace("_", " ")
            if normalized == "black on bottom":
                return "Black on Bottom"
            return "White on Bottom"

        def _normalize_starting_turn(whoseturn):
            return "black" if str(whoseturn).strip().lower() == "black" else "white"

        def _current_position_config():
            if not CpuController.cpu_mode:
                game_mode = "Human vs Human"
            elif CpuController.cpu_color == "black":
                game_mode = "Play as White vs CPU"
            else:
                game_mode = "Play as Black vs CPU"
            return {
                "game_mode": game_mode,
                "board_orientation": "Black on Bottom" if GridController.flipped else "White on Bottom",
                "starting_turn": pending_start_whoseturn,
            }

        def _apply_position_config(config, fallback_whoseturn="white"):
            nonlocal pending_start_whoseturn
            merged_config = POSITION_METADATA_DEFAULTS.copy()
            if config:
                merged_config.update(config)

            game_mode = _normalize_game_mode_label(merged_config["game_mode"])
            if game_mode == "Play as White vs CPU":
                CpuController.cpu_mode = True
                CpuController.cpu_color = "black"
                CpuController.enemy_color = "white"
            elif game_mode == "Play as Black vs CPU":
                CpuController.cpu_mode = True
                CpuController.cpu_color = "white"
                CpuController.enemy_color = "black"
            else:
                CpuController.cpu_mode = False
                CpuController.cpu_color = "black"
                CpuController.enemy_color = "white"

            board_orientation = _normalize_board_orientation_label(merged_config["board_orientation"])
            should_be_flipped = (board_orientation == "Black on Bottom")
            if GridController.flipped != should_be_flipped:
                GridController.flip_grids()

            starting_turn = fallback_whoseturn
            if config and "starting_turn" in config:
                starting_turn = config["starting_turn"]
            elif fallback_whoseturn is None:
                starting_turn = merged_config["starting_turn"]
            pending_start_whoseturn = _normalize_starting_turn(starting_turn)

        def reset_to_default_setup():
            nonlocal pending_start_whoseturn, active_game_mode_key
            if GridController.flipped:
                GridController.flip_grids()
            CpuController.cpu_mode = False
            CpuController.cpu_color = "black"
            CpuController.enemy_color = "white"
            GameProperties.Event = ""
            GameProperties.Site = ""
            GameProperties.Date = ""
            GameProperties.Round = ""
            GameProperties.White = ""
            GameProperties.Black = ""
            GameProperties.Result = ""
            GameProperties.WhiteElo = ""
            GameProperties.BlackElo = ""
            GameProperties.ECO = ""
            GameProperties.TimeControl = "0"
            start_objects.Start.restart_start_positions()
            pos_load_file(reset=True)
            pending_start_whoseturn = "white"
            TextController.remove_check_checkmate_text()
            active_game_mode_key = None

        def _build_current_orientation_config(starting_turn="white"):
            return {
                "game_mode": "Human vs Human",
                "board_orientation": "Black on Bottom" if GridController.flipped else "White on Bottom",
                "starting_turn": _normalize_starting_turn(starting_turn),
            }

        def _reset_board_for_game_mode_load():
            cancel_pending_cpu_move()
            start_objects.Dragging.dragging_all_false()
            start_objects.Start.restart_start_positions()
            TextController.remove_check_checkmate_text()
            GameProperties.Result = ""
            if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                stop_game()

        def _clear_active_game_mode_if_edit_board_changed(previous_snapshot):
            nonlocal active_game_mode_key
            if active_game_mode_key and previous_snapshot != get_dict_rect_positions():
                active_game_mode_key = None

        def _generate_random_setup_position():
            back_rank = [None] * 8
            even_files = [0, 2, 4, 6]
            odd_files = [1, 3, 5, 7]

            light_bishop_index = random.choice(even_files)
            dark_bishop_index = random.choice(odd_files)
            back_rank[light_bishop_index] = "bishop"
            back_rank[dark_bishop_index] = "bishop"

            remaining = [index for index, piece in enumerate(back_rank) if piece is None]
            queen_index = random.choice(remaining)
            back_rank[queen_index] = "queen"

            remaining = [index for index, piece in enumerate(back_rank) if piece is None]
            knight_indices = random.sample(remaining, 2)
            for knight_index in knight_indices:
                back_rank[knight_index] = "knight"

            remaining = sorted(index for index, piece in enumerate(back_rank) if piece is None)
            back_rank[remaining[0]] = "rook"
            back_rank[remaining[1]] = "king"
            back_rank[remaining[2]] = "rook"

            files = "abcdefgh"

            def _coords_for(piece_name, rank):
                return [f"{files[index]}{rank}" for index, piece in enumerate(back_rank) if piece == piece_name]

            return {
                "white_pawn": [f"{file_name}2" for file_name in files],
                "white_bishop": _coords_for("bishop", 1),
                "white_knight": _coords_for("knight", 1),
                "white_rook": _coords_for("rook", 1),
                "white_queen": _coords_for("queen", 1),
                "white_king": _coords_for("king", 1),
                "black_pawn": [f"{file_name}7" for file_name in files],
                "black_bishop": _coords_for("bishop", 8),
                "black_knight": _coords_for("knight", 8),
                "black_rook": _coords_for("rook", 8),
                "black_queen": _coords_for("queen", 8),
                "black_king": _coords_for("king", 8),
            }

        def generateChaosSetup():
            files = "abcdefgh"
            capped_piece_counts = {
                "queen": 2,
                "rook": 3,
                "bishop": 3,
                "knight": 3,
            }

            def _generate_back_rank():
                piece_pool = ["king"]
                for piece_name, max_count in capped_piece_counts.items():
                    piece_pool.extend([piece_name] * max_count)
                chosen_pieces = ["king"]
                chosen_pieces.extend(random.sample(piece_pool[1:], 7))
                random.shuffle(chosen_pieces)
                return chosen_pieces

            def _coords_for(back_rank, piece_name, rank):
                return [
                    f"{files[index]}{rank}"
                    for index, current_piece in enumerate(back_rank)
                    if current_piece == piece_name
                ]

            white_back_rank = _generate_back_rank()
            black_back_rank = _generate_back_rank()

            return {
                "white_pawn": [f"{file_name}2" for file_name in files],
                "white_bishop": _coords_for(white_back_rank, "bishop", 1),
                "white_knight": _coords_for(white_back_rank, "knight", 1),
                "white_rook": _coords_for(white_back_rank, "rook", 1),
                "white_queen": _coords_for(white_back_rank, "queen", 1),
                "white_king": _coords_for(white_back_rank, "king", 1),
                "black_pawn": [f"{file_name}7" for file_name in files],
                "black_bishop": _coords_for(black_back_rank, "bishop", 8),
                "black_knight": _coords_for(black_back_rank, "knight", 8),
                "black_rook": _coords_for(black_back_rank, "rook", 8),
                "black_queen": _coords_for(black_back_rank, "queen", 8),
                "black_king": _coords_for(black_back_rank, "king", 8),
            }

        def loadPawnsOnly():
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            load_position_from_dict({
                "white_pawn": [f"{file_name}2" for file_name in "abcdefgh"],
                "white_bishop": [],
                "white_knight": [],
                "white_rook": [],
                "white_queen": [],
                "white_king": ["e1"],
                "black_pawn": [f"{file_name}7" for file_name in "abcdefgh"],
                "black_bishop": [],
                "black_knight": [],
                "black_rook": [],
                "black_queen": [],
                "black_king": ["e8"],
            })
            _apply_position_config(_build_current_orientation_config("white"))
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = "pawns_only"

        def loadRandomSetup():
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            load_position_from_dict(_generate_random_setup_position())
            _apply_position_config(_build_current_orientation_config("white"))
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = "random_setup"

        def loadChaosSetup():
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            load_position_from_dict(generateChaosSetup())
            _apply_position_config(_build_current_orientation_config("white"))
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = "chaos_setup"

        def loadPeasantsRevolt():
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            load_position_from_dict({
                "white_pawn": [f"{file_name}2" for file_name in "abcdefgh"],
                "white_bishop": [],
                "white_knight": [],
                "white_rook": [],
                "white_queen": [],
                "white_king": ["e1"],
                "black_pawn": ["e7"],
                "black_bishop": [],
                "black_knight": ["b8", "d8", "g8"],
                "black_rook": [],
                "black_queen": [],
                "black_king": ["e8"],
            })
            _apply_position_config(_build_current_orientation_config("white"))
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = "peasants_revolt"

        def loadLightBrigade():
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            load_position_from_dict({
                "white_pawn": [f"{file_name}2" for file_name in "abcdefgh"],
                "white_bishop": [],
                "white_knight": [],
                "white_rook": [],
                "white_queen": ["b1", "d1", "g1"],
                "white_king": ["e1"],
                "black_pawn": [f"{file_name}7" for file_name in "abcdefgh"],
                "black_bishop": [],
                "black_knight": ["a8", "b8", "c8", "d8", "f8", "g8", "h8"],
                "black_rook": [],
                "black_queen": [],
                "black_king": ["e8"],
            })
            _apply_position_config(_build_current_orientation_config("white"))
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = "light_brigade"

        def stop_game():
            nonlocal game_controller, restore_default_setup_on_stop
            cancel_pending_cpu_move()
            start_objects.Dragging.dragging_all_false()
            SwitchModesController.switch_mode(SwitchModesController.EDIT_MODE, play_edit_switch_button)
            del game_controller
            if restore_default_setup_on_stop:
                reset_to_default_setup()
                restore_default_setup_on_stop = False

        play_edit_switch_button = menu_buttons.PlayEditSwitchButton(initvar.PLAY_EDIT_SWITCH_BUTTON_TOPLEFT)
        features_panel = menu_buttons.SidebarSectionPanel(
            (
                initvar.FEATURES_SECTION_X,
                initvar.FEATURES_SECTION_Y,
                initvar.FEATURES_SECTION_W,
                initvar.FEATURES_SECTION_H,
            ),
            "LIBRARY",
        )
        game_modes_button = menu_buttons.SidebarActionButton(initvar.PUZZLES_BUTTON_TOPLEFT, "Game Modes")
        pgn_games_button = menu_buttons.SidebarActionButton(initvar.PGN_GAMES_BUTTON_TOPLEFT, "PGN Games")
        help_button = menu_buttons.HelpButton(initvar.HELP_BUTTON_TOPLEFT)
        flip_board_button = menu_buttons.FlipBoardButton(initvar.FLIP_BOARD_BUTTON_TOPLEFT)
        game_mode_selector = menu_buttons.GameModeSelector(initvar.GAME_MODE_SELECTOR_TOPLEFT)
        starting_turn_selector = menu_buttons.StartingTurnSelector(initvar.TURN_SELECTOR_TOPLEFT)
        help_overlay_open = False
        game_modes_modal_open = False
        pgn_games_modal_open = False
        save_position_modal_open = False
        restore_default_setup_on_stop = False
        pending_start_whoseturn = "white"
        show_help_hint = True
        hint_expire_at = pygame.time.get_ticks() + 4200
        help_panel_width = 430
        help_panel_rect = pygame.Rect(help_button.rect.right - help_panel_width, help_button.rect.bottom + 14, help_panel_width, 320)
        modal_panel_rect = pygame.Rect(0, 0, 0, 0)
        modal_close_rect = pygame.Rect(0, 0, 0, 0)
        game_mode_button_rects = {}
        game_mode_section_rects = {}
        save_turn_button_rects = {}
        game_mode_sections = [
            {
                "section_key": "puzzles",
                "title": "Puzzles",
                "helper_text": "Curated mate positions for fast solving.",
                "collapsible": True,
                "expanded": True,
                "modes": [
                    ("mate_in_1", "🧩", "Mate in 1", "Puzzle", "Find the forced checkmate in one move.", "chess_positions/puzzle1_whitetocheckmate.json", "white"),
                    ("mate_in_2", "🧩", "Mate in 2", "Puzzle", "Play through a position with a forced mate in two.", "chess_positions/puzzle2_whitetocheckmate.json", "white"),
                ],
            },
            {
                "section_key": "variants",
                "title": "Variants",
                "helper_text": "Experimental setups for alternate openings and piece mixes.",
                "collapsible": True,
                "expanded": True,
                "modes": [
                    ("pawns_only", "♟️", "Pawns Only", "Variant", "Strip the board down to kings and pawns on their standard files.", None, "white"),
                    ("random_setup", "🎲", "Random Setup", "Variant", "Generate a fresh Chess960-style back rank while keeping pawns in place.", None, "white"),
                    ("chaos_setup", "⚡", "Chaos Setup", "Variant", "Randomized armies. Standard pawn lines and no castling.", None, "white"),
                    ("peasants_revolt", "⚔️", "Peasant's Revolt", "Variant", "White fields a king with eight pawns against Black's king, three knights, and one pawn.", None, "white"),
                    ("light_brigade", "🐎", "Charge of the Light Brigade", "Variant", "White charges with three queens and a full pawn line against Black's seven knights and pawns.", None, "white"),
                ],
            },
        ]
        active_game_mode_key = None
        emoji_font = None
        for candidate_font_path in (
            "/System/Library/Fonts/Apple Color Emoji.ttc",
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        ):
            if os.path.exists(candidate_font_path):
                try:
                    emoji_font = pygame.freetype.Font(candidate_font_path, 32)
                    break
                except (FileNotFoundError, OSError, pygame.error):
                    emoji_font = None
        pgn_game_button_rects = {}
        pgn_game_options = [
            ("carlsen_kasparov", "Carlsen vs Kasparov (2004)", "pgn_sample_games/carlsen_kasparov_2004.pgn"),
            ("de_los_santos_polgar", "De los Santos vs Polgar (1990)", "pgn_sample_games/de_los_santos_polgar_1990.pgn"),
            ("deep_blue_kasparov", "Deep Blue vs Kasparov (1996)", "pgn_sample_games/DeepBlue_GarryKasparov_02101996.pgn"),
        ]
        file_actions_panel = None
        game_properties_button = None
        if not initvar.ITCH_MODE:
            game_properties_button = menu_buttons.GamePropertiesButton(initvar.GAME_PROPERTIES_BUTTON_TOPLEFT)
            file_actions_panel = menu_buttons.FileActionsPanel()
        reset_board_button = menu_buttons.ResetBoardButton(initvar.RESET_BOARD_BUTTON_TOPLEFT)
        clear_button = menu_buttons.ClearButton(initvar.CLEAR_BUTTON_TOPLEFT)
        scroll_up_button = menu_buttons.ScrollUpButton(initvar.SCROLL_UP_BUTTON_TOPLEFT)
        scroll_down_button = menu_buttons.ScrollDownButton(initvar.SCROLL_DOWN_BUTTON_TOPLEFT)
        beginning_move_button = menu_buttons.BeginningMoveButton(initvar.BEGINNING_MOVE_BUTTON_TOPLEFT)
        prev_move_button = menu_buttons.PrevMoveButton(initvar.PREV_MOVE_BUTTON_TOPLEFT)
        next_move_button = menu_buttons.NextMoveButton(initvar.NEXT_MOVE_BUTTON_TOPLEFT)
        last_move_button = menu_buttons.LastMoveButton(initvar.LAST_MOVE_BUTTON_TOPLEFT)
        undo_move_button = menu_buttons.UndoMoveButton(initvar.UNDO_MOVE_BUTTON_TOPLEFT)
        replay_button_tooltips = (
            (beginning_move_button, "Go to Beginning"),
            (prev_move_button, "Previous Move"),
            (next_move_button, "Next Move"),
            (last_move_button, "Go to Last Move"),
        )
        # Window
        gameicon = pygame.image.load("sprites/chessico.png")
        pygame.display.set_icon(gameicon)
        pygame.display.set_caption('Chess')
        # Load the starting positions of chessboard first
        pos_load_file(reset=True)
        start_game()
        # Pre-create dark overlays for visual contrast.
        # (15, 20, 35): dark navy rather than near-black — the blue channel is visible at
        # lower opacities and keeps the overlay in the space background's color family.
        _OVERLAY_COLOR = (15, 20, 35)
        _shared_x = initvar.X_GRID_START - 45
        _shared_y = initvar.BLACK_X_Y[1] - 5
        _undo_bottom = initvar.UNDO_MOVE_BUTTON_TOPLEFT[1] + 78
        _captured_row_bottom = initvar.BLACK_CAPTURED_Y + board.Y_GRID_HEIGHT
        _shared_bottom = max(_undo_bottom, _captured_row_bottom) + 8
        # Width spans from the left of the board area to the right of the panel — one
        # continuous surface so board and panel read as the same zone, not two boxes.
        _shared_w = (initvar.MOVE_BG_IMAGE_X - 12 + 226) - _shared_x
        _shared_h = _shared_bottom - _shared_y
        _main_bg_overlay = pygame.Surface((_shared_w, _shared_h))
        _main_bg_overlay.fill(_OVERLAY_COLOR)
        _main_bg_overlay.set_alpha(88)
        # ── Design-system tokens ────────────────────────────────────────────
        # Shared across ALL panels (right move-list, Game Setup, player badges,
        # popovers) so every surface feels like part of the same system.
        _PANEL_FILL   = (10, 22, 52)    # unified dark navy
        _PANEL_BORDER = (72, 100, 148)  # steel-blue edge — same as Game Setup
        _PANEL_RADIUS = 12              # consistent corner radius
        _PANEL_RECT   = (initvar.MOVE_BG_IMAGE_X, initvar.MOVE_BG_IMAGE_Y, 202, 628)
        # Pre-render the right panel surface once — avoids rebuilding each frame.
        _rp_surf = pygame.Surface((_PANEL_RECT[2], _PANEL_RECT[3]), pygame.SRCALPHA)
        pygame.draw.rect(_rp_surf, (*_PANEL_FILL, 210), _rp_surf.get_rect(), border_radius=_PANEL_RADIUS)
        pygame.draw.rect(_rp_surf, (*_PANEL_BORDER, 215), _rp_surf.get_rect(), 1, border_radius=_PANEL_RADIUS)
        _rp_shadow = pygame.Surface((_PANEL_RECT[2] + 8, _PANEL_RECT[3] + 8), pygame.SRCALPHA)
        pygame.draw.rect(_rp_shadow, (0, 0, 0, 55), _rp_shadow.get_rect(), border_radius=_PANEL_RADIUS + 3)
        # Sidebar: slightly more opaque so the column reads as a grounded panel.
        _sidebar_bg_overlay = pygame.Surface((210, initvar.SCREEN_HEIGHT))
        _sidebar_bg_overlay.fill(_OVERLAY_COLOR)
        _sidebar_bg_overlay.set_alpha(85)
        _player_name_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 26, bold=True)
        _player_rating_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 17)
        _status_label_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 16, bold=True)
        _status_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 28, bold=True)
        _status_sub_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 20)
        _game_mode_title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)
        _tooltip_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 18)
        _itch_notice_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 12, bold=False)
        _game_mode_badge_fill = (0, 0, 0, 102)
        _game_mode_badge_border = (255, 255, 255, 38)
        _game_mode_badge_text = (242, 247, 255)
        _game_mode_badge_pad_x = 16
        _game_mode_badge_pad_y = 7
        _game_mode_badge_bottom_margin = 4
        _label_color = (165, 195, 230)  # matches "GAME SETUP" label — consistent across panels
        _muted_text  = (150, 175, 210)
        _game_mode_title_by_key = {
            "mate_in_1": "Mate in 1",
            "mate_in_2": "Mate in 2",
            "pawns_only": "Pawns Only",
            "random_setup": "Random Setup",
            "chaos_setup": "Chaos Setup",
            "peasants_revolt": "Peasant's Revolt",
            "light_brigade": "Charge of the Light Brigade",
        }

        def _fit_font(text, max_width, start_size, min_size, bold=False):
            size = start_size
            while size >= min_size:
                font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, size, bold=bold)
                if font.size(text)[0] <= max_width:
                    return font
                size -= 1
            return pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, min_size, bold=bold)

        def _wrap_text_lines(text, font, max_width):
            words = text.split()
            if not words:
                return []
            lines = []
            current_line = words[0]
            for word in words[1:]:
                candidate = f"{current_line} {word}"
                if font.size(candidate)[0] <= max_width:
                    current_line = candidate
                else:
                    lines.append(current_line)
                    current_line = word
            lines.append(current_line)
            return lines

        _player_badge_hover_info = []  # [(pygame.Rect, full_name), ...] — populated each frame

        def _truncate_name(text, font, max_width):
            if font.size(text)[0] <= max_width:
                return text
            ellipsis = "\u2026"
            while text and font.size(text + ellipsis)[0] > max_width:
                text = text[:-1]
            return text + ellipsis

        def _draw_tooltip(text, pos):
            tip_surf = _tooltip_font.render(text, True, (242, 247, 255))
            pad = 6
            tip_w = tip_surf.get_width() + pad * 2
            tip_h = tip_surf.get_height() + pad * 2
            tip_bg = pygame.Surface((tip_w, tip_h), pygame.SRCALPHA)
            pygame.draw.rect(tip_bg, (*_PANEL_FILL, 220), tip_bg.get_rect(), border_radius=8)
            pygame.draw.rect(tip_bg, (*_PANEL_BORDER, 190), tip_bg.get_rect(), 1, border_radius=8)
            tip_bg.blit(tip_surf, (pad, pad))
            tx = min(pos[0] + 12, lis.SCREEN.get_width() - tip_w - 4)
            ty = max(pos[1] - tip_h - 4, 4)
            lis.SCREEN.blit(tip_bg, (tx, ty))

        def _draw_help_hint():
            if not show_help_hint or pygame.time.get_ticks() >= hint_expire_at or help_overlay_open:
                return
            hint_text = _tooltip_font.render("Need help?", True, (242, 247, 255))
            pad_x = 12
            pad_y = 8
            hint_w = hint_text.get_width() + pad_x * 2
            hint_h = hint_text.get_height() + pad_y * 2
            hint_x = help_button.rect.left - hint_w - 12
            hint_y = help_button.rect.centery - hint_h // 2
            hint_bg = pygame.Surface((hint_w, hint_h), pygame.SRCALPHA)
            pygame.draw.rect(hint_bg, (*_PANEL_FILL, 208), hint_bg.get_rect(), border_radius=10)
            pygame.draw.rect(hint_bg, (*_PANEL_BORDER, 190), hint_bg.get_rect(), 1, border_radius=10)
            hint_bg.blit(hint_text, (pad_x, pad_y))
            lis.SCREEN.blit(hint_bg, (hint_x, hint_y))
            pointer = [
                (hint_x + hint_w, help_button.rect.centery - 6),
                (hint_x + hint_w + 8, help_button.rect.centery),
                (hint_x + hint_w, help_button.rect.centery + 6),
            ]
            pygame.draw.polygon(lis.SCREEN, (*_PANEL_FILL, 208), pointer)
            pygame.draw.polygon(lis.SCREEN, (*_PANEL_BORDER, 190), pointer, 1)

        def _draw_itch_notice():
            notice_text = "Best experienced on desktop. If playing on itch.io, please use landscape mode."
            notice_surf = _itch_notice_font.render(notice_text, True, (255, 255, 255))
            notice_surf.set_alpha(204)
            shadow_surf = _itch_notice_font.render(notice_text, True, (0, 0, 0))
            shadow_surf.set_alpha(178)
            notice_x = (lis.SCREEN.get_width() - notice_surf.get_width()) // 2
            notice_y = lis.SCREEN.get_height() - notice_surf.get_height() - 16
            lis.SCREEN.blit(shadow_surf, (notice_x, notice_y + 1))
            lis.SCREEN.blit(shadow_surf, (notice_x, notice_y + 2))
            lis.SCREEN.blit(notice_surf, (notice_x, notice_y))

        def _draw_active_game_mode_title():
            if not active_game_mode_key:
                return

            title_text = _game_mode_title_by_key.get(active_game_mode_key)
            if not title_text:
                return

            title_font = _fit_font(title_text, _shared_w - (_game_mode_badge_pad_x * 2) - 24, 22, 16, bold=True)
            title_surf = title_font.render(title_text, True, _game_mode_badge_text)

            badge_w = title_surf.get_width() + (_game_mode_badge_pad_x * 2)
            badge_h = title_surf.get_height() + (_game_mode_badge_pad_y * 2)
            badge_x = _shared_x + (_shared_w - badge_w) // 2
            badge_y = initvar.SCREEN_HEIGHT - badge_h - _game_mode_badge_bottom_margin
            badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)

            badge_surf = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
            pygame.draw.rect(badge_surf, _game_mode_badge_fill, badge_surf.get_rect(), border_radius=999)
            pygame.draw.rect(badge_surf, _game_mode_badge_border, badge_surf.get_rect(), 1, border_radius=999)
            lis.SCREEN.blit(badge_surf, badge_rect.topleft)

            title_x = badge_rect.x + (badge_rect.width - title_surf.get_width()) // 2
            title_y = badge_rect.y + (badge_rect.height - title_surf.get_height()) // 2
            lis.SCREEN.blit(title_surf, (title_x, title_y))

        def _draw_help_overlay():
            _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
            _dim.fill((5, 10, 24, 165))
            lis.SCREEN.blit(_dim, (0, 0))
            title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 24, bold=True)
            body_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 18)
            muted_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 16)
            content = [
                ("Quick Help", title_font, (242, 247, 255), 20, False),
                ("Drag pieces in setup mode to build a position.", body_font, (226, 235, 248), 72, True),
                ("Use Start Game to switch into play mode.", body_font, (226, 235, 248), None, True),
                ("Flip rotates the board. Undo and replay controls work in play mode.", body_font, (226, 235, 248), None, True),
                ("Undo Move also turns off CPU mode for the current game.", body_font, (226, 235, 248), None, True),
            ]
            if initvar.ITCH_MODE:
                content.extend([
                    ("This itch build focuses on board setup and play.", body_font, (226, 235, 248), None, True),
                    ("Press Esc or click outside to close.", muted_font, (165, 195, 230), None, True),
                ])
            else:
                content.extend([
                    ("In play mode, you can save the PGN of the game you're playing.", body_font, (226, 235, 248), None, True),
                    ("In edit mode, you can load PGN, save positions, and load positions.", body_font, (226, 235, 248), None, True),
                    ("Press Esc or click outside to close.", muted_font, (165, 195, 230), None, True),
                ])

            def _wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current = ""
                for word in words:
                    candidate = word if not current else f"{current} {word}"
                    if font.size(candidate)[0] <= max_width:
                        current = candidate
                    else:
                        if current:
                            lines.append(current)
                        current = word
                if current:
                    lines.append(current)
                return lines

            wrapped_content = []
            y = 20
            max_width = help_panel_width - 40
            line_gap = 8
            section_gap = 12
            for text, font, color, explicit_y, wrap in content:
                if explicit_y is not None:
                    y = explicit_y
                wrapped_lines = _wrap_text(text, font, max_width) if wrap else [text]
                wrapped_content.append((wrapped_lines, font, color, y))
                for wrapped_line in wrapped_lines:
                    y += font.get_linesize() + line_gap
                y += section_gap
            panel_height = y + 12
            panel_x = help_button.rect.right - help_panel_width
            panel_y = help_button.rect.bottom + 14
            panel_y = min(panel_y, lis.SCREEN.get_height() - panel_height - 20)
            help_panel_rect = pygame.Rect(panel_x, panel_y, help_panel_width, panel_height)
            panel = pygame.Surface(help_panel_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(panel, (*_PANEL_FILL, 238), panel.get_rect(), border_radius=16)
            pygame.draw.rect(panel, (*_PANEL_BORDER, 220), panel.get_rect(), 1, border_radius=16)
            for wrapped_lines, font, color, y in wrapped_content:
                for wrapped_line in wrapped_lines:
                    panel.blit(font.render(wrapped_line, True, color), (20, y))
                    y += font.get_linesize() + line_gap
            lis.SCREEN.blit(panel, help_panel_rect.topleft)
            return help_panel_rect

        def _load_game_mode_position(game_mode_key, json_path, whoseturn):
            nonlocal game_modes_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            _reset_board_for_game_mode_load()
            loaded_position = load_position_from_json(json_path)
            _apply_position_config(loaded_position["config"], fallback_whoseturn=whoseturn)
            game_modes_modal_open = False
            restore_default_setup_on_stop = False
            active_game_mode_key = game_mode_key

        def _load_sample_pgn(pgn_path):
            nonlocal game_controller, game_modes_modal_open, pgn_games_modal_open, restore_default_setup_on_stop, pending_start_whoseturn, active_game_mode_key
            cancel_pending_cpu_move()
            start_objects.Dragging.dragging_all_false()
            start_objects.Start.restart_start_positions()
            if CpuController.cpu_mode:
                CpuController.cpu_mode_toggle()
            if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                stop_game()
            game_controller = PgnWriterAndLoader.pgn_load_from_path(play_edit_switch_button, pgn_path)
            game_modes_modal_open = False
            pgn_games_modal_open = False
            restore_default_setup_on_stop = game_controller is not None
            pending_start_whoseturn = "white"
            active_game_mode_key = None

        def _save_position_with_starting_turn(selected_turn):
            nonlocal pending_start_whoseturn
            pending_start_whoseturn = _normalize_starting_turn(selected_turn)
            pos_save_file(_current_position_config())

        def _reset_game_mode_sections():
            for section in game_mode_sections:
                section["expanded"] = False

        def _draw_save_position_modal():
            nonlocal modal_panel_rect, modal_close_rect, save_turn_button_rects
            _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
            _dim.fill((5, 10, 24, 185))
            lis.SCREEN.blit(_dim, (0, 0))

            panel_w = 520
            panel_h = 280
            panel_x = (lis.SCREEN.get_width() - panel_w) // 2
            panel_y = (lis.SCREEN.get_height() - panel_h) // 2
            modal_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            modal_close_rect = pygame.Rect(panel_x + panel_w - 52, panel_y + 14, 36, 36)

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (*_PANEL_FILL, 240), panel.get_rect(), border_radius=18)
            pygame.draw.rect(panel, (*_PANEL_BORDER, 220), panel.get_rect(), 1, border_radius=18)

            title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 28, bold=True)
            body_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 19)
            option_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)
            detail_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 17)
            close_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)

            title = title_font.render("Save Position", True, (242, 247, 255))
            subtitle = body_font.render("Choose who should move first when this position is loaded.", True, (198, 216, 238))
            panel.blit(title, (28, 24))
            panel.blit(subtitle, (28, 64))

            close_hovered = modal_close_rect.collidepoint(mousepos)
            close_bg = (24, 50, 96, 210) if close_hovered else (16, 34, 72, 180)
            close_border = (110, 150, 210, 230) if close_hovered else (82, 110, 158, 190)
            close_local_rect = pygame.Rect(panel_w - 52, 14, 36, 36)
            pygame.draw.rect(panel, close_bg, close_local_rect, border_radius=10)
            pygame.draw.rect(panel, close_border, close_local_rect, 1, border_radius=10)
            close_text = close_font.render("X", True, (242, 247, 255))
            panel.blit(close_text, (close_local_rect.centerx - close_text.get_width() // 2,
                                    close_local_rect.centery - close_text.get_height() // 2 - 1))

            save_turn_button_rects = {}
            options = (
                ("white", "White to move", "Save this setup with White starting."),
                ("black", "Black to move", "Save this setup with Black starting."),
            )
            button_w = panel_w - 56
            button_h = 62
            first_y = 112
            gap = 18
            for index, (turn_key, label, description) in enumerate(options):
                local_rect = pygame.Rect(28, first_y + index * (button_h + gap), button_w, button_h)
                absolute_rect = local_rect.move(panel_x, panel_y)
                save_turn_button_rects[turn_key] = absolute_rect
                hovered = absolute_rect.collidepoint(mousepos)
                is_selected = pending_start_whoseturn == turn_key
                btn_bg = (30, 66, 122, 230) if hovered or is_selected else (18, 42, 86, 192)
                btn_border = (170, 214, 255, 235) if hovered or is_selected else (104, 142, 194, 190)
                pygame.draw.rect(panel, btn_bg, local_rect, border_radius=12)
                pygame.draw.rect(panel, btn_border, local_rect, 1, border_radius=12)
                label_surf = option_font.render(label, True, (244, 248, 255))
                desc_surf = detail_font.render(description, True, (188, 208, 232))
                panel.blit(label_surf, (local_rect.x + 18, local_rect.y + 12))
                panel.blit(desc_surf, (local_rect.x + 18, local_rect.y + 36))

            lis.SCREEN.blit(panel, modal_panel_rect.topleft)

        def _draw_game_modes_modal():
            nonlocal modal_panel_rect, modal_close_rect, game_mode_button_rects, game_mode_section_rects

            def _wrap_text_lines(text, font, max_width):
                words = text.split()
                if not words:
                    return [""]
                lines = []
                current_line = words[0]
                for word in words[1:]:
                    candidate = f"{current_line} {word}"
                    if font.size(candidate)[0] <= max_width:
                        current_line = candidate
                    else:
                        lines.append(current_line)
                        current_line = word
                lines.append(current_line)
                return lines

            _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
            _dim.fill((5, 10, 24, 185))
            lis.SCREEN.blit(_dim, (0, 0))

            title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 28, bold=True)
            option_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 20, bold=True)
            detail_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 16)
            section_title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 18, bold=True)
            section_helper_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 15)
            close_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)

            def _draw_mode_icon(target_surface, mode_key, emoji_text, icon_rect):
                style_by_mode = {
                    "mate_in_1": ((118, 86, 20, 245), (255, 219, 122, 235)),
                    "mate_in_2": ((118, 86, 20, 245), (255, 219, 122, 235)),
                    "pawns_only": ((33, 87, 72, 240), (120, 218, 186, 225)),
                    "random_setup": ((67, 69, 138, 240), (165, 180, 255, 225)),
                    "chaos_setup": ((122, 64, 28, 240), (255, 184, 125, 225)),
                    "peasants_revolt": ((102, 56, 34, 240), (231, 194, 120, 225)),
                    "light_brigade": ((70, 76, 118, 240), (185, 201, 255, 225)),
                }
                badge_fill, badge_border = style_by_mode[mode_key]
                pygame.draw.rect(target_surface, badge_fill, icon_rect, border_radius=12)
                pygame.draw.rect(target_surface, badge_border, icon_rect, 1, border_radius=12)

                if emoji_font is not None:
                    try:
                        icon_surface, icon_bounds = emoji_font.render(emoji_text)
                    except (OSError, pygame.error):
                        icon_surface = None
                        icon_bounds = None
                    if icon_surface is not None and icon_surface.get_width() > 0 and icon_surface.get_height() > 0:
                        icon_pos = (
                            icon_rect.centerx - icon_surface.get_width() // 2,
                            icon_rect.centery - icon_surface.get_height() // 2,
                        )
                        target_surface.blit(icon_surface, icon_pos)
                        return

                fallback_labels = {
                    "mate_in_1": "P1",
                    "mate_in_2": "P2",
                    "pawns_only": "PA",
                    "random_setup": "RD",
                    "chaos_setup": "CH",
                    "peasants_revolt": "PR",
                    "light_brigade": "LB",
                }
                fallback_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 13, bold=True)
                fallback_surface = fallback_font.render(fallback_labels[mode_key], True, (242, 247, 255))
                target_surface.blit(
                    fallback_surface,
                    (
                        icon_rect.centerx - fallback_surface.get_width() // 2,
                        icon_rect.centery - fallback_surface.get_height() // 2 - 1,
                    ),
                )

            subtitle_lines = _wrap_text_lines(
                "Load mate puzzles or quick variants, including a kings-and-pawns setup.",
                detail_font,
                428,
            )

            panel_w = 520
            button_w = panel_w - 56
            button_padding_top = 14
            button_padding_bottom = 16
            detail_y_offset = 40
            description_line_height = 18
            subtitle_y = 58 + (len(subtitle_lines) * 18)
            first_y = subtitle_y + 18
            section_gap = 16
            card_gap = 14
            section_header_h = 60
            button_layout = []
            section_layout = []
            current_y = first_y
            for section in game_mode_sections:
                header_rect = pygame.Rect(28, current_y, button_w, section_header_h)
                helper_lines = _wrap_text_lines(section["helper_text"], section_helper_font, button_w - 148)
                section_layout.append((section, helper_lines, header_rect))
                current_y = header_rect.bottom + 10
                if section["expanded"]:
                    for mode_key, emoji_text, label, mode_type, mode_description, _, _ in section["modes"]:
                        description_lines = _wrap_text_lines(mode_description, detail_font, button_w - 96)
                        if mode_key in {"random_setup", "chaos_setup"}:
                            description_lines.append("Click again to regenerate.")
                        description_start_y = 40 if mode_type in {"Variant", "Puzzle"} else 58
                        bottom_padding = 8 if mode_type in {"Variant", "Puzzle"} else button_padding_bottom
                        button_h = button_padding_top + description_start_y + (len(description_lines) * description_line_height) + bottom_padding
                        local_rect = pygame.Rect(28, current_y, button_w, button_h)
                        button_layout.append((mode_key, emoji_text, label, mode_type, description_lines, local_rect))
                        current_y = local_rect.bottom + card_gap
                current_y += section_gap

            content_bottom = current_y - section_gap if section_layout else first_y
            panel_h = max(420, content_bottom + 28)
            panel_h = min(panel_h, lis.SCREEN.get_height() - 60)
            panel_x = (lis.SCREEN.get_width() - panel_w) // 2
            panel_y = (lis.SCREEN.get_height() - panel_h) // 2
            modal_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            modal_close_rect = pygame.Rect(panel_x + panel_w - 52, panel_y + 14, 36, 36)

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (*_PANEL_FILL, 240), panel.get_rect(), border_radius=18)
            pygame.draw.rect(panel, (*_PANEL_BORDER, 220), panel.get_rect(), 1, border_radius=18)

            title = title_font.render("Game Modes", True, (242, 247, 255))
            panel.blit(title, (28, 24))

            close_hovered = modal_close_rect.collidepoint(mousepos)
            close_bg = (24, 50, 96, 210) if close_hovered else (16, 34, 72, 180)
            close_border = (110, 150, 210, 230) if close_hovered else (82, 110, 158, 190)
            close_local_rect = pygame.Rect(panel_w - 52, 14, 36, 36)
            pygame.draw.rect(panel, close_bg, close_local_rect, border_radius=10)
            pygame.draw.rect(panel, close_border, close_local_rect, 1, border_radius=10)
            close_text = close_font.render("X", True, (242, 247, 255))
            panel.blit(close_text, (close_local_rect.centerx - close_text.get_width() // 2,
                                    close_local_rect.centery - close_text.get_height() // 2 - 1))

            subtitle_y = 58
            for line in subtitle_lines:
                subtitle = detail_font.render(line, True, (188, 208, 232))
                panel.blit(subtitle, (28, subtitle_y))
                subtitle_y += 18

            game_mode_button_rects = {}
            game_mode_section_rects = {}
            for section, helper_lines, header_rect in section_layout:
                absolute_header_rect = header_rect.move(panel_x, panel_y)
                game_mode_section_rects[section["section_key"]] = absolute_header_rect
                header_hovered = absolute_header_rect.collidepoint(mousepos)
                header_bg = (20, 45, 92, 168) if header_hovered else (14, 32, 70, 130)
                header_border = (122, 166, 222, 210) if header_hovered else (84, 122, 178, 180)
                pygame.draw.rect(panel, header_bg, header_rect, border_radius=12)
                pygame.draw.rect(panel, header_border, header_rect, 1, border_radius=12)

                title_surf = section_title_font.render(section["title"], True, (242, 247, 255))
                helper_color = (190, 209, 234) if section["expanded"] else (164, 184, 214)
                helper_y = header_rect.y + 30
                panel.blit(title_surf, (header_rect.x + 16, header_rect.y + 10))
                for helper_line in helper_lines[:1]:
                    helper_surf = section_helper_font.render(helper_line, True, helper_color)
                    panel.blit(helper_surf, (header_rect.x + 16, helper_y))

                if section["collapsible"]:
                    chevron_direction = "v" if section["expanded"] else ">"
                    chevron_surface = section_title_font.render(chevron_direction, True, (214, 229, 248))
                    chevron_x = header_rect.right - chevron_surface.get_width() - 16
                    panel.blit(chevron_surface, (chevron_x, header_rect.y + 9))

            for mode_key, emoji_text, label, mode_type, description_lines, local_rect in button_layout:
                absolute_rect = local_rect.move(panel_x, panel_y)
                game_mode_button_rects[mode_key] = absolute_rect
                hovered = absolute_rect.collidepoint(mousepos)
                selected = active_game_mode_key == mode_key
                btn_bg = (30, 66, 122, 230) if hovered or selected else (18, 42, 86, 192)
                btn_border = (170, 214, 255, 235) if hovered or selected else (104, 142, 194, 190)
                pygame.draw.rect(panel, btn_bg, local_rect, border_radius=12)
                pygame.draw.rect(panel, btn_border, local_rect, 1, border_radius=12)
                label_surf = option_font.render(label, True, (244, 248, 255))
                detail_surf = detail_font.render(mode_type, True, (188, 208, 232))
                content_x = local_rect.x + 70
                icon_rect = pygame.Rect(local_rect.x + 14, local_rect.y + 12, 40, 40)
                _draw_mode_icon(panel, mode_key, emoji_text, icon_rect)
                panel.blit(label_surf, (content_x, local_rect.y + 14))
                description_y = local_rect.y + 40
                if mode_type not in {"Variant", "Puzzle"}:
                    panel.blit(detail_surf, (content_x, local_rect.y + 40))
                    description_y = local_rect.y + 58
                for line in description_lines:
                    description_surf = detail_font.render(line, True, (216, 231, 248))
                    panel.blit(description_surf, (content_x, description_y))
                    description_y += description_line_height

            lis.SCREEN.blit(panel, modal_panel_rect.topleft)

        def _draw_pgn_games_modal():
            nonlocal modal_panel_rect, modal_close_rect, pgn_game_button_rects
            _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
            _dim.fill((5, 10, 24, 185))
            lis.SCREEN.blit(_dim, (0, 0))

            panel_w = 520
            panel_h = 310
            panel_x = (lis.SCREEN.get_width() - panel_w) // 2
            panel_y = (lis.SCREEN.get_height() - panel_h) // 2
            modal_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
            modal_close_rect = pygame.Rect(panel_x + panel_w - 52, panel_y + 14, 36, 36)

            panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            pygame.draw.rect(panel, (*_PANEL_FILL, 240), panel.get_rect(), border_radius=18)
            pygame.draw.rect(panel, (*_PANEL_BORDER, 220), panel.get_rect(), 1, border_radius=18)

            title_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 28, bold=True)
            option_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 20, bold=True)
            close_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 22, bold=True)

            title = title_font.render("PGN Games", True, (242, 247, 255))
            panel.blit(title, (28, 24))

            close_hovered = modal_close_rect.collidepoint(mousepos)
            close_bg = (24, 50, 96, 210) if close_hovered else (16, 34, 72, 180)
            close_border = (110, 150, 210, 230) if close_hovered else (82, 110, 158, 190)
            close_local_rect = pygame.Rect(panel_w - 52, 14, 36, 36)
            pygame.draw.rect(panel, close_bg, close_local_rect, border_radius=10)
            pygame.draw.rect(panel, close_border, close_local_rect, 1, border_radius=10)
            close_text = close_font.render("X", True, (242, 247, 255))
            panel.blit(close_text, (close_local_rect.centerx - close_text.get_width() // 2,
                                    close_local_rect.centery - close_text.get_height() // 2 - 1))

            pgn_game_button_rects = {}
            button_w = panel_w - 56
            button_h = 58
            first_y = 86
            gap = 16
            for index, (game_key, label, _) in enumerate(pgn_game_options):
                local_rect = pygame.Rect(28, first_y + index * (button_h + gap), button_w, button_h)
                absolute_rect = local_rect.move(panel_x, panel_y)
                pgn_game_button_rects[game_key] = absolute_rect
                hovered = absolute_rect.collidepoint(mousepos)
                btn_bg = (26, 58, 110, 224) if hovered else (18, 42, 86, 192)
                btn_border = (150, 204, 255, 235) if hovered else (104, 142, 194, 190)
                pygame.draw.rect(panel, btn_bg, local_rect, border_radius=12)
                pygame.draw.rect(panel, btn_border, local_rect, 1, border_radius=12)
                label_surf = option_font.render(label, True, (244, 248, 255))
                panel.blit(label_surf, (local_rect.x + 18, local_rect.centery - label_surf.get_height() // 2))

            lis.SCREEN.blit(panel, modal_panel_rect.topleft)

        def _draw_player_identity(name, rating, side):
            board_right_x = board.X_GRID_END
            panel_left_x = initvar.MOVE_BG_IMAGE_X
            badge_right_padding = 6
            box_width = panel_left_x - board_right_x - badge_right_padding
            box_height = 62
            box_x = board_right_x
            if side == "top":
                box_y = initvar.Y_GRID_START - box_height
            else:
                box_y = board.Y_GRID_END
            badge = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            pygame.draw.rect(badge, (*_PANEL_FILL, 185), badge.get_rect(), border_radius=_PANEL_RADIUS)
            pygame.draw.rect(badge, (*_PANEL_BORDER, 205), badge.get_rect(), 1, border_radius=_PANEL_RADIUS)
            safe_name = name or "Player"
            max_name_width = box_width - 48  # 40px left margin + 8px right inner padding
            display_name = _truncate_name(safe_name, _player_name_font, max_name_width)
            name_text = _player_name_font.render(display_name, True, (242, 247, 255))
            rating_text = _player_rating_font.render(rating, True, (187, 201, 222)) if rating else None
            indicator_color = (244, 246, 250) if side == "bottom" else (88, 108, 138)
            pygame.draw.circle(badge, indicator_color, (22, 31), 8)
            pygame.draw.circle(badge, (214, 224, 239), (22, 31), 8, 1)
            badge.blit(name_text, (40, 10))
            if rating_text:
                badge.blit(rating_text, (40, 34))
            lis.SCREEN.blit(badge, (box_x, box_y))
            _player_badge_hover_info.append((pygame.Rect(box_x, box_y, box_width, box_height), safe_name))

        def _draw_panel_status(turn_text, detail_text):
            if not turn_text and not detail_text:
                return
            card_x = initvar.MOVE_BG_IMAGE_X + 16
            card_y = initvar.MOVE_BG_IMAGE_Y + 14
            card_width = _PANEL_RECT[2] - ((card_x - _PANEL_RECT[0]) * 2)
            detail_lines = []
            detail_font = None
            if detail_text:
                detail_font = _fit_font(detail_text, card_width, 17, 14)
                detail_lines = _wrap_text_lines(detail_text, detail_font, card_width)
            card_height = 52 + (len(detail_lines) * 18 if detail_lines else 0)
            card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            status_label = _status_label_font.render("STATUS", True, _label_color)
            card.blit(status_label, (0, 0))
            if turn_text:
                turn_font = _fit_font(turn_text, card_width, 24, 16, bold=True)
                turn_surface = turn_font.render(turn_text, True, (244, 248, 255))
                card.blit(turn_surface, (0, 22))
            if detail_lines and detail_font:
                detail_color = (255, 214, 166) if "check" in detail_text.lower() else (206, 220, 238)
                detail_y = 50 if turn_text else 24
                for detail_line in detail_lines:
                    detail_surface = detail_font.render(detail_line, True, detail_color)
                    card.blit(detail_surface, (0, detail_y))
                    detail_y += 18
            lis.SCREEN.blit(card, (card_x, card_y))
            pygame.draw.line(
                lis.SCREEN,
                _PANEL_BORDER,
                (initvar.MOVE_BG_IMAGE_X + 14, initvar.MOVE_BG_IMAGE_Y + 136),
                (initvar.MOVE_BG_IMAGE_X + _PANEL_RECT[2] - 14, initvar.MOVE_BG_IMAGE_Y + 136),
                1,
            )
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
                    if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                        show_help_hint = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE and save_position_modal_open:
                            save_position_modal_open = False
                            continue
                        if event.key == pygame.K_ESCAPE and pgn_games_modal_open:
                            pgn_games_modal_open = False
                            continue
                        if event.key == pygame.K_ESCAPE and game_modes_modal_open:
                            game_modes_modal_open = False
                            continue
                        if event.key == pygame.K_ESCAPE and help_overlay_open:
                            help_overlay_open = False
                            continue
                        if event.key == pygame.K_ESCAPE:
                            app_running = False
                            break
                    # If user wants to debug
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_SPACE:
                            debug_message = 1
                            state = debug
                    if (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]
                            and save_position_modal_open):
                        if modal_close_rect.collidepoint(mousepos):
                            save_position_modal_open = False
                        elif not modal_panel_rect.collidepoint(mousepos):
                            save_position_modal_open = False
                        elif save_turn_button_rects.get("white") and save_turn_button_rects["white"].collidepoint(mousepos):
                            save_position_modal_open = False
                            _save_position_with_starting_turn("white")
                        elif save_turn_button_rects.get("black") and save_turn_button_rects["black"].collidepoint(mousepos):
                            save_position_modal_open = False
                            _save_position_with_starting_turn("black")
                        continue
                    if (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]
                            and pgn_games_modal_open):
                        if modal_close_rect.collidepoint(mousepos):
                            pgn_games_modal_open = False
                        elif not modal_panel_rect.collidepoint(mousepos):
                            pgn_games_modal_open = False
                        else:
                            for game_key, _label, pgn_path in pgn_game_options:
                                if pgn_game_button_rects.get(game_key) and pgn_game_button_rects[game_key].collidepoint(mousepos):
                                    _load_sample_pgn(pgn_path)
                                    break
                        continue
                    if (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]
                            and game_modes_modal_open):
                        if modal_close_rect.collidepoint(mousepos):
                            game_modes_modal_open = False
                        elif not modal_panel_rect.collidepoint(mousepos):
                            game_modes_modal_open = False
                        else:
                            section_toggled = False
                            for section in game_mode_sections:
                                if (section["collapsible"]
                                        and game_mode_section_rects.get(section["section_key"])
                                        and game_mode_section_rects[section["section_key"]].collidepoint(mousepos)):
                                    should_expand = not section["expanded"]
                                    for other_section in game_mode_sections:
                                        other_section["expanded"] = False
                                    section["expanded"] = should_expand
                                    section_toggled = True
                                    break
                            if not section_toggled:
                                for section in game_mode_sections:
                                    for mode_key, _emoji_text, _label, _mode_type, _mode_description, json_path, whoseturn in section["modes"]:
                                        if game_mode_button_rects.get(mode_key) and game_mode_button_rects[mode_key].collidepoint(mousepos):
                                            if mode_key == "pawns_only":
                                                loadPawnsOnly()
                                            elif mode_key == "random_setup":
                                                loadRandomSetup()
                                            elif mode_key == "chaos_setup":
                                                loadChaosSetup()
                                            elif mode_key == "peasants_revolt":
                                                loadPeasantsRevolt()
                                            elif mode_key == "light_brigade":
                                                loadLightBrigade()
                                            else:
                                                _load_game_mode_position(mode_key, json_path, whoseturn)
                                            break
                                    else:
                                        continue
                                    break
                        continue
                    if (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]
                            and help_overlay_open
                            and not help_panel_rect.collidepoint(mousepos)
                            and not help_button.rect.collidepoint(mousepos)):
                        help_overlay_open = False
                        continue
                    # Direct file actions: explicit buttons avoid the old save/load popover collisions.
                    if (event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]
                            and not initvar.ITCH_MODE
                            and (SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE
                                 or SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE)):
                        file_action = file_actions_panel.hit(mousepos, SwitchModesController.GAME_MODE)
                        if file_action == "save_position":
                            save_position_modal_open = True
                            help_overlay_open = False
                            game_modes_modal_open = False
                            pgn_games_modal_open = False
                            continue
                        if file_action == "save_pgn":
                            _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
                            _dim.fill((0, 0, 0, 140))
                            lis.SCREEN.blit(_dim, (0, 0))
                            pygame.display.flip()
                            GameProperties.game_properties_popup()
                            PgnWriterAndLoader.write_moves(MoveTracker.df_moves, game_controller.result_abb)
                            continue
                        if file_action == "load_position":
                            loaded_position = pos_load_file()
                            if loaded_position is not None:
                                _apply_position_config(loaded_position["config"])
                                active_game_mode_key = None
                            continue
                        if file_action == "load_pgn":
                            cancel_pending_cpu_move()
                            if CpuController.cpu_mode:
                                CpuController.cpu_mode_toggle()
                            game_controller = PgnWriterAndLoader.pgn_load(play_edit_switch_button)
                            for grid in board.Grid.grid_list:
                                grid.no_highlight()
                            GridController.update_grid_occupied_detection()
                            active_game_mode_key = None
                            continue
                    # Menu, inanimate buttons at top, and on right side of game board
                    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] \
                        and (mousepos[0] > board.X_GRID_END or mousepos[1] < initvar.Y_GRID_START \
                             or mousepos[0] < initvar.X_GRID_START or mousepos[1] > board.Y_GRID_END):
                        #%% Left click buttons
                        if help_button.rect.collidepoint(mousepos):
                            help_overlay_open = not help_overlay_open
                            continue
                        if (SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE
                                and game_modes_button.rect.collidepoint(mousepos)):
                            _reset_game_mode_sections()
                            game_modes_modal_open = True
                            pgn_games_modal_open = False
                            help_overlay_open = False
                            continue
                        if (SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE
                                and pgn_games_button.rect.collidepoint(mousepos)):
                            pgn_games_modal_open = True
                            game_modes_modal_open = False
                            help_overlay_open = False
                            continue
                        if scroll_up_button.rect.collidepoint(mousepos) and menu_buttons.PanelRectangles.scroll_range[0] > 1: # Scroll up
                            if scroll_up_button.activate:
                                PanelController.update_scroll_range(-1)
                        if scroll_down_button.rect.collidepoint(mousepos) and len(menu_buttons.MoveNumberRectangle.rectangle_list) > initvar.MOVES_PANE_MAX_MOVES and menu_buttons.PanelRectangles.scroll_range[1] < len(menu_buttons.MoveNumberRectangle.rectangle_list): # Scroll down
                            if scroll_down_button.activate:
                                PanelController.update_scroll_range(1)
                        if flip_board_button.rect.collidepoint(mousepos):
                            GridController.flip_grids()
                            if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                                game_controller.captured_pieces_flip(GridController.flipped)
                        if undo_move_button.rect.collidepoint(mousepos) and undo_move_button.clickable:
                            cancel_pending_cpu_move()
                            if CpuController.cpu_mode:
                                CpuController.cpu_mode_toggle()
                            MoveController.undo_move(game_controller)
                        hit_mode = game_mode_selector.hit(mousepos, SwitchModesController.GAME_MODE)
                        if hit_mode is not None:
                            cancel_pending_cpu_move()
                            if hit_mode == "cpu_white":
                                CpuController.cpu_mode = True
                                # Button labels describe the human player's side.
                                CpuController.cpu_color = "black"
                                CpuController.enemy_color = "white"
                            elif hit_mode == "cpu_black":
                                CpuController.cpu_mode = True
                                CpuController.cpu_color = "white"
                                CpuController.enemy_color = "black"
                            else:
                                CpuController.cpu_mode = False
                            # Auto-flip so the human is always at the bottom
                            new_flipped = CpuController.cpu_mode and CpuController.cpu_color == "white"
                            if GridController.flipped != new_flipped:
                                GridController.flip_grids()
                            _sync_cpu_turn_after_mode_change()
                        hit_turn = starting_turn_selector.hit(mousepos, SwitchModesController.GAME_MODE)
                        if hit_turn is not None:
                            pending_start_whoseturn = _normalize_starting_turn(hit_turn)
                        if beginning_move_button.rect.collidepoint(mousepos) and beginning_move_button.clickable:
                            cancel_pending_cpu_move()
                            MoveTracker.selected_move = 1, "white_move"
                            SwitchModesController.replayed_game(True, game_controller, True)
                            GridController.update_prior_move_color()
                            MoveTracker.selected_move = (0, "black_move")
                            PanelController.scroll_to_first_move()
                        if prev_move_button.rect.collidepoint(mousepos) and prev_move_button.clickable:
                            cancel_pending_cpu_move()
                            if MoveTracker.selected_move == (0, "black_move"):
                                pass
                            elif (MoveTracker.selected_move == (1, "black_move")
                                  and MoveTracker.df_moves.get(1, {}).get("white_move", "") == ""):
                                SwitchModesController.replayed_game(True, game_controller, True)
                                GridController.update_prior_move_color()
                                MoveTracker.selected_move = (0, "black_move")
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
                            cancel_pending_cpu_move()
                            if MoveTracker.selected_move[0] != MoveTracker.move_counter():
                                # When selected move is not at the last move number
                                if MoveTracker.selected_move[1] == "black_move":
                                    # When selected move is not at last move number and we are at black move
                                    next_move_number = MoveTracker.selected_move[0] + 1
                                    if (next_move_number == 1
                                            and MoveTracker.df_moves.get(1, {}).get("white_move", "") == ""
                                            and MoveTracker.df_moves.get(1, {}).get("black_move", "") != ""):
                                        MoveTracker.selected_move = (1, "black_move")
                                    else:
                                        MoveTracker.selected_move = (next_move_number, "white_move")
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
                            cancel_pending_cpu_move()
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
                            if reset_board_button.rect.collidepoint(mousepos) and reset_board_button.clickable:
                                pos_load_file(reset=True)
                                active_game_mode_key = None
                            if game_properties_button and game_properties_button.rect.collidepoint(mousepos) and game_properties_button.clickable:
                                _dim = pygame.Surface(lis.SCREEN.get_size(), pygame.SRCALPHA)
                                _dim.fill((0, 0, 0, 140))
                                lis.SCREEN.blit(_dim, (0, 0))
                                pygame.display.flip()
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
                        prior_edit_snapshot = None
                        if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                            prior_edit_snapshot = get_dict_rect_positions()
                        start_objects.Dragging.dragging_to_placed_no_dups(mouse_coord)
                        if prior_edit_snapshot is not None:
                            _clear_active_game_mode_if_edit_board_changed(prior_edit_snapshot)
                        if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                            if pending_cpu_move_at is not None:
                                continue
                            # Moves piece
                            prior_turn = game_controller.whoseturn
                            MoveController.complete_move(mouse_coord, game_controller)
                            # Selects piece
                            MoveController.select_piece_unselect_all_others(mouse_coord, game_controller)
                            if (prior_turn != game_controller.whoseturn and CpuController.cpu_mode
                                and game_controller.whoseturn == CpuController.cpu_color
                                and game_controller.result_abb == "*"):
                                schedule_cpu_move()
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
                            prior_edit_snapshot = get_dict_rect_positions()
                            EditModeController.right_click_destroy(mousepos)
                            _clear_active_game_mode_if_edit_board_changed(prior_edit_snapshot)
                    if event.type == pygame.MOUSEBUTTONUP: #Release Drag
                        if play_edit_switch_button.rect.collidepoint(mousepos):
                            if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE:
                                start_game()
                            elif SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                                stop_game()
                        if clear_button.rect.collidepoint(mousepos):
                            if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE: #Editing mode
                                start_objects.Start.restart_start_positions()
                                # REMOVE ALL SPRITES
                                placed_objects.remove_all_placed()
                                TextController.remove_check_checkmate_text()
                                active_game_mode_key = None

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
                if (pending_cpu_move_at is not None and SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE
                    and not SwitchModesController.REPLAYED):
                    if not CpuController.cpu_mode or game_controller.whoseturn != CpuController.cpu_color or game_controller.result_abb != "*":
                        cancel_pending_cpu_move()
                    elif pygame.time.get_ticks() >= pending_cpu_move_at:
                        CpuController.total_possible_moves_update()
                        if CpuController.total_possible_moves:
                            cpu_move = CpuController.choose_move()
                            cpu_grid = cpu_move[0]
                            cpu_piece = cpu_move[1]
                            cpu_piece.select = True
                            MoveController.complete_move(cpu_grid.coordinate, game_controller)
                        cancel_pending_cpu_move()
                #%% Test code below for debugging purposes

                # Set background
                lis.SCREEN.blit(lis.GAME_BACKGROUND, (0, 0))
                # Dark overlays: reduce background noise, make board and panel pop
                lis.SCREEN.blit(_sidebar_bg_overlay, (0, 0))
                lis.SCREEN.blit(_main_bg_overlay, (_shared_x, _shared_y))
                # Individual sprites update
                help_button.draw(lis.SCREEN)
                flip_board_button.draw(lis.SCREEN)
                if not initvar.ITCH_MODE:
                    file_actions_panel.draw(lis.SCREEN, mousepos, SwitchModesController.GAME_MODE)
                game_setup_state = (
                    "setup" if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE else "playing"
                )
                game_mode_selector.draw(lis.SCREEN, SwitchModesController.GAME_MODE, CpuController.cpu_mode, CpuController.cpu_color, mousepos)
                starting_turn_selector.draw(lis.SCREEN, SwitchModesController.GAME_MODE, pending_start_whoseturn, mousepos)
                play_edit_switch_button.draw(lis.SCREEN, game_setup_state, mousepos)
                features_panel.draw(lis.SCREEN)
                features_enabled = (SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE)
                game_modes_button.draw(lis.SCREEN, mousepos, enabled=features_enabled)
                pgn_games_button.draw(lis.SCREEN, mousepos, enabled=features_enabled)
                # Group sprites update
                menu_buttons.GAME_MODE_SPRITES.draw(lis.SCREEN)
                board.GRID_SPRITES.draw(lis.SCREEN)
                GridController.update_grid_occupied_detection()
                start_objects.START_SPRITES.update(SwitchModesController.GAME_MODE)
                menu_buttons.PLAY_PANEL_SPRITES.update(SwitchModesController.GAME_MODE)
                lis.SCREEN.blit(_rp_shadow, (_PANEL_RECT[0] - 2, _PANEL_RECT[1] + 4))
                lis.SCREEN.blit(_rp_surf,   (_PANEL_RECT[0],     _PANEL_RECT[1]))
                if SwitchModesController.GAME_MODE == SwitchModesController.EDIT_MODE: #Only draw placed sprites in editing mode
                    start_objects.START_SPRITES.draw(lis.SCREEN)
                    if initvar.ITCH_MODE and start_objects.Dragging.drag_piece_name:
                        _sel = start_objects.Start.start_dict[start_objects.Dragging.drag_piece_name]
                        _sel_pos = initvar.STARTPOS[start_objects.Dragging.drag_piece_name]
                        _sel_w, _sel_h = _sel.image.get_size()
                        pygame.draw.rect(lis.SCREEN, (255, 215, 0),
                                         (_sel_pos[0], _sel_pos[1], _sel_w, _sel_h), 3)
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
                # Board Coordinates Drawing
                for text in range(0,len(TextController.coor_letter_text_list)):
                    lis.SCREEN.blit(TextController.coor_letter_text_list[text], (initvar.X_GRID_START+board.X_GRID_WIDTH/3+(board.X_GRID_WIDTH*text), initvar.Y_GRID_START-(board.Y_GRID_HEIGHT*0.75)))
                    lis.SCREEN.blit(TextController.coor_letter_text_list[text], (initvar.X_GRID_START+board.X_GRID_WIDTH/3+(board.X_GRID_WIDTH*text), board.Y_GRID_END+(board.Y_GRID_HEIGHT*0.25)))
                for text in range(0,len(TextController.coor_number_text_list)):
                    lis.SCREEN.blit(TextController.coor_number_text_list[text], (initvar.X_GRID_START-board.X_GRID_WIDTH/2, initvar.Y_GRID_START+board.Y_GRID_HEIGHT/4+(board.Y_GRID_HEIGHT*text)))
                    lis.SCREEN.blit(TextController.coor_number_text_list[text], (board.X_GRID_END+board.X_GRID_WIDTH/3, initvar.Y_GRID_START+board.Y_GRID_HEIGHT/4+(board.Y_GRID_HEIGHT*text)))
                current_turn_text = ""
                status_detail_text = TextController.check_checkmate_text
                if SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                    if game_controller.whoseturn == "white" and game_controller.result_abb == "*":
                        current_turn_text = "White to move"
                    elif game_controller.whoseturn == "black" and game_controller.result_abb == "*":
                        current_turn_text = "Black to move"
                else:
                    current_turn_text = "White to move" if pending_start_whoseturn == "white" else "Black to move"
                    if CpuController.cpu_mode:
                        if pending_start_whoseturn == CpuController.cpu_color:
                            status_detail_text = "CPU will move first"
                        else:
                            status_detail_text = "Player moves first"
                    else:
                        status_detail_text = "Player moves first"
                _draw_panel_status(current_turn_text, status_detail_text)
                _player_badge_hover_info.clear()
                # Use "CPU" / "Player" as fallback when the name hasn't been set in Game
                # Properties; never override a name the user has explicitly entered.
                _white_is_cpu = CpuController.cpu_mode and CpuController.cpu_color == "white"
                _black_is_cpu = CpuController.cpu_mode and CpuController.cpu_color == "black"
                _white_name = GameProperties.White or ("CPU" if _white_is_cpu else "Player")
                _black_name = GameProperties.Black or ("CPU" if _black_is_cpu else "Player")
                if GridController.flipped:
                    _draw_player_identity(_white_name, GameProperties.WhiteElo, "top")
                    _draw_player_identity(_black_name, GameProperties.BlackElo, "bottom")
                else:
                    _draw_player_identity(_black_name, GameProperties.BlackElo, "top")
                    _draw_player_identity(_white_name, GameProperties.WhiteElo, "bottom")
                _draw_active_game_mode_title()
                for _badge_rect, _full_name in _player_badge_hover_info:
                    if _badge_rect.collidepoint(mousepos):
                        _draw_tooltip(_full_name, mousepos)
                        break
                else:
                    if help_button.rect.collidepoint(mousepos):
                        _draw_tooltip("Help", mousepos)
                    elif flip_board_button.rect.collidepoint(mousepos):
                        _draw_tooltip("Flip Board", mousepos)
                    elif game_properties_button and game_properties_button.rect.collidepoint(mousepos):
                        _draw_tooltip("Game Info", mousepos)
                    elif SwitchModesController.GAME_MODE == SwitchModesController.PLAY_MODE:
                        for button, label in replay_button_tooltips:
                            if button.rect.collidepoint(mousepos):
                                _draw_tooltip(label, mousepos)
                                break
                _draw_help_hint()
                if help_overlay_open:
                    help_panel_rect = _draw_help_overlay()
                if save_position_modal_open:
                    _draw_save_position_modal()
                if game_modes_modal_open:
                    _draw_game_modes_modal()
                if pgn_games_modal_open:
                    _draw_pgn_games_modal()
                elif initvar.ITCH_MODE:
                    _draw_itch_notice()
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
