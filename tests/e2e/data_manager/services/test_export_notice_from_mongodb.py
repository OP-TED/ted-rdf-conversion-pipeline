import tempfile
from pathlib import Path

from ted_sws import config
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.services.export_notice_from_mongodb import export_notice_by_id
from ted_sws.data_manager.entrypoints.cli.cmd_export_notices_from_mongodb import main as cli_main, run as cli_run


def test_export_notices_from_mongodb(caplog, cli_runner, packaged_notice, fake_mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(packaged_notice)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        tmp_folder_arg = str(tmp_dirname)
        invalid_notice_id = "invalid_notice_id"
        save_to_path = str(Path(tmp_dirname) / packaged_notice.ted_id)
        is_saved, saved_path = export_notice_by_id(notice_id=packaged_notice.ted_id,
                                                   output_folder=tmp_dirname,
                                                   mongodb_client=fake_mongodb_client)
        assert is_saved
        assert saved_path == save_to_path

        is_saved, saved_path = export_notice_by_id(notice_id=invalid_notice_id,
                                                   output_folder=tmp_dirname)
        assert not is_saved

        response = cli_runner.invoke(cli_main,
                                     ["--notice-id", invalid_notice_id, "--output-folder", tmp_folder_arg])
        assert response.exit_code == 0
        assert f"{invalid_notice_id} is not saved" in response.output

        cli_run(notice_id=[packaged_notice.ted_id], output_folder=tmp_folder_arg, mongodb_client=fake_mongodb_client)
        assert packaged_notice.ted_id in caplog.text
        assert "saved in " + save_to_path in caplog.text

        cli_run(notice_id=[], output_folder=tmp_folder_arg, mongodb_client=fake_mongodb_client)
        assert "List with notices is empty." in caplog.text

        response = cli_runner.invoke(cli_main,
                                     ["--notice-id", invalid_notice_id, "--output-folder", tmp_folder_arg,
                                      "--mongodb-auth-url", config.MONGO_DB_AUTH_URL])
        assert response.exit_code == 0
        assert f"{invalid_notice_id} is not saved" in response.output
