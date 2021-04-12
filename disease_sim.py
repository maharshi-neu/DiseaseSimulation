import pygame
import numpy as np

from conf import *
from entity import *

# ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'


class SIM:
    def process_input(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def __init__(self, RT, T, I0, R0, width=800, height=600):
        self.RT = RT

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
        r2 = PARTICLE_RADIUS * 2
        return np.random.randint(r2, self.X - r2)

    def random_y(self):
        r2 = PARTICLE_RADIUS * 2
        return np.random.randint(r2, self.Y - r2)

    def init_groups(self):
        min_ct = self.clock_tick / 2
        max_ct = self.clock_tick * 2

        for _ in range(self.n_susceptible):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), SUSCEPTIBLE_TYPE,
                    color=SUSCEPTIBLE_COLOR, clock_tick=fps)
            self.susceptible_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_infected):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), INFECTED_TYPE,
                    color=INFECTED_COLOR, clock_tick=fps)
            self.infected_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_recovered):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    self.random_x(), self.random_y(), RECOVERED_TYPE,
                    color=RECOVERED_COLOR, clock_tick=fps)
            self.infected_container.append(p)
            self.all_container.append(p)

    def handle_wall_collision(self, p):
        """
        Discrete collision detection (has tunneling issue.. tmp fix with threshold)
        """
        if p.left <= self.wall_left or p.right >= self.wall_right:
            p.flip_x()
        if p.top <= self.wall_top or p.bottom >= self.wall_bottom:
            p.flip_y()

    def euclidean_distance(self, particle, other_particle):
        x0, y0 = particle.x, particle.y
        x1, y1 = other_particle.x, other_particle.y
        return np.sqrt(np.square(x1 - x0) + np.square(y1 - y0))

    def handle_particle_collision(self):
        # brute force
        diameter = PARTICLE_RADIUS * 2
        newly_infected = list()

        for i in self.infected_container:
            for s in self.susceptible_container:
                d = self.euclidean_distance(i, s)
                if diameter >= d:
                    s.infect()
                    newly_infected.append(s)

        self.susceptible_container = [sus for sus in self.susceptible_container if not sus.status == INFECTED_TYPE]
        self.infected_container.extend(newly_infected)

    def handle_particle_collision(self):
        # sweep n prune
        diameter = PARTICLE_RADIUS * 2
        newly_infected = list()

        self.all_container.sort(key=lambda p: p.x)
        for i in range(0, len(self.all_container) - 1):
            ip = self.all_container[i]
            for j in range(i + 1, len(self.all_container)):
                jp = self.all_container[j]
                condition = (jp.status == INFECTED_TYPE) + (ip.status == INFECTED_TYPE)
                if condition == 1:
                    d = self.euclidean_distance(ip, jp)
                    if diameter >= d:
                        if jp.status == INFECTED_TYPE:
                            ip.infect()
                            newly_infected.append(ip)
                        else:
                            jp.infect()
                            newly_infected.append(jp)
                    else:
                        break
                else:
                    break

        if newly_infected:
            self.susceptible_container = [sus for sus in self.susceptible_container if not sus.status == INFECTED_TYPE]
            self.infected_container.extend(newly_infected)

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, 1, pygame.Color("coral"))
        return fps_text

    def update(self):
        for p in self.all_container:
            p.update_2d_vectors()

    def render(self):
        self.window.fill((0, 0, 0))
        self.draw_walls()
        self.window.blit(self.update_fps(), (10,0))

        self.handle_particle_collision()

        for p in self.all_container:
            self.handle_wall_collision(p)

        for p in self.all_container:
            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)

        pygame.display.update()

    def run(self):
        rt = 0

        while self.running and rt < self.RT:
            rt += 1
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(self.clock_tick)

        pygame.quit()


if __name__ == "__main__":
    run_time = 5000 # in ticks
    T = 1000 # # of particles
    I0 = 1 # initial infected
    R0 = 0 # initial removed
    width = 1300
    height = 600
    sim = SIM(run_time, T, I0, R0, width, height)
    sim.run()

