import click
from pathlib import Path

from ted_sws.rdf_component_detector.services.detect_graph_component import detect_graph_components
from ted_sws.core.adapters.cmd_runner import CmdRunner as BaseCmdRunner

CMD_NAME = "CMD_RDF_COMPONENT_DETECTOR"

"""
USAGE:
# component_detector --help
"""


class CmdRunner(BaseCmdRunner):

    def __init__(self, rdf_file: str, output_file: str = None):
        super().__init__(name=CMD_NAME)
        self.rdf_file: Path = Path(rdf_file)
        self.output_file: Path = Path(output_file) if output_file else None

    def run_cmd(self):
        self.log(f"Detecting nr of components for {self.rdf_file.name}")
        error = None
        try:
            result = detect_graph_components(self.rdf_file)
            if self.output_file:
                with open(self.output_file, "w+") as file:
                    file.write(result)
                self.log(f"Report is writen in {self.output_file}.")
            else:
                self.log(result)
        except Exception as e:
            error = e

        return self.run_cmd_result(error)


@click.command()
@click.argument('rdf-file', required=True)
@click.argument('output-file', required=False)
def main(rdf_file, output_file):
    """
    Given RDF file, detects number of components in graph.
    :param output_file: Output file to store results.
    :param rdf_file: Path to rdf file.
    """
    cmd = CmdRunner(
        rdf_file=rdf_file,
        output_file=output_file
    )
    cmd.run()


if __name__ == '__main__':
    main()
