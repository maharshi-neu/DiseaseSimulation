import pygame
import numpy as np
from collections import deque
import logging
import os

from . import (Particle, cfg, calculate_r_naught,
        bounce_wall, build_walls, random_coord, draw_walls,
        draw_line, display_text, euclidean_distance, bounce_particle,
        uniform_probability, bar_chart, make_grid_array, which_grid)

# ALSA lib pcm.c:8306:(snd_pcm_recover) underrun occurred
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
            elif event.key == pygame.K_SPACE:
                if not self.pause:
                    self.pause = True
                else:
                    self.pause = False

    def __init__(self):

        x = 370
        y = 0
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

        pygame.init()
        self.clock = pygame.time.Clock()
        self.clock_tick = cfg.FPS
        self.pause = False

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
        self.removed_container = list()
        self.all_container = list()

        self.n_susceptible = cfg.POPULATION - cfg.I0 - cfg.R0
        self.n_infected = cfg.I0
        self.n_recovered = cfg.R0
        self.T = cfg.POPULATION

        self.font = pygame.font.SysFont(None, 18)

        self.grid = make_grid_array(cfg.N_GRID_ROW, cfg.N_GRID_COL)
        self.cell_size_w = (cfg.GAME_WIDTH / cfg.N_GRID_COL)
        self.cell_size_h = (cfg.GAME_HEIGHT / cfg.N_GRID_ROW)

        self.init_groups()

        self.day = 0
        self.tick = 0
        self.init_render_stats()

        self.infection_timeseries = list()
        self.diff_infection_timeseries = list()
        self.BETA = list()
        self.Ro = 0.0

        self.bar_chart_height = (cfg.GAME_HEIGHT * .3)

        used_height = cfg.GAME_HEIGHT - (cfg.QUARANTINE_CENTRE_HEIGHT + self.bar_chart_height)
        h = cfg.GAME_HEIGHT - used_height
        self.central_wall_width = h * .1
        self.central_location_wall_vector = build_walls(
                self.central_wall_width, self.main_x, cfg.GAME_WIDTH,
                h,
                cfg.GAME_HEIGHT)

        self.in_central_location = set()

        self.asymptomatic_container = set()

        self.Rmax = -99
        self.to_contact_trace = deque()

        self.vaccine_availability = 0

    @property
    def suslen(self):
        """
            Returns length of susceptible container
        """
        return len(self.susceptible_container)

    @property
    def inflen(self):
        """
            Returns length of infected container
        """
        return len(self.infected_container)

    @property
    def reclen(self):
        """
            Returns length of infected container
        """
        return len(self.removed_container)

    @property
    def alllen(self):
        """
            Returns length of all container
        """
        return len(self.all_container)

    def disperse_vaccine(self):
        """
            Disperses vaccine per day
        """
        if cfg.VACCINE and self.day % 1 == 0:
            self.vaccine_availability += cfg.VACCINE_DISPERSION_RATE

    def init_groups(self):
        """
            Called in __init__ populates all the containers with Particles
        """
        min_ct = self.clock_tick / 2
        max_ct = self.clock_tick * 2

        w = 0
        # SUSCEPTIBLE
        for i in range(self.n_susceptible):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            x = random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS)
            y = random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS)
            p = Particle(
                    x=x,
                    y=y,
                    status=cfg.SUSCEPTIBLE_TYPE,
                    color=cfg.SUSCEPTIBLE_COLOR,
                    clock_tick=fps)
            p.wear_mask()
            p.my_boundries = wv
            self.susceptible_container.append(p)
            self.all_container.append(p)

            row_col = which_grid(self.cell_size_w, x, self.cell_size_h, y)
            p.grid = row_col
            self.grid[row_col[0]][row_col[1]].append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

        # INFECTED
        for _ in range(self.n_infected):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            x = random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS)
            y = random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS)
            p = Particle(
                    x=x,
                    y=y,
                    status=cfg.INFECTED_TYPE,
                    color=cfg.INFECTED_COLOR,
                    clock_tick=fps)
            p.wear_mask()
            p.my_boundries = wv
            self.infected_container.append(p)
            self.all_container.append(p)
            row_col = which_grid(self.cell_size_w, x, self.cell_size_h, y)
            p.grid = row_col
            self.grid[row_col[0]][row_col[1]].append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

        # RECOVERED
        for _ in range(self.n_recovered):
            fps = np.random.randint(min_ct, max_ct)
            wv = self.wall_vector_list[w]
            x = random_coord(wv['x0'], wv['x1'], cfg.PARTICLE_RADIUS)
            y = random_coord(wv['y0'], wv['y1'], cfg.PARTICLE_RADIUS)
            p = Particle(
                    x=x,
                    y=y,
                    status=cfg.REMOVED_TYPE,
                    color=cfg.REMOVED_COLOR,
                    clock_tick=fps)
            p.my_boundries = wv
            self.removed_container.append(p)
            self.all_container.append(p)
            row_col = which_grid(self.cell_size_w, x, self.cell_size_h, y)
            p.grid = row_col
            self.grid[row_col[0]][row_col[1]].append(p)

            w += 1
            if w >= len(self.wall_vector_list):
                w = 0

    ''' COMMENT START
    def handle_particle_collision(self, i):
        """
            Sweep and prune
        """
        diameter = cfg.PARTICLE_RADIUS * 2
        newly_infected = list()

        ip = self.all_container[i]
        for j in range(i + 1, self.alllen):
            jp = self.all_container[j]

            travelling = jp.is_travelling + ip.is_travelling
            if (jp.status != cfg.REMOVED_TYPE != ip.status) and not travelling:
                condition = (jp.is_infected) + (ip.is_infected)
                if condition == 1:
                    d, dx, dy = euclidean_distance(ip.x, ip.y, jp.x, jp.y)
                    if diameter >= d:
                        bounce_particle(ip, jp, dx, dy)
                        if jp.is_infected:
                            if(ip.infect(jp, self.day)):
                                newly_infected.append(ip)
                                if not ip.will_show_symptoms and ip not in self.asymptomatic_container:
                                    self.asymptomatic_container.add(ip)
                            jp.came_in_contact_with.append(ip)
                        else:
                            if(jp.infect(ip, self.day)):
                                newly_infected.append(jp)
                                if not jp.will_show_symptoms and jp not in self.asymptomatic_container:
                                    self.asymptomatic_container.add(jp)
                            ip.came_in_contact_with.append(jp)
                    else:
                        break
                else:
                    break

        return newly_infected
    COMMENT END'''

    def handle_particle_collision(self):
        """
            Uniform grid spatial partition
        """
        diameter = cfg.PARTICLE_DIAMETER
        newly_infected = list()
        for i in range(cfg.N_GRID_ROW):
            for j in range(cfg.N_GRID_COL):
                tocheck = self.grid[i][j]
                for m in range(len(tocheck) - 1):
                    for n in range(m, len(tocheck)):
                        p1 = tocheck[m]
                        p2 = tocheck[n]

                        travelling = p1.is_travelling + p2.is_travelling
                        if (p1.status != cfg.REMOVED_TYPE != p2.status) and not travelling:
                            condition = (p1.status == cfg.INFECTED_TYPE) + (p2.status == cfg.INFECTED_TYPE)
                            if condition == 1:
                                d, dx, dy = euclidean_distance(p1.x, p1.y, p2.x, p2.y)

                                if diameter >= d:
                                    bounce_particle(p1, p2, dx, dy)
                                    if p1.is_infected:
                                        if(p2.infect(p1, self.day)):
                                            newly_infected.append(p2)
                                            if not p2.will_show_symptoms and p2 not in self.asymptomatic_container:
                                                self.asymptomatic_container.add(p2)
                                        p1.came_in_contact_with.append(p2)
                                    else:
                                        if(p1.infect(p2, self.day)):
                                            newly_infected.append(p1)
                                            if not p1.will_show_symptoms and p1 not in self.asymptomatic_container:
                                                self.asymptomatic_container.add(p1)
                                        p2.came_in_contact_with.append(p1)
        return newly_infected

    def update_fps(self):
        """
            Updates & returns FPS per tick
        """
        fps = str(int(self.clock.get_fps()))
        return fps

    def update_time(self):
        """
            Updates & returns(day) time per tick
        """
        self.day = np.round(self.tick / cfg.DAY_IN_CLOCK_TICK, 2)
        return 'Day {}'.format(self.day)

    def move_to_quarantine(self, p, override=False):
        """
            Input:
                p = Particle
                override = flag

            Moves intected particle to quarantine @ recovery rate mentioned in config file.
            In case of contact tracing override flag is passed and even asymptomatic particles \
                    are quarantined

        """
        if cfg.QUARANTINE and p.is_infected and not p.quarantined and not p.is_travelling:

            if ((self.day - p.infected_since) > cfg.QUARANTINE_AT_DAY and p.will_show_symptoms) or override:
                p.fly_to_in_peace(
                        (cfg.QUARANTINE_CENTRE_WIDTH / 2) + self.main_x,
                        (cfg.QUARANTINE_CENTRE_HEIGHT / 2),
                        self.q_centre_wall_vector
                )
                p.quarantined = True
                self.to_contact_trace.append(p)

    def update_containers(self, newly_infected, newly_recovered):
        """
            Input:
                newly_infected = list of newly infected particles
                newly_recovered = list of newly recovered particles

            Updates the infected container with list of newly infected particles
            Updates the removed container with list of newly recovered particles
        """
        if newly_infected:
            self.susceptible_container = [
                    sus for sus in self.susceptible_container if sus.is_susceptible]
            self.infected_container.extend(newly_infected)
        if newly_recovered:
            self.infected_container = [
                    inf for inf in self.infected_container if inf.is_infected]
            self.removed_container.extend(newly_recovered)

    def trace_line(self, p):
        """
            Input:
                p = Particle

            Draws a straight line per tick between the input particle and the particles that \
                    it has come in contact with
        """
        if cfg.CONTACT_TRACING and p.is_infected:
            for i in p.came_in_contact_with:
                draw_line(self.window, cfg.LIGHTYELLOW, p.x, p.y, i.x, i.y)

    def update_stats(self):
        """
            Updates line chart per tick with shaded area with color code of \
                    Susceptible, Infected, Removed.
            Scale is determined with the the number of ticks the simulation will run \
                    (config = RUN_TIME_IN_TICK)
        """
        stats_height = self.stats.get_height()
        stats_width = self.stats.get_width()

        n_sus_now = self.suslen
        n_inf_now = self.inflen
        n_pop_now = self.alllen
        n_rec_now = self.reclen

        t = int((self.tick / cfg.RUN_TIME_IN_TICK) * stats_width) - 1

        y_infect = int(
            stats_height - (n_inf_now / n_pop_now) * stats_height
        )

        y_susceptible = int((n_sus_now / n_pop_now) * stats_height)

        stats_graph = pygame.PixelArray(self.stats)
        stats_graph[t, :y_susceptible] = pygame.Color(*cfg.SUSCEPTIBLE_COLOR)
        stats_graph[t, y_infect:] = pygame.Color(*cfg.INFECTED_COLOR)

    def init_render_stats(self):
        """
            Renders the stats box where chart is drawn in __init__.
            This is called once

            retruns None
        """
        stats_x, stats_y = cfg.GAME_WIDTH // 4, cfg.GAME_HEIGHT // 4
        self.stats = pygame.Surface((stats_x, stats_y))
        self.stats.fill(cfg.GREY)
        self.stats.set_alpha(200)
        self.stats_pos = (10, cfg.GAME_HEIGHT - (stats_y + 10))

    def render_stats(self):
        """
            Renders the chart SIR chart every tick
        """
        self.stats.unlock()
        self.window.blit(self.stats, self.stats_pos)

    def update_tick(self):
        """
            Updates tick counter per tick
        """
        self.tick += 1

    def update_infection_timeseries(self):
        """
            Updates infected time series per day, used to calculate Ro
        """
        if self.day % 1 == 0 and self.inflen != self.T:
            self.infection_timeseries.append(self.inflen)
            if len(self.infection_timeseries) > 1:
                self.diff_infection_timeseries.append(
                        (self.inflen - self.infection_timeseries[-2])
                )
            else:
                self.diff_infection_timeseries.append(self.inflen)

    def travel_to_central_location(self):
        """
            Below runs every 2nd day
                Chosen particle travels to the central localtion right bottom room \
                        which has a smaller area than any other room in the simulation.
                The small area increases the probability of a particle of contracting the virus \
                        iff the a particle with the virus is in the room already.
                Max: 5 particles are chosen at random from the all container
                Min: 0 also can be chosen if the particles do not meet the following criteria.

                Filter critiera:
                    - Particle should not already be already in the room
                    - Particle should not be quarantined

            Below runs every 10th day
                Particles in central location are transfered back to their original room \
                        only criteria filtering this is if the particle is quarantined.
        """
        if not cfg.CENTRAL_LOCATION and self.day % .5 == 0:
            return

        now_there = self.in_central_location
        if (self.day % 10 == 0):
            for p in self.in_central_location:
                if p.quarantined:
                    continue
                p.fly_to_in_peace(p.prev_xy_b[0], p.prev_xy_b[1], p.prev_xy_b[2])
            self.in_central_location = set()

        if (self.day % 2 != 0):
            return

        how_many = 5
        for _ in range(how_many):
            c = np.random.randint(0, self.alllen)

            p = self.all_container[c]

            if p in now_there or p.quarantined:
                continue

            xd = (self.central_location_wall_vector['x1'] - self.central_location_wall_vector['x0']) / 2
            x = self.central_location_wall_vector['x0'] + (xd/2) + self.central_wall_width
            yd = (self.central_location_wall_vector['y1'] - self.central_location_wall_vector['y0']) / 2
            y = self.central_location_wall_vector['y0'] + (yd/2) + self.central_wall_width
            p.fly_to_in_peace(x, y, self.central_location_wall_vector)

            self.in_central_location.add(p)

    def pick_lucky_winners_for_travel(self):
        """
            A particle pair travels inter community per tick if there is more than one community
            Max 2 tries are made to find unique particles suitable for travel
            Max 1 pair travels
            Min 0 pair travels

            Particles are chosen at random form all container

            Filtering criteria:
                - Particles should not be in the same community
                - No particle should be quarantined
                - No particle should be in traveling phase
        """
        if not cfg.TRAVEL:
            return

        should_travel_happen = uniform_probability()
        if should_travel_happen <= cfg.TRAVEL_FREQUENCY:

            p1, p2 = self.all_container[0], self.all_container[0]

            try_till = 2
            i = 0

            while p1.my_boundries == p2.my_boundries and i < try_till:
                c1 = np.random.randint(0, self.alllen)
                c2 = np.random.randint(0, self.alllen)
                p1 = self.all_container[c1]
                p2 = self.all_container[c2]

                i += 1

                q = p1.quarantined + p2.quarantined + p1.is_travelling + p2.is_travelling
                if q != 0:
                    continue

                tmp = p1.my_boundries
                p1.fly_to_in_peace(p2.x, p2.y, p2.my_boundries)
                p2.fly_to_in_peace(p1.x, p1.y, tmp)
                break

    def contact_trace(self):
        """
            Contact tracking done every day
            Contact tracing is constrained with resources, we assume that there exits only \
                    one team of contact tracers for the given population.
            When a infected particle is quarantined it is put into a queue for contact tracing

            Queue.pop() gives the particle to trace
            Every particles maintains a stack of particles whom it came in contact with
            Stack.pop() is done on the trace particle
                if the poped particle is infected then quarantine
                when Stack empty (trace complete) remove particle from queue
        """
        if not cfg.CONTACT_TRACING or self.day % 1:
            return
        if self.to_contact_trace:
            trace = self.to_contact_trace[0]
            if trace.came_in_contact_with:
                to_q = trace.came_in_contact_with.pop()
                self.move_to_quarantine(to_q, True)
            else:
                self.to_contact_trace.popleft()

    def vaccinate(self, p):
        """
            Vaccine sessions are held twice per day
            if vaccine are available then it is provided to particle
            vaccine provides shield to partilce shield brings down the probability \
                    drastically (config.SHIELD_PROVIDED_BY_VACCINE)
            2 doses can be given to a particle, 2nd dose gives complete immunity(depending on the shield value)

            VACCINE_DISPERSION_RATE / suslen  = When susceptible length is high than vaccine distribution is slow \
                    when susceptible length drops distribution is higher than before
        """
        if cfg.VACCINE and self.day % .2 and p.vaccinated < (2 * cfg.SHIELD_PROVIDED_BY_VACCINE) and not p.is_infected:
            probability_of_getting_vaccine = (cfg.VACCINE_DISPERSION_RATE / self.suslen)
            will_p_get_vaccine = uniform_probability()
            if p.vaccinated:
                will_p_get_vaccine += .3
            if will_p_get_vaccine <= probability_of_getting_vaccine and self.vaccine_availability >= 1:
                p.vaccinated += cfg.SHIELD_PROVIDED_BY_VACCINE
                if p.vaccinated == cfg.SHIELD_PROVIDED_BY_VACCINE:
                    p.color = cfg.LIGHTPINK
                elif p.vaccinated > cfg.SHIELD_PROVIDED_BY_VACCINE:
                    p.color = cfg.LIGHTBLUE

                p.radius -= 1
                self.vaccine_availability -= 1


    def lockdown(self, p):
        """
            
        """
        if cfg.LOCKDOWN:
            cfg.TRAVEL_FREQUENCY = 0.0

    def update_the_grid(self, p, old_row_col):
        """
            Updates the grid cell in which the particle has moved to
        """
        self.grid[old_row_col[0]][old_row_col[1]].remove(p)
        self.grid[p.grid[0]][p.grid[1]].append(p)

    def update_and_render(self):
        """
            This function is where everything happnes in terms of updates/renders
            Called in the main game loop
        """
        self.update_tick()
        self.window.fill(cfg.BACKGROUND)

        for wv in self.wall_vector_list:
            draw_walls(self.window, wv, self.wall_width)

        self.window.fill(cfg.BACKGROUND, (self.main_x, 0, cfg.GAME_WIDTH, cfg.GAME_HEIGHT))

        # Quarantine walls
        draw_walls(self.window, self.q_centre_wall_vector, self.wall_width)

        # Central location walls
        draw_walls(self.window, self.central_location_wall_vector, self.central_wall_width)

        self.travel_to_central_location()

        day = self.update_time()
        fps = self.update_fps()

        self.disperse_vaccine()

        self.all_container.sort(key=lambda p: p.x)

        newly_infected = list()
        newly_recovered = list()
        self.contact = 0
        self.time = 0
        for pi in range(self.alllen):
            # update -------
            p = self.all_container[pi]

            if p.is_removed:
                continue

            p.update_2d_vectors()
            bounce_wall(p, p.my_boundries)

            # USEAGE - uniform grid
            row_col = which_grid(self.cell_size_w, p.x, self.cell_size_h, p.y)
            old_row_col = p.update_grid(row_col)
            if (old_row_col):
                self.update_the_grid(p, old_row_col)

            # # USEAGE - sweep n prune
            # if pi < self.T - 1:
            #     newly_infected.extend(self.handle_particle_collision(pi))

            # render ------
            pygame.draw.circle(self.window, p.color, (p.x, p.y), p.radius)
            if(p.is_infected and p.recover(self.day)):
                newly_recovered.append(p)
            self.trace_line(p)
            self.move_to_quarantine(p)
            self.vaccinate(p)

        # USEAGE - uniform grid
        newly_infected = self.handle_particle_collision()

        self.contact_trace()
        self.update_stats()
        self.render_stats()
        self.update_containers(newly_infected, newly_recovered)

        self.update_infection_timeseries()
        self.Ro = calculate_r_naught(self.diff_infection_timeseries, self.Ro)
        self.BETA.append(self.Ro)

        if self.Ro > self.Rmax:
            self.Rmax = self.Ro

        bar_data = {
                'S': (self.suslen, cfg.SUSCEPTIBLE_COLOR),
                'I': (self.inflen, cfg.INFECTED_COLOR),
                'R': (self.reclen, cfg.REMOVED_COLOR),
                'seq': ['S', 'I', 'R'],
                'font': self.font,

            }
        bar_chart(
                self.window, self.main_x,
                cfg.QUARANTINE_CENTRE_HEIGHT, self.X,
                self.T, bar_data, self.bar_chart_height)

        Ro_avg = np.round(np.average(self.BETA), 2)

        display_text(self.window, self.font, fps, 10, 10)
        display_text(self.window, self.font, day, self.main_x / 2 - 10, 10)
        display_text(self.window, self.font, 'Ro {}'.format(self.Ro), 10, 25)
        display_text(self.window, self.font, 'Ro Avg {}'.format(Ro_avg), 10, 35)
        display_text(self.window, self.font, 'Ro max {}'.format(self.Rmax), 10, 45)
        k = np.round(len(self.asymptomatic_container) / self.T, 2)
        display_text(self.window, self.font, 'k {}'.format(k), 10, 55)

        self.pick_lucky_winners_for_travel()

        pygame.display.update()
        self.log()

    def log(self):
        """
            format made easy for data tools
            FORMAT: DAY S I R Ro
        """
        if cfg.LOGGING:
            if self.day % 1 == 0:
                logging.info(
                        " {0} {1} {2} {3} {4}".format(self.day, self.suslen, self.inflen, self.reclen, self.Ro)
                        )

    def run(self):
        """
            The main game loop
        """
        if cfg.LOGGING:
            logging.info("START")

        while self.running:
            if cfg.RUN_TIME_IN_DAYS < self.day:
                font = pygame.font.SysFont(None, 32)
                display_text(
                        self.window, font,
                        "Simulation DONE, reached days limit",
                        cfg.GAME_WIDTH // 4, cfg.GAME_HEIGHT // 2)
                self.pause = True
                pygame.display.update()
            self.process_input()
            if not self.pause:
                self.update_and_render()
                self.clock.tick(self.clock_tick)

        if cfg.LOGGING:
            logging.info("END")

        pygame.quit()

