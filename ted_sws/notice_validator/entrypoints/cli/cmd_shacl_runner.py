#!/usr/bin/python3

from pathlib import Path

import click

from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner, DEFAULT_MAPPINGS_PATH
from ted_sws.core.model.manifestation import RDFManifestation, SHACLTestSuiteValidationReport
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryInFileSystem
from ted_sws.event_manager.adapters.logger import LOG_INFO_TEXT
from ted_sws.notice_validator.entrypoints.cli import DEFAULT_RDF_FOLDER, DEFAULT_TEST_SUITE_REPORT_FOLDER
from ted_sws.notice_validator.services.shacl_test_suite_runner import SHACLTestSuiteRunner, generate_shacl_report

HTML_REPORT = "shacl_{id}.html"
CMD_NAME = "CMD_SHACL_RUNNER"

"""
USAGE:
# shacl_runner --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by SHACL Runner
    """

    def __init__(
            self,
            mapping_suite_id,
            mappings_path
    ):
        super().__init__(name=CMD_NAME)
        self.mapping_suite_id = mapping_suite_id
        self.mappings_path = mappings_path

        repository_path = Path(self.mappings_path)
        mapping_suite_repository = MappingSuiteRepositoryInFileSystem(repository_path=repository_path)
        self.mapping_suite = mapping_suite_repository.get(reference=self.mapping_suite_id)

    def save_report(self, report_path, report_name, report_id, content):
        with open(report_path / report_name.format(id=report_id), "w+") as f:
            f.write(content)

    def validate(self, rdf_file, base_report_path):
        self.log("Validating " + LOG_INFO_TEXT.format(rdf_file.name) + " ... ")
        rdf_manifestation = RDFManifestation(object_data=rdf_file.read_text(encoding="utf-8"))

        report_path = base_report_path / DEFAULT_TEST_SUITE_REPORT_FOLDER
        report_path.mkdir(parents=True, exist_ok=True)

        shacl_test_suites = self.mapping_suite.shacl_test_suites
        for shacl_test_suite in shacl_test_suites:
            test_suite_execution = SHACLTestSuiteRunner(rdf_manifestation=rdf_manifestation,
                                                        shacl_test_suite=shacl_test_suite,
                                                        mapping_suite=self.mapping_suite).execute_test_suite()

            report: SHACLTestSuiteValidationReport = generate_shacl_report(
                shacl_test_suite_execution=test_suite_execution)

            suite_id = shacl_test_suite.identifier
            data = report.object_data
            self.save_report(report_path, HTML_REPORT, suite_id, data)

    def run_cmd(self):
        error = None
        try:
            rdf_path = Path(DEFAULT_RDF_FOLDER.format(mappings_path=self.mappings_path,
                                                      mapping_suite_id=self.mapping_suite_id))
            for d in rdf_path.iterdir():
                if d.is_dir():
                    base_report_path = rdf_path / d.name
                    for f in d.iterdir():
                        if f.is_file():
                            self.validate(rdf_file=f, base_report_path=base_report_path)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(mapping_suite_id=None, opt_mappings_folder=DEFAULT_MAPPINGS_PATH):
    cmd = CmdRunner(
        mapping_suite_id=mapping_suite_id,
        mappings_path=opt_mappings_folder
    )
    cmd.run()


@click.command()
@click.argument('mapping-suite-id', nargs=1, required=False)
@click.option('-m', '--opt-mappings-folder', default=DEFAULT_MAPPINGS_PATH)
def main(mapping_suite_id, opt_mappings_folder):
    """
    Generates SHACL Validation Reports for RDF files
    """
    run(mapping_suite_id, opt_mappings_folder)


if __name__ == '__main__':
    main()
