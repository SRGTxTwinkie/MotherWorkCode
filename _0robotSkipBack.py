import xml.etree.ElementTree as elt
from lxml import etree

class RobotClaim:
    '''
    data structure
    {
        freq: str,
        originalRef: str|none,
        refProvider: obj{name: str, npi: string},
        rendProvider: obj{name: str, npi: string},
        seviceLocation: obj{address: str, npi: string}
    }
    '''
    def __init__(self, xmlFilePath:str, isFacility:bool):
        self.isFacility = isFacility
        self.xmlFilePath = xmlFilePath
        self.claimElements = {
            "freq": None,
            "originalRef": None,
            "refProvider"  : {"name":None, "npi":None},
            "rendProvider" : {"name":None, "npi":None},
            "serviceLoc" : {"address":None, "npi":None}
        }
        self.convertClaim()
        
    def __str__(self):
        return repr(self.claimElements)

    def convertClaim(self):
        with open(self.xmlFilePath, "r", encoding="utf7") as file:
            fileContents = bytes(file.read(), encoding="utf8")
        
        parseTree = etree.fromstring(fileContents)
        
        claimType = "Hospital" if self.isFacility else "Medical"

        self.claimElements['freq'] = parseTree.find(".//loop[@id='2300']/seg/comp/subele[last()]").text #FREQ

        provData = parseTree.find(".//loop[@id='2310A']/seg")
        try:
            self.claimElements['refProvider']['name'] = provData[2].text + " " + provData[3].text #NAME
            self.claimElements['refProvider']['npi'] = provData[-1].text #NPI
        except:
            pass

        if claimType == 'Medical':
            rendData = parseTree.find(".//loop[@id='2310B']/seg")
            try:
                self.claimElements['rendProvider']['name'] = rendData[2].text + " " + rendData[3].text #NAME
                self.claimElements['rendProvider']['npi'] =  rendData[-1].text #NPI
            except:
                pass

            try:
                self.claimElements['serviceLoc']['address'] = parseTree.find(".//loop[@id='2310C']/seg[@id='N3']/ele").text
                self.claimElements['serviceLoc']['npi'] = parseTree.find(".//loop[@id='2310C']/seg[@id='NM1']/ele[@id='NM109']").text
                self.claimElements['serviceLoc']['address'] = parseTree.find(".//loop[@id='2310AA']/seg[@id='N301']/ele").text
                self.claimElements['serviceLoc']['npi'] = parseTree.find(".//loop[@id='2310AA']/seg[@id='NM1']/ele[@id='NM103']").text
            except:
                pass

        else:
            try:
                self.claimElements['serviceLoc']['address'] = parseTree.find(".//loop[@id='2310E']/seg[@id='N3']/ele").text
                self.claimElements['serviceLoc']['npi'] = parseTree.find(".//loop[@id='2310E']/seg[@id='NM1']/ele[@id='NM109']").text
            except:
                pass

        if self.claimElements['freq'] == '7':
            originalRefEls = parseTree.findall(".//loop[@id='2300']/seg[@id='REF']/ele")
            for i in range(len(originalRefEls)):
                if originalRefEls[i].text == 'F8':
                    self.claimElements['originalRef'] = originalRefEls[i + 1].text #ORIGINAL REFERENCE NUMBER
                    break


if __name__ == "__main__":
    claim = RobotClaim("./RobotSkip/firstClaim.xml")
    print(str(claim))

