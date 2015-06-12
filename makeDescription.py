import wx, re, textwrap, os.path
from PIL import ImageFont, Image, ImageDraw

# SETUP
imgWidth, imgHeight = 2560, 1600
#font_size = 150

# Space ratio percentages
description_p, contributor_p = .6, .4
#font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)
img = Image.new("RGB", (imgWidth, imgHeight), (30,30,30))

# Borders/margins
margin = imgHeight / 16
right_margin = margin * 2

# Space between description and contributors
padding = margin / 2

desc_h = 0
cont1_h = 0
cont2_h = 0
cont3_h = 0
#path_with_name = ''
contributors = []

# Justification for character limits with 2560x1600 resolution
# 
# max description + collaborators height = 1400
# 
# description to contributors vertical space ratio = 3:2
# description = 960 pixel height max
# contributors = 640 pixel height max
# 
# Description
# average width of letter = 64
# max characters per line based on average = 35
# line height = 180
# max number of lines = 5
# max characters for description = 175
# 
# Contributors, this was for a slightly larger font around 115
# 
# average width of letter = 48
# characters per line = 47
# line height = 138
# max number of lines = 2.5, rounded up to 3
# max characters for contributors = 141

# Get draw module to draw text onto black background
draw = ImageDraw.Draw(img)

# wxPython gui
class GUI(wx.Frame):
    
    '''
    LAYOUT
    '''

    def __init__(self, parent):
	wx.Frame.__init__(self, parent, title="Make Description Image Tool", size=(500, 325), style=wx.DEFAULT_FRAME_STYLE)

	self.panel = wx.Panel(self)
	self.gridSizer = wx.GridBagSizer(5, 5)

	# Text boxes
	self.description_label = wx.StaticText(self.panel, label="Description")
	self.gridSizer.Add(self.description_label, pos=(1, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.description_text_box = wx.TextCtrl(self.panel, value="This is a sample description.")
	self.gridSizer.Add(self.description_text_box, pos=(1, 1), span=(1,3), flag=wx.TOP|wx.EXPAND, border=5)

	self.contributor1_label = wx.StaticText(self.panel, label="Contributor 1")
	self.gridSizer.Add(self.contributor1_label, pos=(2, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.contributor1_text_box = wx.TextCtrl(self.panel, value="Dr. Heriberto Nieto")
	self.gridSizer.Add(self.contributor1_text_box, pos=(2, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
 
	self.contributor2_label = wx.StaticText(self.panel, label="Contributor 2")
	self.gridSizer.Add(self.contributor2_label, pos=(3, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.contributor2_text_box = wx.TextCtrl(self.panel, value="")
	self.gridSizer.Add(self.contributor2_text_box, pos=(3, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

	self.contributor3_label = wx.StaticText(self.panel, label="Contributor 3")
	self.gridSizer.Add(self.contributor3_label, pos=(4, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.contributor3_text_box = wx.TextCtrl(self.panel, value="")
	self.gridSizer.Add(self.contributor3_text_box, pos=(4, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
	
	self.name_label = wx.StaticText(self.panel, label="File Name")
	self.gridSizer.Add(self.name_label, pos=(5, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.name_text_box = wx.TextCtrl(self.panel, value="sampleImage.jpg")
	self.gridSizer.Add(self.name_text_box, pos=(5, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)
	
	self.output_dir_label = wx.StaticText(self.panel, label="Output Directory")
	self.gridSizer.Add(self.output_dir_label, pos=(6, 0), flag=wx.LEFT|wx.TOP, border=10)

	self.output_dir_text_box = wx.TextCtrl(self.panel, value="/path/to/new/image/")
	self.gridSizer.Add(self.output_dir_text_box, pos=(6, 1), span=(1, 3), flag=wx.TOP|wx.EXPAND, border=5)

	self.output_dir_button = wx.Button(self.panel, label="Browse...")
	self.gridSizer.Add(self.output_dir_button, pos=(6, 4), flag=wx.TOP|wx.RIGHT, border=5)

	self.create_button = wx.Button(self.panel, label="Create")
	self.gridSizer.Add(self.create_button, pos=(8, 0), flag=wx.LEFT, border=10)

	self.gridSizer.AddGrowableCol(2)
	self.panel.SetSizer(self.gridSizer)

	# Bind event handlers to all controls that have one.
	self.output_dir_button.Bind(wx.EVT_BUTTON, self.get_output_dir)
	self.create_button.Bind(wx.EVT_BUTTON, self.create_image)

    '''
    EVENT HANDLERS
    '''

    def get_output_dir(self, event):
        dlg = wx.DirDialog(self, "", style=wx.DD_DEFAULT_STYLE | wx. DD_NEW_DIR_BUTTON)
	if dlg.ShowModal() == wx.ID_OK:
	    selected_path = dlg.GetPath()
	    self.output_dir_text_box.SetValue(selected_path)
	dlg.Destroy()

    def exit_app(self):
	dlg = wx.MessageDialog(self, "Description Image Created", "Exit", wx.OK)
	dlg.ShowModal()
	dlg.Destroy()
	self.Close(True)

    def create_image(self, event):
	#global total_height
	#global padding

	if self.validate_description() and self.validate_output_dir() and self.validate_name() and self.validate_contributor1() and self.validate_contributor2() and self.validate_contributor3():
	    # Compile description and contributors height
	    #total_height = contributor_line_height_count + description_line_height_count + padding
	
	    print("imgHeight: " + str(imgHeight))
	    print("desc_h: " + str(desc_h) + " cont1_h: " + str(cont1_h) + " cont2_h: " + str(cont2_h) + " cont3_h: " + str(cont3_h) + " padding: " + str(padding) + " margin: " + str(margin)) 


	    # Where to start drawing, lateral cursor
	    diff = imgHeight - desc_h - cont1_h - cont2_h - cont3_h - padding - margin - margin
	    if diff > 0:
	        current_height = margin + diff / 2
	    else:
	        current_height = margin

	    font_size = 150
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    # How many pixels are in a space between words
	    offset =  draw.textsize(" ", font=font)[0]

	    # DRAW TEXTWRAPPED DESCRIPTION
	    for line in textwrap.wrap(self.description_text_box.GetValue(), width = imgWidth):
	        # Get width and height of line
	        w, h = draw.textsize(line, font=font)
	        # Starting point for word, horizontal cursor
	        cursor = margin
	        for word in line.split():
		    # If the next word overlaps the border, move to next line
		    if (cursor + (draw.textsize(word, font=font)[0]) + offset + right_margin)  >= imgWidth:
		        current_height += h
		        cursor = margin
	    	    draw.text((cursor, current_height), word, font=font)
		    # Move lateral cursor past word
		    cursor += (draw.textsize(word, font=font)[0]) + offset
	        # Move vertical cursor down a line
	        current_height += h

	    # Space between description and contributors
	    current_height += padding

	    # Smaller font for contributors
	    font_size = 100
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    print(contributors)
	    
	    # DRAW TEXTWRAPPED CONTRIBUTORS
	    for line in contributors:
		if not len(line) == 0:
	            # Get width and height of line
	            w, h = draw.textsize(line, font=font)
	            # Starting point for word, horizontal cursor
	            cursor = margin
	            for word in line.split():
		        # If the next word overlaps the page, move to next line
		        if (cursor + (draw.textsize(word, font=font)[0]) + offset + right_margin) >= imgWidth:
		            current_height += h
		            cursor = margin
	    	        draw.text((cursor, current_height), word, font=font)
		        # Move lateral cursor past word
		        cursor += (draw.textsize(word, font=font)[0]) + offset
	            # Move vertical cursor down a line
	            current_height += h
        
	    # SAVE IMAGE
	    # no error checking
	    #print(path_with_name)
	    path_with_name = self.output_dir_text_box.GetValue() + '/' + self.name_text_box.GetValue()
	    img.save(path_with_name)
	    #print("Your image has been saved.")
	    self.exit_app()

    '''
    IMAGE CREATION
    '''

    

    '''
    VALIDATION
    '''

    def validate_description(self):
	print("validating description")

	global desc_h

	description = self.description_text_box.GetValue()
	if len(description) == 0:
	    wx.MessageBox("Please enter a description.", "Error")
	    self.description_text_box.SetBackgroundColour("pink")
	    self.description_text_box.SetFocus()
	    self.description_text_box.Refresh()
	    return False
	else:
	    # Check how tall lines will be, if pixels greater than 60% height minus margins, re-do
	    font_size = 150
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    description_line_height_count = 0
	    for line in textwrap.wrap(description, width = imgWidth):
	        wraparound_factor = draw.textsize(line, font=font)[0] // (imgWidth - margin - right_margin)
	        if draw.textsize(line, font=font)[0] % (imgWidth - margin - right_margin) > 0:
		    wraparound_factor += 1
	        description_line_height_count += draw.textsize(line, font=font)[1] * wraparound_factor
	    if description_line_height_count > imgHeight * description_p:
	        wx.MessageBox("Description must be 175 characters or less.", "Error")
	        self.description_text_box.SetBackgroundColour("pink")
	        self.description_text_box.SetFocus()
	        self.description_text_box.Refresh()
	        return False
	    else:	
		desc_h = description_line_height_count    
		return True

    def validate_contributor1(self):
	print('validating contributor 1')

	#global total_height
	global contributors
	global cont1_h
	
	contributor = self.contributor1_text_box.GetValue()
	if len(contributor) == 0:
	    wx.MessageBox("Please enter a contributor.", "Error")
	    self.contributor1_text_box.SetBackgroundColour("pink")
	    self.contributor1_text_box.SetFocus()
	    self.contributor1_text_box.Refresh()
	    return False
	else:
	    font_size = 100
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    contributor_line_height_count = 0
	    if draw.textsize(contributor, font=font)[0] > (imgWidth - margin - right_margin):
	        wx.MessageBox("Contributor must be 47 characters or less.", "Error")
	        self.contributor1_text_box.SetBackgroundColour("pink")
	        self.contributor1_text_box.SetFocus()
	        self.contributor1_text_box.Refresh()
	        return False
	    else:
		cont1_h = draw.textsize(contributor, font=font)[1]
		contributors = [contributor]
		#print(contributors)
		return True

    def validate_contributor2(self):
	print('validating contributor 2')
	
	global contributors
	global cont2_h	

	contributor = self.contributor2_text_box.GetValue()
	#print("swag")
	if not len(contributor) == 0:
	    font_size = 100
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    contributor_line_height_count = 0
	    if draw.textsize(contributor, font=font)[0] > (imgWidth - margin - right_margin):
	        wx.MessageBox("Contributor must be 47 characters or less.", "Error")
	        self.contributor2_text_box.SetBackgroundColour("pink")
	        self.contributor2_text_box.SetFocus()
	        self.contributor2_text_box.Refresh()
	        return False
	    else:
		cont2_h = draw.textsize(contributor, font=font)[1]
		contributors.append(contributor)
		#print(contributors)
		return True
	else:	
	    return True

    def validate_contributor3(self):
	print('validating contributor 3')
	
	global contributors
	global cont3_h

	contributor = self.contributor3_text_box.GetValue()
	if not len(contributor) == 0:
	    font_size = 100
	    font = ImageFont.truetype("/home/vislab/Projects/Temp/Micah/avenir-light.ttf", font_size)

	    contributor_line_height_count = 0
	    if draw.textsize(contributor, font=font)[0] > (imgWidth - margin - right_margin):
	        wx.MessageBox("Contributor must be 47 characters or less.", "Error")
	        self.contributor3_text_box.SetBackgroundColour("pink")
	        self.contributor3_text_box.SetFocus()
	        self.contributor3_text_box.Refresh()
	        return False
	    else:
		cont3_h = draw.textsize(contributor, font=font)[1]
		contributors.append(contributor)
		#print(contributors)
		return True
	else:
	    return True

    def validate_name(self):
	print("validating image name")

	#global path_with_name	

	if len(self.name_text_box.GetValue()) == 0:
	    wx.MessageBox("Please enter an image file name.", "Error")
	    self.name_text_box.SetBackgroundColour("pink")
	    self.name_text_box.SetFocus()
	    self.name_text_box.Refresh()
	    return False
	elif not self.name_text_box.GetValue()[-4:] == ".jpg":
	    wx.MessageBox("Please save your file as a .jpg.", "Error")
	    self.name_text_box.SetBackgroundColour("pink")
	    self.name_text_box.SetFocus()
	    self.name_text_box.Refresh()
	    return False
	else:
	    #path_with_name += '/'
	    #path_with_name += self.name_text_box.GetValue()
	    return True

    def validate_output_dir(self):
	print('validating output dir')	
	
	#global path_with_name	

	if len(self.output_dir_text_box.GetValue()) == 0:
	    wx.MessageBox("Please enter an output directory.", "Error")
	    self.output_dir_text_box.SetBackgroundColour("pink")
	    self.output_dir_text_box.SetFocus()
	    self.output_dir_text_box.Refresh()
	    return False
	elif not os.path.exists(self.output_dir_text_box.GetValue()):
	    wx.MessageBox("Please enter a valid output directory.", "Error")
	    self.output_dir_text_box.SetBackgroundColour("pink")
	    self.output_dir_text_box.SetFocus()
	    self.output_dir_text_box.Refresh()
	    return False
	else:
	    #path_with_name += self.output_dir_text_box.GetValue()
	    return True

if __name__ == "__main__":
    app = wx.App(False)
    gui = GUI(None)
    gui.Show()
    app.MainLoop()
