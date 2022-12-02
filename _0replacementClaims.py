import winsound
import os
import pyautogui
import pyperclip
import threading
import mouse
import pytesseract

from PIL import Image
from tesseract import tesseract_
from mouse import RIGHT
from keyboard import *
from _99helperFunctions import *
from _99universalFunctions import *
from _99settingsFile import *
from VPRController import VPRController
from Claim_Structure.Claim import Claim

from X12_Conversion.x12_to_xml import x12_to_xml as xmlConvert
from _0robotSkipBack import RobotClaim

# Init
activateWindow("facets")

# External Settings
settings = SettingsFile("_0settingsRep.txt")
amountOfClaims = settings.readValue("amountOfClaims", int)
incrementNext = settings.readValue("incrementNext", bool)
replaceOriginal = settings.changeValue("replaceOriginal", "True", True, bool)

# Internal Settings
try:
    controller = VPRController(old=True)
except:
    controller = VPRController(old=False)

currentDate = ""
old_data = ""
claimNumber = ""
currentSearch = "Subscriber ID"
lastCommand = None
isFacility = None
pauseAfter = False

# Functions
def parseFacilityLoc():
    global isFacility
    isFacilityLoc = None
    while True:
        isFacility = parseFacility()
        if isFacility == None:
            isFacility = isFacilityLoc
            continue

        isFacilityLoc = isFacility


def openClaimLoc(
    hotkey="f13",
    reprocess=False,
    click=ClickOptions.Default,
    f3=True,
    suffix=1,
    moveToWindow=True,
    highlight=True,
    checkReplacement=False,
):
    global pauseAfter
    openClaim(hotkey, reprocess, click, f3, suffix, moveToWindow, highlight)
    waitForAdj()

    if checkReplacement:
        if not isFacility:
            pressKeyList(["ctrl+up", "tab,1", "shift+tab,7", "space"])
        else:
            pressKeyList(["ctrl+up"])

        print("Shift to go back...")
        catch("shift", hard=True)

        pressKeyList(["tab", "down", "enter", "ctrl+down"])

    pauseAfter = False
    winsound.MessageBeep(winsound.MB_OK)


def switcher(toSwitch):
    global incrementNext, replaceOriginal

    if toSwitch == "incrementNext":
        incrementNext = settings.changeValue(
            "incrementNext", not incrementNext, True, bool
        )
        os.system("cls")
        print("incrementNext: {}".format(incrementNext))
    elif toSwitch == "replaceOriginal":
        replaceOriginal = settings.changeValue(
            "replaceOriginal", not replaceOriginal, True, bool
        )
        os.system("cls")
        print("replaceOriginal: {}".format(replaceOriginal))


def transferOut(other=False, noAuto=False):
    global currentDate, old_data, incrementNext
    activateWindow("facets")

    print(currentTransferType["name"])

    print(old_data)
    old_data = pyperclip.paste()

    # Get Date
    if not other:
        pressKeyList(["ctrl+down", "ctrl+up", "tab,5", "ctrl+home", "ctrl+shift+f10", "a"])

        pressKey("ctrl+c")
        currentDate = pyperclip.paste()

    else:
        print("Click on start date, older date")
        mouse.wait()
        pressKeyList(
            [
                "ctrl+shift+f10",
                "a",
                "ctrl+shift+f10",
                "c",
                "ctrl+shift+f10",
                "c",
            ]
        )
        startDate = pyperclip.paste()

        print("Click on end date, newer date")
        mouse.wait()
        pressKeyList(
            [
                "ctrl+shift+f10",
                "a",
                "ctrl+shift+f10",
                "c",
                "ctrl+shift+f10",
                "c",
            ]
        )
        endDate = pyperclip.paste()

    pyperclip.copy(old_data)

    if isFacility:
        down = currentTransferType["downAmountFacility"]
    else:
        down = currentTransferType["downAmountMedical"]

    amount = currentTransferType["inqTabAmount"]

    pressKeyList(["alt+t", "c", "enter", "down,{}".format(down), "enter"])

    # Open in Claims Inquiry
    assertTopWindow("Claims Inquiry")

    if other:
        pressKeyList(
            [
                "tab,{}".format(amount),
                "-1,{}".format(startDate),
                "tab",
                "-1,{}".format(endDate),
                "alt+r",
                "alt+y",
            ]
        )
    else:
        pressKeyList(
            [
                "tab,{}".format(amount),
                "-1,{}".format(currentDate),
                "tab",
                "-1,{}".format(currentDate),
                "tab,1,0.8",
                "alt+r",
                "alt+y",
            ]
        )

    # AUTO EDI SECTION
    #############################################################################################################################################################################

    controller.updateClaimNum(pyperclip.paste(), True)

    try:
        os.remove("./output.xml")
        os.remove("./input.edi")
    except:
        pass  # ignore errors

    sleep(1)
    for _ in range(5):
        try:
            with open("./input.edi", "w") as ediIn:
                ediIn.write(controller.returnX12())
                ediIn.close()
                system("cls")
        except:
            print("Failed X12 Get")

        sleep(1)

    try:
        myClaim = Claim("./input.edi", "./output.xml")
    except:
        for _ in range(10):
            try:
                myClaim = Claim("./input.edi", "./output.xml")
                sleep(1)
            except:
                pass

    system("cls")
    print("Claim Number:", myClaim.idNum)
    # print(myClaim.freq)
    # input()
    winsound.MessageBeep(winsound.MB_ICONQUESTION)
    if myClaim.idNum != False and len(myClaim.idNum) == 12:
        # mouse.move(x=1051, y=138) Test
        mouse.move(x=1200, y=138) # My Computer
        # mouse.move(x=1470, y=174)
        mouse.click(button=RIGHT)
        activateWindow("Find in: Claim ID")
        assertTopWindow("Find in: Claim ID")
        pressKeyList(
            [
                "-1,{}".format(myClaim.idNum),
                "enter",
            ]
        )

        sleep(0.7)
        assertTopWindow("Find in: Claim ID")

        if checkIfFound():
            pressKeyList(["esc"])
            if noAuto == False:
                if replaceClaim() == False:
                    return False
        else:
            mouse.move(30, -30)
            pressKeyList(["esc"])
            print("Claim not found, from tesseract")

            activateWindow("Select")
            if noAuto == False:
                print("Press enter to replace first claim, type 'n' to cancel")
            print("Claim Number:", myClaim.idNum)
            repFirst = catch("enter", exitKey="n")
            if repFirst == None:
                if noAuto == False:
                    if replaceClaim() == False:
                        return False
                    return True

            else:
                return False
    else:
        print("Edi ID Not Found")
        return False


def checkIfFound():
    my_tesseract = "C:\\Users\\wen165\\AppData\\Local\\Tesseract-OCR\\tesseract.exe"

    try:
        pytesseract.pytesseract.tesseract_cmd = (
            my_tesseract  # Put your own location here
        )
    except (Exception):
        print(Exception)
        print(
            "Need correct tesseract location\n Maybe here: /AppData/Local/Programs/Tesseract-OCR/tesseract"
        )
        print("Or here: /Programs (86)/Tesseract-OCR/tesseract?")

    x1, y1 = 500, 630
    x2, y2 = 642, 648

    pyautogui.screenshot(
        "./_07data/screenshot.png",
        region=(x1, y1, x2 - x1, y2 - y1),
    )

    lookFor = ["Search item was not found", "Search item was found"]
    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    text = pytesseract.image_to_string(Image.open("./_07data/screenshot.png")).strip()
    # os.remove("./_07data/screenshot.png")

    if text == lookFor[0]:
        return False
    elif text == lookFor[1]:
        return True
    else:
        raise Exception(f"Tesseract not working, found: {text}")


def putDate():
    pressKeyList(
        [
            "-1,{}".format(currentDate),
            "tab",
            "-1,{}".format(currentDate),
        ]
    )


def getDate():
    global old_data, currentDate

    old_data = pyperclip.paste()
    pressKeyList(["ctrl+shift+f10", "a", "ctrl+shift+f10", "c"])

    currentDate = pyperclip.paste()
    pyperclip.copy(old_data)


def replaceClaim(alreadyInClaim=False):
    activateWindow("facets")

    if replaceOriginal:
        returnValue = replaceOriginalFunc(alreadyInClaim)
        if returnValue == False:
            return False
    else:
        returnValue = replaceRequestedFunc()
        if returnValue == False:
            return False


def transferToClaimProcess():
    pressKeyList(
        [
            "alt+t",
            "{},{}".format("H" if isFacility else "M", "3" if isFacility else "4"),
            "enter",
        ]
    )


def replaceOriginalFunc(alreadyInClaim=False):
    global replaceOriginal, incrementNext, amountOfClaims
    activateWindow("facets")

    if "Claims Inquiry" in win32gui.GetWindowText(win32gui.GetForegroundWindow()):
        os.system("cls")
        print("Retrying Open Claim...")
        sleep(1)

        transferToClaimProcess()

    if "Claims Inquiry" in win32gui.GetWindowText(win32gui.GetForegroundWindow()):
        os.system("cls")
        print("Failed to open claim...")
        os._exit(-1)

    waitForAdj()

    pressKeyList(
        [
            "ctrl+down,1",
            "alt+e",
            "a",
            "-3,assertTopWindow,Note Attachment",
            "-1,See Replacment Claim: {}".format(pyperclip.paste()),
            "-2,0.6",
            "enter",
            "ctrl+up",
            "-2,0.6",
            "alt+o",
            "alt+c",
            "-3,assertTopWindow,Claim Overrides",
            "shift+tab,{}".format(10 if isFacility else 9),
            "space",
            "tab",
            "-1,OX6",
        ]
    )

    old_data = pyperclip.paste()
    pressKeyList(["ctrl+shift+f10", "a", "ctrl+shift+f10", "c"], 0.3)

    clipboardContents = pyperclip.paste()
    if clipboardContents == "OER":
        pressKeyList(["shift+tab", "space", "shift+tab", "space", "tab", "-1,OX6"])
        pressKeyList(["ctrl+shift+f10", "a", "ctrl+shift+f10", "c"], 0.3)

        if pyperclip.paste() != "OX6":
            winsound.Beep(2500, 500)
            print("OX6 Not Found\nCorrect and press CTRL")
            catch("ctrl", hard=True)

    elif clipboardContents != "OX6":
        winsound.Beep(2500, 500)
        print("OX6 Not Found\nCorrect and press CTRL")
        catch("ctrl", hard=True)

    pyperclip.copy(old_data)

    pressKeyList(["enter,2", "ctrl+o", "right", "space", "ctrl+c"])

    pressKeyList(
        [
            "esc",
            "alt+b,1,1.5",
            "-3,assertTopWindow,EOB Explanation",
            "-1,K33",
            "enter",
            "tab",
            "enter",
            "f3",
        ]
    )
    waitForAdj()

    os.system("cls")
    print("Last Command: Replaced Original Claim")
    print("Press Shift to continue")
    pressKey("f4", 1)
    replaceOriginal = settings.changeValue("replaceOriginal", "False", True, bool)
    incrementClaim()

    getCorrectWindow(isFacility)

    replaceRequestedFunc()


def replaceRequestedFunc():
    global replaceOriginal, replacedLastClaimAuto
    activateWindow("facets")

    pressKeyList(["ctrl+o", "enter", "ctrl+down", "f3"])
    waitForAdj()

    pressKeyList(
        [
            "ctrl+down",
            "alt+e",
            "a,1,0.6",
            "-3,assertTopWindow,Note Attachment",
            "-1,Replaced Claim: {}".format(pyperclip.paste()),
            "enter",
            "ctrl+up",
        ]
    )

    overRidePCA(isFacility, False)
    os.system("cls")
    print("Last Command: Replaced Requested Claim")
    print("Waiting for F4")

    print(f"Pause After: {pauseAfter}")
    key = catch("shift", exitKey="ctrl", time=1)
    if pauseAfter:
        key = "shift"

    # check if getting new claim
    if key != "shift":
        pressKey("f4", delay=0)

        if openClaimArgs["click"] == ClickOptions.Excel:
            incrementClaim(getNewClaim=True)
        else:
            incrementClaim()
    else:
        incrementClaim()
        replaceOriginal = settings.changeValue("replaceOriginal", "True", True, bool)
        return False

    replaceOriginal = settings.changeValue("replaceOriginal", "True", True, bool)


def overRidePCALoc(arg2, arg3):
    global isFacility

    overRidePCA(arg2, arg3)


def incrementClaim(operator="+", getNewClaim=None):
    global claimNumber, amountOfClaims, pauseAfter

    if operator == "+":
        amountOfClaims = settings.changeValue(
            "amountOfClaims", str(amountOfClaims + 1), True, int
        )
    elif operator == "-":
        amountOfClaims = settings.changeValue(
            "amountOfClaims", str(amountOfClaims - 1), True, int
        )
    elif operator == "=":
        amountOfClaims = settings.changeValue("amountOfClaims", "0", True, int)
    else:
        raise ArgumentError("Unknown passed")

    os.system("cls")

    if amountOfClaims != CLAIM_AMOUNT:
        print("Amount of Claims:", amountOfClaims)
        print("Amount Left:", CLAIM_AMOUNT - amountOfClaims)
        print(
            "Percentage Done:",
            str(round((amountOfClaims / CLAIM_AMOUNT) * 100, 2)) + "%",
        )
        time = round(amountOfClaims / CLAIMS_PER_HOUR, 2)
        hours = int(time)
        minutes = int((time * 60) % 60)
        print(f"Time Completed: {hours}:{minutes}")
        x = amountOfClaims % CLAIMS_PER_HOUR
        print(f"Amount left this hour: {CLAIMS_PER_HOUR - x}")
        if x == 0:
            print("Hour Amount Reached")
            print(f"{amountOfClaims} % {CLAIMS_PER_HOUR} = {x}")
            input("Enter to continue...")
    else:
        activateWindow("Select")
        print("{} Claims reached".format(CLAIM_AMOUNT))
        input("Press enter to continue")
        activateWindow("facets")

    if getNewClaim:
        openClaimLoc(
            openClaimArgs["hotkey"],
            openClaimArgs["reprocess"],
            openClaimArgs["click"],
            openClaimArgs["f3"],
            openClaimArgs["suffix"],
            openClaimArgs["moveToWindow"],
            openClaimArgs["highlight"],
            openClaimArgs["checkReplacement"],
        )
        pauseAfter = False


def oneOff():
    overRidePCA()


def voidClaim(claimNumberLoc=None):
    global isFacility

    if claimNumberLoc == None:
        claimNumberLoc = tesseract_()

    while len(claimNumberLoc) != 12:
        claimNumberLoc = input("Invalid Claim Number\nClaim Number: ")
        if claimNumberLoc == "-1":
            return

    activateWindow("facets")

    # Requested Claim

    pressKeyList(
        [
            "ctrl+tab",
            "ctrl+o",
            "-3,assertTopWindow,Open",
            f"-1,{claimNumberLoc}",
            "enter",
            "ctrl+down",
            "alt+o",
            "alt+c",
            "-3,assertTopWindow,Claim Overrides",
            "shift+tab,{}".format("10" if isFacility else "8"),
            "space",
            "tab",
            "-1,OX6",
        ]
    )

    old_data = pyperclip.paste()
    pressKeyList(["ctrl+shift+f10", "a", "ctrl+shift+f10", "c"], 0.3)

    clipboardContents = pyperclip.paste()
    if clipboardContents == "OER":
        pressKeyList(["shift+tab", "space", "shift+tab", "space", "tab", "-1,OX6"])
        pressKeyList(["ctrl+shift+f10", "a", "ctrl+shift+f10", "c"], 0.3)

        if pyperclip.paste() != "OX6":
            winsound.Beep(2500, 500)
            print("OX6 Not Found\nCorrect and press CTRL")
            catch("ctrl", hard=True)

    elif clipboardContents != "OX6":
        winsound.Beep(2500, 500)
        print("OX6 Not Found\nCorrect and press CTRL")
        catch("ctrl", hard=True)

    pyperclip.copy(old_data)

    pressKeyList(
        [
            "enter,2",
            "alt+b",
            "-3,assertTopWindow,EOB Explanation",
            "-1,K39",
            "enter",
            "tab",
            "enter",
            "ctrl+down",
            "alt",
            "e",
            "a",
            "-3,assertTopWindow,Note Attachment",
            f"-1, Void Per Claim: {pyperclip.paste()}",
            "enter",
            "ctrl+o",
            "alt+n",
            "ctrl+c",
            "esc",
            "f3",
            "-3,waitForAdj",
            "ctrl+up",
        ]
    )

    print("Press Shift to continue")
    catch("shift", hard=True)

    pressKey("f4")
    incrementClaim()

    # Original Claim
    pressKeyList(
        [
            "ctrl+shift+tab",
            "ctrl+o",
            "enter",
            "f3",
            "-3,waitForAdj",
            "ctrl+down,2",
            "alt",
            "e",
            "a",
            "-3,assertTopWindow,Note Attachment",
            f"-1, Voided Claim: {pyperclip.paste()}",
            "enter",
            "f3",
            "-3,waitForAdj",
            "alt",
            "f",
            "s",
            "c",
            "-1,{}".format("C423" if isFacility else "C424"),
        ]
    )


def ediCopy():
    waitForRelease("ctrl+c")

    if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == "Viewer Printer":
        pressKeyList(["shift+f10", "c"])


def transferToEdi():
    if controller.updateClaimNum(pyperclip.paste(), True):
        controller.openForm()
        return True
    else:
        print("Open Claim Failed")


def console():
    global lastCommand, pauseAfter
    args = ()
    command = ""
    activateWindow("Select")
    pressKey("alt+v, t, backspace, backspace")

    command = input("Command: ")
    if ";" in command:
        args = command.split(";")
        args = args[1:]
        args = "".join(args).split(",")

    command = command.split(";")[0] if ";" in command else command

    funcDict = {
        "void": voidClaim,
        "oneOff": oneOff,
        "replaceReq": replaceRequestedFunc,
        "replaceOrig": replaceOriginalFunc,
        "switch": switcher,
        "l": listAmount,
        "list": listAmount,
    }
    if command.strip() in ["q", "quit", " ", ""]:
        return
    elif command.strip() in ["info", "i"]:
        try:
            print(funcDict[args[0]].__Select__.co_varnames)
            return
        except:
            print("Requested function does not exist")
    elif command.strip() == ".":
        command = lastCommand
    elif command.strip() in ["stopAfter", "sa", "pauseAfter", "pa"]:
        pauseAfter = True
        print(f"Pause After claim complete: {pauseAfter}")
        return

    try:
        funcDict[command.strip()](*args)
        lastCommand = command.strip()
    except:
        print("Command Not Recognized")


def listAmount():
    print(f"Amount of Claims: {amountOfClaims}")


def switchMode():
    global currentTransferType

    i = 0
    types = ["subscriberID", "memberID", "serviceProvider"]
    while True:
        system("cls")
        print(
            f"Transfer Type: {types[i]} : {transferType[types[i]]}\nPress Shift to cycle thru\nPress Ctrl to exit"
        )
        key = catch("shift", True, exitKey="ctrl")
        if key == "shift":
            i = i + 1 if i != 2 else 0
        else:
            break

    currentTransferType = transferType[types[i]]
    print(f"Selected Type: {types[i]} : {transferType[types[i]]}")


def switchMode2():
    global isFacility
    isFacility = not isFacility
    print("{}".format("Hospital Claim" if isFacility == True else "Medical Claim"))


def inClaimReplacer():
    global isFacility
    replaceClaim(True)


def autoGo():
    while True:
        if transferOut() != False:
            sleep(3)
        else:
            print("Error, Auto Stopped")
            return


def robotSkipAuto():
    while True:
        returnValue = robotSkip()

        if returnValue == 1:
            print("Transfering out...")
            transferOut()
        elif returnValue == 2:
            print("Voiding Claim...")
            voidClaim()
        elif returnValue == -1:
            openClaimLoc(openClaimArgs)
        else:
            print("There is a missing return value somewhere\nAuto Stopped")
            return


def robotSkip() -> int | None:
    currentClaimNum = pyperclip.paste()
    controller.updateClaimNum(currentClaimNum, True)
    with open("./RobotSkip/firstClaim.edi", "w") as file:
        file.write(controller.returnX12())

    xmlConvert("./RobotSkip/firstClaim.edi", "./RobotSkip/firstClaim.xml")
    system("cls")
    firstClaim = RobotClaim("./RobotSkip/firstClaim.xml", isFacility)
    if firstClaim.claimElements["freq"] == "7":
        print("Replace It")
        return 1
    elif firstClaim.claimElements["freq"] == "8":
        print("Void It")
        return 2

    pressKeyList(["f3"])
    waitForAdj()

    newClaimNum = tesseract_(loopUntil=True)
    controller.updateClaimNum(newClaimNum)
    with open("./RobotSkip/secondClaim.edi", "w") as file:
        file.write(controller.returnX12())
    xmlConvert("./RobotSkip/secondClaim.edi", "./RobotSkip/secondClaim.xml")
    secondClaim = RobotClaim("./RobotSkip/secondClaim.xml", isFacility)

    checks = {
        "refName": False,
        "refNPI": False,
        "rendName": False,
        "rendNPI": False,
        "servAddress": False,
        "servNPI": False,
    }

    system("cls")
    if (
        firstClaim.claimElements["refProvider"]["name"]
        == secondClaim.claimElements["refProvider"]["name"]
    ):
        checks["refName"] = True
        print("Ref Name True")

    if (
        firstClaim.claimElements["refProvider"]["npi"]
        == secondClaim.claimElements["refProvider"]["npi"]
    ):
        checks["refNPI"] = True

    if (
        firstClaim.claimElements["rendProvider"]["name"]
        == secondClaim.claimElements["rendProvider"]["name"]
    ):
        checks["rendName"] = True
        print("Rend Name is True")

    if (
        firstClaim.claimElements["rendProvider"]["npi"]
        == secondClaim.claimElements["rendProvider"]["npi"]
    ):
        checks["rendNPI"] = True

    if (
        firstClaim.claimElements["serviceLoc"]["address"]
        == secondClaim.claimElements["serviceLoc"]["address"]
    ):
        checks["servAddress"] = True
        print("Serv Address is True")

    if (
        firstClaim.claimElements["serviceLoc"]["npi"]
        == secondClaim.claimElements["serviceLoc"]["npi"]
    ):
        checks["servNPI"] = True

    count = len([item for item in checks.values() if item == True])

    print(f"Check Count: {count}")
    print(repr(checks))
    if count == 6:
        activateWindow("Select")
        line = input("Line Number (int/'claim'): ")

        try:
            line = line.split(",")
            line = [int(item) for item in line]
        except:
            line = [line]

        activateWindow("facets")
        assertTopWindow("Facets", exact=False)

        if line[0] in ["claim", "c"]:
            pressKeyList(
                [
                    "alt+a",
                    "o",
                    "c",
                    "-3,assertTopWindow,Claim Overrides",
                    "shift+tab,{}".format(11 if isFacility else 10),
                    "space",
                    "tab",
                    "-1,OZ5",
                    "enter,2",
                ]
            )
        else:
            if line == "":
                line = 1

            for i in line:
                i = i - 1
                pressKeyList(
                    [
                        "ctrl+home",
                        "alt+o",
                        "-3,assertTopWindow,Line Item Override",
                        f"alt+n,{i}",
                    ]
                )

                if i == 0:
                    pressKeyList(["tab"])

                pressKeyList(["0", "tab", "-1,O11", "enter"])

    pressKeyList(["f3"])

    waitForAdj()
    return -1


clickTypesArr = [ClickOptions.BiLaunch, ClickOptions.Excel, ClickOptions.Default]
openClaimArgs = {
    "hotkey": "f13",
    "reprocess": False,
    "click": clickTypesArr[1],
    "f3": True,
    "suffix": 1,
    "moveToWindow": True,
    "highlight": False,
    "checkReplacement": False,
}

transferType = {
    "subscriberID": {
        "name": "Subscriber",
        "lineTabAmount": 5,
        "downAmountFacility": 0,
        "downAmountMedical": 0,
        "inqTabAmount": 5,
    },
    "memberID": {
        "name": "Member",
        "lineTabAmount": 5,
        "downAmountFacility": 1,
        "downAmountMedical": 0,
        "inqTabAmount": 5,
    },
    "serviceProvider": {
        "name": "Service Prov",
        "lineTabAmount": 5,
        "downAmountFacility": 2,
        "downAmountMedical": 1,
        "inqTabAmount": 6,
    },
}

currentTransferType = transferType["memberID"]
CLAIM_AMOUNT = settings.readMath("totalClaims")
CLAIMS_PER_HOUR = settings.readValue("claimsPerHour", int)

Hotkey("alt+1", openClaimLoc, openClaimArgs)

Hotkey("alt+2", transferOut)
Hotkey("ctrl+alt+2", transferOut, (True,))
Hotkey(
    "shift+alt+`",
    transferOut,
    ({"noAuto": True, "other": True}),
)
Hotkey(
    "shift+alt+2",
    transferOut,
    ({"noAuto": True}),
)
Hotkey("ctrl+shift+/", autoGo)

Hotkey("alt+3", replaceClaim)
Hotkey("ctrl+alt+3", inClaimReplacer)

Hotkey("alt+4", robotSkip)
Hotkey("ctrl+4", robotSkipAuto)

Hotkey("alt+5", voidClaim)

Hotkey("alt+7", oneOff)
Hotkey("alt+8", checkIfFound)

Hotkey("ctrl+shift+:", console)
Hotkey("]", switcher, ("replaceOriginal",))
Hotkey("alt+/", controller.invertTabState)

add_hotkey("f4", incrementClaim)
add_hotkey("=", incrementClaim)
add_hotkey("-", incrementClaim, ("-",))
add_hotkey("shift+ctrl+=", incrementClaim, ("=",))
add_hotkey("ctrl+c", ediCopy)

threading.Thread(target=parseFacilityLoc, name="FacilityParse", daemon=True).start()

os.system("cls")
    
print("Loaded")
print(currentSearch)
print("Hospital" if isFacility else "Medical" + " Claim")
controller.logCurrentState()

if __name__ == "__main__":
    wait("f13")

# 324251735200
