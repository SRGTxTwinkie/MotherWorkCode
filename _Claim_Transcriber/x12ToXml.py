import pyx12.x12file
import pyx12.x12xml_simple
import pyx12.xmlx12_simple
import pyx12.params
import pyx12.x12n_document
import logging
from io import StringIO

from VPRController import VPRController


def ediToXml(
    ediFile: str = None,
    outXMLFilePath: str = "output.xml",
    readFromString: bool = False,
    supressErrors: bool = True,
):
    """convert x12file to xmlFile

    :param ediFile: string path to ediFile
    :type ediFile: str
    :param outXMLFilePath: string path/name of output XML file
    :param getFromClipboard: read the edi from clipboard rather than a file
    :type getFromClipboard: bool
    """
    if supressErrors:
        logging.disable()

    params = pyx12.params.params()
    params.set("xmlout", "simple")

    if not readFromString:
        with open(ediFile) as ediSourceFile:
            with open(outXMLFilePath, "w+") as outXML:
                pyx12.x12n_document.x12n_document(
                    param=params,
                    src_file=ediSourceFile,
                    fd_xmldoc=outXML,
                    fd_997=None,
                    fd_html=None,
                )
        return

    ediSourceFile = StringIO(ediFile)
    with open(outXMLFilePath, "w+") as outXML:
        pyx12.x12n_document.x12n_document(
            param=params,
            src_file=ediSourceFile,
            fd_xmldoc=outXML,
            fd_997=None,
            fd_html=None,
        )


if __name__ == "__main__":
    try:
        controller = VPRController()
    except:
        controller = VPRController(True)

    outputXml = "output.xml"
    controller.openX12()
    ediString = controller.returnX12()

    ediToXml(ediString, outputXml, True)
