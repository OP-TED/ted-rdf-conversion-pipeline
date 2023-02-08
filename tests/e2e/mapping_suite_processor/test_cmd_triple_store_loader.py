from ted_sws.workbench_tools.mapping_suite_processor.entrypoints.cli.cmd_triple_store_loader import main as cli_main
from ted_sws.mapping_suite_processor.services.load_mapping_suite_output_into_triple_store import repository_exists


def test_triple_store_loader(cli_runner, fake_mapping_suite_id, file_system_repository_path, fuseki_triple_store):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    assert fake_mapping_suite_id in fuseki_triple_store.list_repositories()
    assert fuseki_triple_store.list_repositories()
    fuseki_triple_store.delete_repository(repository_name=fake_mapping_suite_id)
    assert not repository_exists(triple_store=fuseki_triple_store, repository_name=fake_mapping_suite_id)


def test_triple_store_loader_with_invalid_input(cli_runner, file_system_repository_path):
    response = cli_runner.invoke(cli_main, ["invalid-mapping-suite-id",
                                            "--opt-mappings-folder", file_system_repository_path
                                            ])
    assert "FAILED" in response.output
