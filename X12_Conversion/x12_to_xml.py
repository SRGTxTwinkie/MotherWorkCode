import pyx12.x12file
import pyx12.x12xml_simple
import pyx12.xmlx12_simple
import pyx12.params
import pyx12.x12n_document
from io import StringIO

def x12_to_xml(ediFile, xmlFile):
        param = pyx12.params.params()

        fd_source = open(ediFile)
        filename = xmlFile
        with open(filename, 'w+') as fd_xml:
            fd_result = StringIO()
            param.set('xmlout', 'simple')
            pyx12.x12n_document.x12n_document(
                param=param,
                src_file=fd_source,
                fd_997=None,
                fd_html=None,
                fd_xmldoc=fd_xml,
                xslt_files=None
                )
            fd_xml.seek(0)
            fd_result.seek(0)
            pyx12.xmlx12_simple.convert(fd_xml, fd_result)
            fd_source.seek(0)
            fd_result.seek(0)
