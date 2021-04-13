import pygame
import numpy as np

from . import cfg


class Particle:
    def __init__(self, x, y, status, beta, gamma, radius=cfg.PARTICLE_RADIUS, color=cfg.PARTICLE_COLOR, clock_tick=60):
        self.x = x
        self.y = y
        self.status = status

        self.radius = radius
        self.color = color

        self.update_circumference_coordinates()

        self.displacement = cfg.PARTICLE_DISPLACEMENT
        self.angle = self.random_angle()

        self.vel = cfg.PARTICLE_VELOCITY # velocity

        self.f = 0 # frame
        self.clock_tick = clock_tick

        self.recovery_frame = 0.0
        self.gamma = gamma
        self.beta = beta

        self.infected_count = 0

    def random_angle(self):
        return np.random.uniform(0, np.pi * 2)

    def next_direction(self):
        direction = np.random.uniform(0, np.pi * 2)
        self.angle = self.random_angle()

    def update_circumference_coordinates(self):
        self.top = abs(self.y) - self.radius
        self.right = abs(self.x) + self.radius
        self.bottom = abs(self.y) + self.radius
        self.left = abs(self.x) - self.radius

    def get_next_x_circumference_coordinates(self):
        d = (self.radius * 2)
        return abs(self.x) - d, abs(self.x) + d

    def get_next_y_curcumference_coordinates(self):
        d = (self.radius * 2)
        return abs(self.y) - d, abs(self.y) + d

    def update_coordinates(self):
        dx = np.sin(self.angle) * self.vel
        dy = np.cos(self.angle) * self.vel

        self.x += dx
        self.y -= dy

    def update_2d_vectors(self):
        self.f += 1
        if self.f > self.clock_tick:
            self.f = 0
            self.next_direction()

        self.update_coordinates()
        self.update_circumference_coordinates()

    def is_infected(self):
        return True if self.status == cfg.INFECTED_TYPE else False

    def infect(self, infectee):
        infectee.update_infected_count()

        # TODO probability
        self.status = cfg.INFECTED_TYPE
        self.color = cfg.INFECTED_COLOR

    def update_infected_count(self):
        if self.is_infected():
            self.infected_count += 1

    def update_recovery_frame(self):
        if self.is_infected() and self.infected_count > self.beta:
            if self.recovery_frame > 1:
                self.status = cfg.RECOVERED_TYPE
                self.color = cfg.RECOVERED_COLOR
            else:
                self.recovery_frame += self.gamma

    def bounce(self, wall_vector):
        """
        Discrete collision detection (has tunneling issue.. not a problem with particles :P)
        """
        if self.right >= wall_vector[2]:
            self.angle = -self.angle

        elif self.left <= wall_vector[0]:
            self.angle = -self.angle

        if self.bottom >= wall_vector[3]:
            self.angle = np.pi - self.angle

        elif self.top <= wall_vector[1]:
            self.angle = np.pi - self.angle
