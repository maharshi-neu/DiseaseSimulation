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

        #frame = tk.Frame(master, bg='#b3ccff')
        #frame.place(relx=0.1,rely=0.1,relwidth=0.8,relheight=0.8)

        runButton = tk.Button(master, text = "Run", bg = 'gray', fg ='blue',command=guifuncs.simulatecode)
        runButton.place(relx=0.1,rely=0.1,relwidth=0.1,relheight=0.1)

        stopButton = tk.Button(master, text = "Stop", bg = 'gray', fg ='blue',command=guifuncs.destroy)
        stopButton.place(relx=0.3,rely=0.3,relwidth=0.1,relheight=0.1)

