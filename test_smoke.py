"""
Smoke tests for the Chess codebase.

Run with:  python test_smoke.py
No display required — uses the SDL dummy video driver.
"""
import os
import sys

# Must be set BEFORE any pygame import
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["HEADLESS_TEST"] = "1"

# Ensure cwd is the project directory so sprite/image paths resolve
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()

# Now import game modules (they import pygame internally)
import initvar
import board
import play_objects
import placed_objects
import menu_buttons
import main
import gc

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PASSED = 0
FAILED = 0


def check(condition, name):
    global PASSED, FAILED
    if condition:
        print(f"  PASS: {name}")
        PASSED += 1
    else:
        print(f"  FAIL: {name}")
        FAILED += 1


class MockButton:
    """Minimal stand-in for PlayEditSwitchButton."""
    image = None

    def game_mode_button(self, mode):
        return None


_font = None


def _get_font():
    global _font
    if _font is None:
        _font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME,
                                    initvar.MOVE_NOTATION_FONT_SIZE)
    return _font


def make_move(from_coord, to_coord, game_controller):
    """
    Move the piece at from_coord to to_coord, record it, and update the
    move panel so that undo works correctly.
    Returns (prior_moves_dict, captured_abb, special_abb, promoted_queen).
    """
    grid = board.Grid.grid_dict[to_coord]
    piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(from_coord)
    assert piece is not None, f"No piece found at {from_coord}"

    result = main.MoveController.make_move(grid, piece, game_controller)
    prior_moves_dict, captured_abb, special_abb, promoted_queen = result

    check_abb = main.MoveController.game_status_check(game_controller)
    main.MoveController.record_move(
        game_controller, grid, piece,
        prior_moves_dict, captured_abb, special_abb, check_abb, promoted_queen
    )
    # Build the panel rectangles so that undo can remove them later
    main.PanelController.draw_move_rects_on_moves_pane(_get_font())
    return result


def _reset_state():
    """
    Kill all live play sprites, clear class-level piece lists, reset the
    move panel, board-square state, and mode flags.  Does NOT load any
    piece positions — callers do that themselves.
    """
    for spr_list in play_objects.Piece_Lists_Shortcut.all_pieces():
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
    # Reset move-panel bookkeeping
    for spr_list in [menu_buttons.MoveNumberRectangle.rectangle_list,
                     menu_buttons.PieceMoveRectangle.rectangle_list]:
        for obj in spr_list:
            obj.kill()
    menu_buttons.MoveNumberRectangle.rectangle_list = []
    menu_buttons.PieceMoveRectangle.rectangle_list = []
    menu_buttons.MoveNumberRectangle.rectangle_dict = {}
    menu_buttons.PieceMoveRectangle.rectangle_dict = {}
    menu_buttons.PanelRectangles.scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
    # Reset per-square state
    for grid in board.Grid.grid_list:
        grid.reset_play_interaction_vars()
    # Reset mode/replay flags
    main.SwitchModesController.GAME_MODE = main.SwitchModesController.EDIT_MODE
    main.SwitchModesController.REPLAYED = False
    main.TextController.check_checkmate_text = ""
    gc.collect()


def setup_game():
    """
    Return a fresh GameController with pieces in the default starting position.
    Mirrors what GameController.__del__ does so that calling setup_game()
    multiple times in one process works correctly.
    """
    _reset_state()
    mock_button = MockButton()
    # Load default piece positions (placed pieces)
    main.pos_load_file(reset=True)
    # Convert placed → play pieces and restart move tracking
    main.SwitchModesController.switch_mode(
        main.SwitchModesController.PLAY_MODE, mock_button
    )
    game_ctrl = main.GameController(main.GridController.flipped)
    game_ctrl.refresh_objects()
    return game_ctrl


def setup_custom_game(position_dict):
    """
    Return a fresh GameController with a custom board position.

    position_dict uses the same key schema as pos_load_file:
        {'white_pawn': ['e2', ...], 'white_king': ['e1'], 'black_king': ['e8'], ...}
    Any piece type omitted from the dict defaults to an empty list.
    Both kings must be present for the engine to function correctly.
    """
    _reset_state()
    placed_objects.remove_all_placed()

    piece_map = {
        'white_pawn':   (placed_objects.PlacedPawn,   "white"),
        'white_bishop': (placed_objects.PlacedBishop, "white"),
        'white_knight': (placed_objects.PlacedKnight, "white"),
        'white_rook':   (placed_objects.PlacedRook,   "white"),
        'white_queen':  (placed_objects.PlacedQueen,  "white"),
        'white_king':   (placed_objects.PlacedKing,   "white"),
        'black_pawn':   (placed_objects.PlacedPawn,   "black"),
        'black_bishop': (placed_objects.PlacedBishop, "black"),
        'black_knight': (placed_objects.PlacedKnight, "black"),
        'black_rook':   (placed_objects.PlacedRook,   "black"),
        'black_queen':  (placed_objects.PlacedQueen,  "black"),
        'black_king':   (placed_objects.PlacedKing,   "black"),
    }
    for key, (cls, color) in piece_map.items():
        for coord in position_dict.get(key, []):
            cls(coord, color)

    mock_button = MockButton()
    main.SwitchModesController.switch_mode(
        main.SwitchModesController.PLAY_MODE, mock_button
    )
    game_ctrl = main.GameController(main.GridController.flipped)
    game_ctrl.refresh_objects()
    return game_ctrl


# ---------------------------------------------------------------------------
# Test 1: Import and initialization
# ---------------------------------------------------------------------------
print("=== Chess Smoke Tests ===\n")
print("Test 1: Import and initialization")
check(True, "All modules imported without error")
check(len(board.Grid.grid_list) == 64, "Board has 64 squares")
check("e4" in board.Grid.grid_dict, "Grid dict contains e4")

# ---------------------------------------------------------------------------
# Test 2: Default position setup
# ---------------------------------------------------------------------------
print("\nTest 2: Default position setup")
main.pos_load_file(reset=True)
check(len(placed_objects.PlacedPawn.white_pawn_list) == 8, "8 white pawns placed")
check(len(placed_objects.PlacedPawn.black_pawn_list) == 8, "8 black pawns placed")
check(len(placed_objects.PlacedKing.white_king_list) == 1, "1 white king placed")
check(len(placed_objects.PlacedKing.black_king_list) == 1, "1 black king placed")

# ---------------------------------------------------------------------------
# Test 3: Switch to play mode
# ---------------------------------------------------------------------------
print("\nTest 3: Switch to play mode")
game_controller = setup_game()
check(
    main.SwitchModesController.GAME_MODE == main.SwitchModesController.PLAY_MODE,
    "GAME_MODE is PLAY_MODE"
)
check(len(play_objects.PlayPawn.white_pawn_list) == 8, "8 white play pawns")
check(len(play_objects.PlayPawn.black_pawn_list) == 8, "8 black play pawns")
check(len(play_objects.PlayKing.white_king_list) == 1, "1 white play king")
check(main.MoveTracker.move_counter() == 0, "Move counter starts at 0")

# ---------------------------------------------------------------------------
# Test 4: Basic moves  e2-e4, e7-e5
# ---------------------------------------------------------------------------
print("\nTest 4: Basic moves (e2-e4, e7-e5)")
make_move("e2", "e4", game_controller)
check(main.MoveTracker.move_counter() == 1, "Move counter = 1 after white's first move")
check(game_controller.whoseturn == "black", "Black's turn after white moves")
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is not None,
    "White pawn arrived at e4"
)

make_move("e7", "e5", game_controller)
check(main.MoveTracker.move_counter() == 1, "Move counter still 1 after both sides move")
check(game_controller.whoseturn == "white", "White's turn after black moves")
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is not None,
    "Black pawn arrived at e5"
)

# ---------------------------------------------------------------------------
# Test 5: Undo moves
# ---------------------------------------------------------------------------
print("\nTest 5: Undo moves")
main.MoveController.undo_move(game_controller)   # undo black's e7-e5
check(game_controller.whoseturn == "black", "After undo: black's turn")
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e7") is not None,
    "Black pawn restored to e7"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is None,
    "e5 is empty after undo"
)

main.MoveController.undo_move(game_controller)   # undo white's e2-e4
check(game_controller.whoseturn == "white", "After second undo: white's turn")
check(main.MoveTracker.move_counter() == 0, "Move counter back to 0")
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e2") is not None,
    "White pawn restored to e2"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is None,
    "e4 is empty after undo"
)

# ---------------------------------------------------------------------------
# Test 6: En passant capture
# ---------------------------------------------------------------------------
print("\nTest 6: En passant")
# e2-e4, a7-a6, e4-e5, d7-d5  → e5xd6 e.p.
make_move("e2", "e4", game_controller)
make_move("a7", "a6", game_controller)
make_move("e4", "e5", game_controller)
make_move("d7", "d5", game_controller)   # en passant set-up

check(
    board.Grid.grid_dict["d6"].en_passant_skipover,
    "d6 flagged as en passant square after d7-d5"
)

make_move("e5", "d6", game_controller)   # en passant capture

check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d5") is None,
    "Black pawn at d5 captured by en passant"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d6") is not None,
    "White pawn moved to d6 via en passant"
)

# ---------------------------------------------------------------------------
# Test 7: En passant undo
# ---------------------------------------------------------------------------
print("\nTest 7: En passant undo")
main.MoveController.undo_move(game_controller)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d5") is not None,
    "Black pawn restored to d5 after en passant undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is not None,
    "White pawn restored to e5 after en passant undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d6") is None,
    "d6 is empty after en passant undo"
)

# ---------------------------------------------------------------------------
# Test 8: Kingside castling
# ---------------------------------------------------------------------------
print("\nTest 8: Kingside castle (white)")
# Need to clear e1-g1 (knight on g1 and bishop on f1) for white kingside castle.
# Play enough moves to clear the path: Nf3, Bc4 (or just set up via PGN-style).
# Simplest: undo everything back to start, then play: e2-e4, e7-e5, Ng1-f3, Nb8-c6, Bf1-c4, Bf8-c5, e1-g1
game_controller2 = setup_game()
make_move("e2", "e4", game_controller2)
make_move("e7", "e5", game_controller2)
make_move("g1", "f3", game_controller2)   # white knight f3
make_move("b8", "c6", game_controller2)   # black knight c6
make_move("f1", "c4", game_controller2)   # white bishop c4
make_move("f8", "c5", game_controller2)   # black bishop c5
# f1 and g1 are clear; white king on e1 can castle kingside
make_move("e1", "g1", game_controller2)   # white kingside castle

check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("g1") is not None,
    "White king arrived at g1"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("f1") is not None,
    "White rook moved to f1 after kingside castle"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is None,
    "e1 is empty after castle"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("h1") is None,
    "h1 rook moved away after castle"
)

# ---------------------------------------------------------------------------
# Test 9: Castling undo
# ---------------------------------------------------------------------------
print("\nTest 9: Kingside castle undo")
main.MoveController.undo_move(game_controller2)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is not None,
    "White king restored to e1 after castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("h1") is not None,
    "White rook restored to h1 after castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("g1") is None,
    "g1 empty after castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("f1") is None,
    "f1 empty after castle undo"
)

# ---------------------------------------------------------------------------
# Test 10: Pawn capture
# ---------------------------------------------------------------------------
print("\nTest 10: Pawn capture (e4xd5)")
game_controller3 = setup_game()
make_move("e2", "e4", game_controller3)
make_move("d7", "d5", game_controller3)
make_move("e4", "d5", game_controller3)   # white pawn captures black pawn

captured_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord("d5")
check(
    captured_piece is not None and captured_piece.color == "white",
    "White pawn on d5 after capture"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is None,
    "e4 empty after white pawn advances"
)
live_black_pawns = [p for p in play_objects.PlayPawn.black_pawn_list
                    if not p.taken_off_board]
check(len(live_black_pawns) == 7, "7 black pawns remain after capture")

# ---------------------------------------------------------------------------
# Test 11: Queenside castling (white)
# ---------------------------------------------------------------------------
print("\nTest 11: Queenside castle (white)")
# Clear b1 (knight), c1 (bishop), d1 (queen) so the a1 rook can castle.
# Sequence: d4, d5, Bc1-f4, e6, Nb1-c3, Nf6, Qd1-d2, h6, O-O-O
game_controller4 = setup_game()
make_move("d2", "d4", game_controller4)   # open diagonal for c1 bishop
make_move("d7", "d5", game_controller4)
make_move("c1", "f4", game_controller4)   # Bc1-f4: clears c1
make_move("e7", "e6", game_controller4)
make_move("b1", "c3", game_controller4)   # Nb1-c3: clears b1
make_move("g8", "f6", game_controller4)
make_move("d1", "d2", game_controller4)   # Qd1-d2: clears d1
make_move("h7", "h6", game_controller4)
make_move("e1", "c1", game_controller4)   # white queenside castle

check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("c1") is not None,
    "White king arrived at c1 after queenside castle"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d1") is not None,
    "White rook moved to d1 after queenside castle"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is None,
    "e1 empty after queenside castle"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a1") is None,
    "a1 rook moved away after queenside castle"
)

# ---------------------------------------------------------------------------
# Test 12: Queenside castling undo
# ---------------------------------------------------------------------------
print("\nTest 12: Queenside castle undo")
main.MoveController.undo_move(game_controller4)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is not None,
    "White king restored to e1 after queenside castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a1") is not None,
    "White rook restored to a1 after queenside castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("c1") is None,
    "c1 empty after queenside castle undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("d1") is None,
    "d1 empty after queenside castle undo"
)

# ---------------------------------------------------------------------------
# Test 13: Checkmate detection — Fool's Mate
# ---------------------------------------------------------------------------
print("\nTest 13: Checkmate detection (Fool's Mate)")
# f2-f3, e7-e5, g2-g4, Qd8-h4# (black queen checkmates white)
game_controller5 = setup_game()
make_move("f2", "f3", game_controller5)
make_move("e7", "e5", game_controller5)
make_move("g2", "g4", game_controller5)
make_move("d8", "h4", game_controller5)   # Fool's Mate

check(
    game_controller5.result_abb == "0-1",
    "Result is 0-1 after Fool's Mate"
)
check(
    main.TextController.check_checkmate_text == "Black wins",
    "Check/mate text shows 'Black wins' after Fool's Mate"
)
check(
    game_controller5.color_in_check == "white",
    "White king flagged in check after Fool's Mate"
)

# ---------------------------------------------------------------------------
# Test 14: Pawn promotion to queen
# ---------------------------------------------------------------------------
print("\nTest 14: Pawn promotion to queen")
# Custom position: white pawn one step from promotion, both kings safely apart.
# white_king at c1, white_pawn at a7, black_king at h6 (out of queen's reach)
game_controller6 = setup_custom_game({
    'white_pawn':  ['a7'],
    'white_king':  ['c1'],
    'black_king':  ['h6'],
})
_, _, special_abb, promoted_queen = make_move("a7", "a8", game_controller6)

check(special_abb == "=Q", "Promotion flagged as =Q")
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a7") is None,
    "a7 empty after pawn promotion"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a8") is not None,
    "a8 occupied by promoted queen"
)
check(
    len(play_objects.PlayQueen.white_queen_list) == 1,
    "White queen list has 1 entry after promotion"
)

# ---------------------------------------------------------------------------
# Test 15: Pawn promotion undo
# ---------------------------------------------------------------------------
print("\nTest 15: Pawn promotion undo")
main.MoveController.undo_move(game_controller6)

check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a7") is not None,
    "White pawn restored to a7 after promotion undo"
)
check(
    play_objects.Piece_Lists_Shortcut.piece_on_coord("a8") is None,
    "a8 empty after promotion undo"
)
check(
    len(play_objects.PlayQueen.white_queen_list) == 0,
    "White queen list empty after promotion undo"
)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print(f"\n=== Results: {PASSED} passed, {FAILED} failed ===")
if FAILED > 0:
    sys.exit(1)
