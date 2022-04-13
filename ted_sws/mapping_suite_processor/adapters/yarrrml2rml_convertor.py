import abc
import pathlib
import subprocess


class YARRRML2RMLConvertorABC(abc.ABC):
    """
        This class is a general interface of a YARRRML to RML converter.
    """

    @abc.abstractmethod
    def convert(self, yarrrml_input_file_path: pathlib.Path, rml_output_file_path: pathlib.Path):
        """
            This method converts a yarrrml file and writes the result to another rml file.
        :param yarrrml_input_file_path:
        :param rml_output_file_path:
        :return:
        """


class YARRRML2RMLConvertor(YARRRML2RMLConvertorABC):
    """
        This class converts YARRRML to RML using an external docker container that performs conversion logic.
    """
    def convert(self, yarrrml_input_file_path: pathlib.Path, rml_output_file_path: pathlib.Path):
        """
            This method converts a yarrrml file and writes the result to another rml file.
        :param yarrrml_input_file_path:
        :param rml_output_file_path:
        :return:
        """
        bash_script = f"(docker run --rm -i -v {yarrrml_input_file_path.parent}:/data rmlio/yarrrml-parser:latest -i /data/{yarrrml_input_file_path.name}) > {rml_output_file_path}"
        subprocess.run(bash_script, shell=True, stdout=subprocess.PIPE)