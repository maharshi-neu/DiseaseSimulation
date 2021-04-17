import numpy as np
import pygame

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

def calculate_r_naught(diff_infection_timeseries, prev_Ro):
    if not diff_infection_timeseries or len(diff_infection_timeseries) == 1:
        return 0.0

    prev_inf = diff_infection_timeseries[-2]
    now_inf = diff_infection_timeseries[-1]
    if prev_inf != 0 and now_inf != 0:
        r = now_inf / prev_inf
    else:
        r = prev_Ro

    return round(r, 2)

