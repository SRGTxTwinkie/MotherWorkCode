from tkinter import *


class Check():
    def __init__(self, root, label):
        self.label = label
        self.button = Button(root, text= self.label + " - [ ]", command=lambda: self._checkBox())
        self.isChecked = False

        self.button.pack()
        
    def _checkBox(self):
        self.button.configure(text=self.label + " - [X]")
        self.isChecked = not self.isChecked
    
    def checked(self):
        return self.isChecked()    
    
    def getButtonRef(self):
        return self.button
    
