# -*- coding: utf-8 -*- 
from Tkinter import *
import Tkinter as tk

# hlavni = Tk()
# hlavni.geometry("500x500")
# hlavni.resizable(0, 0) 

# def volanafunkce(udalost):
#     print u"kliknuto na pozici:", udalost.x, udalost.y 

# def volanafunkcee(udalost):
#     print u"Button - 1 - kliknuto na pozici:", udalost.x, udalost.y 
#     print u"Button - 1 - kliknuto na pozici: x_root, y_root :", udalost.x_root, udalost.y_root
#     print u"typ udalosti Button-1", udalost.type
#     print u"Widget", udalost.widget

# def volanafunkceee(udalost):
#     print u"Button - 2 - kliknuto na pozici:", udalost.x, udalost.y 
#     print u"Button - 2 - kliknuto na pozici: x_root, y_root :", udalost.x_root, udalost.y_root
#     print u"typ udalosti Button-2", udalost.type
#     print u"Widget", udalost.widget

# def volanafunkceeee(udalost):
#     print u"Button - 3 - kliknuto na pozici:", udalost.x, udalost.y 
#     print u"Button - 3 - kliknuto na pozici: x_root, y_root :", udalost.x_root, udalost.y_root
#     print u"typ udalosti Button-3", udalost.type
#     print u"Widget", udalost.widget

# ramec = LabelFrame(master = hlavni, text = "myFrame", width=500, height=500, bg = "yellow", bd = 3)
# ramec.pack_propagate(0) #Don't allow the widgets inside to determine the frame's width / height
# ramec.pack(fill=tk.BOTH, expand=True)
# ramec.bind("<Button-1>", volanafunkce)
# ramec.grid(sticky=tk.E+tk.W)

# myButton = Button(ramec, text = "button", bg = "red")

# myButton.bind("<ButtonRelease-1>", volanafunkcee)
# myButton.bind("<ButtonRelease-2>", volanafunkceee)
# myButton.bind("<ButtonRelease-3>", volanafunkceeee)
# myButton.grid()
#hlavni.mainloop()

# s = ""
# for i in range(0,512):
#     s += "1"
# print s
# print hex(int(s,2))

# display = Tk()
# display.geometry('1000x800')
# myButtons = []
# #for i in range(0,20):

# canvas = Canvas(display, bd = 5, bg = 'yellow', width = 500)

# canvas.pack()
# frame1 = Frame(canvas, width=1000, height=700, bd = 5, bg = 'red')

# canvas.create_window((0,0), window=frame1, anchor='nw')

# myButton = tk.Button(frame1)
# myButton.grid(columnspan = 2)

# myButton2 = tk.Button(frame1)
# myButton2.grid()

# display.mainloop()




class zoomer(Tk):

    def __init__(self):
        x=100
        y=100
        Tk.__init__(self)
        self.border = 10
        self.size_x = x
        self.size_y = y

        #SIZE
        self.app_sizex = 200
        self.app_sizey = 200
        fontSize=int(x/20)

        self.title("Graphic")
        self.geometry(str(self.app_sizex+10) + "x" + str(self.app_sizey+40))

        #CANVAS + BORDER
        self.canvas = Canvas(self, width = self.app_sizex, height = self.app_sizey, scrollregion=(0,0,x,y))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.create_line(self.border, self.border, self.border, y-self.border)
        self.canvas.create_line(x-self.border, self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, self.border)
        self.canvas.create_line(self.border, y-self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, y-self.border)
        text1=self.canvas.create_text(50, 50, fill="white",font=("Purisa", fontSize))
        self.canvas.itemconfig(text1, text="Graphic Text")

        #SCROLLING BARS
        self.vbar=Scrollbar(self,orient=VERTICAL)
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.vbar.config(command=self.canvas.yview)
        self.hbar=Scrollbar(self,orient=HORIZONTAL)
        self.hbar.grid(row=2, column=0, sticky="ew")
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        #zoom button
        save_button = Button(self, text = "Zoom")
        save_button["command"] = lambda: self.zoom_in()
        save_button.grid(row=3, column = 0, pady = 5)

        #radiobutton
        self.rbVar = tk.IntVar()
        self.rbVar.set(2)
        self.rb1 = tk.Radiobutton(self, indicatoron = 0, text = "Initial condition from matrix", command=self.radiobuttonAction,
                                    variable = self.rbVar, value = 0)
        self.rb1.grid()
        self.rb2 = tk.Radiobutton(self, indicatoron = 0, text = "Initial", command=self.radiobuttonAction,
                                    variable = self.rbVar, value = 1)
        self.rb2.grid()
        self.rb3 = tk.Radiobutton(self, indicatoron = 0, text = "Initialiii", command=self.radiobuttonAction,
                                    variable = self.rbVar, value = 2)
        self.rb3.grid()

    def radiobuttonAction(self):
        print self.rbVar.get()
        

    def zoom_in(self):
        #Clean canvas
        self.canvas.delete("all")
        self.size_x = int(self.size_x * 1.1)
        self.size_y = int(self.size_y * 1.1)
        x=self.size_x
        y=self.size_y
        fontSize=int(x/20)
        self.canvas.create_line(self.border, self.border, self.border, y-self.border)
        self.canvas.create_line(x-self.border, self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border, self.border, x-self.border, self.border)
        self.canvas.create_line(self.border, y-self.border, x-self.border, y-self.border)
        self.canvas.create_line(self.border,   self.border, x-self.border, y-self.border)
        text1=self.canvas.create_text(self.size_x/2, self.size_y/2, fill="white",font=("Purisa", fontSize) )
        self.canvas.itemconfig(text1, text="Graphic Text")
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        #SCROLLING BARS
        self.vbar.config(command=self.canvas.yview)
        self.hbar.config(command=self.canvas.xview)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)


if __name__ == '__main__':
    my_gui=zoomer()
    my_gui.mainloop()