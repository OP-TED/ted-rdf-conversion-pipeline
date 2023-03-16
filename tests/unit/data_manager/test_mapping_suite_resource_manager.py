from pathlib import Path

from ted_sws.data_manager.services.mapping_suite_resource_manager import mapping_suite_notices_grouped_by_path, \
    mapping_suite_files_grouped_by_path, read_flat_file_resources


def test_mapping_suite_notices_grouped_by_path(fake_mapping_suite):
    grouped_notices = mapping_suite_notices_grouped_by_path(
        mapping_suite=fake_mapping_suite
    )
    assert len(grouped_notices) == 1
    grouped_notices = mapping_suite_notices_grouped_by_path(
        mapping_suite=fake_mapping_suite,
        notice_ids=['include-notice']
    )
    assert len(grouped_notices) == 0


def test_mapping_suite_files_grouped_by_path(file_system_package_test_data_path):
    file_resources = read_flat_file_resources(path=file_system_package_test_data_path)
    grouped_files = mapping_suite_files_grouped_by_path(file_resources)
    assert len(grouped_files) == 1
    assert len(grouped_files[Path("batch_N1")]) == 1
