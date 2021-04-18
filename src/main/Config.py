
class Config:
    def __init__(self):
        # Game setup
        self.GAME_TITLE = "Disease Simulator"
        self.GAME_WIDTH = 800
        self.GAME_HEIGHT = 600
        self.FPS = 60
        self.DAY_IN_CLOCK_TICK = self.FPS
        self.WALL_SIZE = 2
        self.RUN_TIME_IN_DAYS = 100
        self.RUN_TIME_IN_TICK = self.RUN_TIME_IN_DAYS * self.DAY_IN_CLOCK_TICK
        self.N_GRID_ROW = 10
        self.N_GRID_COL = 10

        # VIRUS PARAMETERS
        self.QUARANTINE = True
        self.QUARANTINE = False
        self.POPULATION = 1000 # # of particles
        self.I0 = 1 # initial infected
        self.R0 = 0 # initial removed
        self.BETA = 2.4 # R-value
        self.RECOVERED_PERIOD_IN_DAYS = 14
        self.TRANSMISSION_PROBABILITY = .3

        self.MASKS = False
        self.RATIO_OF_POP_WITH_MASKS = .5

        self.MASK_MASK = .05
        self.MASK_NOMASK = 0.125 # (10+15) / 2 .. disease patient without mask
        self.NOMASK_MASK = 0.075 # (5+10) / 2 .. disease patient with mask

        self.QUARANTINE_CENTRE_WIDTH = round(self.GAME_WIDTH * .3)
        self.QUARANTINE_CENTRE_HEIGHT = round(self.GAME_HEIGHT * .3)
        self.GAME_WIDTH += self.QUARANTINE_CENTRE_WIDTH

        # Colors
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.DARKGREEN = (10, 69, 10)
        self.LIGHTGREEN = (0, 60, 0)
        self.BLUE = (0, 0, 70)
        self.BLACK = (0, 0, 0)
        self.GREY = (30, 30, 30)
        self.WHITE = (255, 255, 255)
        self.SICK_YELLOW = (190, 175, 50)
        self.PURPLE = (130, 0, 130)
        self.LIGHTRED = (225, 69, 69)

        self.PARTICLE_RADIUS = 5
        self.PARTICLE_COLOR = (0, 255, 0)
        self.PARTICLE_DISPLACEMENT = .4
        self.PARTICLE_VELOCITY = 1

        self.SUSCEPTIBLE_TYPE = 3
        self.INFECTED_TYPE = 2
        self.RECOVERED_TYPE = 1
        self.REMOVED_TYPE = 0

        self.SUSCEPTIBLE_COLOR = self.LIGHTGREEN
        self.INFECTED_COLOR = self.RED
        self.RECOVERED_COLOR = self.GREY

        self.BACKGROUND = (10, 10, 10)


        self.TESTING_MODE  = True
        # self.TESTING_MODE  = False
        if self.TESTING_MODE:
            self.GAME_WIDTH = 300
            self.GAME_HEIGHT = 300

            self.POPULATION = 30
            self.I0 = 1
            self.PARTICLE_VELOCITY = 1
            # self.RECOVERED_PERIOD_IN_DAYS = 3

            self.QUARANTINE_CENTRE_WIDTH = round(self.GAME_WIDTH * .4)
            self.QUARANTINE_CENTRE_HEIGHT = round(self.GAME_HEIGHT * .4)
            self.GAME_WIDTH += self.QUARANTINE_CENTRE_WIDTH


def knuth_shuffle(n):
    for i in range(len(n)):
        j = random.randrange(i, len(n))
        n[i], [j] = n[j], n[i]
    return n
