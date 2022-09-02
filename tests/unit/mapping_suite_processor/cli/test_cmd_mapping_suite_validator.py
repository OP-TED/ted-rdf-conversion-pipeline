from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_mapping_suite_validator import main as cli_main
from tests import TEST_DATA_PATH


def test_mapping_suite_validator(cli_runner, mapping_suite_id):
    response = cli_runner.invoke(cli_main, [mapping_suite_id, "--opt-mappings-folder",
                                            TEST_DATA_PATH])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output


