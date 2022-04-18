import pathlib

from ted_sws.data_manager.adapters.mapping_suite_repository import TRANSFORM_PACKAGE_NAME, VALIDATE_PACKAGE_NAME, \
    SPARQL_PACKAGE_NAME, METADATA_FILE_NAME, RESOURCES_PACKAGE_NAME, SHACL_PACKAGE_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_files_injection import \
    mapping_suite_processor_inject_resources, mapping_suite_processor_inject_shacl_shapes
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_metadata import \
    mapping_suite_processor_generate_metadata
from ted_sws.mapping_suite_processor.services.conceptual_mapping_generate_sparql_queries import \
    mapping_suite_processor_generate_sparql_queries
from ted_sws.resources import RESOURCES_PATH

CONCEPTUAL_MAPPINGS_FILE_NAME = "conceptual_mappings.xlsx"
CONCEPTUAL_MAPPINGS_ASSERTIONS = "cm_assertions"
SHACL_SHAPE_INJECTION_FOLDER = "ap_data_shape"
SHACL_SHAPE_RESOURCES_FOLDER = "shacl_shapes"
SHACL_SHAPE_FILE_NAME = "ePO_shacl_shapes.rdf"
MAPPING_FILES_RESOURCES_FOLDER = "mapping_files"


def mapping_suite_processor_expand_package(mapping_suite_package_path: pathlib.Path):
    """
        This function reads data from conceptual_mappings.xlsx and expand provided package.
    :param mapping_suite_package_path:
    :return:
    """
    conceptual_mappings_file_path = mapping_suite_package_path / TRANSFORM_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_FILE_NAME
    cm_sparql_folder_path = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SPARQL_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_ASSERTIONS
    metadata_file_path = mapping_suite_package_path / METADATA_FILE_NAME
    resources_folder_path = mapping_suite_package_path / TRANSFORM_PACKAGE_NAME / RESOURCES_PACKAGE_NAME
    mapping_files_resources_folder_path = RESOURCES_PATH / MAPPING_FILES_RESOURCES_FOLDER
    shacl_shape_file_path = RESOURCES_PATH / SHACL_SHAPE_RESOURCES_FOLDER / SHACL_SHAPE_FILE_NAME
    shacl_shape_injection_folder = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SHACL_PACKAGE_NAME / SHACL_SHAPE_INJECTION_FOLDER
    shacl_shape_injection_folder.mkdir(parents=True, exist_ok=True)
    cm_sparql_folder_path.mkdir(parents=True, exist_ok=True)
    resources_folder_path.mkdir(parents=True, exist_ok=True)

    mapping_suite_processor_generate_sparql_queries(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                                    output_sparql_queries_folder_path=cm_sparql_folder_path
                                                    )

    mapping_suite_processor_generate_metadata(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                              output_metadata_file_path=metadata_file_path
                                              )

    mapping_suite_processor_inject_resources(conceptual_mappings_file_path=conceptual_mappings_file_path,
                                             resources_folder_path=mapping_files_resources_folder_path,
                                             output_resources_folder_path=resources_folder_path
                                             )

    mapping_suite_processor_inject_shacl_shapes(shacl_shape_file_path=shacl_shape_file_path,
                                                output_resources_folder_path = shacl_shape_injection_folder
                                                )
