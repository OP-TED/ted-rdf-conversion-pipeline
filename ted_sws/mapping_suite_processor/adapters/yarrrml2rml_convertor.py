import abc
import pathlib
import subprocess


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


class YARRRML2RMLConvertor(YARRRML2RMLConvertorABC):
    """

    """
    def convert(self, yarrrml_input_file_path: pathlib.Path, rml_output_file_path: pathlib.Path):
        """

        :param yarrrml_input_file_path:
        :param rml_output_file_path:
        :return:
        """
        bash_script = f"(docker run --rm -it -v {yarrrml_input_file_path.parent}:/data rmlio/yarrrml-parser:latest -i /data/{yarrrml_input_file_path.name}) > {rml_output_file_path}"
        subprocess.run(bash_script, shell=True, stdout=subprocess.PIPE)