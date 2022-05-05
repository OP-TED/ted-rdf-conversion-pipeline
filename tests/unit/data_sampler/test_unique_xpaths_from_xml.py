import pathlib
import tempfile

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.resources import XSLT_FILES_PATH

UNIQUE_XPATHS_XSLT_FILE_PATH = "get_unique_xpaths.xsl"
XSLT_PREFIX_RESULT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"

def test_unique_xpaths_from_xml(notice_2016):
    with tempfile.NamedTemporaryFile() as fp:
        fp.write(notice_2016.xml_manifestation.object_data.encode("utf-8"))
        xml_path = pathlib.Path(fp.name)
        xslt_path = XSLT_FILES_PATH / UNIQUE_XPATHS_XSLT_FILE_PATH
        xslt_transformer = XMLPreprocessor()
        result = xslt_transformer.transform_with_xslt_to_string(xml_path=xml_path,
                                                                xslt_path=xslt_path)
        xpaths = result[len(XSLT_PREFIX_RESULT):].split(",")
        print(xpaths)
        print(len(xpaths))