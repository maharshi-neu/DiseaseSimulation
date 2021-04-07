import pygame
import numpy as np
from entity import Particle

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREY = (125, 125, 125)

SUSCEPTIBLE = 3
INFECTED = 2
RECOVERED = 1
REMOVED = 0

SUSCEPTIBLE_COLOR = GREEN
INFECTED_COLOR = RED
RECOVERED_COLOR = GREY

class SIM:
    def process_input(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def __init__(self, T=10, I0=3, R0=0, width=1024, height=600):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock_tick = 60

        pygame.display.set_caption("Disease Simulator")

        self.X, self.Y = width, height

        # Wall co-ordinates
        self.wall_width = 5
        self.wall_left = self.wall_width
        self.wall_top = self.wall_width
        self.wall_right =  self.X - self.wall_width
        self.wall_bottom = self.Y - self.wall_width

        self.window = pygame.display.set_mode((self.X, self.Y))

        self.running = True

        self.susceptible_container = list()
        self.infected_container = list()
        self.recovered_container = list()
        self.all_container = list()

        self.n_susceptible = T - I0 - R0
        self.n_infected = I0
        self.n_recovered = R0
        self.T = T
        self.beta = 0.5
        self.gamma = 0.2

        self.init_groups()

    def draw_walls(self):
        wall_color = (50, 0, 150) # RGB
        # left wall
        leftRect = pygame.Rect(0, 0, self.wall_left, self.Y) # left, top, width, height
        pygame.draw.rect(self.window, wall_color, leftRect)
        # top wall
        topRect = pygame.Rect(0, 0, self.X, self.wall_top) # left, top, width, height
        pygame.draw.rect(self.window, wall_color, topRect)
        # right wall
        rightRect = pygame.Rect(self.wall_right, 0, self.wall_right, self.Y) # left, top, width, height
        pygame.draw.rect(self.window, wall_color, rightRect)
        # bottom wall
        bottomRect = pygame.Rect(0, self.wall_bottom, self.X, self.wall_bottom) # left, top, width, height
        pygame.draw.rect(self.window, wall_color, bottomRect)

    def init_groups(self):
        x, y = self.X / 2, self.Y / 2
        for _ in range(self.n_susceptible):
            p = Particle(x, y, SUSCEPTIBLE, color=GREEN, clock_tick=self.clock_tick)
            self.susceptible_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_infected):
            p = Particle(x, y, INFECTED, color=RED, clock_tick=self.clock_tick)
            self.infected_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_recovered):
            p = Particle(x, y, RECOVERED, color=GREY, clock_tick=self.clock_tick)
            self.infected_container.append(p)
            self.all_container.append(p)

    def update(self):
        for p in self.all_container:
            p.update_2d_vectors()

    def handle_collision(self, p):
        """
        Discrete collision detection (has tunneling issue)
        """
        if p.left <= self.wall_left or p.right >= self.wall_right:
            p.flip_x()
            print(p.x)
        elif p.top <= self.wall_top or p.bottom >= self.wall_bottom:
            p.flip_y()
            print(p.y)

    def render(self):
        self.window.fill((0, 0, 0))
        self.draw_walls()

        for p in self.all_container:
            self.handle_collision(p)

        for p in self.all_container:
            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)

        pygame.display.update()

    def run(self):
        self.f = 0
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.clock_tick)

        pygame.quit()


if __name__ == "__main__":
    sim = SIM()
    sim.run()
