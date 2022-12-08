import os
import shutil
import tempfile
from pathlib import Path

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_packager.entrypoints.cli.cmd_bulk_packager import main as cli_main, run as cli_run


def test_bulk_packager(cli_runner, rdf_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        temp_rdfs_path = temp_folder_path / "rdfs"
        shutil.copytree(rdf_files_path, temp_rdfs_path, dirs_exist_ok=True)
        mets_packages_path = temp_folder_path / "mets"

        pkgs_count = 3
        response = cli_runner.invoke(cli_main,
                                     [str(temp_rdfs_path), str(pkgs_count), "--output-folder", str(mets_packages_path)])
        assert response.exit_code == 0
        assert "SUCCESS" in response.output
        assert os.path.exists(mets_packages_path)


def test_bulk_packager_with_notice_id(caplog, mongodb_client, transformed_complete_notice):
    notice = transformed_complete_notice
    notice._distilled_rdf_manifestation = notice._rdf_manifestation
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_folder_path = Path(temp_folder)
        mets_packages_path = temp_folder_path / "mets"

        notice_repository = NoticeRepository(mongodb_client=mongodb_client)
        notice_repository.add(notice)

        cli_run(
            output_folder=mets_packages_path,
            notice_id=[notice.ted_id],
            mongodb_client=mongodb_client
        )
        assert notice.ted_id in caplog.text
        assert "SUCCESS" in caplog.text


def test_bulk_packager_with_non_existing_input(cli_runner, non_existing_rdf_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        mets_packages_path = Path(temp_folder) / "mets"
        response = cli_runner.invoke(cli_main,
                                     [str(non_existing_rdf_files_path), "--output-folder", str(mets_packages_path)])

        assert "No such folder" in response.output


def test_bulk_packager_with_invalid_input(cli_runner, invalid_rdf_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        mets_packages_path = Path(temp_folder) / "mets"
        response = cli_runner.invoke(cli_main,
                                     [str(invalid_rdf_files_path), "--output-folder", str(mets_packages_path)])

        assert "FAILED" in response.output
