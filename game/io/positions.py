import ast
import copy
import json
import logging
import os
import sys

import initvar
import placed_objects
import play_objects

if sys.platform != "emscripten":
    import tkinter as tk
    from tkinter.filedialog import asksaveasfilename, askopenfilename
else:
    tk = None
    asksaveasfilename = None
    askopenfilename = None

log = logging.getLogger("log_guy")


def native_file_dialogs_available():
    return (
        not initvar.ITCH_MODE
        and tk is not None
        and asksaveasfilename is not None
        and askopenfilename is not None
    )


def itch_mode_blocked(action_name):
    log.info("%s is unavailable in itch/browser mode.", action_name)


def pos_load_file(reset=False):
    """
    Load positions of the pieces
    """
    if initvar.ITCH_MODE and not reset:
        itch_mode_blocked("Loading saved positions")
        return
    open_file = None
    if reset:
        loaded_dict = {'white_pawn': ['a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2'],
                       'white_bishop': ['c1', 'f1'], 'white_knight': ['b1', 'g1'],
                       'white_rook': ['a1', 'h1'], 'white_queen': ['d1'], 'white_king': ['e1'],
                       'black_pawn': ['a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7'],
                       'black_bishop': ['c8', 'f8'], 'black_knight': ['b8', 'g8'],
                       'black_rook': ['a8', 'h8'], 'black_queen': ['d8'], 'black_king': ['e8']}
    else:
        if not native_file_dialogs_available():
            itch_mode_blocked("Loading saved positions")
            return
        request_file_name = askopenfilename(defaultextension=".json")
        try:
            open_file = open(request_file_name, "r")
        except FileNotFoundError:
            log.info("File not found")
            return
        loaded_file = open_file.read()
        loaded_dict = ast.literal_eval(loaded_file)

    for obj_list in play_objects.Piece_Lists_Shortcut.all_pieces():
        for obj in obj_list:
            obj.destroy()
    if open_file:
        open_file.close()

    log.info("Removing sprites and loading piece positions...")

    # Removes all placed lists
    placed_objects.remove_all_placed()

    for white_pawn_pos in loaded_dict['white_pawn']:
        placed_objects.PlacedPawn(white_pawn_pos, "white")
    for white_bishop_pos in loaded_dict['white_bishop']:
        placed_objects.PlacedBishop(white_bishop_pos, "white")
    for white_knight_pos in loaded_dict['white_knight']:
        placed_objects.PlacedKnight(white_knight_pos, "white")
    for white_rook_pos in loaded_dict['white_rook']:
        placed_objects.PlacedRook(white_rook_pos, "white")
    for white_queen_pos in loaded_dict['white_queen']:
        placed_objects.PlacedQueen(white_queen_pos, "white")
    for white_king_pos in loaded_dict['white_king']:
        placed_objects.PlacedKing(white_king_pos, "white")
    for black_pawn_pos in loaded_dict['black_pawn']:
        placed_objects.PlacedPawn(black_pawn_pos, "black")
    for black_bishop_pos in loaded_dict['black_bishop']:
        placed_objects.PlacedBishop(black_bishop_pos, "black")
    for black_knight_pos in loaded_dict['black_knight']:
        placed_objects.PlacedKnight(black_knight_pos, "black")
    for black_rook_pos in loaded_dict['black_rook']:
        placed_objects.PlacedRook(black_rook_pos, "black")
    for black_queen_pos in loaded_dict['black_queen']:
        placed_objects.PlacedQueen(black_queen_pos, "black")
    for black_king_pos in loaded_dict['black_king']:
        placed_objects.PlacedKing(black_king_pos, "black")

    log.info("Positioning Loaded Successfully")
    return


def get_dict_rect_positions():
    """
    Returns the tuples of each objects' positions within all classes
    """
    total_placed_list = {'white_pawn': placed_objects.PlacedPawn.white_pawn_list,
                         'white_bishop': placed_objects.PlacedBishop.white_bishop_list,
                         'white_knight': placed_objects.PlacedKnight.white_knight_list,
                         'white_rook': placed_objects.PlacedRook.white_rook_list,
                         'white_queen': placed_objects.PlacedQueen.white_queen_list,
                         'white_king': placed_objects.PlacedKing.white_king_list,
                         'black_pawn': placed_objects.PlacedPawn.black_pawn_list,
                         'black_bishop': placed_objects.PlacedBishop.black_bishop_list,
                         'black_knight': placed_objects.PlacedKnight.black_knight_list,
                         'black_rook': placed_objects.PlacedRook.black_rook_list,
                         'black_queen': placed_objects.PlacedQueen.black_queen_list,
                         'black_king': placed_objects.PlacedKing.black_king_list}
    get_coord_for_all_obj = dict.fromkeys(total_placed_list, list)
    for item_key, item_list in total_placed_list.items():
        item_list_in_name = []
        for item_coord in item_list:
            item_list_in_name.append(item_coord.coordinate)
        get_coord_for_all_obj[item_key] = item_list_in_name
    # Tuple positions converted to string to be JSON-compatible
    all_obj_coord_json = json.dumps(get_coord_for_all_obj)
    return all_obj_coord_json


def pos_save_file():
    """
    Save positions of the pieces
    """
    if not native_file_dialogs_available():
        itch_mode_blocked("Saving positions")
        return
    try:
        save_file_prompt = asksaveasfilename(defaultextension=".json")
        save_file_name = open(save_file_prompt, "w")
        if save_file_name is not None:
            # Write the file to disk
            obj_locations = copy.deepcopy(get_dict_rect_positions())
            save_file_name.write(str(obj_locations))
            save_file_name.close()
            log.info("File Saved Successfully.")
        else:
            log.info("Error! Need king to save!")
    except IOError:
        log.info("Save File Error (IOError)")


def pos_lists_to_coord(pos_score_list):
    """
    When analyzing the board, the function returns the score
    for each of the squares
    """
    score_dict = {}
    coordinate_list = ['a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
                  'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
                  'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
                  'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
                  'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
                  'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
                  'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
                  'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1']
    for item_index in range(0, len(pos_score_list)):
        score_dict[coordinate_list[item_index]] = pos_score_list[item_index]
    return score_dict


class GameProperties():
    Event = ""
    Site = ""
    Date = ""
    Round = ""
    White = ""
    Black = ""
    Result = ""
    WhiteElo = ""
    BlackElo = ""
    ECO = ""
    TimeControl = "0"

    @classmethod
    def game_properties_popup(cls):
        if initvar.ITCH_MODE or tk is None:
            itch_mode_blocked("Game properties")
            return
        field_names = [
            "Event",
            "Site",
            "Date",
            "Round",
            "White",
            "Black",
            "Result",
            "WhiteElo",
            "BlackElo",
            "ECO",
            "TimeControl",
        ]
        window = tk.Tk()
        window.title("Game Properties")
        window.resizable(False, False)
        window.lift()
        window.attributes("-topmost", True)
        window.after(100, lambda: window.attributes("-topmost", False))

        tk.Label(
            window,
            text="Please enter the information for the game below (all fields are optional)",
            wraplength=360,
            justify="left"
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 8), sticky="w")

        entries = {}
        for row_index, field_name in enumerate(field_names, start=1):
            tk.Label(window, text=field_name, width=10, anchor="w").grid(
                row=row_index, column=0, padx=(12, 8), pady=4, sticky="w"
            )
            entry = tk.Entry(window, width=36)
            entry.insert(0, str(getattr(cls, field_name)))
            entry.grid(row=row_index, column=1, padx=(0, 12), pady=4, sticky="ew")
            entries[field_name] = entry

        result = {"confirmed": False, "values": {}}

        def submit():
            result["values"] = {
                field_name: entry.get()
                for field_name, entry in entries.items()
            }
            result["confirmed"] = True
            window.quit()
            window.destroy()

        def cancel():
            window.quit()
            window.destroy()

        button_frame = tk.Frame(window)
        button_frame.grid(row=len(field_names) + 1, column=0, columnspan=2, pady=(8, 12))
        tk.Button(button_frame, text="Ok", width=10, command=submit).pack(side="left", padx=6)
        tk.Button(button_frame, text="Cancel", width=10, command=cancel).pack(side="left", padx=6)

        window.protocol("WM_DELETE_WINDOW", cancel)
        first_entry = entries[field_names[0]]
        first_entry.focus_set()
        window.bind("<Return>", lambda _event: submit())
        window.bind("<Escape>", lambda _event: cancel())
        window.mainloop()

        if not result["confirmed"]:
            return
        for field_name, value in result["values"].items():
            setattr(cls, field_name, value)
