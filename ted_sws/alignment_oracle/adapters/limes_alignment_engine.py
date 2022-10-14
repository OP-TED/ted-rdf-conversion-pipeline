import pathlib
import subprocess
import tempfile

from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams
from ted_sws.alignment_oracle.services.limes_configurator import generate_xml_config_from_limes_config


class LimesAlignmentEngine:
    """
        This is an adapter for limes executable.
    """

    def __init__(self, limes_executable_path: pathlib.Path):
        self.limes_executable_path = limes_executable_path

    def execute(self, limes_config_params: LimesConfigParams):
        """
            This method generate alignment links based on limes_config_params.
        :param limes_config_params:
        :return:
        """
        limes_xml_config = generate_xml_config_from_limes_config(limes_config_params=limes_config_params)
        temp_file = tempfile.NamedTemporaryFile()
        temp_file.write(limes_xml_config.encode(encoding="utf-8"))
        self.execute_from_file_config(config_file_path=pathlib.Path(temp_file.name))
        temp_file.close()

    def execute_from_file_config(self, config_file_path: pathlib.Path):
        """
            This method generate alignment links based on config file.
        :param config_file_path:
        :return:
        """
        bash_script = f"java -jar {self.limes_executable_path} {config_file_path}"
        execution_result = subprocess.run(bash_script, shell=True, capture_output=True)
        print(execution_result.stderr.decode(encoding="utf-8"))
