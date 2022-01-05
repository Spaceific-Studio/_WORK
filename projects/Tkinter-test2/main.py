# -*- coding: utf-8 -*- 
from tkinter import *
import tkinter as tk

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
        #Frame.__init__(self, master, bg = "yellow", bd = 1)
        x=100
        y=100
        Tk.__init__(self)
        self.border = 10
        self.size_x = x
        self.size_y = y

        #SIZE
        self.scrollBarWidth = 50
        self.screen_width = self.winfo_screenwidth() - self.scrollBarWidth
        self.app_sizex = self.screen_width
        self.app_sizey = 800
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
        self.canvasHeight = 2000
        self.interior = interior = Frame(self.canvas, height=self.canvasHeight, width=200, bg="cyan")
        #interior_id = self.canvas.create_window(0,0, window=interior, anchor=NW)
        
        def _configure_interior(event):
        # update the scrollbars to match the size of the inner frame
        	size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
        	self.canvas.config(scrollregion="0 0 %s %s" % size)
        	if interior.winfo_reqwidth() != self.canvas.winfo_width():
        		# update the canvas's width to fit the inner frame
        		self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)
        
        def _configure_canvas(event):
        	if interior.winfo_reqwidth() != self.canvas.winfo_width():
        		# update the inner frame's width to fill the canvas
        		pass
        		#self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)
        
        self.offset_y = 0
        self.prevy = 0
        self.scrollposition = 1
        
        def on_press(event):
            self.offset_y = event.y_root
            #if self.scrollposition < 1:   #commenting out these 2 lines fixed an old scrolling issue that kept resetting the position
            #self.scrollposition = 1
            if self.scrollposition > self.canvasHeight:
            	self.scrollposition = self.canvasheight
            self.canvas.yview_moveto(self.scrollposition / self.canvasHeight)
        
        def on_touch_scroll(event):
        	nowy = event.y_root
        	sectionmoved = 30  # speed of scroll
        	if nowy > (self.prevy):
        		event.delta = -sectionmoved
        	elif nowy < (self.prevy):
        		event.delta = sectionmoved
        	else:
        		event.delta = 0
        	
        	self.prevy= nowy
        	self.scrollposition += event.delta
        	self.canvas.yview_moveto(self.scrollposition/ self.canvasHeight)
        #self.bind("<Enter>", lambda _: self.bind_all('<Button-1>', on_press), '+')  #what does this line do?  apparently not needed
        #self.bind("<Leave>", lambda _: self.unbind_all('<Button-1>'), '+')          ##what does this line do?  apparently not needed
        self.bind("<Enter>", lambda _: self.bind_all('<B1-Motion>', on_touch_scroll), '+')
        self.bind("<Leave>", lambda _: self.unbind_all('<B1-Motion>'), '+')

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
        print(self.rbVar.get())
        

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
	#mainWindow = Tk()
	#mainWindow.grid()
	#mainWindow.grid_propagate(1)
	#app = zoomer(mainWindow)
	#app.master.title("zoom app")
	#app.mainloop()
    my_gui=zoomer()	
    my_gui.mainloop()