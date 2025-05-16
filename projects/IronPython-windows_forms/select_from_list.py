import clr 
#import os 

# Verify these are needed. 
clr.AddReference('System') 
clr.AddReference('System.Drawing') 
clr.AddReference("System.Windows.Forms") 

#  Windows Forms Elements 
from System.Drawing import Point, Icon, Color 
from System.Windows import Forms 
from System.Windows.Forms import Application, Form 
from System.Windows.Forms import DialogResult, GroupBox, FormBorderStyle, Label
from System.Windows.Forms import ComboBox, Button, DialogResult, AnchorStyles, DockStyle, Screen, TextBox, ScrollBars, ToolStripContainer, ToolStrip, TreeView, TreeNode

class SelectFromList(Form): 
	""" 
		form = SelectFromList(floor_types.keys()) 
		form.show() 
			if form.DialogResult == DialogResult.OK: 
			chosen_type_name = form.selected 
	"""

	def __init__(self, title, options, sort=True): 
		"""
			Args: 
				title (str): Title of Prompt 
				options (dict): Name:Object 
				**sort (bool): Sort Entries 
		""" 
		self.selected = None 
		if sort: 
			options = sorted(options) 
		self.num = 0

		screenSize = Screen.GetWorkingArea(self)
		self.Height = screenSize.Height / 2
		self.Width = screenSize.Width / 3

		#  Window Settings 
		self.Text = title or 'Select View Type' 
		self.MinimizeBox = False 
		self.MaximizeBox = False 
		self.BackgroundColor = Color.White 
		self.FormBorderStyle = FormBorderStyle.FixedSingle 
		self.ShowIcon = False 
		
		self.combobox = ComboBox() 
		self.combobox.Width = 200 
		self.combobox.Height = 20
		self.combobox.DataSource = options 
		self.combobox.Parent = self
		self.combobox.Anchor = AnchorStyles.Top
		self.combobox.Dock = DockStyle.Top
		self.combobox.RectangleToScreen
		self.combobox.Click += self.combo_change
		
		self.label = Label()
		self.label.Text = "Nothing selected yet"
		self.label.Width = 250
		self.label.Parent = self
		self.label.Anchor = AnchorStyles.Top
		self.label.Dock = DockStyle.Top

		self.textBox = TextBox()
		self.textBox.Text = "{}".format(dir(Form))
		self.textBox.Width = 250
		self.textBox.Multiline = True
		self.textBox.ScrollBars = ScrollBars.Vertical
		self.textBox.WordWrap = True
		self.textBox.ResumeLayout(False);
		self.textBox.PerformLayout();
		self.textBox.Height = 250
		self.textBox.Parent = self
		self.textBox.Anchor = AnchorStyles.Bottom
		self.textBox.Dock = DockStyle.Top

		self.toolStripContainer1 = ToolStripContainer()
		self.toolStrip1 = ToolStrip()
		self.toolStrip2 = ToolStrip()
		# Add items to the ToolStrip.
		self.toolStrip1.Items.Add("One")
		self.toolStrip1.Items.Add("Two")
		self.toolStrip1.Items.Add("Three")
		self.toolStrip2.Items.Add("EEE")
		self.toolStrip2.Items.Add("AAA")
		self.toolStrip2.Items.Add("SSS")
		self.toolStripContainer1.Anchor = AnchorStyles.Bottom
		self.toolStripContainer1.Dock = DockStyle.Top
		# Add the ToolStrip to the top panel of the ToolStripContainer.
		self.toolStripContainer1.TopToolStripPanel.Controls.Add(self.toolStrip1)
		self.toolStripContainer1.TopToolStripPanel.Controls.Add(self.toolStrip2)
		# Add the ToolStripContainer to the form.
		self.Controls.Add(self.toolStripContainer1)

		self.treeView = TreeView()
		self.treeNode1 = TreeNode("Brucho")
		self.treeView.Nodes.Add(self.treeNode1)
		self.treeNode2 = TreeNode("Hlava")
		self.treeView.Nodes.Add(self.treeNode2)
		#self.nodes1 = [self.treeNode1, self.treeNode2]
		#self.treeView.Nodes.Add(self.nodes1)
		self.treeNode3 = TreeNode("Noha")
		self.treeNode4 = TreeNode("Ruka")
		self.nodes2 = TreeNode("Koncatiny")
		self.nodes2.Nodes.AddRange((self.treeNode3, self.treeNode4))
		self.treeView.Nodes.Add(self.nodes2)
		self.treeView.Anchor = AnchorStyles.Bottom
		self.treeView.Dock = DockStyle.Top
		self.Controls.Add(self.treeView)


		self.selectButton = Button() 
		self.selectButton.Text = 'Select' 
		#self.selectButton.Location = Point(0,50) 
		self.selectButton.Parent = self
		self.selectButton.Anchor = AnchorStyles.Bottom
		self.selectButton.Dock = DockStyle.Bottom
		self.selectButton.Width = self.combobox.Width 
		self.selectButton.Height = 20 
		self.selectButton.Click += self.selectButton_click 		

		self.closeButton = Button() 
		self.closeButton.Text = 'Close' 
		#self.closeButton.Location = Point(0,50) 
		self.closeButton.Parent = self
		self.closeButton.Anchor = AnchorStyles.Bottom
		self.closeButton.Dock = DockStyle.Bottom
		self.closeButton.Width = self.combobox.Width 
		self.closeButton.Height = 20 
		self.closeButton.Click += self.closeButton_click 	
		
		self.Controls.Add(self.combobox)
		self.Controls.Add(self.label) 
		self.Controls.Add(self.textBox) 
		self.Controls.Add(self.selectButton)
		self.Controls.Add(self.closeButton)  
	
	def combo_change(self, sender, event):
		self.selected = self.combobox.SelectedValue 
		myEvent = "{}".format(event)
		self.label.Text = self.selected + myEvent

	def selectButton_click(self, sender, event): 
		self.selected = self.combobox.SelectedValue 
		self.label.Text = self.selected()
		self.DialogResult = DialogResult.OK 

	def closeButton_click(self, sender, event): 
		self.Close() 
		

	
	def show(self): 
		""" Show Dialog """ 
		self.ShowDialog() 

options = {"jano" : "285", "peto" : "5", "Lucka" : "25",}


Application.EnableVisualStyles()

appWindow = SelectFromList("Select something", options, sort=True)
Application.Run(appWindow)