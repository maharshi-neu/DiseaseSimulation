import pygame
import numpy as np

class SIM:
    def __init__(self, width=512, height=512):
        pygame.init()
        self.clock = pygame.time.Clock()

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

        self.r = 5
        self.x, self.y = self.X / 2, self.Y / 2

        self.d = .4
        self.t_x = np.random.choice([-self.d, self.d])
        self.t_y = np.random.choice([self.d, -self.d])

        self.v = np.random.randint(1, 3)

    def process_input(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def update(self):
        if self.f > 60 * 2:
            self.f = 0
            self.v = np.random.randint(1, 2)
            self.t_x = np.random.choice([-self.d, self.d])
            self.t_y = np.random.choice([self.d, -self.d])

        self.f += 1

        dx , dy = self.t_x, self.t_y

        if self.v > 0:
            dx *= self.v
            dy *= self.v
            self.v -= 0.9

        self.x += dx
        self.y += dy

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

    def handle_collision(self, e):
        """
        Discrete collision detection (has tunneling issue)
        """
        if e.left < self.wall_left or e.right > self.wall_right:
            self.t_x = -self.t_x
        elif e.top < self.wall_top or e.bottom > self.wall_bottom:
            self.t_y = -self.t_y

    def render(self):
        self.window.fill((0, 0, 0))

        self.draw_walls()

        l1 = pygame.math.Vector2(self.x, self.y)
        p1 = pygame.draw.circle(self.window, (0, 255, 0), l1, self.r)
        self.handle_collision(p1)
        pygame.display.update()

    def run(self):
        self.f = 0
        while self.running:
            self.process_input()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    sim = SIM()
    sim.run()
