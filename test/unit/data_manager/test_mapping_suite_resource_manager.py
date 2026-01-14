from pathlib import Path

from src.ted_sws.data_manager.services.mapping_suite_resource_manager import mapping_package_notices_grouped_by_path, \
    mapping_package_files_grouped_by_path, read_flat_file_resources


def test_mapping_package_notices_grouped_by_path(fake_mapping_package):
    grouped_notices = mapping_package_notices_grouped_by_path(
        mapping_package=fake_mapping_package
    )
    assert len(grouped_notices) == 1
    grouped_notices = mapping_package_notices_grouped_by_path(
        mapping_package=fake_mapping_package,
        notice_ids=['include-notice']
    )
    assert len(grouped_notices) == 0


def test_mapping_package_files_grouped_by_path(file_system_package_test_data_path):
    file_resources = read_flat_file_resources(path=file_system_package_test_data_path)
    grouped_files = mapping_package_files_grouped_by_path(file_resources)
    assert len(grouped_files) == 1
    assert len(grouped_files[Path("batch_N1")]) == 1
