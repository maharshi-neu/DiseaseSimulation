import numpy as np
import pygame

# np.random.seed(0)

def random_angle():
    """
        Returns random angle uniformly
        pi * 2 covers all the possible angles(radians)
    """
    return np.random.uniform(0, np.pi * 2)

def bounce_particle(particle, other_particle, dx, dy):
    """
        Bounces a collided partile with other particle
        Calculates the tangent from and changes both the particle angles
        Updates both particles x,y co-ordinates with the calculated angle
    """
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
    if particle.destination:
        return
    if particle.right >= wall_vector['r']:
        particle.angle = -particle.angle

    elif particle.left <= wall_vector['l']:
        particle.angle = -particle.angle

    if particle.bottom >= wall_vector['b']:
        particle.angle = np.pi - particle.angle

    elif particle.top <= wall_vector['t']:
        particle.angle = np.pi - particle.angle

def build_walls(wall_width, x_start, x_end, y_start, y_end):
    """
        Calculates returns the walls,
            left, top, right, bottom boundaries from the given
            x start and x end & y start and y end

        returns dict(name: boundary)
    """
    wall_left = x_start + wall_width
    wall_top = y_start + wall_width
    wall_right =  x_end - wall_width
    wall_bottom = y_end - wall_width

    return {
        'l': wall_left,
        't': wall_top,
        'r': wall_right,
        'b': wall_bottom,
        'x0': x_start,
        'y0': y_start,
        'x1': x_end,
        'y1': y_end
    }

def random_coord(a0, a1, radius):
    """
        Returns the next random set of x,y co-ordinates for the particle to move
    """
    d = radius * 2
    return np.random.randint(a0 + d, a1 - d)

def draw_walls(window, wv, wall_width):
    """
        Renders the walls based on wall vectors dict(name:boundary) and the provided width
    """
    wall_color = (28, 21, 0) # RGB
    # left wall
    leftRect = pygame.Rect(wv['x0'], wv['y0'], wall_width, wv['y1']) # left, top, width, height
    pygame.draw.rect(window, wall_color, leftRect)
    # top wall
    topRect = pygame.Rect(wv['x0'], wv['y0'], wv['x1'], wall_width) # left, top, width, height
    pygame.draw.rect(window, wall_color, topRect)
    # right wall
    rightRect = pygame.Rect(wv['r'], wv['t'], wall_width, wv['y1']) # left, top, width, height
    pygame.draw.rect(window, wall_color, rightRect)
    # bottom wall
    bottomRect = pygame.Rect(wv['x0'], wv['b'], wv['x1'], wall_width) # left, top, width, height
    pygame.draw.rect(window, wall_color, bottomRect)

def draw_line(window, color, x1, y1, x2, y2):
    """
        Draws line from one particle to another (contact tracing visualization)
    """
    pygame.draw.line(window, color, (x1, y1), (x2, y2))

def display_text(window, font, txt, x, y, color="white"):
    """
        Renders text on window
    """
    tr = font.render(str(txt), 1, pygame.Color(color))
    window.blit(tr, (x, y))

def euclidean_distance(x0, y0, x1, y1):
    """
        Returns the Euclidean distance between two points (length of a line segment between the two points)
    """
    dx = x1 - x0
    dy = y1 - y0
    return np.sqrt(np.square(dx) + np.square(dy)), dx, dy

def calculate_r_naught(diff_infection_timeseries, prev_Ro):
    """
        Calculates the Ro on basis of the timeseries(infected per day)
        Ro = (newly infected / existing infected)
    """
    if not diff_infection_timeseries or len(diff_infection_timeseries) == 1:
        return 0.0

    prev_inf = diff_infection_timeseries[-2]
    now_inf = diff_infection_timeseries[-1]
    if prev_inf != 0 and now_inf != 0:
        r = now_inf / prev_inf
    else:
        r = prev_Ro

    return round(r, 2)

def uniform_probability():
    """
        Returns uniformly distributed over the half-open interval
        Probability density function of unifrom distribution \
                p(x) = ( 1 / (b - a) )
    """
    return np.random.uniform(0, 1)

def bar_chart(window, x0, y0, x1, T, data, bch):
    """
        Renders the bar chart on the right part of the window from data provided
        data has #susceptible, #infected, #removed
    """
    diff = bch / len(data['seq'])
    len2 = len(data['seq']) * 2
    for i, v in enumerate(data['seq']):
        item = data[v]
        t = y0 + (i * diff)
        rect = pygame.Rect(
                x0,                                  # left
                t,                                   # top
                ((x1-x0) / T)  * (item[0]),          # width
                diff                                 # height
            )
        pygame.draw.rect(window, item[1], rect)
        display_text(window, data['font'], item[0], x0 + 10, (t + (diff/2)), (255,255,255))

