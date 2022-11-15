import tempfile

from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.data_manager.services.export_notice_from_mongodb import export_notice_by_id


def test_export_notice_by_id(transformed_complete_notice, fake_mongodb_client):
    notice_repository = NoticeRepository(mongodb_client=fake_mongodb_client)
    notice_repository.add(transformed_complete_notice)
    with tempfile.TemporaryDirectory() as tmp_dirname:
        is_saved, saved_path = export_notice_by_id(notice_id=transformed_complete_notice.ted_id,
                                                   output_folder=tmp_dirname,
                                                   mongodb_client=fake_mongodb_client)
        assert is_saved
