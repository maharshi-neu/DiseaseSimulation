import tkinter as tk
import main


class simulateInFrame:

        def __init__(self, master):
        # ***** Import the guifunctions from the Main.py file
            guifuncs = main.GUI_Functions(master)
        
            HEIGHT = 700
            WIDTH = 800

            canvas = tk.Canvas(master, height=HEIGHT, width=WIDTH)
            canvas.pack()

            frame = tk.Frame(master, bg='#b3ccff')
            frame.place(relx=0.1,rely=0.1,relwidth=0.8,relheight=0.8)

            button = tk.Button(master, text = "Run", bg = 'gray', fg ='blue',command=guifuncs.simulatecode)
            button.pack(side='left', fill='x',expand=True)
