class Config:
    def __init__(self):
        # Game setup
        self.GAME_TITLE = "Disease Simulator"
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 60
        self.WALL_SIZE = 5

        # Initial values
        self.TOTAL = 1000 # # of particles
        self.I0 = 3 # initial infected
        self.R0 = 0 # initial removed

        self.TESTING_MODE  = True
        self.TESTING_MODE  = False
        if self.TESTING_MODE:
            self.GAME_WIDTH = 100
            self.GAME_HEIGHT = 100
            self.TOTAL = 10
            self.I0 = 1

        # Colors
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.LIGHTGREEN = (0, 60, 0)
        self.BLUE = (0, 0, 70)
        self.BLACK = (0, 0, 0)
        self.GREY = (30, 30, 30)
        self.WHITE = (255, 255, 255)
        self.SICK_YELLOW = (190, 175, 50)

        self.PARTICLE_RADIUS = 5
        self.PARTICLE_COLOR = (0, 255, 0)
        self.PARTICLE_DISPLACEMENT = .4
        self.PARTICLE_VELOCITY = .5

        self.SUSCEPTIBLE_TYPE = 3
        self.INFECTED_TYPE = 2
        self.RECOVERED_TYPE = 1
        self.REMOVED_TYPE = 0

        self.SUSCEPTIBLE_COLOR = self.LIGHTGREEN
        self.INFECTED_COLOR = self.RED
        self.RECOVERED_COLOR = self.GREY

        self.BACKGROUND = (10, 10, 10)

