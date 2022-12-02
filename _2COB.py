from os import system
from time import sleep
from _99universalFunctions import *
from _99helperFunctions import *

import pyautogui
import keyboard as kb

settings = SettingsFile("_0settingsRep.txt")
CLAIM_AMOUNT = settings.readMath("totalClaims")
amountOfClaims = settings.readValue("amountOfClaims", int)


def incrementClaim(operator="+", getNewClaim=None):
    global amountOfClaims, pauseAfter

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
        activateWindow("code")
        print("{} Claims reached".format(CLAIM_AMOUNT))
        input("Press enter to continue")
        activateWindow("facets")

    if getNewClaim:
        pauseAfter = False


def changeAllowedMode(doZeros=False, manDate=False):
    global tClaim
    amount = 1
    amounts = []

    activateWindow("code")
    pressKey("alt+v, t, backspace, backspace", delay=0)
    # lines = input("Line Amount: ")

    # Parse Claims for line amount
    if not manDate:
        parseClaim()

    if tClaim == None:
        lines = int(input("Line Amount: "))
    else:
        lines = len(tClaim.claimLines)

    activateWindow("facets")
    sleep(0.5)

    for i in range(0, lines):

        pressKey("alt+c", delay=0)
        assertTopWindow("Coordination Of Benefits")
        kb.write("C")

        pyautogui.moveTo(556, 311)
        pyautogui.mouseDown(button="left")
        pyautogui.moveTo(778, 338, 0.3)
        pyautogui.mouseUp(button="left")

        for _ in range(10):
            pressKeyList(
                [
                    "tab",
                    "f2",
                ],
                0,
                0,
            )

        activateWindow("code")
        if not doZeros:
            allowed = input("Allowed: ")
            try:
                amounts.append(float(allowed) if allowed != "" else 0.0)
            except:
                allowed = input(f"Conversion failure on {allowed}: ")
                amounts.append(float(allowed) if allowed != "" else 0.0)
        else:
            allowed = 0
            amounts.append(0)

        activateWindow("facets")

        pressKeyList(
            [
                "f2",
                f"-1,{allowed}",
                "shift+tab",
                "f2",
                f"-1,{allowed}",
                "enter,{}".format("0" if i + 1 == lines else "1"),
            ]
        )

        sleep(0.4)

        if i == 0:
            pressKeyList(["tab,4"])

        pressKeyList([f"down,{i + 1}"])

        amount += 1

    for i in range(10):
        if i > 7:
            pressKey("f2", delay=0)
        pressKey("shift+tab", delay=0)

    total = 0
    for item in amounts:
        total += item

    system("cls")
    print("Total:", round(total, 3))
    pressKey("f2", delay=0)
    kb.write(str(round(total, 3)))
    kb.send("tab")
    kb.send("f2")
    kb.write(str(round(total, 3)))


def singleLiner():

    activateWindow("code")
    pressKey("alt+v, t, backspace, backspace", delay=0)
    amount = input("Amount: ")
    activateWindow("facets")
    activateWindow("facets")

    pressKeyList(
        [
            "alt+c,2",
            "-3,assertTopWindow,Coordination Of Benefits",
            "-1,C",
            "tab",
            "f2",
            "-1,{}".format(amount),
            "tab",
            "f2",
            "-1,{}".format(amount),
            "tab",
            "enter",
        ]
    )


def changeFacility():
    global isFacility

    isFacility = not isFacility
    print(f"Facility Value: {isFacility}")


def parseClaim():
    global tClaim
    controller.updateClaimNum(pyperclip.paste(), True)
    controller.openX12()

    x12ToXml.ediToXml(controller.returnX12(), readFromString=True)
    try:
        tClaim = HospitalClaim.HospitalClaim("output.xml")
        print("Claim was Hospital")
    except:
        tClaim = MedicalClaim.MedicalClaim("output.xml")
        print("Claim was Medical")

    print("Done...")


clickTypesArr = [ClickOptions.BiLaunch, ClickOptions.Excel, ClickOptions.Default]
openClaimArgs = {
    "hotkey": "f13",
    "reprocess": False,
    "click": clickTypesArr[settings.readValue("click", int)],
    "f3": True,
    "suffix": 1,
    "moveToWindow": True,
    "highlight": False,
}

import _Claim_Transcriber.x12ToXml as x12ToXml
import _Claim_Transcriber.VPRController as VPRController
import _Claim_Transcriber.MedicalClaim as MedicalClaim
import _Claim_Transcriber.HospitalClaim as HospitalClaim

try:
    controller = VPRController.VPRController()
except:
    controller = VPRController.VPRController(old=True)

isFacility = False
CLAIMS_PER_HOUR = settings.readValue("claimsPerHour", int)
tClaim = None

Hotkey("alt+1", openClaim, openClaimArgs)
Hotkey("alt+2", singleLiner)

Hotkey("alt+3", changeAllowedMode)
Hotkey("ctrl+3", changeAllowedMode, (True,))

Hotkey("alt+4", changeAllowedMode, (False, True))

Hotkey("]", changeFacility)
kb.add_hotkey("f4", incrementClaim)
kb.add_hotkey("=", incrementClaim)
kb.add_hotkey("-", incrementClaim, ("-",))
kb.add_hotkey("shift+=", incrementClaim, ("=",))
system("cls")
print("Loaded")
kb.wait("f13")
