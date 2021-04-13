import pygame
import numpy as np

from . import Particle, cfg

# ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'


class Simulator:
    def process_input(self):
        """
            Keyboard input for exitting
        """
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock_tick = cfg.FPS

        pygame.display.set_caption(cfg.GAME_TITLE)

        self.X, self.Y = cfg.GAME_WIDTH, cfg.GAME_HEIGHT

        # Wall co-ordinates
        self.wall_width = cfg.WALL_SIZE
        self.wall_left = self.wall_width
        self.wall_top = self.wall_width
        self.wall_right =  self.X - self.wall_width
        self.wall_bottom = self.Y - self.wall_width

        self.wall_vector = [
                self.wall_left,
                self.wall_top,
                self.wall_right,
                self.wall_bottom
        ]

        self.window = pygame.display.set_mode((self.X, self.Y))

        self.running = True

        self.susceptible_container = list()
        self.infected_container = list()
        self.recovered_container = list()
        self.all_container = list()

        self.n_susceptible = cfg.TOTAL - cfg.I0 - cfg.R0
        self.n_infected = cfg.I0
        self.n_recovered = cfg.R0
        self.T = cfg.TOTAL
        self.beta = 2
        self.gamma = 20 / self.T

        self.font = pygame.font.SysFont("Arial", 18)

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

    def random_x(self):
        r2 = cfg.PARTICLE_RADIUS * 2
        return np.random.randint(r2, self.X - r2)

    def random_y(self):
        r2 = cfg.PARTICLE_RADIUS * 2
        return np.random.randint(r2, self.Y - r2)

    def init_groups(self):
        min_ct = self.clock_tick / 2
        max_ct = self.clock_tick * 2

        for _ in range(self.n_susceptible):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), cfg.SUSCEPTIBLE_TYPE, self.beta, self.gamma,
                    color=cfg.SUSCEPTIBLE_COLOR, clock_tick=fps)
            self.susceptible_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_infected):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), cfg.INFECTED_TYPE, self.beta, self.gamma,
                    color=cfg.INFECTED_COLOR, clock_tick=fps)
            self.infected_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_recovered):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), cfg.RECOVERED_TYPE, self.beta, self.gamma,
                    color=cfg.RECOVERED_COLOR, clock_tick=fps)
            self.infected_container.append(p)
            self.all_container.append(p)

    def euclidean_distance(self, particle, other_particle):
        x0, y0 = particle.x, particle.y
        x1, y1 = other_particle.x, other_particle.y
        return np.sqrt(np.square(x1 - x0) + np.square(y1 - y0))

    def handle_particle_collision(self, i):
        # sweep n prune
        diameter = cfg.PARTICLE_RADIUS * 2
        newly_infected = list()

        ip = self.all_container[i]
        for j in range(i + 1, len(self.all_container)):
            jp = self.all_container[j]
            condition = (jp.status == cfg.INFECTED_TYPE) + (ip.status == cfg.INFECTED_TYPE)
            if condition == 1:
                d = self.euclidean_distance(ip, jp)
                if diameter >= d:
                    if jp.status == cfg.INFECTED_TYPE:
                        ip.infect(jp)
                        newly_infected.append(ip)
                    else:
                        jp.infect(ip)
                        newly_infected.append(jp)
                else:
                    break
            else:
                break
        return newly_infected

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, 1, pygame.Color("coral"))
        return fps_text

    def update_containers(self, newly_infected):
        if newly_infected:
            self.susceptible_container = [
                    sus for sus in self.susceptible_container if not sus.status == cfg.INFECTED_TYPE]
            self.infected_container.extend(newly_infected)

    def update(self):
        for p in self.all_container:
            p.update_2d_vectors()

    def render(self):
        self.window.fill(cfg.BACKGROUND)
        self.draw_walls()

        self.all_container.sort(key=lambda p: p.x)

        newly_infected = list()
        for pi in range(len(self.all_container)):
            p = self.all_container[pi]

            p.bounce(self.wall_vector)

            if pi < self.T - 1:
                newly_infected = self.handle_particle_collision(pi)

            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)
            p.update_recovery_frame()

        self.update_containers(newly_infected)

        self.window.blit(self.update_fps(), (10,0))

        pygame.display.update()

    def run(self):
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.clock_tick)

        pygame.quit()


