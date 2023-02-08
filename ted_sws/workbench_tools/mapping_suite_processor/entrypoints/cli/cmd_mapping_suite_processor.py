#!/usr/bin/python3

from pathlib import Path
from typing import Tuple, List, Dict

import click
from ordered_set import OrderedSet

from ted_sws.core.adapters.cmd_runner import CmdRunnerForMappingSuite as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.event_manager.adapters.log import SeverityLevelType, LOG_WARN_TEXT
from ted_sws.workbench_tools.mapping_suite_processor.entrypoints.cli import cmd_resources_injector, cmd_sparql_generator, cmd_triple_store_loader, \
    cmd_mapping_suite_validator
from ted_sws.workbench_tools.mapping_suite_processor.entrypoints.cli import cmd_rml_modules_injector, cmd_metadata_generator
from ted_sws.workbench_tools.mapping_suite_processor.entrypoints.cli.cmd_rml_modules_injector import DEFAULT_RML_MODULES_PATH
from ted_sws.workbench_tools.notice_transformer.cli import cmd_mapping_runner
from ted_sws.workbench_tools.notice_validator.cli import cmd_xpath_coverage_runner, cmd_sparql_runner, \
    cmd_validation_summary_runner
from ted_sws.workbench_tools.notice_validator.cli import cmd_shacl_runner
from ted_sws.workbench_tools.rml_to_html.cli import cmd_rml_report_generator

MAPPING_SUITE_VALIDATOR = "mapping_suite_validator"
METADATA_GENERATOR = "metadata_generator"
TRIPLE_STORE_LOADER = "triple_store_loader"
VALIDATION_SUMMARY_RUNNER = "validation_summary_runner"
SHACL_RUNNER = "shacl_runner"
SPARQL_RUNNER = "sparql_runner"
XPATH_COVERAGE_RUNNER = "xpath_coverage_runner"
MAPPING_RUNNER = "mapping_runner"
RML_REPORT_GENERATOR = "rml_report_generator"
SPARQL_GENERATOR = "sparql_generator"
RML_MODULES_INJECTOR = "rml_modules_injector"
RESOURCES_INJECTOR = "resources_injector"

DEFAULT_COMMANDS: Tuple = (
    RESOURCES_INJECTOR,
    RML_MODULES_INJECTOR,
    SPARQL_GENERATOR,
    RML_REPORT_GENERATOR,
    MAPPING_RUNNER,
    XPATH_COVERAGE_RUNNER,
    SPARQL_RUNNER,
    SHACL_RUNNER,
    VALIDATION_SUMMARY_RUNNER,
    TRIPLE_STORE_LOADER,
    METADATA_GENERATOR,
    MAPPING_SUITE_VALIDATOR
)
DEFAULT_GROUPS: Dict = {
    "inject_resources": [RESOURCES_INJECTOR, RML_MODULES_INJECTOR],
    "generate_resources": [SPARQL_GENERATOR, RML_REPORT_GENERATOR],
    "update_resources": [RESOURCES_INJECTOR, RML_MODULES_INJECTOR, SPARQL_GENERATOR, RML_REPORT_GENERATOR],
    "transform_notices": [MAPPING_RUNNER],
    "validate_notices": [XPATH_COVERAGE_RUNNER, SPARQL_RUNNER, SHACL_RUNNER, VALIDATION_SUMMARY_RUNNER],
    "upload_notices": [TRIPLE_STORE_LOADER],
    "validate_mapping_suite": [MAPPING_SUITE_VALIDATOR]
}
CMD_NAME = "CMD_MAPPING_SUITE_PROCESSOR"

"""
USAGE:
# mapping_suite_processor --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Mapping Suite Processor
    """

    groups: List[str] = []
    commands: List[str] = []

    def __init__(
            self,
            mapping_suite_id,
            notice_ids: List[str],
            mappings_path,
            rml_modules_folder,
            commands: List[str] = None,
            groups: List[str] = None
    ):
        super().__init__(name=CMD_NAME)

        self.mapping_suite_id = mapping_suite_id
        self.notice_ids = self._init_list_input_opts(notice_ids)
        self.mappings_path = mappings_path
        self.rml_modules_folder = rml_modules_folder

        if not groups:
            self.commands = self._valid_cmds(self._init_list_input_opts(commands or DEFAULT_COMMANDS))
        else:
            valid_groups = self._valid_groups(self._init_list_input_opts(groups))
            for valid_group in valid_groups:
                self.commands += DEFAULT_GROUPS[valid_group]

            self.groups = valid_groups

        mapping_suite_path = Path(mappings_path).resolve() / Path(mapping_suite_id)
        if not mapping_suite_path.is_dir():
            error_msg = f"No such MappingSuite[{mapping_suite_id}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    def _cmd(self, cmd: str):
        if cmd == RESOURCES_INJECTOR:
            cmd_resources_injector.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == RML_MODULES_INJECTOR:
            cmd_rml_modules_injector.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path,
                opt_rml_modules_folder=self.rml_modules_folder
            )
        elif cmd == SPARQL_GENERATOR:
            cmd_sparql_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == RML_REPORT_GENERATOR:
            cmd_rml_report_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == MAPPING_RUNNER:
            cmd_mapping_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_ids,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == XPATH_COVERAGE_RUNNER:
            cmd_xpath_coverage_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_ids,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == SPARQL_RUNNER:
            cmd_sparql_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_ids,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == SHACL_RUNNER:
            cmd_shacl_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_ids,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == VALIDATION_SUMMARY_RUNNER:
            cmd_validation_summary_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_ids,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == TRIPLE_STORE_LOADER:
            cmd_triple_store_loader.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == MAPPING_SUITE_VALIDATOR:
            cmd_mapping_suite_validator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == METADATA_GENERATOR:
            cmd_metadata_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )

    def _valid_groups(self, groups):
        """
        This method will trim non-existing input groups. Provided input groups must be present in DEFAULT_GROUPS.
        :param groups:
        :return:
        """
        group_set = OrderedSet(groups)
        default_group_set = OrderedSet(tuple(DEFAULT_GROUPS))
        invalid_groups = group_set - default_group_set
        if invalid_groups:
            self.log(
                LOG_WARN_TEXT.format("The following groups will be skipped (invalid): " + ",".join(invalid_groups)))
        return list(group_set & default_group_set)

    def _valid_cmds(self, commands):
        """
        This method will trim non-existing input commands. Provided input commands must be present in DEFAULT_COMMANDS.
        :param commands:
        :return:
        """
        command_set = OrderedSet(commands)
        default_command_set = OrderedSet(DEFAULT_COMMANDS)
        invalid_cmds = command_set - default_command_set
        if invalid_cmds:
            self.log(
                LOG_WARN_TEXT.format("The following commands will be skipped (invalid): " + ",".join(invalid_cmds)))
        return list(command_set & default_command_set)

    def run_cmd(self):
        super().run_cmd()

        if self.groups:
            self.log(LOG_WARN_TEXT.format("Groups: ") + str(self.groups))
        if self.commands:
            self.log(LOG_WARN_TEXT.format("Commands: ") + str(self.commands))
            self.log(LOG_WARN_TEXT.format("#######"))

            for cmd in self.commands:
                self.log(LOG_WARN_TEXT.format("# " + cmd), SeverityLevelType.WARNING)
                self._cmd(cmd)

            self.log(LOG_WARN_TEXT.format("#######"))


def run(mapping_suite_id, notice_id, command=DEFAULT_COMMANDS,
        group=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH, opt_rml_modules_folder=DEFAULT_RML_MODULES_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_ids=list(notice_id or []),
        commands=list(command),
        groups=list(group or []),
        mappings_path=opt_mappings_folder,
        rml_modules_folder=opt_rml_modules_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=True)
@click.option('-n', '--notice-id', required=False, multiple=True, default=None,
              help="Provide notices to be used where applicable")
@click.option('-c', '--command', multiple=True, help=",".join(DEFAULT_COMMANDS))
@click.option('-g', '--group', multiple=True, help=",".join(tuple(DEFAULT_GROUPS)))
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
@click.option('-r', '--opt-rml-modules-folder', default=str(DEFAULT_RML_MODULES_PATH))
def main(mapping_suite_id, notice_id, command, group, opt_mappings_folder, opt_rml_modules_folder):
    """
    Processes Mapping Suite (identified by mapping-suite-id):\n
    - by commands:\n
        --- resources_injector\n
        --- rml_modules_injector\n
        --- sparql_generator\n
        --- rml_report_generator\n
        --- mapping_runner\n
        --- xpath_coverage_runner\n
        --- sparql_runner\n
        --- shacl_runner\n
        --- validation_summary_runner\n
        --- triple_store_loader\n
        --- metadata_generator\n
        --- mapping_suite_validator\n
    - by groups:\n
        --- "inject_resources": ["resources_injector", "rml_modules_injector"]\n
        --- "generate_resources": ["sparql_generator", "rml_report_generator"]\n
        --- "update_resources": ["resources_injector", "rml_modules_injector", "sparql_generator", "rml_report_generator"]\n
        --- "transform_notices": ["mapping_runner"]\n
        --- "validate_notices": ["xpath_coverage_runner", "sparql_runner", "shacl_runner", "validation_summary_runner"]\n
        --- "upload_notices": ["triple_store_loader"]\n
        --- "validate_mapping_suite": ["mapping_suite_validator"]
    """
    run(mapping_suite_id, notice_id, command, group, opt_mappings_folder, opt_rml_modules_folder)


if __name__ == '__main__':
    main()
