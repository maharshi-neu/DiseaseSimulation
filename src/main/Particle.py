import pygame
import numpy as np

from . import random_angle, uniform_probability, euclidean_distance
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
        self.is_masked = False
        self.trans_probab = cfg.TRANSMISSION_PROBABILITY
        self.quarantined = False
        self.will_show_symptoms = True
        self.destination = None

    @property
    def is_travelling(self):
        return True if self.destination else False

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

    def travel_flight_mode(self):
        d, _, _ = euclidean_distance(self.x, self.y, self.destination[0], self.destination[1])
        if d > 10:
            self.angle = np.arctan2(self.destination[1] - self.y, self.destination[0] - self.x)
            self.x += np.cos(self.angle) * self.vel
            self.y += np.sin(self.angle) * self.vel
            self.update_circumference_coordinates()
        else:
            self.destination = None
            self.vel /= 4

    def update_2d_vectors(self):
        if self.is_travelling:
            self.travel_flight_mode()
            return
        self.f += 1
        if self.f > self.clock_tick * 2:
            self.f = 0
            self.angle = random_angle()

        self.update_coordinates()
        self.update_circumference_coordinates()

    @property
    def is_infected(self):
        return True if self.status == cfg.INFECTED_TYPE else False

    @property
    def is_recovered(self):
        return True if self.status == cfg.RECOVERED_TYPE else False

    @property
    def is_susceptible(self):
        return True if self.status == cfg.SUSCEPTIBLE_TYPE else False

    def update_infected_count(self, infected):
        if self.is_infected:
            self.infected_particles.append(infected)

    def _infect(self, infectee, time, probab):
        p = uniform_probability()
        if p <= probab:
            infectee.update_infected_count(self)

            self.status = cfg.INFECTED_TYPE
            self.infected_since = time
            if cfg.SYMPTOMATIC_ASYMPTOMATIC:
                will_show_symptoms = uniform_probability()
                if will_show_symptoms <= cfg.SYM_ASYM_PROBAB:
                    self.will_show_symptoms = False
                    self.color = (252, 3, 202)
            return True

    def infect(self, infectee, time):
        clr = cfg.INFECTED_COLOR
        if not cfg.MASKS:
            t_p = cfg.TRANSMISSION_PROBABILITY
        else:
            if self.is_masked and infectee.is_masked:
                t_p = cfg.MASK_MASK
                clr = cfg.MASKED_INF_COLOR
            elif self.is_masked and not infectee.is_masked:
                t_p = cfg.MASK_NOMASK
            elif not self.is_masked and infectee.is_masked:
                t_p = cfg.NOMASK_MASK
                clr = cfg.MASKED_INF_COLOR
            else:
                t_p = cfg.TRANSMISSION_PROBABILITY

        if self._infect(infectee, time, t_p):
            self.color = clr
            return True

    def recover(self, day):
        if self.is_infected and (day - self.infected_since) >= cfg.RECOVERED_PERIOD_IN_DAYS:
            self.status = cfg.RECOVERED_TYPE
            self.color = cfg.RECOVERED_COLOR
            self.quarantined = False
            self.vel = 0
            return True

    def wear_mask(self):
        if cfg.MASKS:
            will_it_wear = uniform_probability()
            if will_it_wear <= cfg.RATIO_OF_POP_WITH_MASKS:
                self.is_masked = True
                self.color = cfg.MASKED_INF_COLOR if self.is_infected else cfg.MASKED_SUS_COLOR
                return

    def fly_to_in_peace(self, x, y, new_walls):
        self.destination = (x, y)
        self.my_boundries = new_walls
        self.vel *= 4

