import abc
import subprocess
from enum import Enum
from pathlib import Path

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, MS_MAPPINGS_FOLDER_NAME


class SerializationFormat(Enum):
    NQUADS = "nquads"
    TURTLE = "turtle"
    TRIG = "trig"
    TRIX = "trix"
    JSONLD = "jsonld"
    HDT = "hdt"


DEFAULT_SERIALIZATION_FORMAT = SerializationFormat.NQUADS
TURTLE_SERIALIZATION_FORMAT = SerializationFormat.TURTLE


class RMLMapperABC(abc.ABC):
    """
        This class is a general interface of an adapter for rml-mapper.
    """
    serialization_format: SerializationFormat

    def set_serialization_format(self, serialization_format: SerializationFormat):
        """
        Set serialization format of output
        :param serialization_format: nquads (default), turtle, trig, trix, jsonld, hdt
        :return:
        """
        self.serialization_format = serialization_format

    def get_serialization_format(self) -> SerializationFormat:
        """
        Get serialization_format
        :return:
        """
        return self.serialization_format

    def get_serialization_format_value(self) -> str:
        """
        Get serialization_format value
        :return:
        """
        return self.get_serialization_format().value

    @abc.abstractmethod
    def execute(self, package_path: Path) -> str:
        """
            This method allows you to perform an RML mapping based on a file package with a default structure
        :param package_path: path to package
        :return: a string containing the result of the transformation
        """


class RMLMapper(RMLMapperABC):
    """
        This class is a concrete implementation of the rml-mapper adapter.
    """
    def __init__(self, rml_mapper_path: Path, serialization_format: SerializationFormat = TURTLE_SERIALIZATION_FORMAT):
        """
        :param rml_mapper_path: the path to the rml-mapper executable
        :param serialization_format: serialization format
        """
        self.rml_mapper_path = rml_mapper_path
        self.serialization_format = serialization_format

    def execute(self, package_path: Path) -> str:
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
        # java -jar ./rmlmapper.jar -m rml.ttl -s turtle  -o output.ttl
        bash_script = f"cd {package_path} && java -jar {self.rml_mapper_path} -m {package_path / MS_TRANSFORM_FOLDER_NAME / MS_MAPPINGS_FOLDER_NAME / '*'} -s {self.get_serialization_format_value()}"
        script_result = subprocess.run(bash_script, shell=True, capture_output=True)
        error = script_result.stderr.decode('utf-8')
        if error:
            raise Exception(error)
        return script_result.stdout.decode('utf-8')
