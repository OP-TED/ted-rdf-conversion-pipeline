#!/usr/bin/python3

import json
import os
from pathlib import Path

import click

from ted_sws.core.model.notice import Notice
from ted_sws.core.model.manifestation import XMLManifestation
from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, DEFAULT_OUTPUT_PATH
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.logger import LOG_INFO_TEXT
from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE
from ted_sws.notice_validator.services.xpath_coverage_runner import CoverageRunner, coverage_notice_xpath_report
from typing import List

OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH
DEFAULT_TEST_SUITE_REPORT_FOLDER = "test_suite_report"
REPORT_FILE = "xpath_cov_{id}"
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
            conceptual_mappings_file,
            mappings_path,
            xslt_transformer
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path
        self.conceptual_mappings_file_path = Path(os.path.realpath(conceptual_mappings_file))
        self.xslt_transformer = xslt_transformer
        self.output_folder = OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                  mapping_suite_id=self.mapping_suite_id)

        if not self.conceptual_mappings_file_path.is_file():
            error_msg = f"No such Conceptual Mappings file :: [{conceptual_mappings_file}]"
            self.log_failed_msg(error_msg)
            raise FileNotFoundError(error_msg)

        repository_path = Path(self.mappings_path)

        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)
        self.coverage_runner = CoverageRunner(self.conceptual_mappings_file_path)

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

    def coverage_report(self, notices: List[Notice], output_path: Path, label: str):
        self.log("Generating coverage report for " + LOG_INFO_TEXT.format(label) + " ... ")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report = coverage_notice_xpath_report(notices,
                                              self.mapping_suite_id,
                                              self.conceptual_mappings_file_path,
                                              self.coverage_runner,
                                              self.xslt_transformer)
        self.save_json_report(Path(str(output_path) + ".json"), self.coverage_runner.json_report(report))
        self.save_html_report(Path(str(output_path) + ".html"), self.coverage_runner.html_report(report))

    def run_cmd(self):
        output_path = Path(self.output_folder)
        notices: List[Notice] = []
        for data in self.mapping_suite.transformation_test_data.test_data:
            notice: Notice = Notice(ted_id=Path(data.file_name).stem,
                                    xml_manifestation=XMLManifestation(object_data=data.file_content))
            report_file = REPORT_FILE.format(id=notice.ted_id)
            report_path = output_path / notice.ted_id / DEFAULT_TEST_SUITE_REPORT_FOLDER / report_file
            self.coverage_report(notices=[notice], output_path=report_path, label=notice.ted_id)
            notices.append(notice)

        self.coverage_report(notices=notices, output_path=output_path / REPORT_FILE.format(id=self.mapping_suite_id),
                             label='MappingSuite[' + self.mapping_suite_id + ']')

        return self.run_cmd_result()


def run(mapping_suite_id=None, opt_conceptual_mappings_file=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH,
        xslt_transformer=None):
    if opt_conceptual_mappings_file:
        conceptual_mappings_file = opt_conceptual_mappings_file
    else:
        conceptual_mappings_file = CONCEPTUAL_MAPPINGS_FILE.format(
            mappings_path=opt_mappings_folder,
            mapping_suite_id=mapping_suite_id
        )

    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        conceptual_mappings_file=conceptual_mappings_file,
        mappings_path=opt_mappings_folder,
        xslt_transformer=xslt_transformer
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-i', '--opt-conceptual-mappings-file', help="Use to overwrite default INPUT")
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_conceptual_mappings_file, opt_mappings_folder):
    """
    Generates Coverage Reports for Notices
    """
    run(mapping_suite_id, opt_conceptual_mappings_file, opt_mappings_folder)


if __name__ == '__main__':
    main()
