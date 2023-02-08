#!/usr/bin/python3

import json
from pathlib import Path
from typing import List, Dict

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH, DEFAULT_OUTPUT_PATH
from ted_sws.core.model.manifestation import XMLManifestation, RDFManifestation, XPATHCoverageValidationReport, \
    SPARQLTestSuiteValidationReport, SHACLTestSuiteValidationReport, ValidationSummaryReport
from ted_sws.core.model.notice import Notice
from ted_sws.workbench_tools.notice_validator.cli import DEFAULT_TEST_SUITE_REPORT_FOLDER
from ted_sws.workbench_tools.notice_validator.cli.cmd_shacl_runner import JSON_VALIDATIONS_REPORT as JSON_SHACL_REPORT
from ted_sws.workbench_tools.notice_validator.cli.cmd_sparql_runner import JSON_VALIDATIONS_REPORT as JSON_SPARQL_REPORT
from ted_sws.workbench_tools.notice_validator.cli.cmd_xpath_coverage_runner import JSON_REPORT_FILE as XPATH_COV_REPORT
from ted_sws.notice_validator.services.validation_summary_runner import generate_validation_summary_report_notices

OUTPUT_FOLDER = '{mappings_path}/{mapping_suite_id}/' + DEFAULT_OUTPUT_PATH

REPORT_FILE = "validation_summary_report"
CMD_NAME = "CMD_VALIDATION_SUMMARY_RUNNER"

"""
USAGE:
# validation_summary_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by Coverage Runner
    """

    notice_ids: List[str] = []
    notices: List[Notice] = []
    for_mapping_suite: bool = False

    def __init__(
            self,
            mapping_suite_id,
            notice_id: List[str],
            notice_aggregate: bool,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.with_html = True
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path
        self.notice_aggregate = notice_aggregate
        self.output_path = Path(OUTPUT_FOLDER.format(mappings_path=self.mappings_path,
                                                     mapping_suite_id=self.mapping_suite_id))
        if notice_id and len(notice_id) > 0:
            self.notice_ids = notice_id
        else:
            self.for_mapping_suite = True
            self.notice_ids = self._read_output_notice_ids()

    def _notice_output_report_folder(self, notice_id) -> Path:
        return self.output_path / notice_id / DEFAULT_TEST_SUITE_REPORT_FOLDER

    def generate_notice(self, resource) -> Notice:
        """

        :return:
        """
        notice_id = resource.stem
        report_folder = self._notice_output_report_folder(notice_id)
        shacl_validations = self._read_report(report_folder, JSON_SHACL_REPORT)
        sparql_validations = self._read_report(report_folder, JSON_SPARQL_REPORT)
        xpath_coverage_validation = self._read_report(report_folder, XPATH_COV_REPORT)
        notice = Notice(ted_id=notice_id)
        notice.set_xml_manifestation(XMLManifestation(object_data=""))

        rdf_manifestation: RDFManifestation = RDFManifestation(object_data="")
        for validation in shacl_validations:
            rdf_manifestation.add_validation(SHACLTestSuiteValidationReport(**validation))
        for validation in sparql_validations:
            rdf_manifestation.add_validation(SPARQLTestSuiteValidationReport(**validation))
        notice._rdf_manifestation = rdf_manifestation
        notice._distilled_rdf_manifestation = rdf_manifestation

        notice.xml_manifestation.xpath_coverage_validation = XPATHCoverageValidationReport(
            **xpath_coverage_validation
        )

        return notice

    @classmethod
    def save_json_report(cls, output_path, json_report: dict):
        output_path /= (REPORT_FILE + ".json")
        with open(output_path, "w+") as f:
            json.dump(json_report, f, indent=4)
            f.close()

    @classmethod
    def save_html_report(cls, output_path, html_report: str):
        output_path /= (REPORT_FILE + ".html")
        with open(output_path, "w+") as f:
            f.write(html_report)
            f.close()

    def validation_summary(self):
        self._generate_reports()

    @classmethod
    def _read_report(cls, report_folder: Path, report_file: str) -> Dict:
        return json.load((report_folder / report_file).open())

    def _read_output_notice_ids(self) -> List[str]:
        """
        """
        notice_ids: List[str] = []

        for resource in self.output_path.iterdir():
            if resource.is_dir():
                notice_id = resource.stem
                notice_ids.append(notice_id)

        return notice_ids

    def _generate_report(self, notices: List[Notice], label: str, output_path: Path):
        self.log("Generating validation summary report for {label} ... ".format(label=label))

        report: ValidationSummaryReport = generate_validation_summary_report_notices(notices, with_html=self.with_html)

        self.save_html_report(output_path, report.object_data)
        del report.object_data
        self.save_json_report(output_path, report.dict())

    def _generate_reports(self):
        """
        """

        for notice_id in self.notice_ids:
            notice_path = self.output_path / notice_id
            notice = self.generate_notice(notice_path)
            if self.for_mapping_suite or self.notice_aggregate:
                self.notices.append(notice)
            if not self.for_mapping_suite or self.notice_aggregate:
                self._generate_report([notice], "Notice(" + notice.ted_id + ")",
                                      self._notice_output_report_folder(notice.ted_id))

        if self.notices and len(self.notices) > 0:
            self._generate_report(self.notices, "MappingSuite(" + self.mapping_suite_id + ")", self.output_path)

    def run_cmd(self):
        self.validation_summary()
        return self.run_cmd_result()


def run(mapping_suite_id=None, notice_id=None, notice_aggregate=True, opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_id=notice_id,
        notice_aggregate=notice_aggregate,
        mappings_path=opt_mappings_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=True)
@click.option('--notice-id', required=False, multiple=True, default=None)
@click.option('--notice-aggregate', required=False, default=True, type=click.BOOL)
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, notice_id, notice_aggregate, opt_mappings_folder):
    """
    Generates Validation Summary for Notices
    """
    run(mapping_suite_id, notice_id, notice_aggregate, opt_mappings_folder)


if __name__ == '__main__':
    main()
