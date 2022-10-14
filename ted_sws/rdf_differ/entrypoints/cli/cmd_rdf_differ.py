import click
from pathlib import Path
from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner
from ted_sws.event_manager.adapters.log import LOG_INFO_TEXT
from ted_sws.rdf_differ.services.difference_between_rdf_files import generate_rdf_differ_html_report

CMD_NAME = "CMD_RDF_DIFFER"
DEFAULT_REPORT_OUTPUT_FOLDER = "."
DEFAULT_REPORT_FILE_NAME = "rdf_diff_{first_file}_{second_file}.html"

"""
USAGE:
# rdf_differ --help
"""


class CmdRunner(BaseCmdRunner):
    """
    Keeps the logic to be used by RDF Differ
    """

    def __init__(
            self,
            first_file,
            second_file,
            output_folder
    ):
        super().__init__(name=CMD_NAME)
        self.first_file = first_file
        self.second_file = second_file
        self.output_folder = output_folder

    def run_cmd(self):
        self.log("Generating " + LOG_INFO_TEXT.format(self.first_file) + " vs " + LOG_INFO_TEXT.format(
            self.second_file) + " diff ... ")
        error = None
        try:
            report_file_file_name_html = Path(self.output_folder) / (DEFAULT_REPORT_FILE_NAME.format(
                first_file=Path(self.first_file).stem,
                second_file=Path(self.second_file).stem
            ))
            with open(report_file_file_name_html, 'w+') as report_file:
                report_file.write(
                    generate_rdf_differ_html_report(
                        first_rml_file=self.first_file,
                        second_rml_file=self.second_file
                    )
                )
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


def run(first_file: str, second_file: str, output_folder=DEFAULT_REPORT_OUTPUT_FOLDER):
    """
    :param output_folder:
    :param first_file:
    :param second_file:
    :return:
    """

    cmd = CmdRunner(
        first_file=first_file,
        second_file=second_file,
        output_folder=output_folder
    )
    cmd.run()


@click.command()
@click.argument('first-file', required=True)
@click.argument('second-file', required=True)
@click.option('-o', '--output-folder', required=False, default=DEFAULT_REPORT_OUTPUT_FOLDER)
def main(first_file, second_file, output_folder):
    """
    Given two RML files representing turtle-encoded RDF,
    check whether they represent the same graph.
    """
    run(first_file, second_file, output_folder)


if __name__ == '__main__':
    main()
