import winsound
import os
import pyperclip
import threading
import csv
import timeit

from keyboard import *
from _99helperFunctions import *
from _99universalFunctions import *
from _99settingsFile import *
from Claim_Structure.Claim import Claim


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


def lookUpZip(searchZip: str) -> str:
    global zipLookup
    STATE = 0
    ZIPCODE = 1
    CARRIER = 2
    LOCALITY = 3
    RURALIND = 4
    LABCBLOCALITY = 5
    RURALIND2 = 6
    PLUS4FLAG = 7
    PARTBDRUGINDICATOR = 8
    YEAR = 9

    for zip in zipLookup:
        if zip[ZIPCODE] == searchZip:
            return zip[RURALIND2]


def loadCSV(filePath: str) -> list:
    try:
        with open(filePath, "r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            return list(reader)
    except:
        with open(filePath, "r", encoding="utf-16-LE") as file:
            reader = csv.reader(file)
            return list(reader)


def getPricing(searchRow: str, isTN: bool = False, isDetroit: bool = False) -> float:
    global pricing, pricingDetroit

    CODE = 0
    MOD = 1
    FEE = 2

    priceMap = pricingDetroit if isDetroit else pricing

    for row in priceMap:
        if row[CODE] == searchRow:
            if isTN:
                if row[MOD] == "TN":
                    return float(row[FEE][1:])
            else:
                return float(row[FEE][1:])


def calcMilagePrice(hasTN: bool):
    pricePerMile = 0

    milageLine = int(input("Milage Line: "))

    lineOneProc = claim.claimLines[0].procedureCode[:5]
    proc = claim.claimLines[milageLine - 1].procedureCode[:5]

    if claim.ambulancePickupCity != "DETROIT":
        if hasTN:
            pricePerMile = getPricing(proc, True, False)
            lineOnePrice = getPricing(lineOneProc, True, False)
        else:
            pricePerMile = getPricing(proc, isDetroit=False)
            lineOnePrice = getPricing(lineOneProc, isDetroit=False)

    elif claim.ambulancePickupCity == "DETROIT":
        if hasTN:
            pricePerMile = getPricing(proc, True, True)
            lineOnePrice = getPricing(lineOneProc, True, True)
        else:
            pricePerMile = getPricing(proc, isDetroit=True)
            lineOnePrice = getPricing(lineOneProc, isDetroit=True)

    mileage = float(input("How many miles billed: "))
    print(pricePerMile)

    inputMilage = round(pricePerMile * mileage, 2)

    print("Overriding price to: ${}".format(inputMilage))
    print("Line one override to ${}".format(lineOnePrice))
    # TODO: Actually override the price


def startClaim():
    global claim, pricing, pricingDetroit
    system("cls")

    # Get the XML file
    controller.updateClaimNum(pyperclip.paste(), True)
    controller.openX12()
    x12Data = controller.returnX12()
    x12ToXml.ediToXml(x12Data, "_07data/output.xml", True)

    # Generate the claim
    claim = MedicalClaim.MedicalClaim("_07data/output.xml", True)

    activateWindow("code")
    inOrOut = input("In network or out of network? (i/o): ")

    status = lookUpZip(claim.ambulancePickupZip)
    hasTN = False
    if "TN" in claim.claimLines[0].procedureCode:
        hasTN = True

    if inOrOut == "i":

        # in network urban do not need tn
        # in networkRural and superrual need tn

        if hasTN:
            if status == "R":
                print("Rural INN, with TN")
                print("Facets will price correctly")
                overRidePCA()
                return

        if hasTN:
            if status == "U" or status == None:
                print("Urban INN, with TN")
                print("Facets will price correctly")
                overRidePCA()
                return

        if hasTN:
            if status == "B":
                print("Super Rural INN, with TN")

                # TODO: Create this method
                print("Routing to PRC.CFG with C062")
                # routeToPRC()
                return

        print("Urban INN\nFacets will price correctly")
        overRidePCA()
        return

    else:
        if status == "R":
            print("Rural OON")
            # TODO: Create this method
            print("Calculating Mileage Price...")
            calcMilagePrice(hasTN)
            return

        if status == "U" or status == None:
            print("Urban OON")
            print("Facets will price correctly")
            overRidePCA()
            return

        if status == "B":
            print("Super Rural OON")

            # TODO: Create this method
            print("Routing to PRC.CFG with C062")
            # routeToPRC()
            return

        print("Urban OON\nFacets will price correctly")
        overRidePCA()
        return


def overRidePCA(facility=False):
    if PCA_OVERRIDE:
        return

    activateWindow("facets")

    if facility:
        pca_offset = 2
    else:
        pca_offset = 1

    pressKeyList(
        [
            "alt+o",
            "-3,assertTopWindow,Line Item Override",
            "alt+c",
            "-3,assertTopWindow,Claim Overrides",
            "tab,{},0".format(14 + pca_offset),
            "space",
            "tab",
            "-1,PCO",
            "enter,2",
            "-2,0.6",
            "f3",
        ]
    )

    waitForAdj()
    # pressKeyList(["f4"])
    # incrementClaim(getNewClaim=True)


import _Claim_Transcriber.x12ToXml as x12ToXml
import _Claim_Transcriber.VPRController as VPRController
import _Claim_Transcriber.MedicalClaim as MedicalClaim

try:
    controller = VPRController.VPRController()
except:
    controller = VPRController.VPRController(old=True)


# Load the pricing and location information
pricing = loadCSV("./_07data/pricing.csv")
pricingDetroit = loadCSV("./_07data/pricingDetroit.csv")
zipLookup = loadCSV("./_07data/zipLookup.csv")


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

# Used for making pcaOveride do nothing
PCA_OVERRIDE = True


Hotkey("alt+/", controller.invertTabState)
Hotkey("alt+1", openClaimLoc, args=openClaimArgs)
Hotkey("alt+2", startClaim)
Hotkey("alt+3", overRidePCA)

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
