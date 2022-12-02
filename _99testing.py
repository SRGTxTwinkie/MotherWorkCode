from X12_Conversion import x12_to_xml
from Claim_Structure.Claim import Claim
from VPRController import VPRController

controller = VPRController()

with open('./input.edi', 'w') as ediIn:
    ediIn.write(controller.returnX11())
    ediIn.close()

myClaim = Claim("./input.edi", "./output.xml")