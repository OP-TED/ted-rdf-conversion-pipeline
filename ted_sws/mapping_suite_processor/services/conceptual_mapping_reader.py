from pathlib import Path
from typing import Dict, Union, List

import numpy as np
import pandas as pd

from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingXPATH, ConceptualMappingMetadata, \
    ConceptualMappingResource, ConceptualMappingMetadataConstraints, ConceptualMappingRule, ConceptualMappingRMLModule
from ted_sws.mapping_suite_processor import CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME, \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH, RULES_SF_FIELD_ID, RULES_SF_FIELD_NAME, \
    CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME, CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME
from ted_sws.notice_validator import BASE_XPATH_FIELD

CONCEPTUAL_MAPPINGS_FILE_NAME = "conceptual_mappings.xlsx"

# This set of constants refers to fields in the Conceptual Mapping file
VERSION_FIELD = 'Mapping Version'
EPO_VERSION_FIELD = 'EPO version'
DESCRIPTION_FIELD = "Description"
TITLE_FIELD = 'Title'
IDENTIFIER_FIELD = 'Identifier'
E_FORMS_SUBTYPE_FIELD = "eForms Subtype"
START_DATE_FIELD = "Start Date"
END_DATE_FIELD = "End Date"
MIN_XSD_VERSION_FIELD = "Min XSD Version"
MAX_XSD_VERSION_FIELD = "Max XSD Version"


def _read_pd_value(value, default=""):
    if pd.isna(value):
        return default
    return value


def _read_list_from_value(value: str) -> list:
    if value and pd.notna(value):
        return [x.strip() for x in str(value).split(',')]
    return []


def mapping_suite_read_metadata(conceptual_mappings_file_path: Path) -> Dict:
    """
    This feature allows you to read the conceptual mapping metadata.
    :param conceptual_mappings_file_path:
    :return:
    """
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
        metadata = metadata_df.set_index('Field').T.to_dict('list')

    return metadata


def _read_conceptual_mapping_metadata(df: pd.DataFrame) -> ConceptualMappingMetadata:
    """
    :param df:
    :return:
    """

    metadata: ConceptualMappingMetadata = ConceptualMappingMetadata()

    metadata.identifier = _read_pd_value(df[IDENTIFIER_FIELD][0])
    metadata.title = _read_pd_value(df[TITLE_FIELD][0])
    metadata.description = _read_pd_value(df[DESCRIPTION_FIELD][0])
    metadata.mapping_version = _read_pd_value(df[VERSION_FIELD][0])
    metadata.epo_version = _read_pd_value(df[EPO_VERSION_FIELD][0])
    metadata.base_xpath = _read_pd_value(df[BASE_XPATH_FIELD][0])

    metadata_constraints: ConceptualMappingMetadataConstraints = ConceptualMappingMetadataConstraints()
    metadata_constraints.eforms_subtype = _read_list_from_value(df[E_FORMS_SUBTYPE_FIELD][0])
    metadata_constraints.start_date = _read_pd_value(df[START_DATE_FIELD][0])
    metadata_constraints.end_date = _read_pd_value(df[END_DATE_FIELD][0])
    metadata_constraints.min_xsd_version = _read_pd_value(df[MIN_XSD_VERSION_FIELD][0])
    metadata_constraints.max_xsd_version = _read_pd_value(df[MAX_XSD_VERSION_FIELD][0])
    metadata.metadata_constraints = metadata_constraints

    return metadata


def _read_conceptual_mapping_rules(df: pd.DataFrame) -> List[ConceptualMappingRule]:
    """

    :param df:
    :return:
    """


def _read_conceptual_mapping_resources(df: pd.DataFrame) -> List[ConceptualMappingResource]:
    """

    :param df:
    :return:
    """


def _read_conceptual_mapping_rml_modules(df: pd.DataFrame) -> List[ConceptualMappingRMLModule]:
    """

    :param df:
    :return:
    """


def _read_conceptual_mapping_xpaths(df: pd.DataFrame) -> ConceptualMappingMetadata:
    """

    :param df:
    :return:
    """

    metadata = mapping_suite_read_metadata(conceptual_mappings_file_path)
    xpaths = []
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        base_xpath = metadata[BASE_XPATH_FIELD][0]
        rules_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, header=1)
        rules_df[RULES_SF_FIELD_ID].ffill(axis="index", inplace=True)
        rules_df[RULES_SF_FIELD_NAME].ffill(axis="index", inplace=True)
        df_xpaths = rules_df[RULES_FIELD_XPATH].tolist()
        df_sform_field_names = rules_df[RULES_SF_FIELD_NAME].tolist()
        df_sform_field_ids = rules_df[RULES_SF_FIELD_ID].tolist()
        processed_xpaths = set()
        for idx, xpath_row in enumerate(df_xpaths):
            if xpath_row is not np.nan:
                row_xpaths = xpath_row.split('\n')
                for xpath in row_xpaths:
                    if xpath:
                        xpath = base_xpath + "/" + xpath
                        if xpath not in processed_xpaths:
                            form_fields = [df_sform_field_ids[idx], df_sform_field_names[idx]]
                            cm_xpath: ConceptualMappingXPATH = ConceptualMappingXPATH(
                                xpath=xpath,
                                form_field=" - ".join([item for item in form_fields if not pd.isnull(item)])
                            )
                            xpaths.append(cm_xpath)
                            processed_xpaths.add(xpath)

    return xpaths


def mapping_suite_read_conceptual_mapping(conceptual_mappings_file_path: Path) -> \
        Union[ConceptualMapping, None]:
    """
        This feature allows you to read the conceptual mapping in a package.
    :param conceptual_mappings_file_path:
    :param metadata:
    :return:
    """

    if not conceptual_mappings_file_path.exists():
        return None

    conceptual_mapping: ConceptualMapping = ConceptualMapping()

    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        dfs = pd.read_excel(excel_file, sheet_name=None)

        conceptual_mapping.metadata = _read_conceptual_mapping_metadata(dfs[CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME])
        conceptual_mapping.rules = _read_conceptual_mapping_rules(dfs[CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME])
        conceptual_mapping.resources = _read_conceptual_mapping_resources(dfs[CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME])
        conceptual_mapping.rml_modules = _read_conceptual_mapping_rml_modules(
            dfs[CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME])
        conceptual_mapping.xpaths = _read_conceptual_mapping_xpaths(conceptual_mappings_file_path)

    return conceptual_mapping
