import os

from click.testing import CliRunner

from ted_sws.notice_packager.entrypoints.cli.cmd_bulk_packager import main as cli_main

cmdRunner = CliRunner()


def __process_output_dir(mets_packages_path):
    for f in os.listdir(mets_packages_path):
        os.remove(os.path.join(mets_packages_path, f))
    os.rmdir(mets_packages_path)


def test_bulk_packager(rdf_files_path, mets_packages_path):
    pkgs_count = 3
    response = cmdRunner.invoke(cli_main, [str(rdf_files_path), str(mets_packages_path), str(pkgs_count)])
    assert response.exit_code == 0
    assert "SUCCESS" in response.output

    assert os.path.exists(mets_packages_path)
    __process_output_dir(mets_packages_path)


def test_bulk_packager_with_non_existing_input(non_existing_rdf_files_path, mets_packages_path):
    response = cmdRunner.invoke(cli_main, [str(non_existing_rdf_files_path), str(mets_packages_path)])

    assert "No such folder" in response.output


def test_bulk_packager_with_invalid_input(invalid_rdf_files_path, mets_packages_path):
    response = cmdRunner.invoke(cli_main, [str(invalid_rdf_files_path), str(mets_packages_path)])

    assert "FAILED" in response.output
    __process_output_dir(mets_packages_path)
