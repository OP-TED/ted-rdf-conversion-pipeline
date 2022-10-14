import pathlib
import subprocess
import tempfile

from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams
from ted_sws.alignment_oracle.services.limes_configurator import generate_xml_config_from_limes_config


class LimesAlignmentEngine:
    """
        This is a adapter for limes executable.
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
        bash_script = f"java -jar {self.limes_executable_path} {temp_file.name}"
        script_result = subprocess.run(bash_script, shell=True, capture_output=True)
        temp_file.close()
        script_result.stderr.decode('utf-8')
