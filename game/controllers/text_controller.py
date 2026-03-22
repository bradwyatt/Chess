import pygame
import initvar


class TextController():
    """
    Handle all text objects in this class
    """
    universal_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, initvar.UNIVERSAL_FONT_SIZE)
    move_notation_font = pygame.font.SysFont(initvar.UNIVERSAL_FONT_NAME, initvar.MOVE_NOTATION_FONT_SIZE)
    coor_A_text = universal_font.render("a", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_B_text = universal_font.render("b", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_C_text = universal_font.render("c", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_D_text = universal_font.render("d", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_E_text = universal_font.render("e", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_F_text = universal_font.render("f", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_G_text = universal_font.render("g", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_H_text = universal_font.render("h", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_1_text = universal_font.render("1", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_2_text = universal_font.render("2", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_3_text = universal_font.render("3", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_4_text = universal_font.render("4", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_5_text = universal_font.render("5", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_6_text = universal_font.render("6", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_7_text = universal_font.render("7", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_8_text = universal_font.render("8", 1, initvar.UNIVERSAL_TEXT_COLOR)
    coor_letter_text_list = [coor_A_text, coor_B_text, coor_C_text, coor_D_text, coor_E_text, coor_F_text, coor_G_text, coor_H_text]
    coor_number_text_list = [coor_8_text, coor_7_text, coor_6_text, coor_5_text, coor_4_text, coor_3_text, coor_2_text, coor_1_text]
    check_checkmate_text = ""

    @classmethod
    def remove_check_checkmate_text(cls):
        """
        Not in check or checkmate, or resetting the game
        """
        cls.check_checkmate_text = ""

    @classmethod
    def flip_board(cls):
        """
        Coordinate texts flip when the board flips
        """
        cls.coor_letter_text_list.reverse()
        cls.coor_number_text_list.reverse()
