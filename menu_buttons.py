import pygame
import initvar
import start_objects
import load_images_sounds as lis

PLAY_PANEL_SPRITES = pygame.sprite.Group()
GAME_MODE_SPRITES = pygame.sprite.Group()

class Button(pygame.sprite.Sprite):
    def __init__(self, image_key, pos, sprite_group=None,
                 active_in_mode=None, requires_hover=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = lis.IMAGES[image_key]
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self._active_in_mode = active_in_mode
        self._requires_hover = requires_hover
        self.clickable = True
        self.hover = False
        if sprite_group is not None:
            sprite_group.add(self)

    def update(self, game_mode):
        self.clickable = (self._active_in_mode is None
                          or game_mode == self._active_in_mode)

    def draw(self, screen, game_mode=None, hover=False):
        if self._requires_hover:
            if game_mode == self._active_in_mode and hover:
                self.clickable = True
                screen.blit(self.image, self.rect.topleft)
            else:
                self.clickable = False
        else:
            screen.blit(self.image, self.rect.topleft)

# — Shims: preserve old call sites in main.py —
def ClearButton(pos):           return Button("SPR_CLEAR_BUTTON",            pos, start_objects.START_SPRITES, active_in_mode=0)
def InfoButton(pos):            return Button("SPR_INFO_BUTTON",             pos, start_objects.START_SPRITES, active_in_mode=0)
def ResetBoardButton(pos):      return Button("SPR_RESET_BOARD_BUTTON",      pos, start_objects.START_SPRITES, active_in_mode=0)
def ColorButton(pos):           return Button("SPR_COLOR_BUTTON",            pos, start_objects.START_SPRITES, active_in_mode=0)
def GamePropertiesButton(pos):  return Button("SPR_GAME_PROPERTIES_BUTTON",  pos, start_objects.START_SPRITES, active_in_mode=0)

def BeginningMoveButton(pos):   return Button("SPR_BEGINNING_MOVE_BUTTON",   pos, PLAY_PANEL_SPRITES, active_in_mode=1)
def LastMoveButton(pos):        return Button("SPR_LAST_MOVE_BUTTON",         pos, PLAY_PANEL_SPRITES, active_in_mode=1)
def NextMoveButton(pos):        return Button("SPR_NEXT_MOVE_BUTTON",         pos, PLAY_PANEL_SPRITES, active_in_mode=1)
def PrevMoveButton(pos):        return Button("SPR_PREV_MOVE_BUTTON",         pos, PLAY_PANEL_SPRITES, active_in_mode=1)
def UndoMoveButton(pos):        return Button("SPR_UNDO_MOVE_BUTTON",         pos, PLAY_PANEL_SPRITES, active_in_mode=1)

def PosSaveFileButton(pos):     return Button("SPR_POS_SAVE_FILE_BUTTON",     pos, active_in_mode=0, requires_hover=True)
def PGNSaveFileButton(pos):     return Button("SPR_PGN_SAVE_FILE_BUTTON",     pos, active_in_mode=1, requires_hover=True)

def SaveFilePlaceholder(pos):   return Button("SPR_SAVE_FILE_PLACEHOLDER",    pos)
def LoadFilePlaceholder(pos):   return Button("SPR_LOAD_FILE_PLACEHOLDER",    pos)
def FlipBoardButton(pos):       return Button("SPR_FLIP_BOARD_BUTTON",        pos)

# — Subclasses with genuinely different behaviour —

class PlayEditSwitchButton(Button):
    def __init__(self, pos):
        super().__init__("SPR_PLAY_BUTTON", pos, GAME_MODE_SPRITES)
    def game_mode_button(self, game_mode):
        if game_mode == 0:
            self.image = lis.IMAGES["SPR_PLAY_BUTTON"]
        elif game_mode == 1:
            self.image = lis.IMAGES["SPR_STOP_BUTTON"]
        return self.image

class CPUButton(Button):
    def __init__(self, pos, cpu_mode):
        super().__init__("SPR_CPU_BUTTON_OFF", pos)
        self.toggle(cpu_mode)
    def draw(self, screen, game_mode):
        if game_mode == 0:
            self.clickable = True
            screen.blit(self.image, self.rect.topleft)
        else:
            self.clickable = False
    def toggle(self, cpu_mode):
        self.image = lis.IMAGES["SPR_CPU_BUTTON_ON" if cpu_mode else "SPR_CPU_BUTTON_OFF"]

class ScrollUpButton(Button):
    def __init__(self, pos):
        super().__init__("SPR_SCROLL_UP_BUTTON", pos)
        self.activate = False
    def draw(self, screen):
        if PanelRectangles.scroll_range[0] != 1:
            self.activate = True
            screen.blit(self.image, self.rect.topleft)
        else:
            self.activate = False

class ScrollDownButton(Button):
    def __init__(self, pos):
        super().__init__("SPR_SCROLL_DOWN_BUTTON", pos)
        self.activate = False
    def draw(self, screen, latest_move_number):
        if PanelRectangles.scroll_range[1] != latest_move_number and latest_move_number > initvar.MOVES_PANE_MAX_MOVES:
            self.activate = True
            screen.blit(self.image, self.rect.topleft)
        else:
            self.activate = False

class PanelRectangles(pygame.sprite.Sprite):
    scroll_range = [1, initvar.MOVES_PANE_MAX_MOVES]
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
    def update_Y(self):
        if self.move_number >= PanelRectangles.scroll_range[0] and self.move_number <= PanelRectangles.scroll_range[1]:
            # Include rectangle in pane
            self.text_is_visible = True
            self.y = initvar.MOVES_PANE_Y_BEGIN + initvar.LINE_SPACING*((self.move_number+1) - PanelRectangles.scroll_range[0])
            self.rect.topleft = (self.x, self.y)
        else:
            # Hide rectangle in pane
            self.text_is_visible = False

class MoveNumberRectangle(PanelRectangles, pygame.sprite.Sprite):
    # Rectangles behind the move number
    rectangle_list = []
    rectangle_dict = {}
    def __init__(self, move_number, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.x = x - 7*(len(str(move_number))-1) # X moves backward by 7 after each digit (ie 10 moves is 7, 100 moves is 14, etc)
        super().__init__(move_number, self.x, y, width, height)
        self.text = str(self.move_number) + "."
        MoveNumberRectangle.rectangle_list.append(self)
        MoveNumberRectangle.rectangle_dict[move_number] = self

class PieceMoveRectangle(PanelRectangles, pygame.sprite.Sprite):
    # Rectangles behind the moves themselves
    rectangle_list = []
    rectangle_dict = {}
    def __init__(self, move_number, move_notation, move_color, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        super().__init__(move_number, x, y, width, height)
        self.image.fill(initvar.RECTANGLE_FILL_COLOR)
        self.move_notation = move_notation
        self.move_color = move_color
        PieceMoveRectangle.rectangle_list.append(self)
        if move_color == 'white_move':
            PieceMoveRectangle.rectangle_dict[move_number]['white_move'] = self
        else:
            PieceMoveRectangle.rectangle_dict[move_number]['black_move'] = self
        #PieceMoveRectangle.rectangle_dict[move_number].append(self)
    def draw(self, screen):
        if self.text_is_visible == True:
            highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, (138, 176, 235, 130), highlight.get_rect(), border_radius=7)
            pygame.draw.rect(highlight, (207, 227, 255, 210), highlight.get_rect(), 1, border_radius=7)
            screen.blit(highlight, self.rect.topleft)
        else:
            pass
