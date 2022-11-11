#!/usr/bin/python3

import json
from pathlib import Path
from typing import List

import click

from ted_sws.core.adapters.cmd_runner import CmdRunnerForMappingSuite as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.core.model.manifestation import RDFManifestation, XMLManifestation
from ted_sws.core.model.manifestation import XPATHCoverageValidationReport
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.log import LOG_INFO_TEXT
from ted_sws.notice_validator.entrypoints.cli import DEFAULT_RDF_FOLDER
from ted_sws.notice_validator.entrypoints.cli.cmd_xpath_coverage_runner import JSON_REPORT_FILE as XPATH_JSON_FILE, \
    DEFAULT_TEST_SUITE_REPORT_FOLDER
from ted_sws.notice_validator.services.sparql_test_suite_runner import SPARQLTestSuiteRunner, SPARQLReportBuilder, \
    SPARQLTestSuiteValidationReport

JSON_VALIDATIONS_REPORT = "sparql_validations.json"
HTML_REPORT = "sparql_{id}.html"
CMD_NAME = "CMD_SPARQL_RUNNER"

"""
USAGE:
# sparql_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by SPARQL Runner
    """

    def __init__(
            self,
            mapping_suite_id,
            notice_ids: List[str],
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.notice_ids = self._init_list_input_opts(notice_ids)
        self.mappings_path = mappings_path

        repository_path = Path(self.mappings_path)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)

    @classmethod
    def save_report(cls, report_path, report_name, report_id, content):
        if report_id is not None:
            report_name = report_name.format(id=report_id)
        with open(report_path / report_name, "w+") as f:
            f.write(content)

    def validate(self, rdf_file, xpath_report, base_report_path, notice_ids: List[str] = None):
        self.log("Validating " + LOG_INFO_TEXT.format(rdf_file.name) + " ... ")
        rdf_manifestation = RDFManifestation(object_data=rdf_file.read_text(encoding="utf-8"))
        xml_manifestation = None
        if xpath_report:
            xml_manifestation = XMLManifestation(object_data="",
                                                 xpath_coverage_validation=XPATHCoverageValidationReport(
                                                     **xpath_report))

        report_path = base_report_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
        report_path.mkdir(parents=True, exist_ok=True)

        sparql_validations: List[SPARQLTestSuiteValidationReport] = []
        sparql_test_suites = self.mapping_suite.sparql_test_suites
        for sparql_test_suite in sparql_test_suites:
            test_suite_execution = SPARQLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                         xml_manifestation=xml_manifestation,
                                                         sparql_test_suite=sparql_test_suite,
                                                         mapping_suite=self.mapping_suite).execute_test_suite()

            report_builder = SPARQLReportBuilder(sparql_test_suite_execution=test_suite_execution,
                                                 notice_ids=notice_ids, with_html=True)
            report: SPARQLTestSuiteValidationReport = report_builder.generate_report()

            suite_id = sparql_test_suite.identifier
            self.save_report(report_path, HTML_REPORT, suite_id, report.object_data)
            report.object_data = "SPARQLTestSuiteValidationReport"
            sparql_validations.append(report)

        self.save_report(report_path, JSON_VALIDATIONS_REPORT, None,
                         json.dumps(sparql_validations, default=lambda o: o.dict(), sort_keys=True, indent=4))

    def run_cmd(self):
        super().run_cmd()

        error = None
        try:
            rdf_path = Path(DEFAULT_RDF_FOLDER.format(mappings_path=self.mappings_path,
                                                      mapping_suite_id=self.mapping_suite_id))
            for d in rdf_path.iterdir():
                if d.is_dir():
                    notice_id = d.name
                    if self.skip_notice(notice_id):
                        continue
                    base_report_path = rdf_path / notice_id
                    for f in d.iterdir():
                        if f.is_file():
                            xpath_file = f.parent / DEFAULT_TEST_SUITE_REPORT_FOLDER / XPATH_JSON_FILE
                            xpath_report = json.load(open(xpath_file, "r")) if xpath_file.exists() else None
                            self.validate(rdf_file=f, xpath_report=xpath_report, base_report_path=base_report_path,
                                          notice_ids=[notice_id])
        except Exception as e:
            error = e
        return self.run_cmd_result(error)


def run(mapping_suite_id=None, notice_id=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        notice_ids=list(notice_id or []),
        mappings_path=opt_mappings_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('--notice-id', required=False, multiple=True, default=None)
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, notice_id, opt_mappings_folder):
    """
    Generates SPARQL Validation Reports for RDF files
    """
    run(mapping_suite_id, notice_id, opt_mappings_folder)


if __name__ == '__main__':
    main()
