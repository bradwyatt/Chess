import pygame
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
    
class RestartButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_RESTART_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class ColorButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_COLOR_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        
class SaveFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_SAVE_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
    
class LoadFileButton(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = IMAGES["SPR_LOAD_FILE_BUTTON"]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

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