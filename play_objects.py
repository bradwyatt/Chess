import pygame
import load_images_sounds as lis
import board
import initvar

PLAY_SPRITES = pygame.sprite.Group()

class Piece_Lists_Shortcut():
    def all_pieces():
        return [PlayKing.black_king_list, PlayKing.white_king_list,
                PlayPawn.white_pawn_list, PlayBishop.white_bishop_list, 
                PlayKnight.white_knight_list, PlayRook.white_rook_list, 
                PlayQueen.white_queen_list, PlayPawn.black_pawn_list, 
                PlayBishop.black_bishop_list, PlayKnight.black_knight_list, 
                PlayRook.black_rook_list, PlayQueen.black_queen_list]
    def white_pieces():
        return [PlayKing.white_king_list, PlayPawn.white_pawn_list,  
                PlayBishop.white_bishop_list, PlayKnight.white_knight_list, 
                PlayRook.white_rook_list, PlayQueen.white_queen_list]
    def black_pieces():
        return [PlayKing.black_king_list, PlayPawn.black_pawn_list,  
                PlayBishop.black_bishop_list, PlayKnight.black_knight_list, 
                PlayRook.black_rook_list, PlayQueen.black_queen_list]
    def piece_on_coord(grid_coord):
        for piece_list in Piece_Lists_Shortcut.all_pieces():
            for piece in piece_list:
                if piece.coordinate == grid_coord:
                    return piece

class ChessPiece:
    def __init__(self, coord, image, col, piece_type):
        PLAY_SPRITES.add(self)
        self.image = image
        self.color = col
        COLOR_POSSIBILITIES = ["white", "black"]
        OTHER_COLOR_INDEX = (COLOR_POSSIBILITIES.index(self.color)+1)%2
        self.enemy_color = COLOR_POSSIBILITIES[OTHER_COLOR_INDEX]
        self.select = False
        self.pinned = False
        self.disable = False
        self.taken_off_board = False
        self.coordinate = coord
        self.captured_move_number_and_coordinate = None
        self.rect = self.image.get_rect()
        self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
        self.previous_coordinate = self.coordinate
        self.coordinate_history = {}
        self.prior_move_color = False
        self.piece_type = piece_type
        self._image_keys = {
            "normal":      f"SPR_{col.upper()}_{piece_type.upper()}",
            "highlighted": f"SPR_{col.upper()}_{piece_type.upper()}_HIGHLIGHTED",
            "priormove":   f"SPR_{col.upper()}_{piece_type.upper()}_PRIORMOVE",
        }
    def pinned_restrict(self, pin_attacking_coordinates):
        self.pinned = True
        self.pin_attacking_coordinates = pin_attacking_coordinates
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft
    def highlight(self):
        if not self.taken_off_board:
            self.image = lis.IMAGES[self._image_keys["highlighted"]]
            self.select = True
    def no_highlight(self):
        if not self.taken_off_board:
            key = "priormove" if self.prior_move_color else "normal"
            self.image = lis.IMAGES[self._image_keys[key]]
            self.select = False
    def captured(self, x, y, move_number):
        self.taken_off_board = True
        self.captured_move_number_and_coordinate = {'move_number': move_number, 'coordinate': self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        self.image = lis.IMAGES[self._image_keys["normal"]]

class PlayPawn(ChessPiece, pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_PAWN"]
            PlayPawn.white_pawn_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_PAWN"]
            PlayPawn.black_pawn_list.append(self)
        super().__init__(coord, self.image, col, "pawn")
        self.score = initvar.piece_values_dict["pawn"]
    def captured(self, x, y, move_number, ep_grid_after_coord=None):
        self.taken_off_board = True
        if ep_grid_after_coord:
            self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate, 'ep_grid_after_coord':ep_grid_after_coord}
        else:
            self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        self.image = lis.IMAGES[self._image_keys["normal"]]
    def projected(self, game_controller):
        if self.taken_off_board != True:
            self.proj_attacking_coordinates = [self.coordinate]
            row_dir = 1 if self.color == "white" else -1
            col_ordinal = ord(self.coordinate[0])
            row = int(self.coordinate[1])
            for col_offset in (-1, 1):
                coord = chr(col_ordinal + col_offset) + str(row + row_dir)
                if coord in board.Grid.grid_dict:
                    grid = board.Grid.grid_dict[coord]
                    grid.attack_count_increment(self.color, self.coordinate)
                    if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                        #log.info("Check for coordinate " + str(grid.coordinate))
                        game_controller.king_in_check("pawn", self.proj_attacking_coordinates, self.enemy_color)

    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            def pawn_movement():
                if self.color == "white":
                    movement = 1
                    initial_space = 2
                    hop_space = 4
                elif self.color == "black":
                    movement = -1
                    initial_space = 7
                    hop_space = 5
                grid_dict = board.Grid.grid_dict
                col = self.coordinate[0]
                row = int(self.coordinate[1])
                col_ordinal = ord(col)
                # Move one space forward
                fwd1_coord = col + str(row + movement)
                if fwd1_coord in grid_dict:
                    grid = grid_dict[fwd1_coord]
                    if grid.occupied == False:
                        if game_controller.color_in_check == self.color:
                            if self.pinned == True:
                                self.disable = True
                                return
                            elif grid.coordinate in game_controller.check_attacking_coordinates[:-1]:
                                grid.highlight(self.color, self.coordinate)
                        elif self.pinned == False:
                            grid.highlight(self.color, self.coordinate)
                        elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                            grid.highlight(self.color, self.coordinate)
                # Move two spaces forward (only from starting rank)
                if row == initial_space:
                    fwd2_coord = col + str(hop_space)
                    if fwd2_coord in grid_dict:
                        grid = grid_dict[fwd2_coord]
                        if grid.occupied == False:
                            if grid_dict[col + str(hop_space - movement)].occupied == False:
                                if grid.occupied == False:
                                    if game_controller.color_in_check == self.color:
                                        if self.pinned == True:
                                            self.disable = True
                                            return
                                        elif grid.coordinate in game_controller.check_attacking_coordinates[:-1]:
                                            grid.highlight(self.color, self.coordinate)
                                    elif self.pinned == False:
                                        grid.highlight(self.color, self.coordinate)
                                    elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                                        grid.highlight(self.color, self.coordinate)
                # Diagonal captures and en passant
                for col_offset in (-movement, movement):
                    diag_coord = chr(col_ordinal + col_offset) + str(row + movement)
                    if diag_coord not in grid_dict:
                        continue
                    grid = grid_dict[diag_coord]
                    # Enemy pieces
                    if grid.occupied_piece_color == self.enemy_color:
                        # No check and no pin is moving as normal
                        if self.pinned == False and game_controller.color_in_check != self.color:
                            grid.highlight(self.color, self.coordinate)
                        # When checked then only able to take the attacker piece in reach
                        elif game_controller.color_in_check == self.color:
                            if grid.coordinate == game_controller.check_attacking_coordinates[0]:
                                grid.highlight(self.color, self.coordinate)
                        # If attacker is causing pin
                        elif self.pinned == True and grid.coordinate in self.pin_attacking_coordinates:
                            grid.highlight(self.color, self.coordinate)
                    # En Passant
                    if grid.en_passant_skipover == True:
                        if self.pinned == False:
                            grid.highlight(self.color, self.coordinate)
            pawn_movement()



class PlayKnight(ChessPiece, pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_KNIGHT"]
            PlayKnight.white_knight_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_KNIGHT"]
            PlayKnight.black_knight_list.append(self)
        super().__init__(coord, self.image, col, "knight")
        self.score = initvar.piece_values_dict["knight"]
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            self.proj_attacking_coordinates = [self.coordinate]
            def knight_proj_direction(x, y):
                coord = chr(ord(self.coordinate[0]) + x) + str(int(self.coordinate[1]) + y)
                if coord in board.Grid.grid_dict:
                    grid = board.Grid.grid_dict[coord]
                    grid.attack_count_increment(self.color, self.coordinate)
                    if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                        #log.info("Check for coordinate " + str(grid.coordinate))
                        game_controller.king_in_check("knight", self.proj_attacking_coordinates, self.enemy_color)
            knight_proj_direction(-1, -2)
            knight_proj_direction(-1, 2)
            knight_proj_direction(1, -2)
            knight_proj_direction(1, 2)
            knight_proj_direction(-2, -1)
            knight_proj_direction(-2, 1)
            knight_proj_direction(2, -1)
            knight_proj_direction(2, 1)
    def spaces_available(self, game_controller):
        # A knight can't legally move when it is pinned in chess
        if(self.taken_off_board != True and self.disable == False and self.pinned == False):
            def knight_move_direction(x, y):
                coord = chr(ord(self.coordinate[0]) + x) + str(int(self.coordinate[1]) + y)
                if coord in board.Grid.grid_dict:
                    grid = board.Grid.grid_dict[coord]
                    if grid.occupied == 0 or grid.occupied_piece_color != self.color:
                        if game_controller.color_in_check == self.color:
                            if grid.coordinate in game_controller.check_attacking_coordinates[:-1]:
                                grid.highlight(self.color, self.coordinate)
                            else:
                                return
                        grid.highlight(self.color, self.coordinate)
            knight_move_direction(-1, -2)
            knight_move_direction(-1, 2)
            knight_move_direction(1, -2)
            knight_move_direction(1, 2)
            knight_move_direction(-2, -1)
            knight_move_direction(-2, 1)
            knight_move_direction(2, -1)
            knight_move_direction(2, 1)
def bishop_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the bishop and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        coord = chr(ord(piece.coordinate[0]) + x*i) + str(int(piece.coordinate[1]) + y*i)
        if coord not in board.Grid.grid_dict:
            break
        grid = board.Grid.grid_dict[coord]
        # Incrementing the count for allowable grids that this piece moves
        proj_attacking_coordinates.append(grid.coordinate)
        # If King is already in check and it's iterating to next occupied grid space
        if(pieces_in_way == 1 and king_count == 1):
            game_controller.king_in_check(piece_name, proj_attacking_coordinates, piece.enemy_color)
            return
        # Passing this piece's coordinate to this grid
        if pinned_piece_coord is None:
            grid.attack_count_increment(piece.color, piece.coordinate)
        # Counting pieces and Ignoring pieces that are past the king
        if(grid.occupied == 1 and king_count < 1):
            pieces_in_way += 1
            if(grid.occupied_piece == "king" and grid.occupied_piece_color == piece.enemy_color):
                king_count += 1
            else:
                # If there's already no pin
                if pinned_piece_coord is None:
                    pinned_piece_coord = grid.coordinate
                # 2 pieces without a king
                else:
                    return
        # 2 Pieces in way, includes 1 king
        if(pieces_in_way == 2 and king_count == 1):
            #log.info("King is pinned on coordinate " + str(grid.coordinate))
            game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
            return
        # 1 Piece in way which is King
        # This is check, we will iterate one more time to cover the next square king is not allowed to go to
        elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
            #log.info("Check for coordinate " + str(grid.coordinate))
            # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
            # Corner case where king is on the edge of the board
            if((grid.coordinate[0] == 'a' and x == -1) or (grid.coordinate[0] == 'h' and x == 1) or \
               (int(grid.coordinate[1]) == 8 and y == 1) or (int(grid.coordinate[1]) == 1 and y == -1)):
                game_controller.king_in_check(piece_name, proj_attacking_coordinates, piece.enemy_color)
                return

def bishop_direction_spaces_available(bishop, game_controller, x, y):
    for i in range(1,8):
        coord = chr(ord(bishop.coordinate[0]) + x*i) + str(int(bishop.coordinate[1]) + y*i)
        if coord not in board.Grid.grid_dict:
            break
        grid = board.Grid.grid_dict[coord]
        # If no enemy piece on grid
        if grid.occupied == 0:
            # If current king not in check and this piece is not pinned
            if(game_controller.color_in_check != bishop.color and bishop.pinned == False):
                grid.highlight(bishop.color, bishop.coordinate)
            # If current king is in check
            elif game_controller.color_in_check == bishop.color:
                # Disable piece if it is pinned and checked from another enemy piece
                if bishop.pinned == True:
                    bishop.disable = True
                    return
                # Block path of enemy bishop, rook, or queen
                # You cannot have multiple spaces in one direction when blocking so return
                elif grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                    and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                         or game_controller.attacker_piece == "queen"):
                    grid.highlight(bishop.color, bishop.coordinate)
                    return
                # The only grid available is the attacker piece when pawn or knight
                elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                    and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                    grid.highlight(bishop.color, bishop.coordinate)
                    return
            # If pinned and the grid is within the attacking coordinates restraint
            # Includes grid.coordinate != self.coordinate so that staying at same coordinate doesn't count as move
            elif(bishop.pinned == True and grid.coordinate in bishop.pin_attacking_coordinates \
                 and grid.occupied_piece != 'king' and grid.coordinate != bishop.coordinate):
                grid.highlight(bishop.color, bishop.coordinate)
            else:
                # When all the above conditions aren't met, then the bishop can't move further
                return
        # If enemy piece on grid
        elif grid.occupied == 1 and grid.occupied_piece_color == bishop.enemy_color:
            # Check_Attacking_Coordinates only exists when there is check
            if game_controller.color_in_check == bishop.color:
                if grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                    and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                         or game_controller.attacker_piece == "queen"):
                    grid.highlight(bishop.color, bishop.coordinate)
                elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                    and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                    grid.highlight(bishop.color, bishop.coordinate)
            # If pinned, there's a piece on the grid, and grid is within the attacking coordinates restraint
            elif(bishop.pinned == True and grid.occupied_piece != 'king'):
                if grid.coordinate in bishop.pin_attacking_coordinates:
                    # If not in check from another piece
                    if not game_controller.check_attacking_coordinates:
                        grid.highlight(bishop.color, bishop.coordinate)
                        # No return since there are more than one possibility when between king and attacker piece
            else:
                # In all other cases where no check and no pin
                grid.highlight(bishop.color, bishop.coordinate)
            # Will always return function on square with enemy piece
            return
        # If same color piece in the way
        elif grid.occupied == 1 and grid.occupied_piece_color == bishop.color:
            # Will always return function on square with friendly piece
            return

class PlayBishop(ChessPiece, pygame.sprite.Sprite):
    white_bishop_list = []
    black_bishop_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_BISHOP"]
            PlayBishop.white_bishop_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_BISHOP"]
            PlayBishop.black_bishop_list.append(self)
        super().__init__(coord, self.image, col, "bishop")
        self.score = initvar.piece_values_dict["bishop"]
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            bishop_projected("bishop", self, game_controller, -1, -1) #southwest
            bishop_projected("bishop", self, game_controller, -1, 1) #northwest
            bishop_projected("bishop", self, game_controller, 1, -1) #southeast
            bishop_projected("bishop", self, game_controller, 1, 1) #northeast
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            bishop_direction_spaces_available(self, game_controller, -1, -1) #southwest
            bishop_direction_spaces_available(self, game_controller, -1, 1) #northwest
            bishop_direction_spaces_available(self, game_controller, 1, -1) #southeast
            bishop_direction_spaces_available(self, game_controller, 1, 1) #northeast

def rook_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the rook and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        coord = chr(ord(piece.coordinate[0]) + x*i) + str(int(piece.coordinate[1]) + y*i)
        if coord not in board.Grid.grid_dict:
            break
        grid = board.Grid.grid_dict[coord]
        # Incrementing the count for allowable grids that this piece moves
        proj_attacking_coordinates.append(grid.coordinate)
        # If King is already in check and it's iterating to next occupied grid space
        if(pieces_in_way == 1 and king_count == 1):
            game_controller.king_in_check(piece_name, proj_attacking_coordinates, piece.enemy_color)
            return
        # Passing this piece's coordinate to this grid
        if pinned_piece_coord is None:
            grid.attack_count_increment(piece.color, piece.coordinate)
        # Counting pieces and Ignoring pieces that are past the king
        if(grid.occupied == 1 and king_count < 1):
            pieces_in_way += 1
            if(grid.occupied_piece == "king" and grid.occupied_piece_color == piece.enemy_color):
                king_count += 1
            else:
                # If there's already no pin
                if pinned_piece_coord is None:
                    pinned_piece_coord = grid.coordinate
                # 2 pieces without a king
                else:
                    return
        # 2 Pieces in way, includes 1 king
        if(pieces_in_way == 2 and king_count == 1): #2 Pieces in way, includes 1 king
            #log.info("King is pinned on coordinate " + str(grid.coordinate))
            game_controller.pinned_piece(pinned_piece_coord, proj_attacking_coordinates, piece.enemy_color)
            return
        # 1 Piece in way which is King
        # This is check, we will iterate one more time to cover the next square king is not allowed to go to
        elif(pieces_in_way == 1 and king_count == 1 and grid.occupied_piece == "king"):
            #log.info("Check for coordinate " + str(grid.coordinate))
            # If the grid is at the last attacking square, there won't be a next iteration, so call king_in_check
            if((grid.coordinate[0] == 'a' and y == 0) or (grid.coordinate[0] == 'h' and y == 0) or \
               (int(grid.coordinate[1]) == 1 and x == 0) or (int(grid.coordinate[1]) == 8 and x == 0)):
                game_controller.king_in_check(piece_name, proj_attacking_coordinates, piece.enemy_color)
                return
    return

def rook_direction_spaces_available(rook, game_controller, x, y):
    for i in range(1,8):
        coord = chr(ord(rook.coordinate[0]) + x*i) + str(int(rook.coordinate[1]) + y*i)
        if coord not in board.Grid.grid_dict:
            break
        grid = board.Grid.grid_dict[coord]
        # If no enemy piece on grid
        if grid.occupied == 0:
            # If current king not in check and this piece is not pinned
            if(game_controller.color_in_check != rook.color and rook.pinned == False):
                grid.highlight(rook.color, rook.coordinate)
            # If current king is in check
            elif game_controller.color_in_check == rook.color:
                # Disable piece if it is pinned and checked from another enemy piece
                if rook.pinned == True:
                    rook.disable = True
                    return
                # Block path of enemy bishop, rook, or queen
                # You cannot have multiple spaces in one direction when blocking so return
                elif grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                    and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                         or game_controller.attacker_piece == "queen"):
                    grid.highlight(rook.color, rook.coordinate)
                    return
                # The only grid available is the attacker piece when pawn or knight
                elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                    and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                    grid.highlight(rook.color, rook.coordinate)
                    return
            # If pinned and grid is within the attacking coordinates restraint
            elif(rook.pinned == True and grid.coordinate in rook.pin_attacking_coordinates \
                 and grid.occupied_piece != 'king' and grid.coordinate != rook.coordinate):
                grid.highlight(rook.color, rook.coordinate)
            else:
                # When all the above conditions aren't met, then the rook can't move further
                return
        # If enemy piece on grid
        elif grid.occupied == 1 and grid.occupied_piece_color == rook.enemy_color:
            # Check_Attacking_Coordinates only exists when there is check
            if game_controller.color_in_check == rook.color:
                # Block path of enemy bishop, rook, or queen
                # You cannot have multiple spaces in one direction when blocking so return
                if grid.coordinate in game_controller.check_attacking_coordinates[:-1] \
                    and (game_controller.attacker_piece == "bishop" or game_controller.attacker_piece == "rook" \
                         or game_controller.attacker_piece == "queen"):
                    grid.highlight(rook.color, rook.coordinate)
                # The only grid available is the attacker piece when pawn or knight
                elif grid.coordinate == game_controller.check_attacking_coordinates[0] \
                    and (game_controller.attacker_piece == "pawn" or game_controller.attacker_piece == "knight"):
                    grid.highlight(rook.color, rook.coordinate)
            # If pinned and grid is within the attacking coordinates restraint
            elif(rook.pinned == True and grid.coordinate in rook.pin_attacking_coordinates \
                 and grid.occupied_piece != 'king'):
                grid.highlight(rook.color, rook.coordinate)
            else:
                # In all other cases where no check and no pin
                grid.highlight(rook.color, rook.coordinate)
            return
        # If same color piece in the way
        elif grid.occupied == 1 and grid.occupied_piece_color == rook.color:
            return

class PlayRook(ChessPiece, pygame.sprite.Sprite):
    white_rook_list = []
    black_rook_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_ROOK"]
            PlayRook.white_rook_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_ROOK"]
            PlayRook.black_rook_list.append(self)
        super().__init__(coord, self.image, col, "rook")
        self.allowed_to_castle = True
        self.score = initvar.piece_values_dict["rook"]
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            rook_projected("rook", self, game_controller, -1, 0) #west
            rook_projected("rook", self, game_controller, 1, 0) #east
            rook_projected("rook", self, game_controller, 0, 1) #north
            rook_projected("rook", self, game_controller, 0, -1) #south
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            rook_direction_spaces_available(self, game_controller, -1, 0) #west
            rook_direction_spaces_available(self, game_controller, 1, 0) #east
            rook_direction_spaces_available(self, game_controller, 0, 1) #north
            rook_direction_spaces_available(self, game_controller, 0, -1) #south
    def no_highlight(self):
        key = "priormove" if self.prior_move_color else "normal"
        self.image = lis.IMAGES[self._image_keys[key]]
        self.select = False

class PlayQueen(ChessPiece, pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_QUEEN"]
            PlayQueen.white_queen_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_QUEEN"]
            PlayQueen.black_queen_list.append(self)
        super().__init__(coord, self.image, col, "queen")
        self.score = initvar.piece_values_dict["queen"]
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            bishop_projected("queen", self, game_controller, -1, -1) #southwest
            bishop_projected("queen", self, game_controller, -1, 1) #northwest
            bishop_projected("queen", self, game_controller, 1, -1) #southeast
            bishop_projected("queen", self, game_controller, 1, 1) #northeast
            rook_projected("rook", self, game_controller, -1, 0) #west
            rook_projected("rook", self, game_controller, 1, 0) #east
            rook_projected("rook", self, game_controller, 0, 1) #north
            rook_projected("rook", self, game_controller, 0, -1) #south
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            bishop_direction_spaces_available(self, game_controller, -1, -1) #southwest
            bishop_direction_spaces_available(self, game_controller, -1, 1) #northwest
            bishop_direction_spaces_available(self, game_controller, 1, -1) #southeast
            bishop_direction_spaces_available(self, game_controller, 1, 1) #northeast
            rook_direction_spaces_available(self, game_controller, -1, 0) #west
            rook_direction_spaces_available(self, game_controller, 1, 0) #east
            rook_direction_spaces_available(self, game_controller, 0, 1) #north
            rook_direction_spaces_available(self, game_controller, 0, -1) #south

class PlayKing(ChessPiece, pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = lis.IMAGES["SPR_WHITE_KING"]
            PlayKing.white_king_list.append(self)
        elif(col == "black"):
            self.image = lis.IMAGES["SPR_BLACK_KING"]
            PlayKing.black_king_list.append(self)
        self.queen_side_castle_ability = False
        self.king_side_castle_ability = False
        self.castled = False
        super().__init__(coord, self.image, col, "king")
    def castle_check(self, game_controller):
        if(self.castled == False and game_controller.color_in_check != self.color):
            if self.color == "white":
                for white_rook in PlayRook.white_rook_list:
                    if white_rook.allowed_to_castle == True:
                        if(white_rook.coordinate == 'a1'):
                            if(board.Grid.grid_dict['b1'].occupied == 0 and board.Grid.grid_dict['c1'].occupied == 0 and board.Grid.grid_dict['d1'].occupied == 0 \
                               and len(board.Grid.grid_dict['b1'].coords_of_attacking_pieces['black']) == 0 and len(board.Grid.grid_dict['c1'].coords_of_attacking_pieces['black']) == 0 \
                               and len(board.Grid.grid_dict['d1'].coords_of_attacking_pieces['black']) == 0):
                                self.queen_side_castle_ability = True
                            else:
                                self.queen_side_castle_ability = False
                        if(white_rook.coordinate == 'h1'):
                            if(board.Grid.grid_dict['f1'].occupied == 0 and board.Grid.grid_dict['g1'].occupied == 0 \
                               and len(board.Grid.grid_dict['f1'].coords_of_attacking_pieces['black']) == 0 and len(board.Grid.grid_dict['g1'].coords_of_attacking_pieces['black']) == 0):
                                self.king_side_castle_ability = True
                            else:
                                self.king_side_castle_ability = False
            elif self.color == "black":
                for black_rook in PlayRook.black_rook_list:
                    if black_rook.allowed_to_castle == True:
                        if(black_rook.coordinate == 'a8'):
                            if(board.Grid.grid_dict['b8'].occupied == 0 and board.Grid.grid_dict['c8'].occupied == 0 and board.Grid.grid_dict['d8'].occupied == 0 \
                               and len(board.Grid.grid_dict['b8'].coords_of_attacking_pieces['white']) == 0 and len(board.Grid.grid_dict['c8'].coords_of_attacking_pieces['white']) == 0 \
                               and len(board.Grid.grid_dict['d8'].coords_of_attacking_pieces['white']) == 0):
                                self.queen_side_castle_ability = True
                            else:
                                self.queen_side_castle_ability = False
                        if(black_rook.coordinate == 'h8'):
                            if(board.Grid.grid_dict['f8'].occupied == 0 and board.Grid.grid_dict['g8'].occupied == 0 \
                               and len(board.Grid.grid_dict['f8'].coords_of_attacking_pieces['white']) == 0 and len(board.Grid.grid_dict['g8'].coords_of_attacking_pieces['white']) == 0):
                                self.king_side_castle_ability = True
                            else:
                                self.king_side_castle_ability = False
    def highlight(self):
        if(self.color == "white"):
            self.image = lis.IMAGES["SPR_WHITE_KING_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = lis.IMAGES["SPR_BLACK_KING_HIGHLIGHTED"]
        self.select = 1
    def projected(self, game_controller):
        if self.taken_off_board == False:
            grid_dict = board.Grid.grid_dict
            col_ordinal = ord(self.coordinate[0])
            row = int(self.coordinate[1])
            # 8 adjacent squares
            for col_offset in (-1, 0, 1):
                for row_offset in (-1, 0, 1):
                    if col_offset == 0 and row_offset == 0:
                        continue
                    coord = chr(col_ordinal + col_offset) + str(row + row_offset)
                    if coord in grid_dict:
                        grid_dict[coord].attack_count_increment(self.color, self.coordinate)
            # Castling squares
            for castle_col_offset, castle_ability in ((2, self.king_side_castle_ability), (-2, self.queen_side_castle_ability)):
                if castle_ability != 1 or (row != 1 and row != 8):
                    continue
                coord = chr(col_ordinal + castle_col_offset) + str(row)
                if coord in grid_dict:
                    grid = grid_dict[coord]
                    if grid.occupied == 0 or grid.occupied_piece_color != self.color:
                        grid.attack_count_increment(self.color, self.coordinate)
    def spaces_available(self, game_controller):
        if((self.color == "white" and self.coordinate == 'e1') or (self.color == "black" and self.coordinate == 'e8')):
            self.castle_check(game_controller)
        grid_dict = board.Grid.grid_dict
        col_ordinal = ord(self.coordinate[0])
        row = int(self.coordinate[1])
        def check_and_highlight(grid):
            # Direct Enemy Threat refers to how many opposing color pieces are attacking square
            if self.color == "white":
                direct_enemy_threat = len(grid.coords_of_attacking_pieces['black']) > 0
            else:
                direct_enemy_threat = len(grid.coords_of_attacking_pieces['white']) > 0
            # Projected Enemy Threat refers to threatening squares past the king
            projected_enemy_threat = grid.coordinate in game_controller.check_attacking_coordinates
            # If square does not have same color piece on it
            # If square is not directly threatened by opposing piece
            # If square is not in enemy piece projection OR if enemy piece in reach to be take-able
            if(grid.occupied_piece_color != self.color and direct_enemy_threat == False and \
               (projected_enemy_threat == False or grid.occupied_piece_color == self.enemy_color)):
                grid.highlight(self.color, self.coordinate)
        # King can have only one move in all directions
        for col_offset in (-1, 0, 1):
            for row_offset in (-1, 0, 1):
                if col_offset == 0 and row_offset == 0:
                    continue
                coord = chr(col_ordinal + col_offset) + str(row + row_offset)
                if coord in grid_dict:
                    check_and_highlight(grid_dict[coord])
        # Castle
        if not self.castled and (row == 1 or row == 8):
            for castle_col_offset, castle_ability in ((2, self.king_side_castle_ability), (-2, self.queen_side_castle_ability)):
                if castle_ability != 1:
                    continue
                coord = chr(col_ordinal + castle_col_offset) + str(row)
                if coord in grid_dict:
                    check_and_highlight(grid_dict[coord])
    def no_highlight(self):
        if(self.color == "white"):
            if(self.prior_move_color == True):
                self.image = lis.IMAGES["SPR_WHITE_KING_PRIORMOVE"]
            else:
                self.image = lis.IMAGES["SPR_WHITE_KING"]
        elif(self.color == "black"):
            if(self.prior_move_color == True):
                self.image = lis.IMAGES["SPR_BLACK_KING_PRIORMOVE"]
            else:
                self.image = lis.IMAGES["SPR_BLACK_KING"]
        self.select = 0


PLAY_PIECE_CLASS = {
    "pawn":   PlayPawn,
    "bishop": PlayBishop,
    "knight": PlayKnight,
    "rook":   PlayRook,
    "queen":  PlayQueen,
    "king":   PlayKing,
}

