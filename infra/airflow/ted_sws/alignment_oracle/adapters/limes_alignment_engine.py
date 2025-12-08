import pathlib
import subprocess
import tempfile

from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams
from ted_sws.alignment_oracle.services.limes_configurator import generate_xml_config_from_limes_config
from ted_sws.event_manager.services.log import log_info


class LimesAlignmentEngine:
    """
        This is an adapter for limes executable.
    """

    def __init__(self, limes_executable_path: pathlib.Path, use_caching: bool = None):
        self.limes_executable_path = limes_executable_path
        self.use_caching = use_caching if use_caching is not None else True

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

        def execute_bash_script(execution_dir_path: str):
            bash_script = f"cd {execution_dir_path} && java -jar {self.limes_executable_path} {config_file_path}"
            execution_result = subprocess.run(bash_script, shell=True, capture_output=True)
            log_info(message=execution_result.stderr.decode(encoding="utf-8"))

        if self.use_caching:
            execute_bash_script(str(self.limes_executable_path.parent))
        else:
            with tempfile.TemporaryDirectory() as tmp_execution_dir_path:
                execute_bash_script(execution_dir_path=tmp_execution_dir_path)
