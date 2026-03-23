"""
Visual smoke test — all 60 checks from test_smoke.py, shown live on the board.

Run with:  python visual_test.py
Press Q or close the window to quit at any time.
"""
import os, sys, time
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import pygame

import initvar
import load_images_sounds as lis
import board
import play_objects
import placed_objects
import menu_buttons
import main
import gc

MOVE_DELAY  = 0.7   # seconds to hold after a move
CHECK_PAUSE = 0.9   # seconds to show each check result
LABEL_PAUSE = 1.2   # seconds to show a section heading

# ── check tracking ────────────────────────────────────────────────────────────
PASSED = 0
FAILED = 0
_last_check_text  = ""
_last_check_ok    = True


def check(condition, name):
    global PASSED, FAILED, _last_check_text, _last_check_ok
    _last_check_text = name
    _last_check_ok   = bool(condition)
    if condition:
        PASSED += 1
        print(f"  PASS: {name}")
    else:
        FAILED += 1
        print(f"  FAIL: {name}")


# ── rendering ─────────────────────────────────────────────────────────────────
def draw(title="", description="", game_controller=None, show_check=False):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.quit(); sys.exit()

    lis.SCREEN.blit(lis.GAME_BACKGROUND, (0, 0))
    board.GRID_SPRITES.draw(lis.SCREEN)
    main.GridController.update_grid_occupied_detection()
    lis.SCREEN.blit(lis.MOVE_BG_IMAGE, (initvar.MOVE_BG_IMAGE_X, initvar.MOVE_BG_IMAGE_Y))
    if main.SwitchModesController.GAME_MODE == main.SwitchModesController.EDIT_MODE:
        placed_objects.PLACED_SPRITES.update()
        placed_objects.PLACED_SPRITES.draw(lis.SCREEN)
    else:
        play_objects.PLAY_SPRITES.update()
        play_objects.PLAY_SPRITES.draw(lis.SCREEN)

    font_big  = main.TextController.universal_font
    font_sm   = main.TextController.move_notation_font

    # Board coordinate letters / numbers
    for i, t in enumerate(main.TextController.coor_letter_text_list):
        lis.SCREEN.blit(t, (initvar.X_GRID_START + board.X_GRID_WIDTH/3 + board.X_GRID_WIDTH*i,
                            initvar.Y_GRID_START - board.Y_GRID_HEIGHT*0.75))
    for i, t in enumerate(main.TextController.coor_number_text_list):
        lis.SCREEN.blit(t, (initvar.X_GRID_START - board.X_GRID_WIDTH/2,
                            initvar.Y_GRID_START + board.Y_GRID_HEIGHT/4 + board.Y_GRID_HEIGHT*i))

    # Whose-turn / check text
    if game_controller:
        if game_controller.result_abb == "*":
            turn_txt = ("White's move" if game_controller.whoseturn == "white"
                        else "Black's move")
            lis.SCREEN.blit(font_big.render(turn_txt, True, initvar.UNIVERSAL_TEXT_COLOR),
                            initvar.WHITE_MOVE_X_Y)
        if main.TextController.check_checkmate_text:
            lis.SCREEN.blit(
                font_big.render(main.TextController.check_checkmate_text,
                                True, initvar.UNIVERSAL_TEXT_COLOR),
                initvar.CHECK_CHECKMATE_X_Y)

    # ── top: yellow test-group title ──────────────────────────────────────────
    if title:
        lis.SCREEN.blit(font_big.render(title, True, (255, 220, 50)), (initvar.X_GRID_START, 10))

    # ── bottom area: description + check result + running tally ───────────────
    bottom_y = board.Y_GRID_END + 20

    if description:
        lis.SCREEN.blit(font_big.render(description, True, (200, 200, 200)),
                        (initvar.X_GRID_START, bottom_y))

    if show_check:
        color  = (80, 220, 80) if _last_check_ok else (220, 80, 80)
        prefix = "PASS" if _last_check_ok else "FAIL"
        lis.SCREEN.blit(font_sm.render(f"{prefix}: {_last_check_text}", True, color),
                        (initvar.X_GRID_START, bottom_y + 36))

    tally_color = (80, 220, 80) if FAILED == 0 else (220, 80, 80)
    lis.SCREEN.blit(font_sm.render(f"Checks: {PASSED} passed  {FAILED} failed",
                                   True, tally_color),
                    (initvar.X_GRID_START, bottom_y + 60))

    pygame.display.update()


def pause(seconds, title="", game_controller=None, description="", show_check=False):
    end = time.time() + seconds
    while time.time() < end:
        draw(title, description, game_controller, show_check)
        pygame.time.wait(30)


def show_check(title, description, game_controller=None):
    """Flash the last check result on screen for CHECK_PAUSE seconds."""
    pause(CHECK_PAUSE, title, game_controller, description, show_check=True)


# ── game helpers ──────────────────────────────────────────────────────────────
_panel_font = None
def _get_font():
    global _panel_font
    if _panel_font is None:
        _panel_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME,
                                          initvar.MOVE_NOTATION_FONT_SIZE)
    return _panel_font


def make_move(from_coord, to_coord, game_controller, title="", description=""):
    grid  = board.Grid.grid_dict[to_coord]
    piece = play_objects.Piece_Lists_Shortcut.piece_on_coord(from_coord)
    assert piece is not None, f"No piece at {from_coord}"
    result    = main.MoveController.make_move(grid, piece, game_controller)
    check_abb = main.MoveController.game_status_check(game_controller)
    main.MoveController.record_move(game_controller, grid, piece,
                                    result[0], result[1], result[2], check_abb, result[3])
    main.PanelController.draw_move_rects_on_moves_pane(_get_font())
    pause(MOVE_DELAY, title, game_controller, description)
    return result


def _reset_state():
    """Kill all live play sprites, clear class-level lists, reset board and mode."""
    for spr_list in play_objects.Piece_Lists_Shortcut.all_pieces():
        for obj in spr_list: obj.kill()
    play_objects.PlayPawn.white_pawn_list    = []
    play_objects.PlayBishop.white_bishop_list = []
    play_objects.PlayKnight.white_knight_list = []
    play_objects.PlayRook.white_rook_list     = []
    play_objects.PlayQueen.white_queen_list   = []
    play_objects.PlayKing.white_king_list     = []
    play_objects.PlayPawn.black_pawn_list    = []
    play_objects.PlayBishop.black_bishop_list = []
    play_objects.PlayKnight.black_knight_list = []
    play_objects.PlayRook.black_rook_list     = []
    play_objects.PlayQueen.black_queen_list   = []
    play_objects.PlayKing.black_king_list     = []
    for spr_list in [menu_buttons.MoveNumberRectangle.rectangle_list,
                     menu_buttons.PieceMoveRectangle.rectangle_list]:
        for obj in spr_list: obj.kill()
    menu_buttons.MoveNumberRectangle.rectangle_list  = []
    menu_buttons.PieceMoveRectangle.rectangle_list   = []
    menu_buttons.MoveNumberRectangle.rectangle_dict  = {}
    menu_buttons.PieceMoveRectangle.rectangle_dict   = {}
    menu_buttons.PanelRectangles.scroll_range        = [1, initvar.MOVES_PANE_MAX_MOVES]
    for g in board.Grid.grid_list: g.reset_play_interaction_vars()
    main.SwitchModesController.GAME_MODE  = main.SwitchModesController.EDIT_MODE
    main.SwitchModesController.REPLAYED   = False
    main.TextController.check_checkmate_text = ""
    gc.collect()


def setup_game():
    """Fresh GameController with the standard starting position."""
    _reset_state()

    class _Btn:
        image = None
        def game_mode_button(self, mode): return None

    main.pos_load_file(reset=True)
    main.SwitchModesController.switch_mode(main.SwitchModesController.PLAY_MODE, _Btn())
    gc_ = main.GameController(main.GridController.flipped)
    gc_.refresh_objects()
    return gc_


def setup_custom_game(position_dict):
    """
    Fresh GameController with a custom board position.
    position_dict keys: 'white_pawn', 'white_bishop', 'white_knight', 'white_rook',
                        'white_queen', 'white_king', 'black_pawn', 'black_bishop',
                        'black_knight', 'black_rook', 'black_queen', 'black_king'.
    Each value is a list of coordinate strings.  Omitted keys default to [].
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

    class _Btn:
        image = None
        def game_mode_button(self, mode): return None

    main.SwitchModesController.switch_mode(main.SwitchModesController.PLAY_MODE, _Btn())
    gc_ = main.GameController(main.GridController.flipped)
    gc_.refresh_objects()
    return gc_


# ── window setup ──────────────────────────────────────────────────────────────
pygame.display.set_caption("Chess — Visual Smoke Test (60 checks)")
pygame.display.set_icon(pygame.image.load("sprites/chessico.png"))


# ════════════════════════════════════════════════════════════════════════════
# TEST 1 — Import and initialization  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 1: Import & initialization"
print(f"\n{T}")
pause(LABEL_PAUSE, T, description="Verifying modules loaded and board is ready")

check(True, "All modules imported without error")
show_check(T, "All modules imported without error")

check(len(board.Grid.grid_list) == 64, "Board has 64 squares")
show_check(T, f"Board has {len(board.Grid.grid_list)} squares (expected 64)")

check("e4" in board.Grid.grid_dict, "Grid dict contains e4")
show_check(T, "Grid dict contains e4")

# ════════════════════════════════════════════════════════════════════════════
# TEST 2 — Default position setup  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 2: Default position setup"
print(f"\n{T}")
main.pos_load_file(reset=True)          # puts placed pieces on the board
main.SwitchModesController.GAME_MODE = main.SwitchModesController.EDIT_MODE
pause(LABEL_PAUSE, T, description="Placed pieces loaded — counting pawns and kings")

check(len(placed_objects.PlacedPawn.white_pawn_list) == 8, "8 white pawns placed")
show_check(T, f"White pawns: {len(placed_objects.PlacedPawn.white_pawn_list)} (expected 8)")

check(len(placed_objects.PlacedPawn.black_pawn_list) == 8, "8 black pawns placed")
show_check(T, f"Black pawns: {len(placed_objects.PlacedPawn.black_pawn_list)} (expected 8)")

check(len(placed_objects.PlacedKing.white_king_list) == 1, "1 white king placed")
show_check(T, f"White kings: {len(placed_objects.PlacedKing.white_king_list)} (expected 1)")

check(len(placed_objects.PlacedKing.black_king_list) == 1, "1 black king placed")
show_check(T, f"Black kings: {len(placed_objects.PlacedKing.black_king_list)} (expected 1)")

# ════════════════════════════════════════════════════════════════════════════
# TEST 3 — Switch to play mode  (5 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 3: Switch to play mode"
print(f"\n{T}")
gc1 = setup_game()
pause(LABEL_PAUSE, T, gc1, "Placed pieces converted to play pieces")

check(main.SwitchModesController.GAME_MODE == main.SwitchModesController.PLAY_MODE,
      "GAME_MODE is PLAY_MODE")
show_check(T, "GAME_MODE switched to PLAY_MODE", gc1)

check(len(play_objects.PlayPawn.white_pawn_list) == 8, "8 white play pawns")
show_check(T, f"White play pawns: {len(play_objects.PlayPawn.white_pawn_list)} (expected 8)", gc1)

check(len(play_objects.PlayPawn.black_pawn_list) == 8, "8 black play pawns")
show_check(T, f"Black play pawns: {len(play_objects.PlayPawn.black_pawn_list)} (expected 8)", gc1)

check(len(play_objects.PlayKing.white_king_list) == 1, "1 white play king")
show_check(T, f"White play kings: {len(play_objects.PlayKing.white_king_list)} (expected 1)", gc1)

check(main.MoveTracker.move_counter() == 0, "Move counter starts at 0")
show_check(T, f"Move counter: {main.MoveTracker.move_counter()} (expected 0)", gc1)

# ════════════════════════════════════════════════════════════════════════════
# TEST 4 — Basic moves e2-e4, e7-e5  (6 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 4: Basic moves  e2→e4, e7→e5"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc1, "White plays e2→e4 …")

make_move("e2", "e4", gc1, T, "White: e2 → e4")

check(main.MoveTracker.move_counter() == 1, "Move counter = 1 after white's move")
show_check(T, f"Move counter: {main.MoveTracker.move_counter()} (expected 1)", gc1)

check(gc1.whoseturn == "black", "Black's turn after white moves")
show_check(T, f"Whose turn: {gc1.whoseturn} (expected black)", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is not None,
      "White pawn arrived at e4")
show_check(T, "White pawn is on e4", gc1)

make_move("e7", "e5", gc1, T, "Black: e7 → e5")

check(main.MoveTracker.move_counter() == 1,
      "Move counter still 1 after both sides move")
show_check(T, f"Move counter: {main.MoveTracker.move_counter()} (expected 1)", gc1)

check(gc1.whoseturn == "white", "White's turn after black moves")
show_check(T, f"Whose turn: {gc1.whoseturn} (expected white)", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is not None,
      "Black pawn arrived at e5")
show_check(T, "Black pawn is on e5", gc1)

# ════════════════════════════════════════════════════════════════════════════
# TEST 5 — Undo both moves  (7 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 5: Undo both moves"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc1, "Undoing black's move first …")

main.MoveController.undo_move(gc1)
pause(MOVE_DELAY, T, gc1, "Black's e5 pawn undone")

check(gc1.whoseturn == "black", "After undo: black's turn")
show_check(T, f"Whose turn: {gc1.whoseturn} (expected black)", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e7") is not None,
      "Black pawn restored to e7")
show_check(T, "Black pawn is back on e7", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is None,
      "e5 is empty after undo")
show_check(T, "e5 is now empty", gc1)

pause(0.4, T, gc1, "Now undoing white's move …")
main.MoveController.undo_move(gc1)
pause(MOVE_DELAY, T, gc1, "White's e4 pawn undone")

check(gc1.whoseturn == "white", "After second undo: white's turn")
show_check(T, f"Whose turn: {gc1.whoseturn} (expected white)", gc1)

check(main.MoveTracker.move_counter() == 0, "Move counter back to 0")
show_check(T, f"Move counter: {main.MoveTracker.move_counter()} (expected 0)", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e2") is not None,
      "White pawn restored to e2")
show_check(T, "White pawn is back on e2", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is None,
      "e4 is empty after undo")
show_check(T, "e4 is now empty", gc1)

# ════════════════════════════════════════════════════════════════════════════
# TEST 6 — En passant capture  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 6: En passant capture"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc1, "Setting up: e2→e4, a7→a6, e4→e5, d7→d5")
make_move("e2", "e4", gc1, T, "White: e2 → e4")
make_move("a7", "a6", gc1, T, "Black: a7 → a6  (neutral)")
make_move("e4", "e5", gc1, T, "White: e4 → e5")
make_move("d7", "d5", gc1, T, "Black: d7 → d5  (en passant now possible!)")

check(board.Grid.grid_dict["d6"].en_passant_skipover,
      "d6 flagged as en passant square after d7-d5")
show_check(T, "d6 is the en passant square", gc1)

make_move("e5", "d6", gc1, T, "White: e5 × d6  (en passant — d5 pawn vanishes!)")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d5") is None,
      "Black pawn at d5 captured by en passant")
show_check(T, "Black pawn on d5 is gone", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d6") is not None,
      "White pawn moved to d6 via en passant")
show_check(T, "White pawn is on d6", gc1)

# ════════════════════════════════════════════════════════════════════════════
# TEST 7 — En passant undo  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 7: En passant undo"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc1, "Undoing the en passant — captured pawn should reappear")
main.MoveController.undo_move(gc1)
pause(MOVE_DELAY, T, gc1, "En passant reversed")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d5") is not None,
      "Black pawn restored to d5 after en passant undo")
show_check(T, "Black pawn restored to d5", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e5") is not None,
      "White pawn restored to e5 after en passant undo")
show_check(T, "White pawn restored to e5", gc1)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d6") is None,
      "d6 is empty after en passant undo")
show_check(T, "d6 is empty", gc1)

# ════════════════════════════════════════════════════════════════════════════
# TEST 8 — Kingside castling  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 8: Kingside castle"
print(f"\n{T}")
gc2 = setup_game()
pause(LABEL_PAUSE, T, gc2, "Opening to clear f1 and g1, then O-O")
make_move("e2", "e4", gc2, T, "White: e2 → e4")
make_move("e7", "e5", gc2, T, "Black: e7 → e5")
make_move("g1", "f3", gc2, T, "White: Ng1 → f3  (clearing g1)")
make_move("b8", "c6", gc2, T, "Black: Nb8 → c6")
make_move("f1", "c4", gc2, T, "White: Bf1 → c4  (clearing f1)")
make_move("f8", "c5", gc2, T, "Black: Bf8 → c5")
pause(LABEL_PAUSE, T, gc2, "f1 and g1 clear — castling!")
make_move("e1", "g1", gc2, T, "White: O-O  (king→g1, rook→f1)")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("g1") is not None,
      "White king arrived at g1")
show_check(T, "King is on g1", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("f1") is not None,
      "White rook moved to f1 after kingside castle")
show_check(T, "Rook is on f1", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is None,
      "e1 is empty after castle")
show_check(T, "e1 is empty", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("h1") is None,
      "h1 rook moved away after castle")
show_check(T, "h1 is empty", gc2)

# ════════════════════════════════════════════════════════════════════════════
# TEST 9 — Castling undo  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 9: Kingside castle undo"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc2, "Undoing the castle — king and rook should return")
main.MoveController.undo_move(gc2)
pause(MOVE_DELAY, T, gc2, "Castle reversed")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is not None,
      "White king restored to e1 after castle undo")
show_check(T, "King is back on e1", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("h1") is not None,
      "White rook restored to h1 after castle undo")
show_check(T, "Rook is back on h1", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("g1") is None,
      "g1 empty after castle undo")
show_check(T, "g1 is empty", gc2)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("f1") is None,
      "f1 empty after castle undo")
show_check(T, "f1 is empty", gc2)

# ════════════════════════════════════════════════════════════════════════════
# TEST 10 — Pawn capture  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 10: Pawn capture (e4xd5)"
print(f"\n{T}")
gc3 = setup_game()
pause(LABEL_PAUSE, T, gc3, "White plays e4, Black plays d5, White captures")
make_move("e2", "e4", gc3, T, "White: e2 → e4")
make_move("d7", "d5", gc3, T, "Black: d7 → d5")
make_move("e4", "d5", gc3, T, "White: e4 × d5  (capture!)")

captured_piece = play_objects.Piece_Lists_Shortcut.piece_on_coord("d5")
check(captured_piece is not None and captured_piece.color == "white",
      "White pawn on d5 after capture")
show_check(T, "White pawn occupies d5", gc3)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e4") is None,
      "e4 empty after white pawn advances")
show_check(T, "e4 is empty", gc3)

live_black_pawns = [p for p in play_objects.PlayPawn.black_pawn_list
                    if not p.taken_off_board]
check(len(live_black_pawns) == 7, "7 black pawns remain after capture")
show_check(T, f"Live black pawns: {len(live_black_pawns)} (expected 7)", gc3)

# ════════════════════════════════════════════════════════════════════════════
# TEST 11 — Queenside castling  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 11: Queenside castle (white)"
print(f"\n{T}")
gc4 = setup_game()
pause(LABEL_PAUSE, T, gc4, "Clearing b1, c1, d1 to allow O-O-O")
make_move("d2", "d4", gc4, T, "White: d2 → d4  (opens diagonal for Bc1)")
make_move("d7", "d5", gc4, T, "Black: d7 → d5")
make_move("c1", "f4", gc4, T, "White: Bc1 → f4  (c1 cleared)")
make_move("e7", "e6", gc4, T, "Black: e7 → e6")
make_move("b1", "c3", gc4, T, "White: Nb1 → c3  (b1 cleared)")
make_move("g8", "f6", gc4, T, "Black: Ng8 → f6")
make_move("d1", "d2", gc4, T, "White: Qd1 → d2  (d1 cleared)")
make_move("h7", "h6", gc4, T, "Black: h7 → h6")
pause(LABEL_PAUSE, T, gc4, "b1, c1, d1 all clear — queenside castling!")
make_move("e1", "c1", gc4, T, "White: O-O-O  (king→c1, rook→d1)")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("c1") is not None,
      "White king arrived at c1 after queenside castle")
show_check(T, "King is on c1", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d1") is not None,
      "White rook moved to d1 after queenside castle")
show_check(T, "Rook is on d1", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is None,
      "e1 empty after queenside castle")
show_check(T, "e1 is empty", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a1") is None,
      "a1 rook moved away after queenside castle")
show_check(T, "a1 is empty", gc4)

# ════════════════════════════════════════════════════════════════════════════
# TEST 12 — Queenside castling undo  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 12: Queenside castle undo"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc4, "Undoing O-O-O — king back to e1, rook back to a1")
main.MoveController.undo_move(gc4)
pause(MOVE_DELAY, T, gc4, "Queenside castle reversed")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("e1") is not None,
      "White king restored to e1 after queenside castle undo")
show_check(T, "King is back on e1", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a1") is not None,
      "White rook restored to a1 after queenside castle undo")
show_check(T, "Rook is back on a1", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("c1") is None,
      "c1 empty after queenside castle undo")
show_check(T, "c1 is empty", gc4)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("d1") is None,
      "d1 empty after queenside castle undo")
show_check(T, "d1 is empty", gc4)

# ════════════════════════════════════════════════════════════════════════════
# TEST 13 — Checkmate detection: Fool's Mate  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 13: Checkmate — Fool's Mate"
print(f"\n{T}")
gc5 = setup_game()
pause(LABEL_PAUSE, T, gc5, "f3, e5, g4 — then Qh4# delivers Fool's Mate")
make_move("f2", "f3", gc5, T, "White: f2 → f3  (fatally weakens king)")
make_move("e7", "e5", gc5, T, "Black: e7 → e5")
make_move("g2", "g4", gc5, T, "White: g2 → g4  (opens h4-e1 diagonal)")
make_move("d8", "h4", gc5, T, "Black: Qd8 → h4#  (Fool's Mate!)")

check(gc5.result_abb == "0-1", "Result is 0-1 after Fool's Mate")
show_check(T, f"result_abb = '{gc5.result_abb}' (expected 0-1)", gc5)

check(main.TextController.check_checkmate_text == "Black wins",
      "Check/mate text shows 'Black wins'")
show_check(T, f"Status text: '{main.TextController.check_checkmate_text}'", gc5)

check(gc5.color_in_check == "white",
      "White king flagged in check after Fool's Mate")
show_check(T, f"color_in_check = '{gc5.color_in_check}' (expected white)", gc5)

# ════════════════════════════════════════════════════════════════════════════
# TEST 14 — Pawn promotion to queen  (4 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 14: Pawn promotion to queen"
print(f"\n{T}")
# Custom position: white pawn on a7 one step from promotion.
# Kings placed safely out of each other's way.
gc6 = setup_custom_game({
    'white_pawn':  ['a7'],
    'white_king':  ['c1'],
    'black_king':  ['h6'],
})
pause(LABEL_PAUSE, T, gc6, "White pawn on a7 — one push to promote!")
result = make_move("a7", "a8", gc6, T, "White: a7 → a8=Q  (promotion!)")
_, _, special_abb, _ = result

check(special_abb == "=Q", "Promotion flagged as =Q")
show_check(T, f"special_abb = '{special_abb}' (expected =Q)", gc6)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a7") is None,
      "a7 empty after pawn promotion")
show_check(T, "a7 is empty (pawn gone)", gc6)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a8") is not None,
      "a8 occupied by promoted queen")
show_check(T, "a8 has the promoted queen", gc6)

check(len(play_objects.PlayQueen.white_queen_list) == 1,
      "White queen list has 1 entry after promotion")
show_check(T, f"White queens: {len(play_objects.PlayQueen.white_queen_list)} (expected 1)", gc6)

# ════════════════════════════════════════════════════════════════════════════
# TEST 15 — Pawn promotion undo  (3 checks)
# ════════════════════════════════════════════════════════════════════════════
T = "Test 15: Pawn promotion undo"
print(f"\n{T}")
pause(LABEL_PAUSE, T, gc6, "Undoing a8=Q — pawn should return to a7, queen removed")
main.MoveController.undo_move(gc6)
pause(MOVE_DELAY, T, gc6, "Promotion reversed")

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a7") is not None,
      "White pawn restored to a7 after promotion undo")
show_check(T, "Pawn is back on a7", gc6)

check(play_objects.Piece_Lists_Shortcut.piece_on_coord("a8") is None,
      "a8 empty after promotion undo")
show_check(T, "a8 is empty", gc6)

check(len(play_objects.PlayQueen.white_queen_list) == 0,
      "White queen list empty after promotion undo")
show_check(T, f"White queens: {len(play_objects.PlayQueen.white_queen_list)} (expected 0)", gc6)

# ════════════════════════════════════════════════════════════════════════════
# Done
# ════════════════════════════════════════════════════════════════════════════
result_txt = (f"All {PASSED} checks passed!"
              if FAILED == 0 else f"{PASSED} passed, {FAILED} FAILED")
print(f"\n=== Results: {PASSED} passed, {FAILED} failed ===")
pause(4.0, result_txt, gc6, "Press Q to close")
pygame.quit()
