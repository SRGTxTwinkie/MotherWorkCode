from lxml import etree


class LineItem:
    def __init__(
        self,
        lineNumber: int,
        procedureCode: str,
        referencedDiagnosis: int,
        dollarAmount: int,
        unitQuantity: int,
        unitLabel: str,
        date: str,
        misc: str,
        revCode: str,
    ) -> None:
        self.lineNumber = lineNumber
        self.procedureCode = procedureCode
        self.referencedDiagnosis = referencedDiagnosis
        self.dollarAmount = dollarAmount
        self.unitQuantity = unitQuantity
        self.unitLabel = unitLabel
        self.date = date
        self.misc = misc
        self.revCode = revCode

    def printInfo(self):
        print(
            f"LineItem: lineNumber={self.lineNumber}, procedureCode={self.procedureCode}",
            f"referencedDiagnosis={self.referencedDiagnosis}, dollarAmount={self.dollarAmount}",
            f"unitQuantity={self.unitQuantity}, unitLabel={self.unitLabel}",
            f"date={self.date}, notes={self.misc} ",
        )


class HospitalClaim:
    def __init__(self, xmlFilePath: str):
        with open(xmlFilePath, "r") as f:
            self.xmlTree = etree.fromstring(
                bytes(bytearray(f.read(), encoding="utf-8"))
            )

        self.internalLog = []

        # Information Source
        try:
            self.claimNumber = int(
                (
                    self.xmlTree.xpath("//loop[@id='2000B']/loop[@id='2300']")[2]
                    .xpath("seg/ele")[1]
                    .text
                )
            )
        except:
            self.claimNumber = int(
                (
                    self.xmlTree.xpath(
                        "//loop[@id='DETAIL']/loop[@id='2000A']/loop[@id='2000B']/loop[@id='2300']"
                    )[1]
                    .xpath("seg")[6]
                    .xpath("ele")[1]
                    .text
                )
            )

        # Billing Provider
        self.submitter = (
            self.xmlTree.xpath("//loop/loop/loop[@id='HEADER']")[2]
            .xpath("loop/seg/ele")[2]
            .text
        )
        self.infoContact = (
            self.xmlTree.xpath("//loop/loop/loop[@id='HEADER']")[2]
            .xpath("loop/seg")[1]
            .xpath("ele")[1]
            .text
        )
        self.infoContactPhone = (
            self.xmlTree.xpath("//loop/loop/loop[@id='HEADER']")[2]
            .xpath("loop/seg")[1]
            .xpath("ele")[3]
            .text
        )

        try:
            self.infoContactEmail = (
                self.xmlTree.xpath("//loop/loop/loop[@id='HEADER']")[2]
                .xpath("loop/seg")[1]
                .xpath("ele")[7]
                .text
            )
        except:
            self.infoContactEmail = "Not Provided"

        self.reciver = (
            self.xmlTree.xpath("//loop/loop/loop[@id='HEADER']")[2]
            .xpath("loop")[1]
            .xpath("seg/ele")[2]
            .text
        )
        self.billingProvider = self.xmlTree.xpath(
            "//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg/ele"
        )[2].text
        self.billingProviderNPI = self.xmlTree.xpath(
            "//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg/ele[@id='NM109']"
        )[0].text
        self.billingProviderAddress = (
            self.xmlTree.xpath("//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg")[1]
            .xpath("ele[@id='N301']")[0]
            .text
        )
        self.billingProviderEIN = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg[@id='REF']"
            )[0]
            .xpath("ele[@id='REF02']")[0]
            .text
        )

        try:
            self.billingProviderInfoContact = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg[@id='PER']"
                )[0]
                .xpath("ele[@id='PER02']")[0]
                .text
            )
        except:
            self.billingProviderInfoContact = "Not Provided"

        try:
            self.billingProviderPhoneNumber = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop/seg[@id='PER']"
                )[0]
                .xpath("ele[@id='PER04']")[0]
                .text
            )
        except:
            self.billingProviderPhoneNumber = "Not Provided"

        # Subscriber Information
        self.payerResponsiblitySequence = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("seg[@id='SBR']")[0]
            .xpath("ele")[0]
            .text
        )
        self.relationship = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("seg[@id='SBR']")[0]
            .xpath("ele[@id='SBR02']")[0]
            .text
        )

        try:
            self.groupOrPolicyNumber = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("seg[@id='SBR']")[0]
                .xpath("ele[@id='SBR03']")[0]
                .text
            )
        except:
            self.groupOrPolicyNumber = "Not Provided"

        self.claimFilingIndicator = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("seg[@id='SBR']")[0]
            .xpath("ele[@id='SBR09']")[0]
            .text
        )
        self.insuredOrSubscriberNameLast = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg/ele[@id='NM103']")[0]
            .text
        )
        self.insuredOrSubscriberNameFirst = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg/ele[@id='NM104']")[0]
            .text
        )

        try:
            self.insuredOrSubscriberNameMiddle = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2010BA']")[0]
                .xpath("seg/ele[@id='NM105']")[0]
                .text
            )
        except:
            self.insuredOrSubscriberNameMiddle = "No Middle Name"

        self.memberId = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg/ele[@id='NM109']")[0]
            .text
        )
        self.memberAddress = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg[@id='N3']")[0]
            .xpath("ele[@id='N301']")[0]
            .text
        )

        self.memberCity = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg[@id='N4']")[0]
            .xpath("ele[@id='N401']")[0]
            .text
        )
        self.memberState = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg[@id='N4']")[0]
            .xpath("ele[@id='N402']")[0]
            .text
        )
        self.memberZip = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg[@id='N4']")[0]
            .xpath("ele[@id='N403']")[0]
            .text
        )

        self.memberDOB = None
        datePre = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BA']")[0]
            .xpath("seg[@id='DMG']")[0]
            .xpath("ele[@id='DMG02']")[0]
            .text
        )
        year = datePre[0:4]
        month = datePre[4:6]
        day = datePre[6:8]
        self.memberDOB = f"{day}/{month}/{year}"

        # Payer Info
        self.payorName = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BB']")[0]
            .xpath("seg[@id='NM1']")[0]
            .xpath("ele[@id='NM103']")[0]
            .text
        )
        self.payorID = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2010BB']")[0]
            .xpath("seg[@id='NM1']")[0]
            .xpath("ele[@id='NM109']")[0]
            .text
        )

        # Claim Line Information
        # Basic Information
        self.claimSubmitterIdentifier = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM01']")[0]
            .text
        )
        self.totalClaimAmount = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM02']")[0]
            .text
        )
        self.placeOfService = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("comp[@id='CLM']")[0]
            .xpath("subele[@id='CLM05-01']")[0]
            .text
        )
        self.freq = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("comp[@id='CLM']")[0]
            .xpath("subele[@id='CLM05-03']")[0]
            .text
        )
        try:
            self.providerSignatureOnFile = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[0]
                .xpath("seg[@id='CLM']")[0]
                .xpath("ele[@id='CLM06']")[0]
                .text
            )
        except:
            self.providerSignatureOnFile = "Missing"

        self.providerAcceptAssignment = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM07']")[0]
            .text
        )
        self.assignmentOfBenifitsIndicator = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM08']")[0]
            .text
        )
        self.releaseOfInformation = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[0]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM09']")[0]
            .text
        )

        # EDI Determinted Information
        self.memberID = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[1]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM01']")[0]
            .text
        )
        self.groupNumber = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[1]
            .xpath("seg[@id='CLM']")[0]
            .xpath("ele[@id='CLM02']")[0]
            .text
        )
        self.providerParProviderID = (
            self.xmlTree.xpath(
                "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
            )[0]
            .xpath("loop[@id='2300']")[1]
            .xpath("seg[@id='CLM']")[0]
            .xpath("comp[@id='CLM']")[0]
            .xpath("subele[@id='CLM05-01']")[0]
            .text
        )

        try:
            self.ph_relationship = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[1]
                .xpath("seg[@id='CLM']")[0]
                .xpath("ele[@id='CLM06']")[0]
                .text
            )
        except:
            self.ph_relationship = None

        try:
            self.phDCN = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("seg[@id='CLM']")[0]
                .xpath("ele[@id='CLM02']")[0]
                .text
            )
        except:
            self.phDCN = "Missing"

        try:
            self.originalReferenceNumber = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("seg[@id='REF']")[0]
                .xpath("ele[@id='REF02']")[0]
                .text
            )
        except:
            self.originalReferenceNumber = "Missing"

        try:
            self.billerSentClaimNumber = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("seg[@id='REF']")[1]
                .xpath("ele[@id='REF02']")[0]
                .text
            )
        except:
            self.billerSentClaimNumber = "No Claim Number Provided By Biller"

        try:
            self.billerNote = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("seg[@id='NTE']")[0]
                .xpath("ele[@id='NTE02']")[0]
                .text
            )
        except:
            self.billerNote = "No Note Provided By Biller"
        try:
            dxSeg = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("seg[@id='HI']/comp")
            )
        except:
            dxSeg = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[1]
                .xpath("seg[@id='HI']/comp")
            )

        safeDxCodes = ["ABK", "ABF", "ABJ"]
        safeOccSpanCodes = ["BI"]
        safeOccCodes = ["BH"]
        safeValCodes = ["BE"]
        safeCondCodes = ["BG", "DR"]
        safeProcCodes = ["BBQ", "BBR"]
        skipCodes = ["APR", "ABN"]

        self.diagnosisCodes = []
        self.procedureCodes = []
        self.occSpanCodes = []
        self.condCodes = []
        self.occCodes = []
        self.valCodes = []

        for i in dxSeg:
            if i.xpath("subele")[0].text in safeDxCodes:
                self.diagnosisCodes.append(i.xpath("subele")[1].text)
            elif i.xpath("subele")[0].text in safeOccCodes:
                self.occCodes.append(i.xpath("subele")[1].text)
            elif i.xpath("subele")[0].text in safeValCodes:
                self.valCodes.append(
                    {
                        "value": i.xpath("subele")[1].text,
                        "amount": i.xpath("subele")[4].text,
                    }
                )
            elif i.xpath("subele")[0].text in safeCondCodes:
                self.condCodes.append(i.xpath("subele")[1].text)
            elif i.xpath("subele")[0].text in safeProcCodes:
                self.procedureCodes.append(i.xpath("subele")[1].text)
            elif i.xpath("subele")[0].text in safeOccSpanCodes:
                occCode = {"code": i.xpath("subele")[1].text}
                occCode.update({"from": i.xpath("subele")[3].text[:8]})
                occCode.update({"to": i.xpath("subele")[3].text[9:]})
                self.occSpanCodes.append(occCode)
            elif i.xpath("subele")[0].text in skipCodes:
                pass
            else:
                raise Exception(
                    "Diagnosis Code Error\n" + str(i.xpath("subele")[0].text)
                )

        # Remove Duplicates
        self.diagnosisCodes = list(dict.fromkeys(self.diagnosisCodes))

        # Physical Information
        # Referring Provider
        try:
            self.referringProviderNameFirst = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310A']")[0]
                .xpath("seg/ele[@id='NM104']")[0]
                .text
            )
            self.referringProviderNameLast = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310A']")[0]
                .xpath("seg/ele[@id='NM103']")[0]
                .text
            )
            self.referringProviderNPI = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310A']")[0]
                .xpath("seg/ele[@id='NM109']")[0]
                .text
            )
        except:
            self.referringProviderNameFirst = None
            self.referringProviderNameLast = None
            self.referringProviderNPI = None

        # Rendering Provider
        try:
            self.renderingProviderNameFirst = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310B']")[0]
                .xpath("seg/ele[@id='NM103']")[0]
                .text
            )
            self.renderingProviderNameLast = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310B']")[0]
                .xpath("seg/ele[@id='NM104']")[0]
                .text
            )
            self.renderingProviderNPI = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310B']")[0]
                .xpath("seg/ele[@id='NM109']")[0]
                .text
            )
        except:
            self.renderingProviderNameFirst = None

        # Service Location
        try:
            self.serviceLocationName = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310C']")[0]
                .xpath("seg/ele[@id='NM103']")[0]
                .text
            )
            self.serviceLocationNPI = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310C']")[0]
                .xpath("seg/ele[@id='NM109']")[0]
                .text
            )
            self.serviceLocationAddress = (
                self.xmlTree.xpath(
                    "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
                )[0]
                .xpath("loop[@id='2300']")[2]
                .xpath("loop[@id='2310C']")[0]
                .xpath("seg[@id='N3']")[0]
                .xpath("ele[@id='N301']")[0]
                .text
            )
        except:
            self.serviceLocationName = None

        # Claim Lines
        self.claimLines = []

        for i in self.xmlTree.xpath(
            "//loop/loop/loop/loop[@id='DETAIL']/loop/loop[@id='2000B']"
        )[0].xpath("loop[@id='2300']/loop[@id='2400']"):
            line = i.xpath("seg/ele")[0].text
            # procCodes = i.xpath("seg[@id='SV1']/comp/subele")

            # Remove identifier at start of list
            try:
                proc = i.xpath("seg[@id='SV2']/comp[@id='SV2']/subele[@id='SV202-02']")[
                    0
                ].text
            except:
                proc = None

            amt = i.xpath("seg[@id='SV2']/ele[@id='SV203']")[0].text
            qty = i.xpath("seg[@id='SV2']/ele[@id='SV205']")[0].text
            unit = i.xpath("seg[@id='SV2']/ele[@id='SV204']")[0].text
            try:
                date = i.xpath("seg[@id='DTP']/ele[@id='DTP03']")[0].text
                year = date[0:4]
                month = date[4:6]
                day = date[6:8]
                date = f"{month}/{day}/{year}"
            except:
                date = None

            revCode = i.xpath("seg[@id='SV2']/ele[@id='SV201']")[0].text
            try:
                misc = i.xpath("seg[@id='REF']/ele[@id='REF02']")[0].text
            except:
                misc = None

            self.claimLines.append(
                LineItem(line, proc, None, amt, qty, unit, date, misc, revCode)
            )

        self.claimLines = [item for item in self.claimLines if item != None]


if __name__ == "__main__":
    from x12ToXml import ediToXml
    from VPRController import VPRController

    controller = VPRController()
    controller.openX12()
    x12Data = controller.returnX12()
    ediToXml(x12Data, "outputHospital.xml", readFromString=True)

    claimHospital = HospitalClaim("./outputHospital.xml")

    print(claimHospital.claimLines[0].procedureCode)
