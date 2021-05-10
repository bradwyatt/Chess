import pygame
from load_images_sounds import *
import board

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

class ChessPiece:
    def __init__(self, coord, image, col):
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
        for grid in board.Grid.grid_list:
            if grid.coordinate == self.coordinate:
                self.rect.topleft = grid.rect.topleft
        self.previous_coordinate = self.coordinate
        self.coordinate_history = {}
        self.prior_move_color = False
    def pinned_restrict(self, pin_attacking_coordinates):
        self.pinned = True
        self.pin_attacking_coordinates = pin_attacking_coordinates
    def update(self):
        if self.coordinate is not None:
            self.rect.topleft = board.Grid.grid_dict[self.coordinate].rect.topleft

class PlayPawn(ChessPiece, pygame.sprite.Sprite):
    white_pawn_list = []
    black_pawn_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_PAWN"]
            PlayPawn.white_pawn_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
            PlayPawn.black_pawn_list.append(self)
        super().__init__(coord, self.image, col)
    def captured(self, x, y, move_number, ep_grid_after_coord=None):
        self.taken_off_board = True
        if ep_grid_after_coord:
            self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate, 'ep_grid_after_coord':ep_grid_after_coord}
        else:
            self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_PAWN"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_PAWN"]
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_PAWN_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_PAWN_HIGHLIGHTED"]
            self.select = True
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_PAWN_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_PAWN"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_PAWN_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_PAWN"]
            self.select = False
    def projected(self, game_controller):
        if self.taken_off_board != True:
            self.proj_attacking_coordinates = [self.coordinate]
            if(self.color == "white"):
                for grid in board.Grid.grid_list:
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            elif(self.color == "black"):
                for grid in board.Grid.grid_list:
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1):
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("pawn", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
                
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
                for grid in board.Grid.grid_list:
                    # Move one space up
                    if (grid.coordinate[0] == self.coordinate[0] and \
                        int(grid.coordinate[1]) == int(self.coordinate[1])+movement): 
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
                    # Move two spaces up
                    if (int(self.coordinate[1]) == initial_space and grid.coordinate[0] == self.coordinate[0] and \
                        int(grid.coordinate[1]) == hop_space and grid.occupied == False):
                        # If space before hop space is occupied by a piece
                        if board.Grid.grid_dict[grid.coordinate[0] + str(hop_space-movement)].occupied == False:
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
                    # Enemy pieces
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
                    grid.occupied_piece_color == self.enemy_color):
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
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
                    grid.occupied_piece_color == self.enemy_color):
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
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
                    grid.en_passant_skipover == True):
                        if self.pinned == False:
                            grid.highlight(self.color, self.coordinate)
                    if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+movement and int(grid.coordinate[1]) == int(self.coordinate[1])+movement and \
                    grid.en_passant_skipover == True):
                        if self.pinned == False:
                            grid.highlight(self.color, self.coordinate)
            pawn_movement()



class PlayKnight(ChessPiece, pygame.sprite.Sprite):
    white_knight_list = []
    black_knight_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
            PlayKnight.white_knight_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
            PlayKnight.black_knight_list.append(self)
        super().__init__(coord, self.image, col)
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            self.proj_attacking_coordinates = [self.coordinate]
            def knight_proj_direction(x, y):
                for grid in board.Grid.grid_list:
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and int(grid.coordinate[1]) == int(self.coordinate[1])+y:
                        grid.attack_count_increment(self.color, self.coordinate)
                        if grid.occupied_piece == "king" and grid.occupied_piece_color == self.enemy_color:
                            #log.info("Check for coordinate " + str(grid.coordinate))
                            game_controller.king_in_check("knight", self.coordinate, self.proj_attacking_coordinates, self.enemy_color)
            knight_proj_direction(-1, -2)
            knight_proj_direction(-1, 2)
            knight_proj_direction(1, -2)
            knight_proj_direction(1, 2)
            knight_proj_direction(-2, -1)
            knight_proj_direction(-2, 1)
            knight_proj_direction(2, -1)
            knight_proj_direction(2, 1)
    def captured(self, x, y, move_number):
        self.taken_off_board = True
        self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_KNIGHT"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KNIGHT"]
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_KNIGHT_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_KNIGHT_HIGHLIGHTED"]
            self.select = True
    def spaces_available(self, game_controller):
        # A knight can't legally move when it is pinned in chess
        if(self.taken_off_board != True and self.disable == False and self.pinned == False):
            def knight_move_direction(x, y):
                for grid in board.Grid.grid_list:
                    if ord(grid.coordinate[0]) == ord(self.coordinate[0])+x and int(grid.coordinate[1]) == int(self.coordinate[1])+y \
                        and (grid.occupied == 0 or grid.occupied_piece_color != self.color):
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
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_KNIGHT_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_KNIGHT"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_KNIGHT_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_KNIGHT"]
            self.select = False

def bishop_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the bishop and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        for grid in board.Grid.grid_list:
            if(ord(grid.coordinate[0]) == ord(piece.coordinate[0])+(x*i) and int(grid.coordinate[1]) == int(piece.coordinate[1])+(y*i)):
                # Incrementing the count for allowable grids that this piece moves
                proj_attacking_coordinates.append(grid.coordinate) 
                # If King is already in check and it's iterating to next occupied grid space
                if(pieces_in_way == 1 and king_count == 1):
                    game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
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
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        print("Queen test 2 " + str(game_controller.check_attacking_coordinates))
                        return

def bishop_direction_spaces_available(bishop, game_controller, x, y):
    for i in range(1,8):
        for grid in board.Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(bishop.coordinate[0])+(x*i) \
                   and int(grid.coordinate[1]) == int(bishop.coordinate[1])+(y*i):
                # If no enemy piece on grid
                if grid.occupied == 0:
                    # If current king not in check and this piece is not pinned
                    if(game_controller.color_in_check != bishop.color and bishop.pinned == False):
                        grid.highlight(bishop.color, bishop.coordinate)
                    # If current king is in check
                    elif game_controller.color_in_check == bishop.color:
                        
                        # Disable piece if it is pinned and checked from another enemy piece
                        try:
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
                        except:
                            print("BISHOP COORD " + str(bishop.coordinate))
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
                        print("PROBLEM GRID " + str(grid.coordinate))
                        print("checkattackingcoords " + str(game_controller.check_attacking_coordinates))
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
            self.image = IMAGES["SPR_WHITE_BISHOP"]
            PlayBishop.white_bishop_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
            PlayBishop.black_bishop_list.append(self)
        super().__init__(coord, self.image, col)
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            bishop_projected("bishop", self, game_controller, -1, -1) #southwest
            bishop_projected("bishop", self, game_controller, -1, 1) #northwest
            bishop_projected("bishop", self, game_controller, 1, -1) #southeast
            bishop_projected("bishop", self, game_controller, 1, 1) #northeast
    def captured(self, x, y, move_number):
        self.taken_off_board = True
        self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_BISHOP"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_BISHOP"]
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_BISHOP_HIGHLIGHTED"]
            elif(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_BISHOP_HIGHLIGHTED"]
            self.select = True
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            bishop_direction_spaces_available(self, game_controller, -1, -1) #southwest
            bishop_direction_spaces_available(self, game_controller, -1, 1) #northwest
            bishop_direction_spaces_available(self, game_controller, 1, -1) #southeast
            bishop_direction_spaces_available(self, game_controller, 1, 1) #northeast
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_BISHOP_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_BISHOP"]
            elif(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_BISHOP_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_BISHOP"]
            self.select = False

def rook_projected(piece_name, piece, game_controller, x, y):
    pieces_in_way = 0 #Pieces between the rook and the enemy King
    king_count = 0 #Checks to see if there's a king in a direction
    pinned_piece_coord = None
    proj_attacking_coordinates = [piece.coordinate]
    for i in range(1, 8):
        for grid in board.Grid.grid_list:
            if(ord(grid.coordinate[0]) == ord(piece.coordinate[0])+(x*i) \
               and int(grid.coordinate[1]) == int(piece.coordinate[1])+(y*i)):
                # Incrementing the count for allowable grids that this piece moves
                proj_attacking_coordinates.append(grid.coordinate)
                # If King is already in check and it's iterating to next occupied grid space
                if(pieces_in_way == 1 and king_count == 1):
                    game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
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
                        game_controller.king_in_check(piece_name, piece.coordinate, proj_attacking_coordinates, piece.enemy_color)
                        return
    return

def rook_direction_spaces_available(rook, game_controller, x, y):
    for i in range(1,8):
        for grid in board.Grid.grid_list:
            if ord(grid.coordinate[0]) == ord(rook.coordinate[0])+(x*i) and int(grid.coordinate[1]) == int(rook.coordinate[1])+(y*i):
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
                        # When all the above conditions aren't met, then the bishop can't move further
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
            self.image = IMAGES["SPR_WHITE_ROOK"]
            PlayRook.white_rook_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
            PlayRook.black_rook_list.append(self)
        super().__init__(coord, self.image, col)
        self.allowed_to_castle = True
    def captured(self, x, y, move_number):
        self.taken_off_board = True
        self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK"]
    def projected(self, game_controller):
        if(self.taken_off_board != True):
            rook_projected("rook", self, game_controller, -1, 0) #west
            rook_projected("rook", self, game_controller, 1, 0) #east
            rook_projected("rook", self, game_controller, 0, 1) #north
            rook_projected("rook", self, game_controller, 0, -1) #south
    def highlight(self):
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_ROOK_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_ROOK_HIGHLIGHTED"]
        self.select = True
    def spaces_available(self, game_controller):
        if(self.taken_off_board != True and self.disable == False):
            rook_direction_spaces_available(self, game_controller, -1, 0) #west
            rook_direction_spaces_available(self, game_controller, 1, 0) #east
            rook_direction_spaces_available(self, game_controller, 0, 1) #north
            rook_direction_spaces_available(self, game_controller, 0, -1) #south
    def no_highlight(self):
        if(self.color == "white"):
            if(self.prior_move_color == True):
                self.image = IMAGES["SPR_WHITE_ROOK_PRIORMOVE"]
            else:
                self.image = IMAGES["SPR_WHITE_ROOK"]
        elif(self.color == "black"):
            if(self.prior_move_color == True):
                self.image = IMAGES["SPR_BLACK_ROOK_PRIORMOVE"]
            else:
                self.image = IMAGES["SPR_BLACK_ROOK"]
        self.select = False

class PlayQueen(ChessPiece, pygame.sprite.Sprite):
    white_queen_list = []
    black_queen_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
            PlayQueen.white_queen_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
            PlayQueen.black_queen_list.append(self)
        super().__init__(coord, self.image, col)
    def captured(self, x, y, move_number):
        self.taken_off_board = True
        self.captured_move_number_and_coordinate = {'move_number':move_number, 'coordinate':self.coordinate}
        self.coordinate = None
        self.rect.topleft = x, y
        self.prior_move_color = False
        if(self.color == "white"):
            self.image = IMAGES["SPR_WHITE_QUEEN"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_QUEEN"]
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
    def highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                self.image = IMAGES["SPR_WHITE_QUEEN_HIGHLIGHTED"]
            if(self.color == "black"):
                self.image = IMAGES["SPR_BLACK_QUEEN_HIGHLIGHTED"]
            self.select = True
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
    def no_highlight(self):
        if self.taken_off_board != True:
            if(self.color == "white"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_WHITE_QUEEN_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_WHITE_QUEEN"]
            if(self.color == "black"):
                if(self.prior_move_color == True):
                    self.image = IMAGES["SPR_BLACK_QUEEN_PRIORMOVE"]
                else:
                    self.image = IMAGES["SPR_BLACK_QUEEN"]
            self.select = False

class PlayKing(ChessPiece, pygame.sprite.Sprite):
    white_king_list = []
    black_king_list = []
    def __init__(self, coord, col):
        pygame.sprite.Sprite.__init__(self)
        if(col == "white"):
            self.image = IMAGES["SPR_WHITE_KING"]
            PlayKing.white_king_list.append(self)
        elif(col == "black"):
            self.image = IMAGES["SPR_BLACK_KING"]
            PlayKing.black_king_list.append(self)
        self.queen_side_castle_ability = False
        self.king_side_castle_ability = False
        self.castled = False
        super().__init__(coord, self.image, col)
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
            self.image = IMAGES["SPR_WHITE_KING_HIGHLIGHTED"]
        elif(self.color == "black"):
            self.image = IMAGES["SPR_BLACK_KING_HIGHLIGHTED"]
        self.select = 1
    def projected(self, game_controller):
        if self.taken_off_board == False:
            for grid in board.Grid.grid_list:
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.attack_count_increment(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.king_side_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
                if (ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    (grid.occupied == 0 or grid.occupied_piece_color != self.color) and
                    self.queen_side_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8)):
                        grid.attack_count_increment(self.color, self.coordinate)
    def spaces_available(self, game_controller):
        if((self.color == "white" and self.coordinate == 'e1') or (self.color == "black" and self.coordinate == 'e8')):
            self.castle_check(game_controller)
        for grid in board.Grid.grid_list:
            # Direct Enemy Threat refers to how many opposing color pieces are attacking square
            if self.color == "white":
                direct_enemy_threat = len(grid.coords_of_attacking_pieces['black']) > 0
            elif self.color == "black":
                direct_enemy_threat = len(grid.coords_of_attacking_pieces['white']) > 0
            # Projected Enemy Threat refers to threatening squares past the king
            projected_enemy_threat = grid.coordinate in game_controller.check_attacking_coordinates
            # If square does not have same color piece on it
            # If square is not directly threatened by opposing piece
            # If square is not in enemy piece projection OR if enemy piece in reach to be take-able
            if(grid.occupied_piece_color != self.color and direct_enemy_threat == False and \
               (projected_enemy_threat == False or grid.occupied_piece_color == self.enemy_color)):
                # King can have only one move in all directions
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])-1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0]) and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])-1:
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1]):
                    grid.highlight(self.color, self.coordinate)
                if ord(grid.coordinate[0]) == ord(self.coordinate[0])+1 and int(grid.coordinate[1]) == int(self.coordinate[1])+1:
                    grid.highlight(self.color, self.coordinate)
                # Castle
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])+2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    self.king_side_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8) and \
                    self.castled == False):
                        grid.highlight(self.color, self.coordinate)
                if(ord(grid.coordinate[0]) == ord(self.coordinate[0])-2 and int(grid.coordinate[1]) == int(self.coordinate[1]) and \
                    self.queen_side_castle_ability == 1 and (int(self.coordinate[1]) == 1 or int(self.coordinate[1])==8) and \
                    self.castled == False):
                        grid.highlight(self.color, self.coordinate)
    def no_highlight(self):
        if(self.color == "white"):
            if(self.prior_move_color == True):
                self.image = IMAGES["SPR_WHITE_KING_PRIORMOVE"]
            else:
                self.image = IMAGES["SPR_WHITE_KING"]
        elif(self.color == "black"):
            if(self.prior_move_color == True):
                self.image = IMAGES["SPR_BLACK_KING_PRIORMOVE"]
            else:
                self.image = IMAGES["SPR_BLACK_KING"]
        self.select = 0

