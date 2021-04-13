from src import Simulator

if __name__ == "__main__":
    run_time = 5000 # in ticks
    T = 1000 # # of particles
    I0 = 1 # initial infected
    R0 = 0 # initial removed
    width = 1200
    height = 600

    test = 0
    if test:
        T = 10
        I0 = 1
        width = 100
        height = 100

    sim = Simulator(run_time, T, I0, R0, width, height)
    sim.run()
