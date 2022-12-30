from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingMetadata
from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME, \
    MS_CONCEPTUAL_MAPPING_FILE_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_differ import mapping_suite_diff_conceptual_mappings, \
    mapping_suite_diff_files_conceptual_mappings, mapping_suite_diff_repo_conceptual_mappings


def test_mapping_suite_diff_conceptual_mappings():
    mapping1: ConceptualMapping = ConceptualMapping()
    metadata1: ConceptualMappingMetadata = ConceptualMappingMetadata()
    metadata1.base_xpath = "BASE1"
    mapping1.metadata = metadata1
    mapping2: ConceptualMapping = ConceptualMapping()
    metadata2: ConceptualMappingMetadata = ConceptualMappingMetadata()
    metadata2.base_xpath = "BASE2"
    mapping2.metadata = metadata2

    assert mapping_suite_diff_conceptual_mappings([mapping1, mapping2])

    mapping2.metadata = metadata1

    assert not mapping_suite_diff_conceptual_mappings([mapping1, mapping2])['data']['html']


def test_mapping_suite_diff_file_conceptual_mappings(package_folder_path, package_F03_folder_path):
    """"""
    filepath1 = package_folder_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME
    filepath2 = package_F03_folder_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME

    diff = mapping_suite_diff_files_conceptual_mappings([filepath1, filepath2])
    assert diff['metadata']
    assert diff['data']['original']


def test_mapping_suite_diff_repo_conceptual_mappings(github_mapping_suite_id, package_folder_path):
    """"""

    diff = mapping_suite_diff_repo_conceptual_mappings(
        branch_or_tag_name=["main"],
        mapping_suite_id=[github_mapping_suite_id],
    )
    assert not diff['data']['original']

    diff = mapping_suite_diff_repo_conceptual_mappings(
        branch_or_tag_name=["main"],
        mapping_suite_id=[github_mapping_suite_id],
        filepath=package_folder_path / MS_TRANSFORM_FOLDER_NAME / MS_CONCEPTUAL_MAPPING_FILE_NAME
    )
    assert diff['data']['original']

    diff = mapping_suite_diff_repo_conceptual_mappings(
        branch_or_tag_name=["main"],
        mapping_suite_id=[github_mapping_suite_id, "package_F03_test"]
    )
    assert diff['data']['original']
