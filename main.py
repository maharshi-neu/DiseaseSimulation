from src import ui, Simulator

WANT_UI = True

if __name__ == "__main__":
    if WANT_UI:
        ui()
    else:
        sim = Simulator()
        sim.run()
