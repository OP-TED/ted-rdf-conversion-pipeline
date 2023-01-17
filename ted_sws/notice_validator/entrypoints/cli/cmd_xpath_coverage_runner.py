#!/usr/bin/python3

import json
import os
from pathlib import Path
from typing import List, Dict

import click

from ted_sws.core.adapters.cmd_runner import CmdRunnerForMappingSuite as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, \
    DEFAULT_OUTPUT_PATH
from ted_sws.core.model.manifestation import XMLManifestation, ReportNotice
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.data_manager.services.mapping_suite_resource_manager import file_resource_output_path
from ted_sws.event_manager.adapters.log import LOG_INFO_TEXT
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE_TEMPLATE
from ted_sws.notice_validator.adapters.xpath_coverage_runner import CoverageRunner
from ted_sws.notice_validator.entrypoints.cli import DEFAULT_TEST_SUITE_REPORT_FOLDER
from ted_sws.notice_validator.services.xpath_coverage_runner import coverage_notice_xpath_report, \
    xpath_coverage_html_report, xpath_coverage_json_report

OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH
REPORT_FILE = "xpath_coverage_validation"
JSON_REPORT_FILE = REPORT_FILE + ".json"
CMD_NAME = "CMD_XPATH_COVERAGE_RUNNER"

"""
USAGE:
# xpath_coverage_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Coverage Runner
    """

    def __init__(
            self,
            mapping_suite_id,
            notice_ids: List[str],
            conceptual_mappings_file,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.with_html = True
        self.mapping_suite_id = mapping_suite_id
        self.notice_ids = self._init_list_input_opts(notice_ids)
        self.mappings_path = mappings_path
        self.conceptual_mappings_file_path = Path(os.path.realpath(conceptual_mappings_file))
        self.output_folder = OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                  mapping_suite_id=self.mapping_suite_id)

        if not self.conceptual_mappings_file_path.is_file():
            error_msg = f"No such Conceptual Mappings file :: [{conceptual_mappings_file}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

        repository_path = Path(self.mappings_path)

        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)
        self.coverage_runner = CoverageRunner(mapping_suite_id=self.mapping_suite_id,
                                              conceptual_mappings_file_path=self.conceptual_mappings_file_path)

    @classmethod
    def save_json_report(cls, output_path, json_report: dict):
        with open(output_path, "w+") as f:
            json.dump(json_report, f, indent=4)
            f.close()

    @classmethod
    def save_html_report(cls, output_path, html_report: str):
        with open(output_path, "w+") as f:
            f.write(html_report)
            f.close()

    def coverage_report(self, notices: List[NoticeForReport], output_path: Path, label: str, group_path: Path = None):
        self.log("Generating coverage report for " + LOG_INFO_TEXT.format(label) + " ... ")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = coverage_notice_xpath_report(notices,
                                              self.mapping_suite_id,
                                              self.conceptual_mappings_file_path,
                                              self.coverage_runner)
        self.save_json_report(Path(str(output_path) + ".json"), xpath_coverage_json_report(report))
        if self.with_html:
            self.save_html_report(Path(str(output_path) + ".html"),
                                  xpath_coverage_html_report(report, group_path=group_path))

    def run_cmd(self):
        super().run_cmd()

        output_path = Path(self.output_folder)
        notices: List[NoticeForReport] = []
        group_notices: Dict[Path, List[NoticeForReport]] = {}
        for data in self.mapping_suite.transformation_test_data.test_data:
            notice_id = Path(data.file_name).stem
            if self.skip_notice(notice_id):
                continue
            notice: Notice = Notice(ted_id=notice_id,
                                    xml_manifestation=XMLManifestation(object_data=data.file_content))
            report_file = REPORT_FILE
            group_path = file_resource_output_path(data)
            notice_for_report = NoticeForReport(notice=notice, group_path=group_path)
            report_path = output_path / group_path / notice.ted_id / DEFAULT_TEST_SUITE_REPORT_FOLDER / report_file
            self.coverage_report(notices=[notice_for_report], output_path=report_path,
                                 label=str(file_resource_output_path(data) / data.file_name))

            if group_path not in group_notices:
                group_notices[group_path] = []
            group_notices[group_path].append(notice_for_report)

            notices.append(notice_for_report)

        for group_path in group_notices:
            notices = group_notices[group_path]
            report_path = output_path / group_path / REPORT_FILE
            self.coverage_report(notices=notices, output_path=report_path, label="Group[" + str(group_path) + ']')

        ms_label = 'MappingSuite[' + self.mapping_suite_id + ']'
        self.coverage_report(notices=notices, output_path=output_path / REPORT_FILE, label=ms_label)

        return self.run_cmd_result()


def run(mapping_suite_id=None, notice_id=None, opt_conceptual_mappings_file=None,
        opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    if opt_conceptual_mappings_file:
        conceptual_mappings_file = opt_conceptual_mappings_file
    else:
        conceptual_mappings_file = CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_ids=list(notice_id or []),
        conceptual_mappings_file=conceptual_mappings_file,
        mappings_path=opt_mappings_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('--notice-id', required=False, multiple=True, default=None)
@click.option('-i', '--opt-conceptual-mappings-file', help="Use to overwrite default INPUT")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, notice_id, opt_conceptual_mappings_file, opt_mappings_folder):
    """
    Generates Coverage Reports for Notices
    """
    run(mapping_suite_id, notice_id, opt_conceptual_mappings_file, opt_mappings_folder)


if __name__ == '__main__':
    main()
