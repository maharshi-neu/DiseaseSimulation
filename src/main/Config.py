class Config:
    def __init__(self):
        self.GAME_TITLE = "Disease Simulator"
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
        self.PARTICLE_VELOCITY = 2

        self.SUSCEPTIBLE_TYPE = 3
        self.INFECTED_TYPE = 2
        self.RECOVERED_TYPE = 1
        self.REMOVED_TYPE = 0

        self.SUSCEPTIBLE_COLOR = self.LIGHTGREEN
        self.INFECTED_COLOR = self.RED
        self.RECOVERED_COLOR = self.GREY

        self.BACKGROUND = (10, 10, 10)

