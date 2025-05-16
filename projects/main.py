import Tkinter as tk 
from Tkinter import *
import ttk

class CaAPP(tk.Frame):
    def __init__(self, master = None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        self.quitButton = tk.Button(self, text = "Quit", command = self.quit)
        self.quitButton.grid()

app = CaAPP()
app.master.title("Celular automaton Application")
app.mainloop()