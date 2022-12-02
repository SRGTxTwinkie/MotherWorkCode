from _ReplacementGuiData.Check import Check
from tkinter import *
from tkinter import ttk
from _0replacementClaims import transferOut, replaceOriginalFunc, pauseAfter

import threading
import os
import time


class MyWindow:
    def __init__(self, root: Tk):
        self.WINWIDTH = 320
        self.WINHEIGHT = 500
        self.root = root

        self.diagnosticWindow = Toplevel(self.root)

        self.debugLog = None

        self.centerX = int(self.root.winfo_screenwidth() / 2)
        self.centerY = int(self.root.winfo_screenheight() / 2)
        self.drag_id = ""

        self.root.wm_title("Replacement Claim")
        self.root.geometry(f"{self.WINWIDTH}x{self.WINHEIGHT}")
        self.root.geometry(
            f"+{self.centerX - self.WINWIDTH}+{self.centerY - self.WINHEIGHT}"
        )
        self.root.resizable(False, False)
        root.attributes("-topmost", True)
        root.update()

        self.getManDate = None
        self.otherCheck = None

        self.checkValButton = None
        self.exitButton = None

        self.buttonPlaceAttrs = {"bordermode": OUTSIDE, "height": 25, "width": 160}

        self.createDebugLog()
        self.otherWindow()
        self.createTexts()
        self.createRadios()
        self.createButtons()

        self.setHandlers()

        self.mousePosLabel = Label(self.diagnosticWindow, text="X: Y:")
        self.mousePosLabel.pack()

    def createTexts(self):
        # Create a text box for the user to enter a string to be eval'd
        self.evalText = Text(self.root, height=1, width=30)
        self.evalText.place(x=1, y=255)

        label = Label(
            text="Eval Text",
        )
        label.place(x=5, y=234)

    def runEvalText(self):
        try:
            exec(self.evalText.get("1.0", END))
        except Exception as e:
            self.debugPrint("ERROR", str(e))
        finally:
            self.evalText.delete("1.0", END)

    def createButtons(self):
        # Create other buttons here
        sep = ttk.Separator(self.root, orient="horizontal")
        sep.place(x=0, y=55, relwidth=1)

        self.debugPrint(
            "INFO",
            f"Manual Date: {self.getManDate.isChecked}\n"
            + f"Other Check: {self.otherCheck.isChecked}",
        )

        transferOutButton = Button(
            self.root,
            text="Transfer Out",
            command=lambda: threading.Thread(
                target=lambda: transferOut(
                    self.getManDate.isChecked,
                    self.otherCheck.isChecked,
                ),
                daemon=True,
            ).start(),
        )
        transferOutButton.place(y=60, x=0, **self.buttonPlaceAttrs)

        replaceOriginalButton = Button(
            self.root,
            text="Replace Original",
            command=lambda: threading.Thread(
                target=lambda: replaceOriginalFunc(),
                daemon=True,
            ).start(),
        )
        replaceOriginalButton.place(y=60, x=160, **self.buttonPlaceAttrs)

        # Eval Check Button
        self.checkValButton = Button(
            self.root, text="Run", command=lambda: self.runEvalText()
        )
        self.checkValButton.place(y=251, x=250, width=60)

        # Exit Button
        self.exit = Button(self.root, text="Exit", command=lambda: os._exit(0))
        self.exit.place(x=150, y=470, **self.buttonPlaceAttrs)
        self.exit.focus()

    def createRadios(self):
        # Create Radios
        self.getManDate = Check(self.root, "Select Date Manually")
        self.getManDate.getButtonReference().configure(anchor="w")
        self.getManDate.getButtonReference().place(x=0, y=0, **self.buttonPlaceAttrs)

        self.otherCheck = Check(self.root, "Disable Auto Get Claim")
        self.otherCheck.getButtonReference().configure(anchor="w")
        self.otherCheck.getButtonReference().place(x=0, y=25, **self.buttonPlaceAttrs)

        self.pauseAfterButton = Check(self.root, "Pause After")
        self.pauseAfterButton.getButtonReference().configure(anchor="w")
        self.pauseAfterButton.getButtonReference().place(
            x=160, y=0, **self.buttonPlaceAttrs
        )
        self.pauseAfterButton.getButtonReference().bind(
            "<Button>", lambda event: self.invertPauseAfter(), add="+"
        )

    def otherWindow(self):
        # Do the new window stuff here
        self.diagnosticWindow.geometry("60x40")
        self.diagnosticWindow.geometry(f"+{self.centerX - 120}+{self.centerY}")
        self.diagnosticWindow.protocol("WM_DELETE_WINDOW", lambda: None)
        self.diagnosticWindow.resizable(False, False)

    def createDebugLog(self):
        sep = ttk.Separator(self.root, orient="horizontal")
        sep.place(x=0, y=230, relwidth=1)

        label = Label(
            text="Debug Output",
        )
        label.place(x=5, y=282)

        self.debugLog = Text(
            self.root, height=10, width=39, yscrollcommand=1, state=NORMAL
        )
        self.debugLog.place(x=1, y=300)

    def setHandlers(self):
        self.root.bind("<Motion>", self.updateMousePos)
        self.root.bind("<Control-c>", self.handleExit)
        self.root.bind("<Configure>", self.handleDrag)
        self.evalText.bind("<Return>", lambda event: self.runEvalText())

    def updateMousePos(self, event):
        self.mousePosLabel.configure(text=f"X:{event.x} Y:{event.y}")

    def invertPauseAfter(self):
        global pauseAfter

        self.debugPrint("INFO", "Inverting Pause After")
        pauseAfter = not pauseAfter

    def handleExit(self, event):
        if event.widget is self.root:
            os.system("cls")
            print("Program Force Quit")
            os._exit(0)
        else:
            print(event.widget)

    def handleDrag(self, event):

        if event.widget is self.root:
            if self.drag_id == "":
                self.root.update()
            else:
                self.diagnosticWindow.geometry(
                    f"+{self.root.winfo_rootx() + 180}+{self.root.winfo_rooty() + 470}"
                )
                self.root.after_cancel(self.drag_id)

            self.drag_id = self.root.after(100, self.stop_drag)

    def stop_drag(self):
        self.drag_id = ""

    def debugPrint(self, label: str, out: str):
        label = f"[{label}]"
        timeStampUnix = f"[Timestamp: {int(time.time())}]"

        # Center text using spaces, there are 40 cols
        label = label.center(40, " ")
        timeStampUnix = timeStampUnix.center(40, " ")

        self.debugLog.insert(
            END,
            f"{label}{timeStampUnix}\n{''.join(out)}\n\n",
        )
        self.debugLog.see(END)


if __name__ == "__main__":

    def printOut(rootClass, label, msg, sleepTime, pauseAfter):
        time.sleep(sleepTime)
        rootClass.debugPrint(label, msg)

    root = Tk()
    newWindow = MyWindow(root)

    root.mainloop()
