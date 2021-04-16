import pygame
import numpy as np

from . import random_angle
from . import cfg


class Particle:
    def __init__(self, x, y, status, radius=cfg.PARTICLE_RADIUS, color=cfg.PARTICLE_COLOR, clock_tick=60):
        self.x = x
        self.y = y
        self.status = status

        self.radius = radius
        self.color = color

        self.update_circumference_coordinates()

        self.displacement = cfg.PARTICLE_DISPLACEMENT
        self.angle = random_angle()

        self.vel = cfg.PARTICLE_VELOCITY # velocity

        self.f = 0 # frame
        self.clock_tick = clock_tick

        self.infected_particles = list()
        self.my_boundries = dict()
        self.infected_since = 0

    def update_circumference_coordinates(self):
        self.top = abs(self.y) - self.radius
        self.right = abs(self.x) + self.radius
        self.bottom = abs(self.y) + self.radius
        self.left = abs(self.x) - self.radius

    def update_coordinates(self):
        dx = np.sin(self.angle) * self.vel
        dy = np.cos(self.angle) * self.vel

        self.x += dx
        self.y -= dy

    def update_2d_vectors(self):
        self.f += 1
        if self.f > self.clock_tick * 2:
            self.f = 0
            self.angle = random_angle()

        self.update_coordinates()
        self.update_circumference_coordinates()

    def is_infected(self):
        return True if self.status == cfg.INFECTED_TYPE else False

    def update_infected_count(self, infected):
        if self.is_infected():
            self.infected_particles.append(infected)

    def infect(self, infectee, time):
        infectee.update_infected_count(self)

        self.status = cfg.INFECTED_TYPE
        self.color = cfg.INFECTED_COLOR
        self.infected_since = time

    def recover(self, day):
        if self.is_infected() and (day - self.infected_since) >= cfg.RECOVERED_PERIOD_IN_DAYS:
            self.status = cfg.RECOVERED_TYPE
            self.color = cfg.RECOVERED_COLOR

