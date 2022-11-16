import tempfile
from pathlib import Path

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.services.export_notice_from_mongodb import export_notice_by_id


def test_export_notice_by_id(packaged_notice, fake_mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(packaged_notice)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        is_saved, saved_path = export_notice_by_id(notice_id=packaged_notice.ted_id,
                                                   output_folder=tmp_dirname,
                                                   mongodb_client=fake_mongodb_client)
        assert is_saved
        assert saved_path == str(Path(tmp_dirname) / packaged_notice.ted_id)

        is_saved = export_notice_by_id(notice_id="invalid_notice_id",
                                       output_folder=tmp_dirname)
        assert not is_saved
