import pygame
import numpy as np

from . import (Particle, cfg, calculate_r_naught,
        bounce_wall, build_walls, random_coord, draw_walls,
        draw_line, display_text, euclidean_distance, bounce_particle,
        make_grid_array, grid_cell, populate_grid)

# ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'


class Simulator:
    def process_input(self):
        """
            Keyboard input for exitting
        """
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock_tick = cfg.FPS

        pygame.display.set_caption(cfg.GAME_TITLE)

        self.X = cfg.GAME_WIDTH
        self.Y = cfg.GAME_HEIGHT

        self.main_x = self.X
        self.main_y = self.Y

        self.wall_width = cfg.WALL_SIZE

        if cfg.QUARANTINE:
            self.main_x = self.X - cfg.QUARANTINE_CENTRE_WIDTH
            self.quarantine_centre_wall_vector = build_walls(
                    self.wall_width, self.main_x, self.X, 0, cfg.QUARANTINE_CENTRE_HEIGHT)

        # Wall co-ordinates
        self.wall_vector = build_walls(self.wall_width, 0, self.main_x, 0, self.main_y)

        self.window = pygame.display.set_mode((self.X, self.Y))

        self.running = True

        self.susceptible_container = list()
        self.infected_container = list()
        self.recovered_container = list()
        self.all_container = list()

        self.n_susceptible = cfg.POPULATION - cfg.I0 - cfg.R0
        self.n_infected = cfg.I0
        self.n_recovered = cfg.R0
        self.T = cfg.POPULATION

        self.font = pygame.font.SysFont("Arial", 12)

        self.init_groups()

        self.day = 1
        self.tick = 0
        self.init_render_stats()

        self.infection_timeseries = list()
        self.BETA = list()
        self.grid = make_grid_array(cfg.N_GRID_ROW, cfg.N_GRID_COL)

    def init_groups(self):
        min_ct = self.clock_tick / 2
        max_ct = self.clock_tick * 2

        for _ in range(self.n_susceptible):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    random_coord(cfg.PARTICLE_RADIUS, self.main_x),
                    random_coord(cfg.PARTICLE_RADIUS, self.main_y), cfg.SUSCEPTIBLE_TYPE,
                    color=cfg.SUSCEPTIBLE_COLOR, clock_tick=fps)
            p.my_boundries = self.wall_vector
            self.susceptible_container.append(p)
            self.all_container.append(p)

        for _ in range(self.n_infected):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    random_coord(cfg.PARTICLE_RADIUS, self.main_x),
                    random_coord(cfg.PARTICLE_RADIUS, self.main_y), cfg.INFECTED_TYPE,
                    color=cfg.INFECTED_COLOR, clock_tick=fps)
            p.my_boundries = self.wall_vector
            self.infected_container.append(p)
            self.infected_since = 0
            self.all_container.append(p)

        for _ in range(self.n_recovered):
            fps = np.random.randint(min_ct, max_ct)
            p = Particle(
                    random_coord(cfg.PARTICLE_RADIUS, self.main_x),
                    random_coord(cfg.PARTICLE_RADIUS, self.main_y), cfg.RECOVERED_TYPE,
                    color=cfg.RECOVERED_COLOR, clock_tick=fps)
            p.my_boundries = self.wall_vector
            self.infected_container.append(p)
            self.all_container.append(p)

    def handle_particle_collision(self, i):
        # sweep n prune
        diameter = cfg.PARTICLE_RADIUS * 2
        newly_infected = list()

        ip = self.all_container[i]
        for j in range(i + 1, len(self.all_container)):
            jp = self.all_container[j]

            if (jp.status != cfg.RECOVERED_TYPE != ip.status):
                condition = (jp.status == cfg.INFECTED_TYPE) + (ip.status == cfg.INFECTED_TYPE)
                if condition == 1:
                    d, dx, dy = euclidean_distance(ip, jp)
                    if diameter >= d:
                        bounce_particle(ip, jp, dx, dy)
                        if jp.status == cfg.INFECTED_TYPE:
                            if(ip.infect(jp, self.day)):
                                newly_infected.append(ip)
                        else:
                            if(jp.infect(ip, self.day)):
                                newly_infected.append(jp)
                    else:
                        break
                else:
                    break

        return newly_infected

    def handle_particle_collision(self):
        self.grid = populate_grid(cfg.N_GRID_ROW, cfg.N_GRID_COL, self.grid, self.all_container, cfg.GAME_WIDTH, cfg.GAME_HEIGHT)
        diameter = cfg.PARTICLE_RADIUS * 2
        newly_infected = list()
        for i in range(cfg.N_GRID_ROW):
            for j in range(cfg.N_GRID_COL):
                tocheck = self.grid[i][j]
                for m in range(len(tocheck) - 1):
                    for n in range(m, len(tocheck)):
                        p1 = tocheck[m]
                        p2 = tocheck[n]
                        if (p1.status != cfg.RECOVERED_TYPE != p2.status):
                            condition = (p1.status == cfg.INFECTED_TYPE) + (p2.status == cfg.INFECTED_TYPE)
                            if condition == 1:
                                d, dx, dy = euclidean_distance(p1, p2)
                                if diameter >= d:
                                    bounce_particle(p1, p2, dx, dy)
                                    if p1.status == cfg.INFECTED_TYPE:
                                        if(p2.infect(p1, self.day)):
                                            newly_infected.append(p2)
                                    else:
                                        if(p1.infect(p2, self.day)):
                                            newly_infected.append(p1)
        return newly_infected

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        return fps

    def update_time(self):
        self.day = np.round(self.tick / cfg.DAY_IN_CLOCK_TICK, 2)
        return 'Day {}'.format(self.day)

    def move_to_quarantine(self):
        if cfg.QUARANTINE:
            i = 0
            while i < len(self.infected_container):
                infected = self.infected_container[i]

                if len(infected.infected_particles) >= round(cfg.BETA):
                    infected.x = (cfg.QUARANTINE_CENTRE_WIDTH / 2) + self.main_x
                    infected.y = (cfg.QUARANTINE_CENTRE_HEIGHT / 2)
                    infected.my_boundries = self.quarantine_centre_wall_vector
                    infected.infected_particles = list()
                i += 1

    def update_containers(self, newly_infected, newly_recovered):
        if newly_infected:
            self.susceptible_container = [
                    sus for sus in self.susceptible_container if sus.status == cfg.SUSCEPTIBLE_TYPE]
            self.infected_container.extend(newly_infected)
        if newly_recovered:
            self.infected_container = [
                    inf for inf in self.infected_container if inf.status == cfg.INFECTED_TYPE]
            self.recovered_container.extend(newly_recovered)

    def trace_line(self, p):
        if p.is_infected():
            for i in p.infected_particles:
                draw_line(self.window, cfg.INFECTED_COLOR, p.x, p.y, i.x, i.y)

    def update_stats(self):
        stats_height = self.stats.get_height()
        stats_width = self.stats.get_width()

        n_sus_now = len(self.susceptible_container)
        n_inf_now = len(self.infected_container)
        n_pop_now = len(self.all_container)
        n_rec_now = len(self.recovered_container)

        t = int((self.tick / cfg.RUN_TIME_IN_TICK) * stats_width)

        y_infect = int(
            stats_height - (n_inf_now / n_pop_now) * stats_height
        )
        # print(n_inf_now / n_pop_now, y_infect)

        y_susceptible = int((n_sus_now / n_pop_now) * stats_height)

        stats_graph = pygame.PixelArray(self.stats)
        stats_graph[t, :y_susceptible] = pygame.Color(*cfg.SUSCEPTIBLE_COLOR)
        stats_graph[t, y_infect:] = pygame.Color(*cfg.INFECTED_COLOR)

    def init_render_stats(self):
        stats_x, stats_y = cfg.GAME_WIDTH // 4, cfg.GAME_HEIGHT // 4
        self.stats = pygame.Surface((stats_x, stats_y))
        self.stats.fill(cfg.GREY)
        self.stats.set_alpha(230)
        self.stats_pos = (10, cfg.GAME_HEIGHT - (stats_y + 10))

    def render_stats(self):
        self.stats.unlock()
        self.window.blit(self.stats, self.stats_pos)

    def update_tick(self):
        self.tick += 1

    def update_infection_timeseries(self):
        if self.day % 1 == 0 and len(self.infected_container) != self.T:
            self.infection_timeseries.append(len(self.infected_container))

    def update_and_render(self):
        self.update_tick()
        self.window.fill(cfg.BACKGROUND)
        draw_walls(self.window, self.wall_vector,
                self.wall_width, 0, 0, self.main_x, self.main_y)
        if cfg.QUARANTINE:
            draw_walls(self.window, self.quarantine_centre_wall_vector,
                    self.wall_width, self.main_x, self.main_y, self.X, self.Y)

        display_text(self.window, self.font, self.update_fps(), 10, 10)
        display_text(self.window, self.font, self.update_time(), self.main_x / 2 - 10, 10)

        self.all_container.sort(key=lambda p: p.x)

        newly_infected = list()
        newly_recovered = list()
        self.contact = 0
        self.time = 0
        for pi in range(len(self.all_container)):
            # update -------
            p = self.all_container[pi]

            p.update_2d_vectors()
            bounce_wall(p, p.my_boundries)

            # if pi < self.T - 1:
            #     newly_infected.extend(self.handle_particle_collision(pi))

            # render ------
            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)
            if(p.status == cfg.INFECTED_TYPE and p.recover(self.day)):
                newly_recovered.append(p)
            # self.trace_line(p)
            self.move_to_quarantine()

        newly_infected = self.handle_particle_collision()

        self.update_stats()
        self.render_stats()
        self.update_containers(newly_infected, newly_recovered)

        self.update_infection_timeseries()
        Ro = calculate_r_naught(self.infection_timeseries)
        self.BETA.append(Ro)
        display_text(self.window, self.font, 'Ro {}'.format(Ro), 10, 20)

        pygame.display.update()

    def run(self):
        while self.running and cfg.RUN_TIME_IN_DAYS > self.day:
            self.process_input()
            self.update_and_render()
            self.clock.tick(self.clock_tick)

        pygame.quit()

