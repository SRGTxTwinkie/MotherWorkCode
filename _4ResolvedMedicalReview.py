from _99universalFunctions import *
from _99helperFunctions import *
from _99settingsFile import *
import keyboard as kb
import re
from re import Match
import pyperclip as clip
import os
import threading
import mouse

settings = SettingsFile("_0settingsRep.txt")
amountOfClaims = settings.readValue("amountOfClaims", int)
isFacility = None


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
    openClaim(hotkey, reprocess, click, f3, suffix, moveToWindow, highlight)
    waitForAdj()

    pressKey("ctrl+down", delay=0)


def incrementClaim(operator="+"):
    global amountOfClaims

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
            f"Percentage Done:",
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
        activateWindow("code")
        print("{} Claims reached".format(CLAIM_AMOUNT))
        input("Press enter to continue")
        activateWindow("facets")


openClaimArgs = {
    "hotkey": "f13",
    "reprocess": False,
    "click": ClickOptions.Excel,
    "f3": True,
    "suffix": 1,
    "moveToWindow": True,
    "highlight": False,
}


def parseFacilityLoc():
    global isFacility
    isFacilityLoc = None
    while True:
        isFacility = parseFacility()
        if isFacility == None:
            isFacility = isFacilityLoc
            continue

        isFacilityLoc = isFacility


def overRidePCALoc(facility):
    pressKeyList(["ctrl+up"])
    overRidePCA(facility)


################################################################
############### START OF NOT BOILERPLATE #######################
################################################################
def setClipboard():
    mouse.move(580, 471)
    mouse.click(button="right")
    sleep(0.4)
    pressKeyList(
        [
            "a",
        ]
    )
    sleep(0.3)
    pressKeyList(
        [
            "ctrl+c,2",
        ]
    )

    val = pyperclip.paste()
    return val


def parseCodeReview(doSetClipboard: bool = True):
    global denyType
    LOOP_LIMIT = 20

    initalClip = pyperclip.paste()
    clipContents = None

    if doSetClipboard:
        newClip = setClipboard()
        pyperclip.copy("")

        loopAmount = 0
        while newClip == "" and loopAmount < LOOP_LIMIT:
            newClip = setClipboard()
            loopAmount += 1

        clipContents = newClip

        if loopAmount == LOOP_LIMIT or newClip == "":
            print("Loop limit reached")
            print("Clipboard not set, do it now")
            waitForRelease("ctrl+c")
            return
    else:
        clipContents = initalClip

    pyperclip.copy(initalClip)
    isDeny = False
    if re.search("deny", clipContents) != None:
        denyType = 0
        isDeny = True
    elif re.search("denial", clipContents) != None:
        denyType = 1
        isDeny = True

    if isDeny:
        print("Is Deny")
        denyProc(clipContents)
        return

    print("Not Denial")
    regProc(clipContents)
    return


def regProc(clipContents: str):
    infoType = 0

    info = re.search(
        r"line\s(\d+)[\w\s\@]+\$([\d\.]+)[\w\s]+([A-Z\d]{4})", clipContents
    )
    if info == None:
        infoType = 1
        info = re.search(r"allow[\w\s]+\$([\d/.]+)", clipContents)

    if info == None:
        print("Fallback to custom...")
        custom()
        return

    if infoType == 0:
        getLine = re.search(r"line\s(\d+)", clipContents).group(1)
        getPrice = tryReg(info, 2, "Price")
        getTOS = tryReg(info, 3, "TOS", True)
    elif infoType == 1:
        getPrice = tryReg(info, 1, "Price")
        getLine = re.search(r"line\s(\d+)", clipContents).group(1)
        getTOS = tryReg(info, 3, "TOS", True)

    ob = [{"line": getLine, "code": "OF5", "price": getPrice, "tos": getTOS}]
    print(ob)

    lineProc(ob, False)


def tryReg(
    regOb: Match[str],
    groupNumb: int,
    label: str,
    skipIfNone: bool = False,
    alt: str = None,
):
    try:
        return regOb.group(groupNumb)
    except:
        if skipIfNone:
            if alt != None:
                return alt
            return None

        print(label + " Not Found")
        returnValue = input(label + ": ")
        return returnValue


def denyProc(clipContents: str):
    infoType = 0

    if denyType == 0:
        info = re.search(r"line?\(s\)\s(\d+)\s([A-Z\d]+)", clipContents)
        if not info:
            infoType = 1
            info = re.search(r"line\s(\d)+[\w\s\,]+([A-Z\d]{4})", clipContents)
    else:
        infoType = 2
        info = re.search(r"denial[\w\s]+([A-Z\d]{3,4})[\w\s]+(\d)+", clipContents)

    if info == None:
        print("Fallback to custom...")
        custom()
        return

    if infoType == 0:
        getLine = tryReg(info, 1, "Line Number")
        getCode = tryReg(info, 2, "Code", True, "OF5")
        getTos = tryReg(info, 3, "TOS", True)
    elif infoType == 1:
        getLine = tryReg(info, 1, "Line Number")
        getTos = tryReg(info, 2, "TOS")
        getCode = "OF5"
    elif infoType == 2:
        getCode = tryReg(info, 1, "Code")
        getLine = tryReg(info, 2, "Line Number")
        getTos = None

    else:
        raise Exception("Unknown info type")

    ob = [{"line": getLine, "code": getCode, "tos": getTos}]
    print(ob)

    lineProc(ob, True)


def custom():
    getLine = enterOrDefault("Line", "1")
    getPrice = enterOrDefault("Price", "0.00")
    getCode = enterOrDefault("Code", "OF5")
    getTos = enterOrDefault("TOS", None)

    ob = [{"line": getLine, "price": getPrice, "code": getCode, "tos": getTos}]

    lineProc(ob, False)


def enterOrDefault(label, default):
    returnValue = input(label + ": ")
    if returnValue == "":
        return default

    return returnValue


def lineProc(obList: list[dict[str, str]], isDeny: bool):
    activateWindow("Facets")
    assertTopWindow("Facets", exact=False)

    pressKeyList(
        [
            "ctrl+up",
            "alt+o",
            "-3,assertTopWindow,Line Item Override",
        ]
    )

    for i in obList:
        if i["line"] != "1":
            pressKeyList(
                [
                    "alt+n,{}".format(int(i["line"]) - 1),
                ]
            )
        else:
            pressKeyList(["tab"])

        if isDeny:
            pressKeyList(["-1,0", "tab", "-1,{}".format(i["code"])])

        else:
            pressKeyList(
                [
                    "-1,{}".format(i["price"]),
                    "tab",
                    "-1,{}".format(i["code"]),
                ]
            )

        if i["tos"] != None:
            pressKeyList(["tab,18", "-1,{}".format(i["tos"]), "tab", "-1,O87"])

    print("Done...")


CLAIM_AMOUNT = settings.readMath("totalClaims")
CLAIMS_PER_HOUR = settings.readValue("claimsPerHour", int)
denyType = -1

threading.Thread(target=parseFacilityLoc, name="FacilityParse", daemon=True).start()

Hotkey("alt+1", openClaimLoc, openClaimArgs)
Hotkey("alt+2", setClipboard)
Hotkey("alt+3", parseCodeReview)
Hotkey("alt+4", parseCodeReview, (False,))
Hotkey("alt+5", custom)


kb.add_hotkey("f4", incrementClaim)
kb.add_hotkey("=", incrementClaim)
kb.add_hotkey("-", incrementClaim, ("-",))
kb.add_hotkey("shift+ctrl+=", incrementClaim, ("=",))
os.system("cls")
print("Loaded...")
kb.wait("f13")
