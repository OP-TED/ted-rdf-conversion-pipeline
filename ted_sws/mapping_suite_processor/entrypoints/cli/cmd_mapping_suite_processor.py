#!/usr/bin/python3

import os
from pathlib import Path
from typing import Tuple, List, Dict
from ordered_set import OrderedSet

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.event_manager.adapters.log import SeverityLevelType, LOG_INFO_TEXT, LOG_WARN_TEXT
from ted_sws.mapping_suite_processor.entrypoints.cli import cmd_resources_injector, cmd_rml_modules_injector, \
    cmd_sparql_generator, cmd_triple_store_loader, cmd_metadata_generator, cmd_mapping_suite_validator
from ted_sws.notice_transformer.entrypoints.cli import cmd_mapping_runner
from ted_sws.notice_validator.entrypoints.cli import cmd_xpath_coverage_runner, cmd_sparql_runner, cmd_shacl_runner, \
    cmd_validation_summary_runner
from ted_sws.rml_to_html.entrypoints.cli import cmd_rml_report_generator

DEFAULT_COMMANDS: Tuple = (
    "resources_injector",
    "rml_modules_injector",
    "sparql_generator",
    "rml_report_generator",
    "mapping_runner",
    "xpath_coverage_runner",
    "sparql_runner",
    "shacl_runner",
    "validation_summary_runner",
    "triple_store_loader",
    "mapping_suite_validator",
    "metadata_generator"
)
DEFAULT_GROUPS: Dict = {
    "update_resources": ["resources_injector", "rml_modules_injector", "sparql_generator", "rml_report_generator"],
    "transform_notices": ["mapping_runner"],
    "validate_notices": ["xpath_coverage_runner", "sparql_runner", "shacl_runner", "validation_summary_runner"],
    "upload_notices": ["triple_store_loader"],
    "validate_mapping_suite": ["mapping_suite_validator"]
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

    def __init__(
            self,
            mapping_suite_id,
            notice_id: List[str],
            mappings_path,
            command: List[str] = None,
            group: List[str] = None
    ):
        super().__init__(name=CMD_NAME)

        self.mapping_suite_id = mapping_suite_id
        self.notice_id = self._init_list_input_opts(notice_id)
        self.mappings_path = mappings_path
        self.group = []
        self.command = []
        if not (group and len(group) > 0):
            self.command = self._valid_cmds(self._init_list_input_opts(command or DEFAULT_COMMANDS))
        else:
            self.command = []
            valid_groups = self._valid_groups(self._init_list_input_opts(group))
            for valid_group in valid_groups:
                self.command += DEFAULT_GROUPS[valid_group]

            self.group = valid_groups

        mapping_suite_path = Path(os.path.realpath(mappings_path)) / Path(mapping_suite_id)
        if not mapping_suite_path.is_dir():
            error_msg = f"No such MappingSuite[{mapping_suite_id}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

    @classmethod
    def _init_list_input_opts(cls, input_val):
        input_set = OrderedSet()
        if len(input_val) > 0:
            for item in input_val:
                input_set |= OrderedSet(map(lambda x: x.strip(), item.split(",")))
        return list(input_set)

    def _cmd(self, cmd: str):
        if cmd == 'resources_injector':
            cmd_resources_injector.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'rml_modules_injector':
            cmd_rml_modules_injector.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'sparql_generator':
            cmd_sparql_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'rml_report_generator':
            cmd_rml_report_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'mapping_runner':
            cmd_mapping_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'xpath_coverage_runner':
            cmd_xpath_coverage_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'sparql_runner':
            cmd_sparql_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'shacl_runner':
            cmd_shacl_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'validation_summary_runner':
            cmd_validation_summary_runner.run(
                mapping_suite_id=self.mapping_suite_id,
                notice_id=self.notice_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'triple_store_loader':
            cmd_triple_store_loader.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'mapping_suite_validator':
            cmd_mapping_suite_validator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )
        elif cmd == 'metadata_generator':
            cmd_metadata_generator.run(
                mapping_suite_id=self.mapping_suite_id,
                opt_mappings_folder=self.mappings_path
            )

    def _valid_groups(self, group):
        group_set = OrderedSet(group)
        default_group_set = OrderedSet(tuple(DEFAULT_GROUPS))
        invalid_groups = group_set - default_group_set
        if len(invalid_groups) > 0:
            self.log(
                LOG_WARN_TEXT.format("The following groups will be skipped (invalid): " + ",".join(invalid_groups)))
        return list(group_set & default_group_set)

    def _valid_cmds(self, command):
        command_set = OrderedSet(command)
        default_command_set = OrderedSet(DEFAULT_COMMANDS)
        invalid_cmds = command_set - default_command_set
        if len(invalid_cmds) > 0:
            self.log(
                LOG_WARN_TEXT.format("The following commands will be skipped (invalid): " + ",".join(invalid_cmds)))
        return list(command_set & default_command_set)

    def run_cmd(self):
        if len(self.group) > 0:
            self.log(LOG_INFO_TEXT.format(self.group) + " command groups:")
        if len(self.command):
            self.log("Running " + LOG_INFO_TEXT.format(self.command) + " commands for " + LOG_INFO_TEXT.format(
                f"MappingSuite[{self.mapping_suite_id}]"
            ) + " ... ")
            self.log(LOG_WARN_TEXT.format("#######"))

            for cmd in self.command:
                self.log(LOG_WARN_TEXT.format("# " + cmd), SeverityLevelType.WARNING)
                self._cmd(cmd)

            self.log(LOG_WARN_TEXT.format("#######"))


def run(mapping_suite_id, notice_id, opt_mappings_folder=DEFAULT_MAPPINGS_PATH, command=DEFAULT_COMMANDS,
        group=None):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_id=list(notice_id),
        mappings_path=opt_mappings_folder,
        command=list(command),
        group=list(group)
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=True)
@click.option('-n', '--notice-id', required=False, multiple=True, default=None,
              help="Provide notices to be used where applicable")
@click.option('-c', '--command', multiple=True, help=",".join(DEFAULT_COMMANDS))
@click.option('-g', '--group', multiple=True, help=",".join(tuple(DEFAULT_GROUPS)))
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, notice_id, opt_mappings_folder, command, group):
    """
    Processes Mapping Suite (identified by mapping-suite-id):
    - resources_injector
    - rml_modules_injector
    - sparql_generator
    - rml_report_generator
    - mapping_runner
    - xpath_coverage_runner
    - sparql_runner
    - shacl_runner
    - validation_summary_runner
    - triple_store_loader
    - mapping_suite_validator
    - metadata_generator
    """
    run(mapping_suite_id, notice_id, opt_mappings_folder, command, group)


if __name__ == '__main__':
    main()
