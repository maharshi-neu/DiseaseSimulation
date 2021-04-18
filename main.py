from src import Simulator
import ui_control
from tkinter import * 

class GUI_Functions():

    def __init__(self,parent):
        pass

    def simulatecode(self):
        # Runs a Simulation Code
        sim = Simulator()
        sim.run()

if __name__ == "__main__":
    root = Tk()
    GUI_Frame = ui_control.simulateInFrame(root)
    root.mainloop()