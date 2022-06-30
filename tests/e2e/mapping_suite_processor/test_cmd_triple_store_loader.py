from ted_sws.mapping_suite_processor.entrypoints.cli.cmd_triple_store_loader import main as cli_main
from ted_sws.mapping_suite_processor.services.load_mapping_suite_output_into_triple_store import repository_exists


def test_triple_store_loader(cli_runner, fake_mapping_suite_id, file_system_repository_path, allegro_triple_store):
    response = cli_runner.invoke(cli_main,
                                 [fake_mapping_suite_id, "--opt-mappings-folder", file_system_repository_path])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output
    assert fake_mapping_suite_id in allegro_triple_store.list_repositories()
    assert allegro_triple_store._get_repository(repository_name=fake_mapping_suite_id).getConnection().size() > 0
    allegro_triple_store.delete_repository(repository_name=fake_mapping_suite_id)


def test_check_repository_exists(allegro_triple_store, fake_mapping_suite_id):
    assert not repository_exists(triple_store=allegro_triple_store, repository_name=fake_mapping_suite_id)


def test_triple_store_loader_with_invalid_input(cli_runner, file_system_repository_path):
    response = cli_runner.invoke(cli_main, ["invalid-mapping-suite-id",
                                            "--opt-mappings-folder", file_system_repository_path,
                                            "--opt-catalog-name", "CATALOG"])
    assert "FAILED" in response.output
