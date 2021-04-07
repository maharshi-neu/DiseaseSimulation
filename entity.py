import pygame
import numpy as np

PARTICLE_RADIUS = 5
PARTICLE_COLOR = (0, 255, 0)
PARTICLE_DISPLACEMENT = .4

class Particle:
    def __init__(self, x, y, status, radius=PARTICLE_RADIUS, color=PARTICLE_COLOR, clock_tick=60):
        self.x = x
        self.y = y
        self.status = status

        self.radius = radius
        self.color = color

        self.update_circumference_coordinates()


        self.location = pygame.math.Vector2(self.x, self.y)

        self.displacement = PARTICLE_DISPLACEMENT
        self.p_x = self.displacement # init position
        self.p_y = self.displacement # init position

        self.vel = 1 # velocity

        self.f = 0 # frame
        self.clock_tick = clock_tick

    def next_direction(self):
        self.p_x = np.random.choice([-self.displacement, self.displacement])
        self.p_y = np.random.choice([self.displacement, -self.displacement])

    def update_velocity(self):
        self.vel = np.random.randint(1, 5)

    def update_circumference_coordinates(self):
        self.top = abs(self.y) - self.radius
        self.right = abs(self.x) + self.radius
        self.bottom = abs(self.y) + self.radius
        self.left = abs(self.x) - self.radius

    def update_coordinates(self):
        dx = self.p_x
        dy = self.p_y

        if self.vel > 0:
            dx *= self.vel
            dy *= self.vel
            self.vel -= 0.3

        self.x += dx
        self.y += dy

    def update_2d_vectors(self):
        self.f += 1
        if self.f > self.clock_tick * 2:
            self.f = 0
            self.next_direction()
            self.update_velocity()

        self.update_coordinates()
        self.update_circumference_coordinates()

    def flip_x(self):
        self.p_x = -self.p_x

    def flip_y(self):
        self.p_y = -self.p_y

