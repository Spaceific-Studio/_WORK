#https://markheath.net/post/wpf-and-mvvm-in-ironpython

"""
#What we need is a basic library of MVVM helper functions. First is a class 
#to load an object from a XAML file.
"""
import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import os
import clr
clr.AddReference("PresentationFramework")
clr.AddReference("PresentationCore")

from System.IO import File
from System.Windows.Markup import XamlReader

class XamlLoader(object):
	def __init__(self, xamlPath):
		stream = File.OpenRead(xamlPath)
		self.Root = XamlReader.Load(stream)
		
	def __getattr__(self, item):
		"""Maps values to attributes.
		Only called if there *isnt* an attribute with this name
		"""
		return self.Root.FindName(item)

"""
#In addition to loading the XAML, Ive added a helper method 
#to make it easy to access any named items within your XAML file, 
#just in case the MVVM approach is proving problematic and you decide 
#to work directly with the controls.

#Next we need a base class for our view models to inherit from, which 
#implements INotifyPropertyChanged. I thought it might be tricky to inherit 
#from .NET interfaces that contain events, but it turns out to be remarkably 
#simple. We just inplement add_PropertyChanged and remove_PropertyChanged, 
#and then we can raise notifications whenever we want.
"""

from System.ComponentModel import INotifyPropertyChanged
from System.ComponentModel import PropertyChangedEventArgs

class ViewModelBase(INotifyPropertyChanged):
	def __init__(self):
		self.propertyChangedHandlers = []

	def RaisePropertyChanged(self, propertyName):
		args = PropertyChangedEventArgs(propertyName)
		for handler in self.propertyChangedHandlers:
			handler(self, args)
			
	def add_PropertyChanged(self, handler):
		self.propertyChangedHandlers.append(handler)
		
	def remove_PropertyChanged(self, handler):
		self.propertyChangedHandlers.remove(handler)

"""
#The next thing we need is a way of creating command objects. I created a very
#basic class that inherits from ICommand and allows us to run our own function 
#when Execute is called. Obviously it could easily be enhanced to properly support 
#CanExecuteChanged and command parameters.
"""

from System.Windows.Input import ICommand

class Command(ICommand):
	def __init__(self, execute):
		self.execute = execute
	
	def Execute(self, parameter):
		self.execute()
		
	def add_CanExecuteChanged(self, handler):
		pass
	
	def remove_CanExecuteChanged(self, handler):
		pass

	def CanExecute(self, parameter):
		return True

"""
#And now we are ready to create our application. Heres some basic XAML. 
#Look into wpfBindingTest.xaml
#Ive only named the grid to demonstrate accessing members directly, 
#but it obviously is not good MVVM practice.
"""
"""
#Now we can make our ViewModel. It will have FirstName and Surname attributes 
#as well as an instance of our Command object:
"""

class ViewModel(ViewModelBase):
	def __init__(self):
		ViewModelBase.__init__(self)
		self.FirstName = "Joe"
		self.Surname = "Smith"
		self.ChangeCommand = Command(self.change)
		self.CloseCommand = Command(self.close)
	
	def change(self):
		self.FirstName = "Dave"
		self.Surname = "Brown"
		self.RaisePropertyChanged("FirstName")
		self.RaisePropertyChanged("Surname")

	def close(self):
		self.Close()

"""
#And finally we are ready to create our application. 
#Simply load the XAML in with the XamlLoader and set the DataContext. 
#I also demonstrate setting the background colour here, 
#to show how easy it is to access named elements in the XAML:
"""

from System.Windows import Application
from System.Windows.Media import Brushes

splittedFile = __file__.split("\\")
rpsFileDir = "\\".join(splittedFile[:-1]) if len(splittedFile) > 2 else ""

xaml = XamlLoader(os.path.join(rpsFileDir, 'wpfBindingTest.xaml'))
xaml.Root.DataContext = ViewModel()
xaml.grid1.Background = Brushes.DarkSalmon
app = Application()
app.Run(xaml.Root)