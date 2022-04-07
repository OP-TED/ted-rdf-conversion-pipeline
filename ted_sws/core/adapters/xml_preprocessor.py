import os
import pathlib
from abc import ABC, abstractmethod

from ted_sws import config


class XMLPreprocessorABC(ABC):
    """
        This class provides an abstraction for a XML preprocessor
    """

    @abstractmethod
    def transform_with_xslt_to_string(self, xslt_path: pathlib.Path, xml_path: pathlib.Path) -> str:
        """
            Method to get the result of the xslt transformation in a string format
        :return:
        """

    @abstractmethod
    def transform_with_xslt_to_file(self, result_file_path: pathlib.Path, xslt_path: pathlib.Path,
                                    xml_path: pathlib.Path):
        """
            Method to get the result of the xslt transformation in a file
        :return:
        """


class XMLPreprocessor(XMLPreprocessorABC):
    """
        This class provides XML preprocessing
    """

    def __init__(self, path_to_processor: pathlib.Path = config.XML_PROCESSOR_PATH):
        self.path_to_processor = path_to_processor

    def _generate_xslt_command(self, xml_path, xslt_path):
        """
            Method to build the command necessary to run the processor
        :return:
        """
        return f"java -jar {self.path_to_processor} -s:{xml_path} -xsl:{xslt_path}"

    def transform_with_xslt_to_string(self, xslt_path, xml_path) -> str:
        """
            Method to transform an XML with XSLT and get the result in a string format
        :return:
        """
        return os.popen(self._generate_xslt_command(xml_path=xml_path, xslt_path=xslt_path)).read()

    def transform_with_xslt_to_file(self, result_file_path: pathlib.Path, xml_path, xslt_path):
        """
            Method to transform an XML with XSLT and get the result in a file
        :return:
        """
        command = self._generate_xslt_command(xml_path=xml_path, xslt_path=xslt_path) + f" -o:{result_file_path}"
        os.system(command=command)
