import tempfile
from pathlib import Path

from ted_sws.rdf_component_detector.services.detect_graph_component import detect_graph_components
from ted_sws.rdf_component_detector.entrypoints.cli.cmd_rdf_component_detector import main as cli_main


def test_rdf_component_detector(fully_connected_graph_file_path, not_connected_graph_file_path, cli_runner):
    result = detect_graph_components(fully_connected_graph_file_path)
    assert "is fully connected" in result
    result = detect_graph_components(not_connected_graph_file_path)
    assert "is not fully connected." in result

    with tempfile.TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        response = cli_runner.invoke(cli_main, [str(fully_connected_graph_file_path)])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "is fully connected" in response.output

        output_file = temp_folder_path / "rdf_component_report.txt"
        response = cli_runner.invoke(cli_main, [str(not_connected_graph_file_path),
                                                str(output_file)])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert "is not fully connected" not in response.output
        assert output_file.is_file()
        assert "is not fully connected" in output_file.read_text()

        response = cli_runner.invoke(cli_main, ["invalid_file.ttl"])
        assert response.exit_code == 0
        assert "FAILED" in response.output
