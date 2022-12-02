from X12_Conversion.x12_to_xml import x12_to_xml

from Claim_Structure.original_ref import original_ref

import xml.etree.ElementTree as elt


class Claim:
    def __init__(self, input, output, checkInState=False):

        self._x12_xml_(input, output)

        content = elt.parse(output)
        self.root = content.getroot()

        self.idNum = original_ref(self.root, checkInState)
        self.freq = self.getFreq(self.root)

    def _x12_xml_(self, ediFile, xmlFile):
        x12_to_xml(ediFile, xmlFile)

    def getFreq(self, eltree):
        self.freq = eltree.find(
            ".//*seg[@id='CLM']/comp[@id='CLM']/subele[@id='CLM05-03']"
        ).text
