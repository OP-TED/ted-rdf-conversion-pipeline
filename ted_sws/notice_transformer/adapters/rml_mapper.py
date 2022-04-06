import abc
import pathlib
import subprocess

from ted_sws.data_manager.adapters.mapping_suite_repository import TRANSFORM_PACKAGE_NAME, MAPPINGS_PACKAGE_NAME


class RMLMapperABC(abc.ABC):
    """
        This class is a general interface of an adapter for rml-mapper.
    """

    @abc.abstractmethod
    def execute(self, package_path: pathlib.Path) -> str:
        """
            This method allows you to perform an RML mapping based on a file package with a default structure.
        :param package_path: path to package
        :return: a string containing the result of the transformation
        """


class RMLMapper(RMLMapperABC):
    """
        This class is a concrete implementation of the rml-mapper adapter.
    """

    def __init__(self, rml_mapper_path: pathlib.Path):
        """
        :param rml_mapper_path: the path to the rml-mapper executable
        """
        self.rml_mapper_path = rml_mapper_path

    def execute(self, package_path: pathlib.Path) -> str:
        """
            This method allows you to perform an RML mapping based on a file package with a default structure.
            The package structure must be as follows:
                /package_name
                    /transformation
                        /mappings
                            *.rml.tll

                        /resources
                            *.json
                            ...
                            *.xml
        :param package_path: path to package
        :return: a string containing the result of the transformation
        """
        bash_script = f"cd {package_path} && java -jar {self.rml_mapper_path} -m {package_path / TRANSFORM_PACKAGE_NAME / MAPPINGS_PACKAGE_NAME / '*'}"
        script_result = subprocess.run(bash_script, shell=True, stdout=subprocess.PIPE)
        return script_result.stdout.decode('utf-8')
