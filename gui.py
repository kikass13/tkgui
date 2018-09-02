
#from Tkinter import *
from mttkinter import mtTkinter as tk



import GUI


import threading
import time





############################################################################################
############################################################################################
############################################################################################
############################################################################################


class UserInputWindow(GUI.Window):
	def __init__(self, **kwargs):
		super(UserInputWindow, self).__init__(**kwargs)
		
	def createViews(self, layout):
		### config my window
		myColor = "white"
		self.config(bg=myColor)
		GUI.setGlobalButtonColor("lavender")

		### create some views
		userInput = GUI.EntryField("field_user", "Your Name: ")
		robotInfo = GUI.FileDialogField("field_robotInfo", "Robot info file: ")
		self.selectors = [	
						#GUI.GitRepoSelector("selectorStack", "Software Stack", repositorys=["repo1"], branches=["branch1"]),
						GUI.GitRepoSelector("selectorSw", "Software Stack", repositorys=["repo1"], branches=["branch1"], type=0),
						GUI.GitRepoSelector("selectorDriver", "Drivers Stack", repositorys=["repo1"], branches=["branch1"], type=1),
						GUI.GitRepoSelector("selectorHw", "HwSetups", repositorys=["repo1"], branches=["branch111111111"], type = 1),
					]

		h = GUI.Horizontal("", padding=0)
		btnUpdate = GUI.ActionButton("btn_updateBlob", "Update Blob Info", height=3, actionCallback=self.btnUpdateClicked)
		btnNext = GUI.ActionButton("btn_next", "Next", height=3, actionCallback=self.btnNextClicked)
		h.addView(btnUpdate)
		h.addView(btnNext)

		###config these
		userInput.config(bg=myColor)
		robotInfo.config(bg=myColor)
		#btnNext.config(buttoncolor="lavender")
		for v in self.selectors:
			v.config(bg="white smoke", headerbg="coral")
		
		##add these to our window layout
		layout.addView(userInput)
		layout.addView(robotInfo)
		layout.addView(self.selectors)
		layout.addView(h)

		return layout

	def btnUpdateClicked(self, sender):
		print("update")
		self.close()
	def btnNextClicked(self, sender):
		print("next")
		for v in self.selectors:
			print(v.getValue())
		#open new window
		deployUtilsWindow = DeployUtilsWindow(manager=self.manager, key="Do some stuff ...", size="250x400")
		self.manager.openWindow(deployUtilsWindow)

class DeployUtilsWindow(GUI.Window):
	def __init__(self, **kwargs):
		super(DeployUtilsWindow, self).__init__(**kwargs)
		
	def createViews(self, layout):
		### config my window
		myColor = "white"
		self.config(bg=myColor)

		### create some views
		vert = GUI.Vertical("", padding=1)
		self.masterHost = GUI.OptionField("masterHost", "Master host: ", ["host1", "host2"], direction="vertical", boxWidth=12)
		self.deployHost = GUI.OptionField("deployHost", "Deploy host: ", ["host1", "host2"], direction="horizontal", boxWidth=12)
		self.commandFields = [
								GUI.ButtonField("sleep1", "Sleep for 1s", actionCallback=self.cmdBtnClicked, height=4),
								GUI.ButtonField("sleep3", "Sleep for 3s", actionCallback=self.cmdBtnClicked, height=4),
							]
		self.cbx1 = GUI.CheckboxField("cbx1_", "do you love me?", selectColor="lavender")
		self.cbx2 = GUI.CheckboxField("cbx2_", "do you really really love me???", selectColor="lavender")
		###config these
		self.masterHost.config(bg=myColor)
		self.deployHost.config(bg=myColor)
		for v in self.commandFields:
			v.config(bg="white smoke")
		self.cbx1.config(bg=myColor)
		self.cbx2.config(bg=myColor)
		### change padding from the main layout of this window
		layout.padding=7
		##add these to our window layout
		layout.addView(self.masterHost)
		layout.addView(self.deployHost)
		vert.addView(self.commandFields)
		layout.addView(vert)
		layout.addView(self.cbx1)
		layout.addView(self.cbx2)

		###done layout
		return layout

	def cmdBtnClicked(self, sender):
		command = sender.key
		print(self.cbx1.getValue())
		print(self.cbx2.getValue())
		t = threading.Thread(name='my_service', target=lambda:(self.taskStart(sender), self.someTask(command), self.taskDone(sender)) )
		t.start()

	def someTask(self, command):
		print threading.currentThread().getName(), "Starting %s" % command
		print(command)
		if(command == "sleep1"):	
			time.sleep(1)
		elif(command == "sleep3"):
			time.sleep(3)
		else:
			"%s unknown" % command
		print threading.currentThread().getName(), "Exiting %s" % command


	def taskStart(self, sender):
		sender.button.config(bg="red")
		sender.button.config(state="disabled")
	def taskDone(self, sender):
		sender.button.config(bg="#d9d9d9")
		sender.button.config(state="normal")
	

class Nick():
	def __init__(self):
		pass

	def main(self):
		wm = GUI.WindowManager()
		userInputWindow = UserInputWindow(manager=wm, key="Choose your stuff ...", size="600x500")
		wm.openWindow(userInputWindow)
		wm.spin()



def main():
	nick = Nick()
	nick.main()

if __name__ == '__main__':
	main()