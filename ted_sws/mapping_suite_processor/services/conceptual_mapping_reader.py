from pathlib import Path
from typing import Dict, Union, List

import numpy as np
import pandas as pd

from ted_sws.core.model.transform import ConceptualMapping, ConceptualMappingXPATH, ConceptualMappingMetadata, \
    ConceptualMappingResource, ConceptualMappingMetadataConstraints, ConceptualMappingRule, ConceptualMappingRMLModule, \
    ConceptualMappingRemark, ConceptualMappingControlledList
from ted_sws.mapping_suite_processor import CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME, \
    CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME, RULES_FIELD_XPATH, RULES_SF_FIELD_ID, RULES_SF_FIELD_NAME, \
    CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME, CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME, RULES_E_FORM_BT_ID, \
    RULES_E_FORM_BT_NAME, RULES_FIELD_XPATH_CONDITION, CONCEPTUAL_MAPPINGS_REMARKS_SHEET_NAME, \
    CONCEPTUAL_MAPPINGS_CL2_ORGANISATIONS_SHEET_NAME, CONCEPTUAL_MAPPINGS_CL1_ROLES_SHEET_NAME, CL_MAPPING_REFERENCE, \
    CL_SUPERTYPE, CL_FIELD_VALUE, CL_XML_PATH_FRAGMENT
from ted_sws.mapping_suite_processor.services.conceptual_mapping_files_injection import FILE_NAME_KEY
from ted_sws.notice_validator import BASE_XPATH_FIELD

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

RULES_CLASS_PATH = 'Class path (M)'
RULES_PROPERTY_PATH = 'Property path (M)'


def _read_pd_value(value, default=""):
    if pd.isna(value):
        return default
    return value


def _read_list_from_pd_value(value) -> list:
    if value and pd.notna(value):
        return [x.strip() for x in str(value).split(',')]
    return []


def _read_list_from_pd_multiline_value(value: str) -> list:
    if value and pd.notna(value):
        return [x.strip() for x in str(value).split('\n')]
    return []


def _df_to_dict(df: pd.DataFrame, key: str) -> dict:
    return df.copy().set_index(key).T.to_dict('list')


def _df_to_list(df: pd.DataFrame) -> list:
    return df.copy().tolist()


def mapping_suite_read_metadata(conceptual_mappings_file_path: Path) -> Dict:
    """
    This feature allows you to read the conceptual mapping metadata.
    :param conceptual_mappings_file_path:
    :return:
    """
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        metadata_df = pd.read_excel(excel_file, sheet_name=CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME)
        metadata = _df_to_dict(metadata_df, 'Field')

    return metadata


def _read_conceptual_mapping_metadata(df: pd.DataFrame) -> ConceptualMappingMetadata:
    """
    :param df:
    :return:
    """

    raw_metadata = _df_to_dict(df, 'Field')

    metadata: ConceptualMappingMetadata = ConceptualMappingMetadata()

    metadata.identifier = _read_pd_value(raw_metadata[IDENTIFIER_FIELD][0])
    metadata.title = _read_pd_value(raw_metadata[TITLE_FIELD][0])
    metadata.description = _read_pd_value(raw_metadata[DESCRIPTION_FIELD][0])
    metadata.mapping_version = _read_pd_value(raw_metadata[VERSION_FIELD][0])
    metadata.epo_version = _read_pd_value(raw_metadata[EPO_VERSION_FIELD][0])
    metadata.base_xpath = _read_pd_value(raw_metadata[BASE_XPATH_FIELD][0])

    metadata_constraints: ConceptualMappingMetadataConstraints = ConceptualMappingMetadataConstraints()
    metadata_constraints.eforms_subtype = _read_list_from_pd_value(raw_metadata[E_FORMS_SUBTYPE_FIELD][0])
    metadata_constraints.start_date = str(_read_pd_value(raw_metadata[START_DATE_FIELD][0]))
    metadata_constraints.end_date = str(_read_pd_value(raw_metadata[END_DATE_FIELD][0]))
    metadata_constraints.min_xsd_version = _read_pd_value(raw_metadata[MIN_XSD_VERSION_FIELD][0])
    metadata_constraints.max_xsd_version = _read_pd_value(raw_metadata[MAX_XSD_VERSION_FIELD][0])
    metadata.metadata_constraints = metadata_constraints

    return metadata


def _read_conceptual_mapping_rules(df: pd.DataFrame) -> List[ConceptualMappingRule]:
    """

    :param df:
    :return:
    """

    df.columns = df.iloc[0]
    rules_df = df[1:].copy()
    rules_df[RULES_SF_FIELD_ID].ffill(axis="index", inplace=True)
    rules_df[RULES_SF_FIELD_NAME].ffill(axis="index", inplace=True)

    rules = []
    rule: ConceptualMappingRule
    for idx, row in rules_df.iterrows():
        rule = ConceptualMappingRule()
        rule.standard_form_field_id = _read_pd_value(row[RULES_SF_FIELD_ID])
        rule.standard_form_field_name = _read_pd_value(row[RULES_SF_FIELD_NAME])
        rule.eform_bt_id = _read_pd_value(row[RULES_E_FORM_BT_ID])
        rule.eform_bt_name = _read_pd_value(row[RULES_E_FORM_BT_NAME])
        rule.field_xpath = _read_list_from_pd_multiline_value(row[RULES_FIELD_XPATH])
        rule.field_xpath_condition = _read_list_from_pd_multiline_value(row[RULES_FIELD_XPATH_CONDITION])
        rule.class_path = _read_list_from_pd_multiline_value(row[RULES_CLASS_PATH])
        rule.property_path = _read_list_from_pd_multiline_value(row[RULES_PROPERTY_PATH])
        rules.append(rule)
    return rules


def _read_conceptual_mapping_remarks(df: pd.DataFrame) -> List[ConceptualMappingRemark]:
    """

    :param df:
    :return:
    """

    remarks_df = df[0:].copy()
    remarks = []
    remark: ConceptualMappingRemark
    for idx, row in remarks_df.iterrows():
        remark = ConceptualMappingRemark()
        remark.standard_form_field_id = _read_pd_value(row[RULES_SF_FIELD_ID])
        remark.standard_form_field_name = _read_pd_value(row[RULES_SF_FIELD_NAME])
        remark.field_xpath = _read_list_from_pd_multiline_value(row[RULES_FIELD_XPATH])
        remarks.append(remark)
    return remarks


def _read_conceptual_mapping_resources(df: pd.DataFrame) -> List[ConceptualMappingResource]:
    """

    :param df:
    :return:
    """

    resources = []
    resource: ConceptualMappingResource
    for value in list(df[FILE_NAME_KEY].values):
        resource = ConceptualMappingResource()
        resource.file_name = _read_pd_value(value)
        resources.append(resource)
    return resources


def _read_conceptual_mapping_rml_modules(df: pd.DataFrame) -> List[ConceptualMappingRMLModule]:
    """

    :param df:
    :return:
    """

    rml_modules = []
    rml_module: ConceptualMappingRMLModule
    for value in list(df[FILE_NAME_KEY].values):
        rml_module = ConceptualMappingRMLModule()
        rml_module.file_name = _read_pd_value(value)
        rml_modules.append(rml_module)
    return rml_modules


def _read_conceptual_mapping_controlled_list(df: pd.DataFrame) -> List[ConceptualMappingControlledList]:
    """

    :param df:
    :return:
    """

    df.columns = df.iloc[0]
    controlled_list_df = df[1:].copy()

    controlled_list = []
    item: ConceptualMappingControlledList
    for idx, row in controlled_list_df.iterrows():
        item = ConceptualMappingControlledList()
        item.field_value = _read_pd_value(row[CL_FIELD_VALUE])
        item.mapping_reference = _read_pd_value(row[CL_MAPPING_REFERENCE])
        item.super_type = _read_pd_value(row[CL_SUPERTYPE])
        item.xml_path_fragment = _read_pd_value(row[CL_XML_PATH_FRAGMENT])
        controlled_list.append(item)
    return controlled_list


def _read_conceptual_mapping_xpaths(rules_df: pd.DataFrame, base_xpath: str) -> List[ConceptualMappingXPATH]:
    """

    :param df:
    :param base_xpath:
    :return:
    """

    xpaths = []
    rules_df[RULES_SF_FIELD_ID].ffill(axis="index", inplace=True)
    rules_df[RULES_SF_FIELD_NAME].ffill(axis="index", inplace=True)
    df_xpaths = _df_to_list(rules_df[RULES_FIELD_XPATH])
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

        metadata = _read_conceptual_mapping_metadata(dfs[CONCEPTUAL_MAPPINGS_METADATA_SHEET_NAME])
        conceptual_mapping.metadata = metadata
        conceptual_mapping.rules = _read_conceptual_mapping_rules(dfs[CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME])
        conceptual_mapping.mapping_remarks = _read_conceptual_mapping_remarks(dfs[CONCEPTUAL_MAPPINGS_REMARKS_SHEET_NAME])
        conceptual_mapping.resources = _read_conceptual_mapping_resources(dfs[CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME])
        conceptual_mapping.rml_modules = _read_conceptual_mapping_rml_modules(
            dfs[CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME])
        conceptual_mapping.cl1_roles = _read_conceptual_mapping_controlled_list(
            dfs[CONCEPTUAL_MAPPINGS_CL1_ROLES_SHEET_NAME])
        conceptual_mapping.cl2_organisations = _read_conceptual_mapping_controlled_list(
            dfs[CONCEPTUAL_MAPPINGS_CL2_ORGANISATIONS_SHEET_NAME])
        conceptual_mapping.xpaths = _read_conceptual_mapping_xpaths(
            rules_df=dfs[CONCEPTUAL_MAPPINGS_RULES_SHEET_NAME][1:].copy(),
            base_xpath=metadata.base_xpath
        )

    return conceptual_mapping
