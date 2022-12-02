import xml.etree.ElementTree as elt


def original_ref(root, checkInState=False):
    pairs = []
    seg = root.findall(".//*loop[@id='2300']/seg/ele")

    if checkInState:
        inState = root.find(".//seg[@id='N4']/ele[@id='N402']").text
        if inState != "MI":
            print("Out Of State, need to reprice?")
            input("Press Enter to continue...")

    for i in range(0, len(seg)):
        try:
            pairs.append([seg[i], seg[i + 1]])
        except:
            print("No More Pairs")

    for i in range(len(pairs)):
        if pairs[i][0].text == "F8":
            returnValue = pairs[i][1].text
            print("Claim Number:", returnValue)
            return returnValue

    print("Not Found")
    return False
