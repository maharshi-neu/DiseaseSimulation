import numpy as np
import pygame
from functools import lru_cache

def random_angle():
    return np.random.uniform(0, np.pi * 2)

def bounce_particle(particle, other_particle, dx, dy):
    tangent = np.arctan2(dx, dy)
    particle.angle = 2 * tangent - particle.angle
    other_particle.angle = 2 * tangent - other_particle.angle

    angle = 0.5 * np.pi + tangent
    particle.x += np.sin(angle)
    particle.y -= np.cos(angle)
    other_particle.x -= np.sin(angle)
    other_particle.y += np.cos(angle)

def bounce_wall(particle, wall_vector):
    """
    Discrete collision detection (has tunneling issue.. not a problem with particles :P)
    """
    if particle.right >= wall_vector['r']:
        particle.angle = -particle.angle

    elif particle.left <= wall_vector['l']:
        particle.angle = -particle.angle

    if particle.bottom >= wall_vector['b']:
        particle.angle = np.pi - particle.angle

    elif particle.top <= wall_vector['t']:
        particle.angle = np.pi - particle.angle

def build_walls(wall_width, x_start, x_end, y_start, y_end):
    wall_left = x_start + wall_width
    wall_top = y_start + wall_width
    wall_right =  x_end - wall_width
    wall_bottom = y_end - wall_width

    return {
        'l': wall_left,
        't': wall_top,
        'r': wall_right,
        'b': wall_bottom
    }

def random_coord(radius, axis):
    d = radius * 2
    return np.random.randint(d, axis - d)

def draw_walls(window, wv, wall_width, x0, y0, x1, y1):
    wall_color = (50, 0, 150) # RGB
    # left wall
    leftRect = pygame.Rect(x0, y0, wv['l'], y1) # left, top, width, height
    pygame.draw.rect(window, wall_color, leftRect)
    # top wall
    # top = 0 if x0 == y0 else y0
    topRect = pygame.Rect(x0, y0, x1, wv['t']) # left, top, width, height
    pygame.draw.rect(window, wall_color, topRect)
    # right wall
    rightRect = pygame.Rect(wv['r'], 0, wall_width, y1) # left, top, width, height
    pygame.draw.rect(window, wall_color, rightRect)
    # bottom wall
    bottomRect = pygame.Rect(x0, wv['b'], x1, wv['b']) # left, top, width, height
    pygame.draw.rect(window, wall_color, bottomRect)

def draw_line(window, color, x1, y1, x2, y2):
    pygame.draw.line(window, color, (x1, y1), (x2, y2))

def display_text(window, font, txt, x, y, color="coral"):
    tr = font.render(str(txt), 1, pygame.Color(color))
    window.blit(tr, (x, y))

def euclidean_distance(particle, other_particle):
    dx = particle.x - other_particle.x
    dy = particle.y - other_particle.y
    return np.sqrt(np.square(dx) + np.square(dy)), dx, dy

def calculate_r_naught(infection_timeseries):
    """
        Transmissibility
        r = new_infections / contact

        Avg. rate of contact
        c = contact / time

        Duration of infectiousness
        d = time / infection

        Ro = r * c * d
    """
    # TODO improve algorithm
    if not infection_timeseries or len(infection_timeseries) == 1:
        return 0
    r = np.diff(infection_timeseries) / np.diff(infection_timeseries, prepend=0)[:len(infection_timeseries)-1]
    return round(r[-1], 2)

@lru_cache()
def make_grid_array(nrow, ncol):
    grid = dict()
    for r in range(nrow):
        grid[r] = dict()
        for c in range(ncol):
            grid[r][c] = list()

    return grid

@lru_cache()
def grid_cell(r, c, nrow, ncol, width, height):
    cell_w = (width / ncol)
    cell_h = (height / nrow)

    x0, y0 = c * cell_w, r * cell_h
    x1, y1 = (c + 1) * cell_w, (r + 1) * cell_h
    return x0, y0, x1, y1


def populate_grid(nrow, ncol, grid, particles, width, height):
    done = set()
    for i in range(nrow):
        for j in range(ncol):
            for p in particles:
                if p in done:
                    continue

                x0, y0, x1, y1 = grid_cell(i, j, nrow, ncol, width, height)
                if (p.x >= x0 and p.y >= y0) and (p.x <= x1 and p.y <= y1):
                    grid[i][j].append(p)
                    done.add(p)
    return grid
