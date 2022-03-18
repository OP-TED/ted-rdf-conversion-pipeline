import abc
import pathlib
import subprocess

class RMLMapperABC(abc.ABC):
    """

    """

    @abc.abstractmethod
    def execute(self, package_path: pathlib.Path) -> str:
        """

        """


class RMLMapper(RMLMapperABC):
    """

    """

    def __init__(self, rml_mapper_path: pathlib.Path):
        """

        """
        self.rml_mapper_path = rml_mapper_path

    def execute(self, package_path: pathlib.Path) -> str:
        """

        """
        bash_script = f"cd {package_path} && java -jar {self.rml_mapper_path} -m {package_path / 'transform/mappings/*'}"
        script_result = subprocess.run(bash_script, shell= True, stdout=subprocess.PIPE)
        return script_result.stdout.decode('utf-8')
