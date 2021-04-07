# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 12:06:29 2020

@author: Brad
"""

class InfoScreen():
    def __init__(self,screen):
        self.screen = screen
        self.title = INFO_SCREEN
        self.clock = pygame.time.Clock()
        self.main_loop()

    def main_loop(self):
        global MENUON
        while MENUON == 2:
            self.clock.tick(60)
            self.screen.blit(self.title, (0, 0))
            events = pygame.event.get()
            pygame.display.flip()
            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        MENUON = 1