#from Tkinter import *
#from mttkinter import mtTkinter as tk
from mttkinter import mtTkinter as mtk

import tkFileDialog

import time

################################################################################
################ D E F I N E     G U I     F I E L D S  ########################
################################################################################


GLOBAL_BUTTON_COLOR="light gray"
def setGlobalButtonColor(color):
	global GLOBAL_BUTTON_COLOR
	GLOBAL_BUTTON_COLOR = color

def chooseButtonColor(configColor):
	global GLOBAL_BUTTON_COLOR
	btnColor = GLOBAL_BUTTON_COLOR
	if(configColor):
		btnColor = configColor
	return btnColor

def convertToColorCode(widget, color):
	if(color[0] != "#"):
		bgCode = widget.winfo_rgb(color)
		color = "#%04x%04x%04x" % bgCode
	return color
def clamp(val, minimum=0, maximum=65535):
	if val < minimum:
		return minimum
	if val > maximum:
		return maximum
	return val
def colorscale(hexstr, scalefactor):
	"""
	Scales a hex string by ``scalefactor``. Returns scaled hex string.

	To darken the color, use a float value between 0 and 1.
	To brighten the color, use a float value greater than 1.

	>>> colorscale("#DF3C3C", .5) >>> #6F1E1E
	"""
	hexstr = hexstr.strip('#')
	if scalefactor < 0 or len(hexstr) != 12: return hexstr
	r, g, b = int(hexstr[:4], 16), int(hexstr[4:8], 16), int(hexstr[8:], 16)
	r = clamp(r * scalefactor)
	g = clamp(g * scalefactor)
	b = clamp(b * scalefactor)
	#print(r,g,b)
	return "#%04x%04x%04x" % (r, g, b)

def findLongestStrInList(list):
	lenList=[]
	for x in list: 
		lenList.append(len(x))
	return max(lenList)
def findLongestStrInLists(lists):
	list = []
	for l in lists: list.extend(l)
	return findLongestStrInList(list)

class View(object):
	def __init__(self, key=""):
		self.key = key
		self.parent = None
		self.views = []
		self.tk=None
		self.configArgs = {}
	def setParent(self, parent):
		self.parent = parent
	def getContext(self):
		return self.parent.getContext()
	def addView(self, view):
		views = []
		if(isinstance(view, View)): self.views.append(view)
		else: self.views.extend(view)
		for v in self.views:
			v.setParent(self)

		
	def __str__(self, depth=0):
		s = " "*depth + "[%s] %s\n" % (type(self), self.key)
		s += ("").join([" "*depth + "%s" % (c.__str__(depth+2)) for c in self.views])
		return s
	#def makeView(self, r=0, c=0):
	#	return r,c
	def makeView(self,r, c, master):
		for v in self.views:
			v.makeView(r,c, master)
		return r,c, master
	def getValue(self):
		return None
	def setValue(self, v):
		pass

	def config(self, **kwargs):
		self.configArgs = kwargs

	def grabConfigArg(self, cfg):
		arg = None
		if(cfg in self.configArgs):
			arg = self.configArgs.get(cfg)
			del self.configArgs[cfg]
		return arg


class Text(View):
	def __init__(self, key, label):
		super(Text, self).__init__(key)
		self.label = label
	def makeView(self, master):
		l = mtk.Label(master, text=self.label, **self.configArgs)
		l.pack()
		return l

class ActionButton(View):
	def __init__(self, key, label, actionCallback=None, height=0, width=0):
		super(ActionButton, self).__init__(key)
		self.label = label
		self.args = {}
		if(width != 0): self.args["width"] = width
		if(height !=0): self.args["height"]=height
		self.actionCallback = actionCallback
		self.state = False
	def onClick(self):
		self.state = not self.state
		if(self.actionCallback):
			self.actionCallback(self)
	def makeView(self, master):
		bg = master.cget('bg')
		frame = mtk.Frame(master, bg=bg)
		buttonbg = convertToColorCode(master, chooseButtonColor(self.grabConfigArg("buttoncolor")))
		b = mtk.Button(	frame, text=self.label, anchor='w', 
					bg=buttonbg, 
					activebackground=colorscale(buttonbg, 0.95),
					command = self.onClick, **self.args)
		b.pack(padx=5, pady=5)
		return frame

class Checkbox(View):
	def __init__(self, key, label, actionCallback=None, selectColor=""):
		super(Checkbox, self).__init__(key)
		self.label = label
		self.actionCallback = actionCallback
		self.state = False
		self.selectColor = selectColor
	def onClick(self):
		self.state = not self.state
		if(self.actionCallback):
			self.actionCallback(self)
	def makeView(self, master):
		bg = master.cget('bg')
		frame = mtk.Frame(master, bg=bg)
		checkbuttonState = mtk.IntVar()
		checkbuttonState.set(int(self.state))
		b = mtk.Checkbutton(frame, variable=checkbuttonState, anchor='w', bg=bg, 
						command = self.onClick, 
						highlightthickness=0, bd=0, selectcolor=self.selectColor)
		b.pack(padx=5, pady=5)
		return frame
	def getValue(self):
		return self.state


class Container(View):
	def __init__(self, key):
		super(Container, self).__init__(key)
	def makeView(self, master):
		f = mtk.Frame(master)
		for v in self.views:
			tk = v.makeView(f)
			tk.pack()
		return f

class Horizontal(Container):
	def __init__(self, key, padding=0, direction="left"):
		super(Horizontal, self).__init__(key)
		self.direction = mtk.LEFT
		if(direction == "right"):
			self.direction=mtk.RIGHT
		self.padding = padding

	def makeView(self, master):
		horizontal = mtk.Frame(master, bg=master.cget('bg'))
		for v in self.views:
			tk = v.makeView(horizontal)
			tk.pack(side=self.direction, anchor="w", padx=self.padding)
		horizontal.pack()
		self.tk = horizontal

		return horizontal

class Vertical(Container):
	def __init__(self, key, padding=0):
		super(Vertical, self).__init__(key)
		self.padding = padding

	def makeView(self, master):
		vertical = mtk.Frame(master, bg=master.cget('bg'))
		for v in self.views:
			tk = v.makeView(vertical)
			tk.pack(side = mtk.TOP, fill=mtk.X, anchor="w", pady=self.padding)
		self.tk = vertical
		vertical.pack()
		return vertical


class ButtonField(View):
	def __init__(self, key, label, actionCallback=None, height=0, width=0):
		super(ButtonField, self).__init__(key)
		self.label = label
		self.state = False
		self.actionCallback = actionCallback
		self.args = {}
		if(width != 0): self.args["width"] = width
		if(height !=0): self.args["height"]=height

	def onClick(self, mybutton):
		self.state = not self.state
		if(self.actionCallback):
			self.actionCallback(self)

	def makeView(self, master):
		frame = mtk.Frame(master, **self.configArgs)
		frame.pack(side=mtk.TOP, fill=mtk.X, padx=5, pady=5)
		l = mtk.Label(frame, width=15, text=self.label, anchor='w', **self.configArgs)
		l.pack(side=mtk.LEFT)
		self.button = ActionButton("", self.label, actionCallback=self.onClick, **self.args)
		self.button.config(**self.configArgs)
		buttonTk = self.button.makeView(frame)
		buttonTk.pack(side=mtk.RIGHT)
		return frame


class CheckboxField(View):
	def __init__(self, key, label, actionCallback=None, selectColor=""):
		super(CheckboxField, self).__init__(key)
		self.label = label
		self.state = False
		self.actionCallback = actionCallback
		self.selectColor = selectColor

	def onClick(self, mybutton):
		self.state = not self.state
		if(self.actionCallback):
			self.actionCallback(self)

	def makeView(self, master):
		frame = mtk.Frame(master, **self.configArgs)
		frame.pack(side=mtk.TOP, fill=mtk.X, padx=5, pady=5)
		l = mtk.Label(frame, text=self.label, anchor='w', **self.configArgs)
		l.pack(side=mtk.LEFT)
		self.cbx = Checkbox("", self.label, actionCallback=self.onClick, selectColor=self.selectColor)
		self.cbx.config(**self.configArgs)
		tk = self.cbx.makeView(frame)
		tk.pack(side=mtk.RIGHT)
		return frame
	def getValue(self):
		return self.cbx.getValue()

class EntryField(View):
	def __init__(self, key, label, defaultEntry="", enterCallback=None):
		super(EntryField, self).__init__(key)
		self.label = label
		self.defaultEntry = defaultEntry
		self.entryConfig = {}
		self.enterCallback = self.enter
		if(enterCallback): self.enterCallback=enterCallback
		
	def makeView(self, master):
		frame = mtk.Frame(master, **self.configArgs)
		bg = frame.cget('bg')
		l = mtk.Label(frame, width=15, text=self.label, bg=bg, anchor="w")
		v = mtk.StringVar(frame, value=self.defaultEntry)
		self.ent = mtk.Entry(frame, textvariable=v)
		self.ent.bind("<Return>", self.enterCallback)
		l.pack(side=mtk.LEFT, padx=5)
		self.ent.pack(side=mtk.LEFT, expand=True, fill=mtk.X)
		frame.pack(fill=mtk.X, pady=5, anchor="w")
		return frame
#	def config(self, **kwargs):
#		self.entryConfig = kwargs
	def enter(self, event):
		pass
	def getValue(self):
		return self.ent.get()
	def setValue(self, val):
		self.ent.delete(0,mtk.END)
		self.ent.insert(0,val)

class FileDialogField(View):
	def __init__(self, key, label, defaultEntry=""):
		super(FileDialogField, self).__init__(key)
		self.label = label
		self.defaultEntry = defaultEntry
	def makeView(self, master):
		frame = mtk.Frame(master, **self.configArgs)
		bg = frame.cget('bg')
		holder = mtk.Frame(frame, bg=bg)
		self.ent = EntryField("", self.label)
		self.ent.config(**self.configArgs)
		entTk = self.ent.makeView(holder)
		b = mtk.Button(entTk, text="...", bg=chooseButtonColor(self.grabConfigArg("buttoncolor")), command = self.onClick)
		b.pack(side=mtk.RIGHT, padx=(5,0), pady=1)
		holder.pack(fill=mtk.X, pady=5)
		frame.pack()
		return frame
	def onClick(self):
		path = tkFileDialog.askopenfilename(initialdir = "/",title = "Select file")
		self.defaultEntry = path
		self.ent.setValue(path)
	def getValue(self):
		return self.ent.getValue()


class OptionField(View):
	def __init__(self, key, label, options=[], direction="horizontal", boxWidth=None, labelWidth=None):
		super(OptionField, self).__init__(key)
		self.label = label
		self.options = options
		if(not self.options): 	### if list of options is empty, we have to have an option at all times
			self.options.append(" ")
		self.direction = direction
		### preset values in comboBox
		self.defaultEntry = options[0]
		self.selectedValue = self.defaultEntry

		### configure boxwidth for longest element in optionsList or set to given value
		### or better not do that
		self.boxWidth = boxWidth
		### configure min labelWidth if necessary
		self.labelWidth = len(self.label)
		if(labelWidth): self.labelWidth = labelWidth


	### Define gui for checked fields
	def makeView(self, master):
		frame = mtk.Frame(master, **self.configArgs)
		bg = frame.cget('bg')
		bg = convertToColorCode(master, bg)

		l = mtk.Label(frame, text=self.label, width=self.labelWidth, anchor="w", bg=bg)
		variable = mtk.StringVar(frame)
		variable.set(self.defaultEntry)
		self.optionMenu = mtk.OptionMenu(frame, variable, command=self.valueChanged, *self.options)
		self.optionMenu.config(bg=bg, highlightthickness=0,  activebackground=colorscale(bg,0.95))#, activeforeground=colorscale(bg,1.5) )
		if(self.boxWidth): self.optionMenu.config(width=self.boxWidth)

		if(self.direction == "vertical"):
			l.pack(side=mtk.TOP, fill=mtk.X)
			self.optionMenu.pack(side=mtk.BOTTOM, fill=mtk.X, expand=True)
		else:
			l.pack(side=mtk.LEFT, fill=mtk.X)
			self.optionMenu.pack(side=mtk.RIGHT, fill=mtk.X, expand=True)
		
		frame.pack(fill=mtk.X, expand=True)
		return frame

	def valueChanged(self, value):
		self.selectedValue = value
	def getValue(self):
		return self.selectedValue

class GitRepoSelector(View):
	def __init__(self, key, label, repositorys=[], branches=[], type=0):
		super(GitRepoSelector, self).__init__(key)
		self.label = label
		self.repositorys = repositorys
		self.branches = branches
		self.type=type

		self.REPOLABELSTR = "Repository: "
		self.BRANCHLABELSTR = "Branch: "

	def makeView(self, master):
		### grab specific args
		headerbg = self.grabConfigArg("headerbg")
		frame = mtk.Frame(master, **self.configArgs)
		bg = frame.cget('bg')

		frame1 = mtk.Frame(frame, **self.configArgs)
		frame2 = mtk.Frame(frame, **self.configArgs)
		
		l = Text("", self.label)

		### special configuration for this view
		minLabelWidth = max(len(self.REPOLABELSTR), len(self.BRANCHLABELSTR))
		minBoxWidth = None
		if(self.type==0): minBoxWidth = findLongestStrInLists([self.repositorys, self.branches])
		else: minBoxWidth = 18
		self.repo = OptionField(self.key+"_repo", self.REPOLABELSTR, self.repositorys, direction="horizontal", boxWidth=minBoxWidth, labelWidth=minLabelWidth)
		self.branch = OptionField(self.key+"_branch", self.BRANCHLABELSTR, self.branches, direction="horizontal", boxWidth=minBoxWidth, labelWidth=minLabelWidth)

		### configurate these views
		l.config(anchor='w', font='Helvetica 10 bold', bg=headerbg)
		self.repo.config(bg=bg)
		self.branch.config(bg=bg)

		### create those new views for realz
		ltk = l.makeView(frame)
		repotk = self.repo.makeView(frame1)
		branchtk = self.branch.makeView(frame2)
		
		ltk.pack(side=mtk.TOP, fill=mtk.X)
		if(self.type==1):
			frame1.pack(side=mtk.LEFT, padx=5, pady=5, fill=mtk.X)
			frame2.pack(side=mtk.RIGHT, padx=5, pady=5, fill=mtk.X)
		else:
			frame1.pack(side=mtk.TOP, padx=5, pady=5, anchor="w", fill=mtk.X)
			frame2.pack(side=mtk.BOTTOM, padx=5, pady=5,anchor="w", fill=mtk.X)
		return frame
	def getValue(self):
		repo = self.repo.getValue()
		branch = self.branch.getValue()
		return {"repo" : repo, "branch" : branch}


################################################################################
####################### W I N D O W   T H I N G S ##############################
################################################################################


from threading import Thread, Lock


class Window(View, Thread):
	""" holder class for a window, manages the Tk() object and creates a default layout
		which will be used (vertical layout in this case). It is used as an abstraction layer
		for the user, so that nobody has to manage these references and/or so that the
		user has a consistent idea about what a window is"""
	def __init__(self, manager, key, size="100x100", bg="light gray"):
		#super(WindowT, self).__init__()
		View.__init__(self, key)
		Thread.__init__(self)
		self.inited = False

		self.manager = manager
		self.key = key
		self.size = size
		self.bg = bg

		### create first layout
		self.layout = Vertical("layout", padding=5)

		self.ok = True
		self.isClosing = False

	def run(self):
		while(self.ok):
			if(self.inited):
				time.sleep(0.01)
				self.root.update()
				self.root.update_idletasks()
				self.onUpdate()
			else:
				self.init()
		### do we want to destroy this? the thread is about to end so the window should disappear anyways?!?!?!
		### possible memory leak???
		self.destroy()

	def init(self):
		self.root = mtk.Tk()
		self.root.protocol("WM_DELETE_WINDOW", self.closeEvent)
		self.root.title(self.key)
		self.root.geometry(self.size)
		self.root.config(bg=self.bg)
		self.inited = True
		
		self.layout = self.createViews(self.layout)
		### apply window configs to layout!!!
		self.layout.config(**self.configArgs) 
		self.root.config(**self.configArgs)
		### add main layout to window
		self.addView(self.layout)
		### mainframe parent
		self.tk = self.layout.makeView(self.root)

	### own internal close event trigger
	def closeEvent(self):
		self.close()
	### function to close this window (will spin up the manager to do it)
	def close(self):
		self.ok = False
		self.manager.onWindowClose(self)
	### this view does not return its parent context, it IS the context
	def getContext(self):
		return self.root
	def destroy(self):
		self.root.quit()
		self.root.destroy()

	### overridable by user
	def onUpdate(self): pass
	def onClose(self): pass


class WindowManager(object):
	def __init__(self):
		self.windows = []
		self.ok = True

	def openWindow(self, window):
		self.windows.append(window)
		window.start()

	#def closeWindow(self, window):
	#	#print("Closed Window %s" % window.key)
	#	self.windows.remove(window)
	#	### notify user that this window is about to close
	#	window.onClose()
	#	### close the window by stopping the thread supporting it
	#	window.stop()
	#	self.ok = len(self.windows) != 0
	
	def onWindowClose(self, window):
		self.windows.remove(window)
		self.ok = len(self.windows) != 0

	def spin(self):
		### wait for all windows to close
		while(self.ok):
			time.sleep(0.2)
		print("All Windows closed, manager ended ...")


################################################################################
########################### F U N C T I O N S ##################################
################################################################################

# Print a message that will be shown during 'sleep' milliseconds
def fieldMessageBoxSleep(messageText, sleep):
	root = Tk()
	root.title('Startscript')
	message = Message(root, text=messageText)
	message.config(width=200)
	message.pack(padx=80, pady=50, side=mtk.LEFT)
	root.after(sleep, root.destroy) # Sleep in ms
	root.mainloop()

# Print a message that will be shown during 'sleep' milliseconds
def fieldMessageBoxSleep2(messageText, sleep):
	root = Tk()
	root.title('Startscript')
	message = Message(root, text=messageText)
	message.config(width=200)
	message.pack(padx=80, pady=50, side=mtk.LEFT)
	root.update_idletasks()
	sleepSec = sleep / 1000
	time.sleep(sleepSec) # Sleep in s
	root.destroy()