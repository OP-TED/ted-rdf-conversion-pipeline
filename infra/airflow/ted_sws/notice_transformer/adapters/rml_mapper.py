import abc
import os
import signal
import subprocess
from enum import Enum
from pathlib import Path

from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_MAPPINGS_FOLDER_NAME


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
    def __init__(self, rml_mapper_path: Path, serialization_format: SerializationFormat = TURTLE_SERIALIZATION_FORMAT,
                 transformation_timeout: float = None
                 ):
        """
        :param rml_mapper_path: the path to the rml-mapper executable
        :param serialization_format: serialization format
        :param serialization_format: transformation_timeout
        """
        self.rml_mapper_path = rml_mapper_path
        self.serialization_format = serialization_format
        self.transformation_timeout = transformation_timeout

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
        process = subprocess.Popen(bash_script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        if self.transformation_timeout:
            try:
                process.wait(timeout=self.transformation_timeout)
            except subprocess.TimeoutExpired as e:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                raise e
        output, error = process.communicate()
        error = error.decode(encoding="utf-8")
        if error:
            raise Exception(error)
        return output.decode(encoding="utf-8")

