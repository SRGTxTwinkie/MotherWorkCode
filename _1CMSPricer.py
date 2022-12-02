import winsound
import os
import pyperclip
import threading
import mouse

from keyboard import *
from _99helperFunctions import *
from _99universalFunctions import *
from _99settingsFile import *


# External Settings
settings = SettingsFile("_0settingsRep.txt")
amountOfClaims = settings.readValue("amountOfClaims", int)
incrementNext = settings.readValue("incrementNext", bool)
replaceOriginal = settings.changeValue("replaceOriginal", "True", True, bool)
isFacility = None

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


################################
### Start of not boilerplate ###
################################
class LineItem:
    def __init__(self, line, _from, _to, rev, tos, proc, unit, charges, dx):
        self.line = line
        self._from = _from
        self._to = _to
        self.rev = rev
        self.tos = tos
        self.proc = proc
        self.unit = unit
        self.charges = charges
        self.dx = dx


def parseClaim():
    global tClaim
    controller.updateClaimNum(pyperclip.paste(), True)
    controller.openX12()

    x12ToXml.ediToXml(controller.returnX12(), readFromString=True)
    tClaim = HospitalClaim.HospitalClaim("output.xml")
    print("Done...")


def summaryScreen():
    global tClaim
    manualCodes = []

    print("Click on the first DX...")
    mouse.wait(target_types=mouse._mouse_event.UP)
    for enum, i in enumerate(tClaim.diagnosisCodes[1:]):
        if i[0] == "Z":
            manualCodes.append(i)
            continue
        pressKeyList(["-1,{}".format(i), "down"])
        if enum > 10:
            system("cls")
            print("Waiting for click...")
            mouse.wait()
        sleep(0.4)

    if len(manualCodes) > 0:
        print("Enter the manual codes...")
        for i in manualCodes:
            pressKeyList(["-1,{}".format(i), "down"])
            print("Waiting for click...")
            mouse.wait()


def lineItemsSummary():
    global tClaim, _from
    procCodes = tClaim.claimLines
    if _from == None:
        _from = input("Enter the starting date: ")

    print("Click on the first rev code ON INTERNET...")
    mouse.wait(target_types=mouse._mouse_event.UP)
    for i in procCodes:
        if i.procedureCode == "" or i.procedureCode == None:
            continue

        pressKeyList(
            [
                "-1,{}".format(i.revCode),
                "tab",
                "-1,{}".format(i.procedureCode),
                "tab,3",
                "-1,{}".format(i.unitQuantity),
                "tab",
                "-1,{}".format(_from[0:2]),
                "-2,0.4",
                "-1,{}".format(_from[2:4]),
                "-2,0.4",
                "-1,{}".format(_from[4:]),
                "tab,2",
                "-1,{}".format(i.dollarAmount),
                "tab,3",
            ]
        )
        # print("Waiting for click...")
        # mouse.wait()


def enterBasicInfoCaller():
    global tClaim

    if tClaim == None:
        parseClaim()

    typesArr = ["Home Health", "Rehab", "Psych"]
    types = [
        #   [patType, payID, billType, useNPI]
        ["07", "09", "0329", True],
        ["05", "09", None, True],
        ["03", "09", None, False],
    ]

    for iter, item in enumerate(typesArr):
        print(f"{iter + 1}. {item}")
    selected = int(input("Enter the type of claim: ")) - 1

    enterBasicInfo(*types[selected])


def enterBasicInfo(patType: str, payID: str, billType: str, useNPI: bool = True):
    global tClaim, _from

    if not useNPI:
        # It will still put it in there but it will be blank
        tClaim.billingProviderNPI = ""

    if len(tClaim.valCodes) == 0:
        print("Send missing info letter, no val codes")
        return

    useLast = input("Use Last: ")
    if useLast == "" or useLast == "n":
        print("Alt+t, Facility, Registration")
        facID = input("Facility ID: ")

        _from = input("Start Date: ")
        _to = input("End Date: ")
        gender = input("Gender: ")
        age = input("Age: ")
        dStat = input("Discharge Status: ")
        if billType == None:
            billType = input("Bill Type: ")

        with open("last.txt", "w") as f:
            f.write(f"{facID}\n")
            f.write(f"{_from}\n")
            f.write(f"{_to}\n")
            f.write(f"{gender}\n")
            f.write(f"{age}\n")
            f.write(f"{dStat}\n")
            f.write(f"{billType}\n")
    else:
        with open("last.txt", "r") as f:
            items = f.readlines()

        facID = items[0].strip()
        _from = items[1].strip()
        _to = items[2].strip()
        gender = items[3].strip()
        age = items[4].strip()
        dStat = items[5].strip()
        billType = items[6].strip()

    print('Click on "Patient Type" and let it go...')
    mouse.wait(target_types=mouse._mouse_event.UP)

    pressKeyList(
        [
            "-1,{}".format(patType),
            "tab,2",
            "-1,{}".format(tClaim.billingProviderNPI),
            "tab,3",
            "-1,{}".format(facID),
            "tab",
            "-1,{}".format(payID),
            "tab",
            "-1,{}".format(tClaim.claimNumber),
            "tab,2",
            "-2,2",
            "-1,{}".format(_from[:2]),
            "-2,1",
            "-1,{}".format(_from[2:4]),
            "-2,1",
            "-1,{}".format(_from[4:]),
            "tab",
            "-1,{}".format(_to[:2]),
            "-2,1",
            "-1,{}".format(_to[2:4]),
            "-2,1",
            "-1,{}".format(_to[4:]),
            "tab,7",
            "-1,{}".format(gender),
            "tab",
            "-1,{}".format(age),
            "tab,3",
            "-1,{}".format(dStat),
            "tab",
            "ctrl+a",
            "backspace",
            "-1,{}".format(billType),
            "tab",
            "-1,{}".format(tClaim.totalClaimAmount),
        ]
    )
    input("Open Value and Occurrence Code tabs and press enter")
    enterValCodes(tClaim.valCodes)
    enterOccCodes(tClaim.occCodes, _from)
    enterOccSpanCodes(tClaim.occSpanCodes)
    enterCondCodes(tClaim.condCodes)


def enterOccSpanCodes(codes: list):
    global tClaim
    print("Click on the first Occurrence Span Code...")
    mouse.wait(target_types=mouse._mouse_event.UP)
    for i in codes:
        pressKeyList(
            [
                "-1,{}".format(i["code"]),
                "tab",
                "-1,{}".format(i["from"]),
                "tab",
                "-1,{}".format(i["to"]),
                "tab",
            ]
        )


def enterCondCodes(codes: list):
    global tClaim
    print("Click on the first Condition Code...")
    mouse.wait(target_types=mouse._mouse_event.UP)
    for i in codes:
        pressKeyList(
            [
                "-1,{}".format(i),
                "tab",
            ]
        )


def enterOccCodes(codes, date):
    print("Click on Occurrence Code 1 and let it go...")
    mouse.wait(target_types=mouse._mouse_event.UP)
    for i in codes:
        pressKeyList(["-1,{}".format(i), "tab", "-1,{}".format(date), "tab"])


def enterValCodes(valCodes):
    print("Click on the first value code...")
    mouse.wait(target_types=mouse._mouse_event.UP)

    for valCode in valCodes:
        pressKeyList(
            [
                "-1,{}".format(valCode["value"]),
                "tab",
                "-1,{}".format(valCode["amount"]),
                "tab",
            ]
        )


def enterPricing():
    global tClaim
    if tClaim == None:
        parseClaim()
    claimLines = tClaim.claimLines
    pricingAmount = float(input("Enter CMS pricing amount: "))

    activateWindow("facets")
    pressKeyList(
        [
            "f3",
            "alt+b",
        ]
    )
    assertTopWindow("EOB Explanation")
    pressKeyList(["esc", "alt+o"])
    activateWindow("Line Item Override")
    pressKeyList(["tab"])

    for i in claimLines:
        print(f"Dollars left to distribute: {pricingAmount}")
        if float(i.dollarAmount) <= 0.01:
            pressKeyList(["alt+n"])
            continue

        if pricingAmount - float(i.dollarAmount) <= 0:
            pressKeyList(["-1,{}".format(pricingAmount), "tab", "-1,M05", "alt+n"])
            break
        else:
            pricingAmount -= float(i.dollarAmount)
            pressKeyList(["-1,{}".format(i.dollarAmount), "tab", "-1,M05", "alt+n"])

    print("Claim Priced...")


def noteAndPCA():

    print("Waiting for clipboard to change...")
    pyperclip.waitForNewPaste()
    activateWindow("facets")
    sleep(1)
    activateWindow("facets")

    pressKeyList(
        [
            "alt+o",
            "alt+c",
        ]
    )
    assertTopWindow("Claim Overrides")
    pressKeyList(
        [
            "shift+tab,18",
            "space",
            "tab",
            "-1,PCO",
            "enter,2",
            "ctrl+down",
            "alt+e",
            "a",
        ]
    )
    assertTopWindow("Note Attachment")
    pressKeyList(
        [
            "-1,Pricing:",
            "tab",
            "ctrl+v",
            "tab",
            "space",
            "ctrl+up",
            "f3",
            "alt+b",
        ]
    )
    assertTopWindow("EOB Explanation", press="alt+b")
    pressKeyList(
        [
            "esc",
        ]
    )

    print("Done...")


import _Claim_Transcriber.x12ToXml as x12ToXml
import _Claim_Transcriber.VPRController as VPRController
import _Claim_Transcriber.MedicalClaim as MedicalClaim
import _Claim_Transcriber.HospitalClaim as HospitalClaim

try:
    controller = VPRController.VPRController()
except:
    controller = VPRController.VPRController(old=True)

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

CLAIM_AMOUNT = settings.readMath("totalClaims")
CLAIMS_PER_HOUR = settings.readValue("claimsPerHour", int)
tClaim = None
_from = None


Hotkey("alt+/", controller.invertTabState)
Hotkey("alt+1", openClaimLoc, args=openClaimArgs)
Hotkey("alt+2", parseClaim)
Hotkey("alt+3", enterBasicInfoCaller)
Hotkey("alt+4", summaryScreen)
Hotkey("alt+5", lineItemsSummary)

Hotkey("alt+6", enterPricing)
Hotkey("alt+7", noteAndPCA)

add_hotkey("f4", incrementClaim)
add_hotkey("=", incrementClaim)
add_hotkey("-", incrementClaim, ("-",))
add_hotkey("shift+ctrl+=", incrementClaim, ("=",))

threading.Thread(target=parseFacilityLoc, name="FacilityParse", daemon=True).start()

os.system("cls")

print("Loaded")
print("Hospital" if isFacility else "Medical" + " Claim")
controller.logCurrentState()

wait("f13")
