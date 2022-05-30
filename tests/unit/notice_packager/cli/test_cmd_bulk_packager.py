import os

from ted_sws.notice_packager.entrypoints.cli.cmd_bulk_packager import main as cli_main


def post_process(mets_packages_path):
    for f in os.listdir(mets_packages_path):
        os.remove(os.path.join(mets_packages_path, f))
    os.rmdir(mets_packages_path)


def test_bulk_packager(cli_runner, rdf_files_path, mets_packages_path):
    pkgs_count = 3
    response = cli_runner.invoke(cli_main, [str(rdf_files_path), str(mets_packages_path), str(pkgs_count)])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    assert os.path.exists(mets_packages_path)
    post_process(mets_packages_path)


def test_bulk_packager_with_non_existing_input(cli_runner, non_existing_rdf_files_path, mets_packages_path):
    response = cli_runner.invoke(cli_main, [str(non_existing_rdf_files_path), str(mets_packages_path)])

    assert "No such folder" in response.output


def test_bulk_packager_with_invalid_input(cli_runner, invalid_rdf_files_path, mets_packages_path):
    response = cli_runner.invoke(cli_main, [str(invalid_rdf_files_path), str(mets_packages_path)])

    assert "FAILED" in response.output
    post_process(mets_packages_path)
