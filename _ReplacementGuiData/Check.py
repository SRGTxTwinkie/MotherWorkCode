from tkinter import *


class Check():
    def __init__(self, root, label):
        self.label = label
        self.button = Button(root, text= self.label + " - []", command=lambda: self.checkBox())
        self.isChecked = False

        self.button.pack()
    
    def checkBox(self, event=None):
        if(not self.isChecked):
            self.button.configure(text=self.label + " - [X]")
        else:
            self.button.configure(text=self.label + " - []")
        
        self.isChecked = not self.isChecked
    
    def getButtonReference(self):
        return self.button
