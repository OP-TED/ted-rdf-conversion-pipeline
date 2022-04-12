import abc
import pathlib


class YARRRML2RMLConvertorABC(abc.ABC):
    """

    """

    @abc.abstractmethod
    def convert(self, yarrrml_input_file_path: pathlib.Path, rml_output_file_path: pathlib.Path):
        """

        :param yarrrml_input_file_path:
        :param rml_output_file_path:
        :return:
        """
        

