import pygame

from . import cfg
from . import Simulator
from . import MainMenu


class Game():
    def __init__(self):
        pygame.init()
        self.running = True
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False
        self.display = pygame.Surface((cfg.WIDTH, cfg.HEIGHT))
        self.window = pygame.display.set_mode(((cfg.WIDTH, cfg.HEIGHT)))

        self.sim = Simulator(self)
        self.simulate = False

        self.main_menu = MainMenu(self)
        self.curr_menu = self.main_menu

    def run(self):
        while self.running:
            self.curr_menu.display_menu()
            self.check_events()

            if self.simulate:
                self.sim.run()

            pygame.display.update()
            self.reset_keys()
        pygame.quit()

    def check_events(self):
        """
            Keyboard input for exitting
        """
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
            self.curr_menu.run_display = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            if event.key == pygame.K_RETURN:
                self.START_KEY = True
            if event.key == pygame.K_BACKSPACE:
                self.BACK_KEY = True
            if event.key == pygame.K_DOWN:
                self.DOWN_KEY = True
            if event.key == pygame.K_UP:
                self.UP_KEY = True

    def reset_keys(self):
        self.UP_KEY, self.DOWN_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False

    def draw_text(self, text, size, x, y ):
        font = pygame.font.SysFont(None, 18)
        text_surface = font.render(text, True, cfg.WHITE)
        text_rect = text_surface.get_rect()
        text_rect.center = (x,y)
        self.display.blit(text_surface,text_rect)





