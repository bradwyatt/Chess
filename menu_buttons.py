import pygame
import initvar
from load_images_sounds import *

class ClearButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_CLEAR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class InfoButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_INFO_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class ResetBoardButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_RESET_BOARD_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class ColorButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_COLOR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class PosSaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_POS_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class PosLoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_POS_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class PGNSaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PGN_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def draw(self, screen):
        screen.blit(self.image, (self.rect.topleft))
    
class PGNLoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PGN_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def draw(self, screen):
        screen.blit(self.image, (self.rect.topleft))

class FlipBoardButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_FLIP_BOARD_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class GamePropertiesButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_GAME_PROPERTIES_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class ScrollUpButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SCROLL_UP_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def draw(self, screen):
        if MoveNumberRectangle.scroll_range[0] != 1:
            screen.blit(self.image, (self.rect.topleft))
        else:
            pass
        
class ScrollDownButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SCROLL_DOWN_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    def draw(self, screen, latest_move_number):
        if MoveNumberRectangle.scroll_range[1] != latest_move_number and latest_move_number >= 20:
            screen.blit(self.image, (self.rect.topleft))
        else:
            pass

class BeginningMoveButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_BEGINNING_MOVE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)
        
class LastMoveButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_LAST_MOVE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)
        
class NextMoveButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_NEXT_MOVE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)

class PrevMoveButton(pygame.sprite.Sprite):
    def __init__(self, pos, PLAY_SPRITES):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_PREV_MOVE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        PLAY_SPRITES.add(self)
        
class PanelRectangles(pygame.sprite.Sprite):
    def __init__(self, move_number, x, y, width, height):
        self.x = x
        self.y = y
        self.image = pygame.Surface((height, width))
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        self.height = height
        self.width = width
        self.move_number = move_number
        self.text_is_visible = True
        
class PieceMoveRectangle(PanelRectangles, pygame.sprite.Sprite):
    rectangle_list = []
    rectangle_dict = {}
    def __init__(self, move_number, move_notation, move_color, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        super().__init__(move_number, x, y, width, height)
        self.image.fill((255, 211, 0))
        self.move_notation = move_notation
        self.move_color = move_color
        PieceMoveRectangle.rectangle_list.append(self)
        PieceMoveRectangle.rectangle_dict[move_number].append(self)
    def draw(self, screen):
        if self.text_is_visible == True:
            # Makes sure that all other rectangles overlapping this one that have invisible text are NOT selected
            screen.blit(self.image, (self.rect.topleft))
        else:
            pass
    def update_Y(self):
        if self.move_number >= MoveNumberRectangle.scroll_range[0] and self.move_number <= MoveNumberRectangle.scroll_range[1]:
            # Include rectangle
            self.text_is_visible = True
            self.y = initvar.MOVES_PANE_Y_BEGIN + initvar.LINE_SPACING*((self.move_number+1) - MoveNumberRectangle.scroll_range[0])
            self.rect.topleft = (self.x, self.y)
        else:
            # Hide rectangle
            self.text_is_visible = False
        
class MoveNumberRectangle(PanelRectangles, pygame.sprite.Sprite):
    rectangle_list = []
    rectangle_dict = {}
    scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
    def __init__(self, move_number, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.x = x - 7*(len(str(move_number))-1) # X moves backward by 7 after each digit (ie 10 moves is 7, 100 moves is 14, etc)
        super().__init__(move_number, self.x, y, width, height)
        self.text = str(self.move_number) + "."
        MoveNumberRectangle.rectangle_list.append(self)
        MoveNumberRectangle.rectangle_dict[move_number] = self
    def update_Y(self):
        if self.move_number >= MoveNumberRectangle.scroll_range[0] and self.move_number <= MoveNumberRectangle.scroll_range[1]:
            # Include rectangle
            self.text_is_visible = True
            self.y = initvar.MOVES_PANE_Y_BEGIN + initvar.LINE_SPACING*((self.move_number+1) - MoveNumberRectangle.scroll_range[0])
            self.rect.topleft = (self.x, self.y)
        else:
            # Hide rectangle
            self.text_is_visible = False
            

