# script that is run when Revit starts in the IExternalApplication.Startup event.

import sys 
# import subprocess

lib_path = r'H:\_WORK\PYTHON\REVIT_API\LIB'
# startUp_path = r'C:\_WORK\PYTHON\REVIT_API\LIB\Startup'
sys.path.append(lib_path)
# sys.path.append(startUp_path)

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Drawing
import System.Windows.Forms
from System.Drawing import *
from System.Windows.Forms import Application, Button, Form, ComboBox, Label, TextBox, DockStyle, AnchorStyles
# Import RevitAPI
# clr.AddReference("RevitAPI")
# import Autodesk.Revit.ApplicationServices as revit
from VolumeInquire import *


class MainForm(Form):
    def __init__(self):
        self.InitializeComponent()
    def InitializeComponent(self):
        self.Text = "SWECO INIT SCRIPTS"
        self.Width = 500
        self.Height = 200

        self.label = Label()
        self.label.Text = "Potvrď spuštění iniciačních skriptů pro update parametrů ve výkresu"
        self.label.Width = 250
        self.label.Parent = self
        self.label.Anchor = AnchorStyles.Top
        self.label.Dock = DockStyle.Top

        self.submitButton = Button()
        self.submitButton.Text = 'OK'
        self.submitButton.Click += self.update
        self.submitButton.Parent = self
        self.submitButton.Anchor = AnchorStyles.Bottom
        self.submitButton.Dock = DockStyle.Bottom

        self.cancelButton = Button()
        self.cancelButton.Text = 'Cancel'
        self.cancelButton.Click += self.close
        self.cancelButton.Parent = self
        self.cancelButton.Anchor = AnchorStyles.Bottom
        self.cancelButton.Dock = DockStyle.Bottom

    def runScripts(self):
        self.script = CalculateVolume()
        self.script.run()
        self.label.Text = self.script.getVolume()

    def update(self, sender, event):
        self.runScripts()
        #self.Close()

    def close(self, sender, event):
        self.Close()
    def OnChanged(self, sender, event):
        self.label.Text = sender.Text

def on_document_open(sender, event):
    try:
        Application.EnableVisualStyles()
        myDialogWindow = MainForm()
        Application.Run(myDialogWindow)
        #print event.Document
    except Exception as ex:
        error_type, error_instance, traceback = sys.exc_info()	
        print("Creating event in on_document_open() failed. \
                            Exception: {0} error_type: {1}, error_instance {2}, traceback -{3}" \
                                .format(ex \
                                ,error_type \
                                ,error_instance \
                                ,traceback))
class RunStartup():
    def __init__(self, revitApp):
        self.revitApp = revitApp
        self.dialogWindow = MainForm()
    def run(self):
        try:
            print ("Načítám SWECO init scripts...")
            self.revitApp.Application.DocumentOpened += on_document_open
#            __window__.Close()  # closes the window 
        except Exception as ex:
                error_type, error_instance, traceback = sys.exc_info()	
                print("Creating event in on_document_open() failed. \
                                    Exception: {0} error_type: {1}, error_instance {2}, traceback -{3}" \
                                        .format(ex \
                                        ,error_type \
                                        ,error_instance \
                                        ,traceback))
