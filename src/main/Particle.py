import pygame
import numpy as np
from collections import deque

from . import random_angle, uniform_probability, euclidean_distance
from . import cfg


class Particle:
    def __init__(self, x, y, status, color, clock_tick=60):
        self.x = x
        self.y = y
        self.status = status

        self.radius = cfg.PARTICLE_RADIUS
        self.color = color

        self.update_circumference_coordinates()

        self.displacement = cfg.PARTICLE_DISPLACEMENT
        self.angle = random_angle()

        self.vel = cfg.PARTICLE_VELOCITY # velocity

        self.f = 0 # frame
        self.clock_tick = cfg.FPS

        self.infected_particles = list()
        self.my_boundries = dict()
        self.infected_since = 0
        self.is_masked = False
        self.trans_probab = cfg.TRANSMISSION_PROBABILITY
        self.quarantined = False
        self.will_show_symptoms = True
        self.destination = None
        self.prev_xy_b = None

        self.came_in_contact_with = deque()
        self.vaccinated = 0

    @property
    def is_travelling(self):
        """
            Returns the travelling status of the particle
            i.e. is particle in transition state from one room to another
        """
        return True if self.destination else False

    def update_circumference_coordinates(self):
        """
            Updates the particle circumference co-ordinates
            i.e. top, right, bottom, left (central co-ordinate +- radius)
        """
        self.top = abs(self.y) - self.radius
        self.right = abs(self.x) + self.radius
        self.bottom = abs(self.y) + self.radius
        self.left = abs(self.x) - self.radius

    def update_coordinates(self):
        """
            Updates the new particle central location (x,y)
        """
        dx = np.sin(self.angle) * self.vel
        dy = np.cos(self.angle) * self.vel

        self.x += dx
        self.y -= dy

    def travel_flight_mode(self):
        """
            This function provides smooth transition between rooms
        """
        d, _, _ = euclidean_distance(self.x, self.y, self.destination[0], self.destination[1])
        if d > 5:
            self.angle = np.arctan2(self.destination[1] - self.y, self.destination[0] - self.x)
            self.x += np.cos(self.angle) * self.vel
            self.y += np.sin(self.angle) * self.vel
            self.update_circumference_coordinates()
        else:
            self.x = self.destination[0]
            self.y = self.destination[1]
            self.destination = None
            self.vel /= 4

    def control_velocity(self):
        """
            Sometimes particles miss the excat location by a few pixels when transition ends \
                    from one room to another then this function helps lower the velocity which \
                    was set for transition
        """
        if self.vel > (cfg.PARTICLE_VELOCITY + 2) and not self.is_travelling and self.will_show_symptoms:
            self.vel = cfg.PARTICLE_VELOCITY

    def update_2d_vectors(self):
        """
            Calculates and updates the central location + circumference using helper function
            Generates random angle for the particle to move next
        """
        if self.is_travelling:
            self.travel_flight_mode()
            return
        self.f += 1
        if self.f > self.clock_tick * 2:
            self.f = 0
            self.angle = random_angle()

        self.update_coordinates()
        self.update_circumference_coordinates()
        self.control_velocity()

    @property
    def is_infected(self):
        """
            Returns infected status for the given particle
        """
        return True if self.status == cfg.INFECTED_TYPE else False

    @property
    def is_removed(self):
        """
            Returns removed status for the given particle
        """
        return True if self.status == cfg.REMOVED_TYPE else False

    @property
    def is_susceptible(self):
        """
            Returns susceptible status for the given particle
        """
        return True if self.status == cfg.SUSCEPTIBLE_TYPE else False

    def update_infected_count(self, infected):
        """
            Maintains a list of infected particles infected by a particle
        """
        if self.is_infected:
            self.infected_particles.append(infected)

    def _infect(self, infectee, time, probab, color):
        """
            infects with a particle with probability \
                    taking into consideration if the particle is wearing mask/vaccinated
            If infected it also decides weather the particle will show symptoms or will be asymptomatic
            Asymptomatic particles dont get quarantined, only case where this particle may get quarantined \
                    is through contact tracing
        """
        p = uniform_probability() + self.vaccinated
        if p <= probab:
            infectee.update_infected_count(self)

            self.status = cfg.INFECTED_TYPE
            self.color = color
            self.infected_since = time
            if cfg.SYMPTOMATIC_ASYMPTOMATIC:
                will_show_symptoms = uniform_probability()
                if will_show_symptoms <= cfg.SYM_ASYM_PROBAB:
                    self.will_show_symptoms = False
                    self.radius = 7.5
                    self.vel += .75
            return True

    def infect(self, infectee, time):
        """
            calls _infect with appropriate chance of getting quarantined and color
            color is dependent upon if the particle is masked or not
        """
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

        return self._infect(infectee, time, t_p, clr)

    def recover(self, day):
        """
            checks for recovery period from config(RECOVERED_PERIOD_IN_DAYS)
            if the difference of now - infected since is greater then the recovery period
            then marks particle as recovered/removed
        """
        if self.is_infected and (day - self.infected_since) >= cfg.RECOVERED_PERIOD_IN_DAYS:
            self.status = cfg.REMOVED_TYPE
            self.color = cfg.REMOVED_COLOR
            self.vel = 0
            return True

    def wear_mask(self):
        """
            decides weather the particle will wear a mask (deciding factor config.RATIO_OF_POP_WITH_MASKS),
            updates the color and is_masked flag appropriately
        """
        if cfg.MASKS:
            will_it_wear = uniform_probability()
            if will_it_wear <= cfg.RATIO_OF_POP_WITH_MASKS:
                self.is_masked = True
                self.color = cfg.MASKED_INF_COLOR if self.is_infected else cfg.MASKED_SUS_COLOR
                return

    def fly_to_in_peace(self, x, y, new_walls):
        """
            given particle will transition to a new room with updated boundies to collide with
        """
        self.destination = (x, y)
        self.prev_xy_b = (self.x, self.y, self.my_boundries)
        self.my_boundries = new_walls
        self.vel *= 4

