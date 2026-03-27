import pygame
import initvar
import start_objects
import load_images_sounds as lis

PLAY_PANEL_SPRITES = pygame.sprite.Group()
GAME_MODE_SPRITES = pygame.sprite.Group()


def _clamp(value, lower=0.0, upper=1.0):
    return max(lower, min(upper, value))


def _lerp(a, b, t):
    return a + (b - a) * t


def _mix_color(a, b, t):
    return tuple(int(_lerp(a[i], b[i], t)) for i in range(len(a)))


def _draw_scaled_surface(screen, surf, rect, scale):
    if abs(scale - 1.0) < 0.001:
        screen.blit(surf, rect.topleft)
        return
    scaled_size = (
        max(1, int(round(rect.width * scale))),
        max(1, int(round(rect.height * scale))),
    )
    scaled = pygame.transform.smoothscale(surf, scaled_size)
    scaled_rect = scaled.get_rect(center=rect.center)
    screen.blit(scaled, scaled_rect.topleft)

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
def HelpButton(pos):            return Button("SPR_HELP_BUTTON",              pos)
def FlipBoardButton(pos):       return Button("SPR_FLIP_BOARD_BUTTON",        pos)

# — Subclasses with genuinely different behaviour —

class PlayEditSwitchButton:
    BTN_W = 160
    BTN_H = 52

    _ICON_SIZE = 10  # icon bounding box size in pixels

    def __init__(self, top_left):
        x, y = top_left
        self.rect = pygame.Rect(x, y, self.BTN_W, self.BTN_H)
        font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 14, bold=True)
        self._start_text = font.render("Start Game", True, (242, 247, 255))
        self._stop_text  = font.render("Stop Game",  True, (242, 247, 255))

    def game_mode_button(self, game_mode):
        pass  # kept for switch_modes compatibility; no longer image-based

    @staticmethod
    def _draw_play_icon(surf, cx, cy, size, color):
        """Draw a right-pointing triangle centred at (cx, cy)."""
        half = size // 2
        points = [(cx - half + 2, cy - half), (cx - half + 2, cy + half), (cx + half, cy)]
        pygame.draw.polygon(surf, color, points)

    @staticmethod
    def _draw_stop_icon(surf, cx, cy, size, color):
        """Draw a filled square centred at (cx, cy)."""
        half = size // 2
        pygame.draw.rect(surf, color, (cx - half, cy - half, size, size))

    def draw(self, screen, game_state, mousepos):
        is_hovered = self.rect.collidepoint(mousepos)
        is_pressed = is_hovered and pygame.mouse.get_pressed()[0]
        is_start   = (game_state == "setup")
        text_surf  = self._start_text if is_start else self._stop_text

        if is_start:
            bg     = (52, 110, 195, 230)
            border = (125, 180, 255, 255)
            if is_hovered:
                bg     = (68, 132, 220, 242)
                border = (162, 205, 255, 255)
        else:
            # Same component styling, with a slightly darker tone while active.
            bg     = (16,  34,  72, 168)
            border = (64,  90, 132, 190)
            if is_hovered:
                bg     = (24,  50,  96, 188)
                border = (82,  110, 158, 214)

        surf = pygame.Surface((self.BTN_W, self.BTN_H), pygame.SRCALPHA)
        pygame.draw.rect(surf, bg,     surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, border, surf.get_rect(), 1, border_radius=10)

        icon_gap = 6
        total_w  = self._ICON_SIZE + icon_gap + text_surf.get_width()
        x0 = (self.BTN_W - total_w) // 2
        cy = self.BTN_H // 2
        icon_color = (242, 247, 255)

        if is_start:
            self._draw_play_icon(surf, x0 + self._ICON_SIZE // 2, cy, self._ICON_SIZE, icon_color)
        else:
            self._draw_stop_icon(surf, x0 + self._ICON_SIZE // 2, cy, self._ICON_SIZE, icon_color)

        surf.blit(text_surf, (x0 + self._ICON_SIZE + icon_gap,
                              cy - text_surf.get_height() // 2))
        _draw_scaled_surface(screen, surf, self.rect, 0.98 if is_pressed else 1.0)


class SidebarActionButton:
    BTN_W = 160
    BTN_H = 52

    def __init__(self, top_left, label):
        x, y = top_left
        self.rect = pygame.Rect(x, y, self.BTN_W, self.BTN_H)
        font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 14, bold=True)
        self._text = font.render(label, True, (242, 247, 255))

    def draw(self, screen, mousepos, enabled=True):
        is_hovered = enabled and self.rect.collidepoint(mousepos)
        is_pressed = is_hovered and pygame.mouse.get_pressed()[0]

        bg = (16, 34, 72, 168) if enabled else (10, 18, 38, 120)
        border = (64, 90, 132, 190) if enabled else (46, 58, 84, 130)
        text = self._text.copy()
        if is_hovered:
            bg = (24, 50, 96, 188)
            border = (82, 110, 158, 214)
        if not enabled:
            text.set_alpha(150)

        surf = pygame.Surface((self.BTN_W, self.BTN_H), pygame.SRCALPHA)
        pygame.draw.rect(surf, bg, surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, border, surf.get_rect(), 1, border_radius=10)
        surf.blit(text, ((self.BTN_W - text.get_width()) // 2, (self.BTN_H - text.get_height()) // 2))
        _draw_scaled_surface(screen, surf, self.rect, 0.98 if is_pressed else 1.0)


class SidebarSectionPanel:
    def __init__(self, rect, label):
        self.rect = pygame.Rect(rect)
        font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 11, bold=True)
        self._label = font.render(label, True, (165, 195, 230))

    def draw(self, screen):
        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 22, 52, 185), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (72, 100, 148, 210), panel.get_rect(), 1, border_radius=12)
        panel.blit(self._label, (14, 12))

        sep_y = 12 + self._label.get_height() + 6
        sep = pygame.Surface((self.rect.width - 24, 1), pygame.SRCALPHA)
        sep.fill((90, 125, 178, 90))
        panel.blit(sep, (12, sep_y))

        screen.blit(panel, self.rect.topleft)


class RadioOption:
    TRANSITION_MS = 180
    PRESS_SCALE = 0.98

    def __init__(self, rect, mode, label_surface, label_x, indicator_color):
        self.rect = rect
        self.mode = mode
        self.label_surface = label_surface
        self.label_x = label_x
        self.indicator_color = indicator_color
        self._selected_t = 0.0
        self._hover_t = 0.0

    def update(self, delta_ms, is_hovered, is_selected):
        step = delta_ms / self.TRANSITION_MS if self.TRANSITION_MS else 1.0
        self._selected_t = _lerp(self._selected_t, 1.0 if is_selected else 0.0, _clamp(step))
        self._hover_t = _lerp(self._hover_t, 1.0 if is_hovered else 0.0, _clamp(step))

    def draw(self, screen, mousepos):
        is_hovered = self.rect.collidepoint(mousepos)
        is_pressed = is_hovered and pygame.mouse.get_pressed()[0]

        selected_bg = (44, 96, 182, 224)
        idle_bg = (12, 24, 54, 150)
        hover_bg = (22, 44, 90, 176)
        bg = _mix_color(idle_bg, hover_bg, self._hover_t)
        bg = _mix_color(bg, selected_bg, self._selected_t)

        selected_border = (145, 194, 255, 245)
        idle_border = (42, 62, 102, 150)
        hover_border = (72, 100, 148, 210)
        border = _mix_color(idle_border, hover_border, self._hover_t)
        border = _mix_color(border, selected_border, self._selected_t)

        text_idle = (212, 223, 240)
        text_selected = (244, 248, 255)
        text_color = _mix_color(text_idle, text_selected, self._selected_t)
        label = self.label_surface.copy()
        label.fill((*text_color, 255), special_flags=pygame.BLEND_RGBA_MULT)

        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, bg, surf.get_rect(), border_radius=10)
        pygame.draw.rect(surf, border, surf.get_rect(), 1, border_radius=10)

        indicator_center = (16, self.rect.height // 2)
        if self._selected_t > 0.02:
            ring_alpha = int(180 * self._selected_t)
            ring_color = (*_mix_color((95, 125, 170), (220, 235, 255), self._selected_t), ring_alpha)
            pygame.draw.circle(surf, ring_color, indicator_center, 9, 2)

            fill_radius = max(1, int(round(_lerp(2, 5, self._selected_t))))
            fill_alpha = int(_lerp(0, 255, self._selected_t))
            fill_color = self.indicator_color if self.indicator_color is not None else (170, 205, 255)
            fill = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(fill, (*fill_color, fill_alpha), (10, 10), fill_radius)
            surf.blit(fill, (indicator_center[0] - 10, indicator_center[1] - 10))

        surf.blit(label, (self.label_x, (self.rect.height - label.get_height()) // 2))
        _draw_scaled_surface(screen, surf, self.rect, self.PRESS_SCALE if is_pressed else 1.0)

class GameModeSelector:
    """Three-option selector: Play as White vs CPU / Play as Black vs CPU / Two Players.
    Replaces the old CPU-on/off and Black/White toggles. Only active in EDIT_MODE."""

    BTN_W = 160
    BTN_H = 52
    GAP = 8
    LABEL_X = 28

    _MODES = [
        ("cpu_white",   "Play as White vs CPU", (230, 230, 230)),
        ("cpu_black",   "Play as Black vs CPU", (30,  30,  30)),
        ("two_players", "Human vs Human",      (170, 205, 255)),
    ]

    def __init__(self, top_left):
        x, y = top_left
        # Section container drawn behind mode buttons + Start Game button
        self._section_rect = pygame.Rect(
            initvar.GAME_SETUP_SECTION_X, initvar.GAME_SETUP_SECTION_Y,
            initvar.GAME_SETUP_SECTION_W, initvar.GAME_SETUP_SECTION_H,
        )
        self._group_rect = pygame.Rect(
            x - 2,
            y - 4,
            self.BTN_W + 4,
            len(self._MODES) * self.BTN_H + (len(self._MODES) - 1) * self.GAP + 8,
        )
        self._divider_y = initvar.PLAY_EDIT_SWITCH_BUTTON_TOPLEFT[1] - 11
        lf = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 11, bold=True)
        self._section_label = lf.render("GAME SETUP", True, (165, 195, 230))
        # Find the largest font size where every label fits its pill, then render all at that size
        chosen_sz = 14
        for sz in (14, 13, 12, 11, 10):
            f = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, sz, bold=True)
            if all(
                f.render(label, True, (242, 247, 255)).get_width()
                    <= self.BTN_W - self.LABEL_X - 10
                for _, label, _ in self._MODES
            ):
                chosen_sz = sz
                break
        f = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, chosen_sz, bold=True)
        self._options = []
        for i, (mode, label, indicator_color) in enumerate(self._MODES):
            rect = pygame.Rect(x, y + i * (self.BTN_H + self.GAP), self.BTN_W, self.BTN_H)
            label_surface = f.render(label, True, (242, 247, 255))
            self._options.append(RadioOption(rect, mode, label_surface, self.LABEL_X, indicator_color))
        self._last_tick = pygame.time.get_ticks()

    @staticmethod
    def _selected_mode(cpu_mode, cpu_color):
        if not cpu_mode:
            return "two_players"
        # Option ids are named for the human player's color, not the CPU's color.
        if cpu_color == "black":
            return "cpu_white"
        return "cpu_black"

    def hit(self, mousepos, game_mode):
        if game_mode != 0:
            return None
        for option in self._options:
            if option.rect.collidepoint(mousepos):
                return option.mode
        return None

    def draw(self, screen, game_mode, cpu_mode, cpu_color, mousepos):
        now = pygame.time.get_ticks()
        delta_ms = now - self._last_tick
        self._last_tick = now

        sx, sy = self._section_rect.x, self._section_rect.y
        sw, sh = self._section_rect.width, self._section_rect.height

        # ── Section container ──
        sec = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.rect(sec, (10, 22, 52, 185), sec.get_rect(), border_radius=12)
        pygame.draw.rect(sec, (72, 100, 148, 210), sec.get_rect(), 1, border_radius=12)
        screen.blit(sec, (sx, sy))

        # ── "GAME SETUP" label ──
        label_x = sx + 14
        label_y = sy + 12
        screen.blit(self._section_label, (label_x, label_y))

        # Thin separator line below the label
        sep_y = label_y + self._section_label.get_height() + 6
        sep = pygame.Surface((sw - 24, 1), pygame.SRCALPHA)
        sep.fill((90, 125, 178, 90))
        screen.blit(sep, (sx + 12, sep_y))

        selected = self._selected_mode(cpu_mode, cpu_color)
        if game_mode == 0:
            for option in self._options:
                is_selected = (option.mode == selected)
                is_hovered = option.rect.collidepoint(mousepos)
                option.update(delta_ms, is_hovered, is_selected)
                option.draw(screen, mousepos)
        else:
            # Draw radio options frozen (no hover) then dim with an overlay.
            for option in self._options:
                option.update(delta_ms, False, option.mode == selected)
                option.draw(screen, (-9999, -9999))
                dim = pygame.Surface(option.rect.size, pygame.SRCALPHA)
                dim.fill((0, 0, 0, 80))
                screen.blit(dim, option.rect.topleft)

        # Divider between the radio group and the primary action.
        divider = pygame.Surface((sw - 28, 1), pygame.SRCALPHA)
        divider.fill((90, 125, 178, 62))
        screen.blit(divider, (sx + 14, self._divider_y))


class StartingTurnSelector:
    """Two-option selector for the side to move in setup mode."""

    BTN_W = 160
    BTN_H = 52
    GAP = 8
    LABEL_X = 28

    _OPTIONS = [
        ("white", "White to move", (230, 230, 230)),
        ("black", "Black to move", (30, 30, 30)),
    ]

    def __init__(self, top_left):
        x, y = top_left
        self._group_rect = pygame.Rect(
            x - 2,
            y - 4,
            self.BTN_W + 4,
            len(self._OPTIONS) * self.BTN_H + (len(self._OPTIONS) - 1) * self.GAP + 8,
        )
        lf = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 11, bold=True)
        self._section_label = lf.render("STARTING TURN", True, (165, 195, 230))
        font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, 13, bold=True)
        self._options = []
        for i, (turn_key, label, indicator_color) in enumerate(self._OPTIONS):
            rect = pygame.Rect(x, y + i * (self.BTN_H + self.GAP), self.BTN_W, self.BTN_H)
            label_surface = font.render(label, True, (242, 247, 255))
            self._options.append(RadioOption(rect, turn_key, label_surface, self.LABEL_X, indicator_color))
        self._last_tick = pygame.time.get_ticks()
        self._label_x = x
        self._label_y = y - 30
        self._separator_y = y - 8

    def hit(self, mousepos, game_mode):
        if game_mode != 0:
            return None
        for option in self._options:
            if option.rect.collidepoint(mousepos):
                return option.mode
        return None

    def draw(self, screen, game_mode, starting_turn, mousepos):
        now = pygame.time.get_ticks()
        delta_ms = now - self._last_tick
        self._last_tick = now

        screen.blit(self._section_label, (self._label_x, self._label_y))
        sep = pygame.Surface((initvar.GAME_SETUP_SECTION_W - 28, 1), pygame.SRCALPHA)
        sep.fill((90, 125, 178, 90))
        screen.blit(sep, (self._label_x, self._separator_y))

        if game_mode == 0:
            for option in self._options:
                is_selected = (option.mode == starting_turn)
                is_hovered = option.rect.collidepoint(mousepos)
                option.update(delta_ms, is_hovered, is_selected)
                option.draw(screen, mousepos)
        else:
            for option in self._options:
                option.update(delta_ms, False, option.mode == starting_turn)
                option.draw(screen, (-9999, -9999))
                dim = pygame.Surface(option.rect.size, pygame.SRCALPHA)
                dim.fill((0, 0, 0, 80))
                screen.blit(dim, option.rect.topleft)


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
