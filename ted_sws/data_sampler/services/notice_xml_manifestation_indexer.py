import abc
import pathlib
import tempfile

from ted_sws.core.adapters.xml_preprocessor import XMLPreprocessor
from ted_sws.core.model.metadata import XMLMetadata
from ted_sws.core.model.notice import Notice
from ted_sws.resources import XSLT_FILES_PATH

UNIQUE_XPATHS_XSLT_FILE_PATH = "get_unique_xpaths.xsl"
XSLT_PREFIX_RESULT = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"


class NoticeXMLIndexerABC(abc.ABC):
    """

    """

    @abc.abstractmethod
    def index_notice(self, notice: Notice):
        """

        :param notice:
        :return:
        """


class NoticeXMLIndexer(NoticeXMLIndexerABC):
    """

    """

    def index_notice(self, notice: Notice) -> Notice:
        """

        :param notice:
        :return:
        """
        with tempfile.NamedTemporaryFile() as fp:
            fp.write(notice.xml_manifestation.object_data.encode("utf-8"))
            xml_path = pathlib.Path(fp.name)
            xslt_path = XSLT_FILES_PATH / UNIQUE_XPATHS_XSLT_FILE_PATH
            xslt_transformer = XMLPreprocessor()
            result = xslt_transformer.transform_with_xslt_to_string(xml_path=xml_path,
                                                                    xslt_path=xslt_path)
            unique_xpaths = result[len(XSLT_PREFIX_RESULT):].split(",")
            notice.xml_metadata = XMLMetadata(unique_xpaths=unique_xpaths)

        return notice
