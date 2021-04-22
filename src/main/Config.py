
class Config:
    def __init__(self):
        # Game setup
        self.LOGGING = True
        self.GAME_TITLE = "Disease Simulator"
        self.GAME_WIDTH = 800
        self.GAME_HEIGHT = 600
        self.FPS = 60
        self.DAY_IN_CLOCK_TICK = self.FPS
        self.WALL_SIZE = 2
        self.RUN_TIME_IN_DAYS = 60
        self.RUN_TIME_IN_TICK = self.RUN_TIME_IN_DAYS * self.DAY_IN_CLOCK_TICK
        self.N_GRID_ROW = 10
        self.N_GRID_COL = 10

        self.COMMUNITY_ROWS = 1 # how many rows
        self.COMMUNITY_COLS = 1 # how many cols

        # --------------------------------------------------------------
        # VIRUS PARAMETERS
        self.POPULATION = 300 # number of particles
        self.I0 = 3 # initial infected
        self.R0 = 0 # initial removed

        self.RECOVERED_PERIOD_IN_DAYS = 14
        self.TRANSMISSION_PROBABILITY = 0.90



        # OPTION 1
        self.QUARANTINE = True
        self.QUARANTINE_AT_DAY = 5
        self.QUARANTINE_CENTRE_WIDTH = round(self.GAME_WIDTH * .3)
        self.QUARANTINE_CENTRE_HEIGHT = round(self.GAME_HEIGHT * .4)
        self.GAME_WIDTH += self.QUARANTINE_CENTRE_WIDTH


        # OPTION 2
        self.TRAVEL = True
        self.TRAVEL_FREQUENCY = .05


        # OPTION 3
        self.CENTRAL_LOCATION = True
        if self.CENTRAL_LOCATION and self.TRAVEL:
            self.TRAVEL_FREQUENCY = .01


        # OPTION 4
        self.SYMPTOMATIC_ASYMPTOMATIC = True
        self.SYM_ASYM_PROBAB = 0.101


        # OPTION 5
        self.MASKS = True
        self.MASK_EFFECTIVENESS = .95
        self.RATIO_OF_POP_WITH_MASKS = .3
        self.MASK_MASK = 1 - self.MASK_EFFECTIVENESS
        self.MASK_NOMASK = 0.125 # (10+15) / 2 .. disease patient without mask
        self.NOMASK_MASK = 0.075 # (5+10) / 2 .. disease patient with mask


        # OPTION 6
        self.CONTACT_TRACING = True


        # OPTION 7
        # VACCINE
        self.VACCINE = True
        self.VACCINE_DISPERSION_RATE = self.POPULATION / (self.RUN_TIME_IN_DAYS / 2)
        self.SHIELD_PROVIDED_BY_VACCINE = .5


        #Option 8
        self.LOCKDOWN = True



        # FOR INFLUENZA UNCOMMENT THE BELOW
        self.TRANSMISSION_PROBABILITY = 0.50
        self.RECOVERED_PERIOD_IN_DAYS = 5

        # --------------------------------------------------------------
        # TESTING MODE
        self.TESTING_MODE  = False
        if self.TESTING_MODE:
            self.GAME_WIDTH = 300
            self.GAME_HEIGHT = 300

            self.POPULATION = 45
            self.I0 = 3
            self.PARTICLE_VELOCITY = 1

            self.QUARANTINE_CENTRE_WIDTH = round(self.GAME_WIDTH * .4)
            self.QUARANTINE_CENTRE_HEIGHT = round(self.GAME_HEIGHT * .4)
            self.GAME_WIDTH += self.QUARANTINE_CENTRE_WIDTH


        # --------------------------------------------------------------
        # Colors
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.DARKGREEN = (10, 69, 10)
        self.LIGHTGREEN = (0, 60, 0)
        self.BLUE = (0, 0, 70)
        self.BLACK = (0, 0, 0)
        self.GREY = (30, 30, 30)
        self.LIGHTYELLOW = (255, 255, 153)
        self.WHITE = (255, 255, 255)
        self.SICK_YELLOW = (190, 175, 50)
        self.PURPLE = (130, 0, 130)
        self.ORANGERED = (225, 69, 0)
        self.MASKGREEN = (2, 150, 90)
        self.LIGHTORANGE = (255, 204, 102)
        self.LIGHTPINK = (255, 204, 255)
        self.LIGHTBLUE = (179, 255, 255)

        self.PARTICLE_RADIUS = 5
        self.PARTICLE_DIAMETER = self.PARTICLE_RADIUS * 2
        self.PARTICLE_COLOR = (0, 255, 0)
        self.PARTICLE_DISPLACEMENT = .4
        self.PARTICLE_VELOCITY = 1

        self.SUSCEPTIBLE_TYPE = 3
        self.INFECTED_TYPE = 2
        self.REMOVED_TYPE = 1

        self.SUSCEPTIBLE_COLOR = self.LIGHTGREEN
        self.MASKED_SUS_COLOR = self.LIGHTORANGE
        self.INFECTED_COLOR = self.RED
        self.MASKED_INF_COLOR = self.ORANGERED
        self.REMOVED_COLOR = self.GREY
        self.VACCINATED = self.LIGHTPINK

        self.BACKGROUND = (10, 10, 10)
