import pygame
import numpy as np

from . import (Particle, cfg, calculate_r_naught,
        bounce_wall, build_walls, random_coord, draw_walls,
        draw_line, display_text, euclidean_distance, bounce_particle,
        uniform_probability, bar_chart)

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

        # if cfg.QUARANTINE:
        self.main_x = self.X - cfg.QUARANTINE_CENTRE_WIDTH
        self.q_centre_wall_vector = build_walls(
                self.wall_width, self.main_x, self.X, 0, cfg.QUARANTINE_CENTRE_HEIGHT)

        # Wall co-ordinates
        self.wall_vectors = list()

        self.xpart = self.main_x / cfg.COMMUNITY_COLS
        self.ypart = self.main_y / cfg.COMMUNITY_ROWS

        self.wall_vector_list = list()
        for y in range(cfg.COMMUNITY_ROWS):
            for x in range(cfg.COMMUNITY_COLS):
                x0, y0 = x * self.xpart, y * self.ypart
                x1, y1 = x0 + self.xpart, y0 + self.ypart
                self.wall_vector_list.append(build_walls(self.wall_width, x0, x1, y0, y1))

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

        self.font = pygame.font.SysFont(None, 18)

        self.init_groups()

        self.day = 0
        self.tick = 0
        self.init_render_stats()

        self.infection_timeseries = list()
        self.diff_infection_timeseries = list()
        self.BETA = list()
        self.Ro = 0.0

    @property
    def suslen(self):
        return len(self.susceptible_container)

    @property
    def inflen(self):
        return len(self.infected_container)

    @property
    def reclen(self):
        return len(self.recovered_container)

    @property
    def alllen(self):
        return len(self.all_container)

    def init_groups(self):
        min_ct = self.clock_tick / 2
        max_ct = self.clock_tick * 2

        w = 0
        # SUSCEPTIBLE
        for i in range(self.n_susceptible):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            p = Particle(
                    random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS),
                    random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS), cfg.SUSCEPTIBLE_TYPE,
                    color=cfg.SUSCEPTIBLE_COLOR, clock_tick=fps)
            p.wear_mask()
            p.my_boundries = wv
            self.susceptible_container.append(p)
            self.all_container.append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

        # INFECTED
        for _ in range(self.n_infected):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            p = Particle(
                    random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS),
                    random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS), cfg.INFECTED_TYPE,
                    color=cfg.INFECTED_COLOR, clock_tick=fps)
            p.wear_mask()
            p.my_boundries = wv
            self.infected_container.append(p)
            self.all_container.append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

        # RECOVERED
        for _ in range(self.n_recovered):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            p = Particle(
                    random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS),
                    random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS), cfg.RECOVERED_TYPE,
                    color=cfg.RECOVERED_COLOR, clock_tick=fps)
            p.my_boundries = wv
            self.recovered_container.append(p)
            self.all_container.append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

    def handle_particle_collision(self, i):
        # sweep n prune
        diameter = cfg.PARTICLE_RADIUS * 2
        newly_infected = list()

        ip = self.all_container[i]
        for j in range(i + 1, self.alllen):
            jp = self.all_container[j]

            if (jp.status != cfg.RECOVERED_TYPE != ip.status):
                condition = (jp.is_infected) + (ip.is_infected)
                if condition == 1:
                    d, dx, dy = euclidean_distance(ip.x, ip.y, jp.x, jp.y)
                    if diameter >= d:
                        bounce_particle(ip, jp, dx, dy)
                        if jp.is_infected:
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

    def update_fps(self):
        fps = str(int(self.clock.get_fps()))
        return fps

    def update_time(self):
        self.day = np.round(self.tick / cfg.DAY_IN_CLOCK_TICK, 2)
        return 'Day {}'.format(self.day)

    def move_to_quarantine(self, p):
        """
            if Ro is low its easy to quarantine people, easy to detect
        """
        if not cfg.QUARANTINE or not p.is_infected or p.quarantined:
            return

        if not p.will_show_symptoms:
            return

        if (self.day - p.infected_since) > cfg.QUARANTINE_AT_DAY:
            p.fly_to_in_peace(
                    (cfg.QUARANTINE_CENTRE_WIDTH / 2) + self.main_x,
                    (cfg.QUARANTINE_CENTRE_HEIGHT / 2),
                    self.q_centre_wall_vector
            )
            p.quarantined = True

    def update_containers(self, newly_infected, newly_recovered):
        if newly_infected:
            self.susceptible_container = [
                    sus for sus in self.susceptible_container if sus.is_susceptible]
            self.infected_container.extend(newly_infected)
        if newly_recovered:
            self.infected_container = [
                    inf for inf in self.infected_container if inf.is_infected]
            self.recovered_container.extend(newly_recovered)

    def trace_line(self, p):
        if p.is_infected:
            for i in p.infected_particles:
                draw_line(self.window, cfg.INFECTED_COLOR, p.x, p.y, i.x, i.y)

    def update_stats(self):
        stats_height = self.stats.get_height()
        stats_width = self.stats.get_width()

        n_sus_now = self.suslen
        n_inf_now = self.inflen
        n_pop_now = self.alllen
        n_rec_now = self.reclen

        t = int((self.tick / cfg.RUN_TIME_IN_TICK) * stats_width)

        y_infect = int(
            stats_height - (n_inf_now / n_pop_now) * stats_height
        )

        y_susceptible = int((n_sus_now / n_pop_now) * stats_height)

        stats_graph = pygame.PixelArray(self.stats)
        stats_graph[t, :y_susceptible] = pygame.Color(*cfg.SUSCEPTIBLE_COLOR)
        stats_graph[t, y_infect:] = pygame.Color(*cfg.INFECTED_COLOR)

    def init_render_stats(self):
        stats_x, stats_y = cfg.GAME_WIDTH // 4, cfg.GAME_HEIGHT // 4
        self.stats = pygame.Surface((stats_x, stats_y))
        self.stats.fill(cfg.GREY)
        self.stats.set_alpha(200)
        self.stats_pos = (10, cfg.GAME_HEIGHT - (stats_y + 10))

    def render_stats(self):
        self.stats.unlock()
        self.window.blit(self.stats, self.stats_pos)

    def update_tick(self):
        self.tick += 1

    def update_infection_timeseries(self):
        if self.day % 1 == 0 and self.inflen != self.T:
            self.infection_timeseries.append(self.inflen)
            if len(self.infection_timeseries) > 1:
                self.diff_infection_timeseries.append(
                        (self.inflen - self.infection_timeseries[-2])
                )
            else:
                self.diff_infection_timeseries.append(self.inflen)

    def pick_lucky_winners_for_travel(self):
        if not cfg.TRAVEL:
            return

        should_travel_happen = uniform_probability()
        if should_travel_happen <= cfg.TRAVEL_FREQUENCY:

            p1, p2 = self.all_container[0], self.all_container[0]
            q = p1.quarantined + p2.quarantined

            try_till = 3
            i = 0

            while p1.my_boundries == p2.my_boundries and q == 0:
                c1 = np.random.randint(0, self.alllen)
                c2 = np.random.randint(0, self.alllen)
                p1 = self.all_container[c1]
                p2 = self.all_container[c2]
                q = p1.quarantined + p2.quarantined
                i += 1
                if i == try_till:
                    return

            tmp = p1.my_boundries
            p1.fly_to_in_peace(p2.x, p2.y, p2.my_boundries)
            p2.fly_to_in_peace(p1.x, p1.y, tmp)

    def update_and_render(self):
        self.update_tick()
        self.window.fill(cfg.BACKGROUND)

        for wv in self.wall_vector_list:
            draw_walls(self.window, wv,
                    self.wall_width, wv['x0'], wv['y0'], wv['x1'], wv['y1'])

        self.window.fill(cfg.BACKGROUND, (self.main_x, 0, cfg.GAME_WIDTH, cfg.GAME_HEIGHT))

        # Quarantine Walls
        draw_walls(self.window, self.q_centre_wall_vector,
                self.wall_width, self.main_x, 0, self.X, cfg.QUARANTINE_CENTRE_HEIGHT)

        day = self.update_time()
        fps = self.update_fps()

        self.all_container.sort(key=lambda p: p.x)

        newly_infected = list()
        newly_recovered = list()
        self.contact = 0
        self.time = 0
        for pi in range(self.alllen):
            # update -------
            p = self.all_container[pi]

            if p.is_recovered:
                continue

            p.update_2d_vectors()
            bounce_wall(p, p.my_boundries)

            if pi < self.T - 1:
                newly_infected.extend(self.handle_particle_collision(pi))

            # render ------
            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)
            if(p.is_infected and p.recover(self.day)):
                newly_recovered.append(p)
            # self.trace_line(p)
            self.move_to_quarantine(p)

        self.update_stats()
        self.render_stats()
        self.update_containers(newly_infected, newly_recovered)

        self.update_infection_timeseries()
        self.Ro = calculate_r_naught(self.diff_infection_timeseries, self.Ro)
        self.BETA.append(self.Ro)

        bar_data = {
                'S': (self.suslen, cfg.SUSCEPTIBLE_COLOR),
                'I': (self.inflen, cfg.INFECTED_COLOR),
                'R': (self.reclen, cfg.RECOVERED_COLOR),
                'seq': ['S', 'I', 'R'],
                'font': self.font,

            }
        bar_chart(
                self.window, self.main_x,
                cfg.QUARANTINE_CENTRE_HEIGHT, self.X,
                self.T, bar_data, cfg.GAME_HEIGHT)

        Ro_avg = np.round(np.average(self.BETA), 2)

        display_text(self.window, self.font, fps, 10, 10)
        display_text(self.window, self.font, day, self.main_x / 2 - 10, 10)
        display_text(self.window, self.font, 'Ro {}'.format(self.Ro), 10, 25)
        display_text(self.window, self.font, 'Ro Avg {}'.format(Ro_avg), 10, 35)

        self.pick_lucky_winners_for_travel()

        pygame.display.update()

    def run(self):
        while self.running and cfg.RUN_TIME_IN_DAYS > self.day:
            self.process_input()
            self.update_and_render()
            self.clock.tick(self.clock_tick)

        pygame.quit()

