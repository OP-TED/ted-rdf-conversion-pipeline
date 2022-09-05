from ted_sws.data_manager.adapters.mapping_suite_repository import MS_TRANSFORM_FOLDER_NAME
from ted_sws.mapping_suite_processor.services.conceptual_mapping_reader import CONCEPTUAL_MAPPINGS_FILE_NAME

CONCEPTUAL_MAPPINGS_FILE_TEMPLATE = '{mappings_path}/{mapping_suite_id}/' + MS_TRANSFORM_FOLDER_NAME + '/' \
                                    + CONCEPTUAL_MAPPINGS_FILE_NAME
MAPPING_SUITE_FILE_TEMPLATE = '{mappings_path}/{mapping_suite_id}'
