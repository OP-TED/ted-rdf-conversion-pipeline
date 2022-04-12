import pathlib
from typing import Iterator

import pandas as pd

from ted_sws.data_manager.adapters.mapping_suite_repository import TRANSFORM_PACKAGE_NAME, VALIDATE_PACKAGE_NAME, \
    SPARQL_PACKAGE_NAME

CONCEPTUAL_MAPPINGS_FILE_NAME = "conceptual_mappings.xlsx"
CONCEPTUAL_MAPPINGS_ASSERTIONS = "cm_assertions"

def sparql_validation_generator(data: pd.DataFrame) -> Iterator[str]:
    """
        This function generates SPARQL queries based on data in the dataframe.
    :param data:
    :return:
    """
    for index, row in data.iterrows():
        sf_field_id = row['Standard Form Field ID (M)']
        sf_field_name = row['Standard Form Field Name (M)']
        e_form_bt_id = row['eForm BT-ID (O)']
        e_form_bt_name = row['eForm BT Name (O)']
        base_xpath = row['Base XPath (for anchoring) (M)']
        field_xpath = row['Field XPath (M)']
        class_path = row['Class path (M)']
        property_path = row['Property path (M)']
        yield f"#title: {sf_field_id} - {sf_field_name}\n" \
              f"#description: “{sf_field_id} - {sf_field_name}” in SF corresponds to “{e_form_bt_id} {e_form_bt_name}” in eForms. The corresponding XML element is {base_xpath}{field_xpath}. The expected ontology instances are epo: {class_path} .\n" \
              f"ASK WHERE {{ {property_path} }}"


def mapping_suite_processor_generate_sparql_queries(mapping_suite_package_path: pathlib.Path):
    """
        This function reads data from conceptual_mappings.xlsx and generates SPARQL validation queries in provided package.
    :param mapping_suite_package_path:
    :return:
    """
    conceptual_mappings_file_path = mapping_suite_package_path / TRANSFORM_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_FILE_NAME
    with open(conceptual_mappings_file_path, 'rb') as excel_file:
        conceptual_mappings_rules_df = pd.read_excel(excel_file, sheet_name="Rules")
        conceptual_mappings_rules_df.columns = conceptual_mappings_rules_df.iloc[0]
        conceptual_mappings_rules_df = conceptual_mappings_rules_df[1:]
    sparql_queries = sparql_validation_generator(conceptual_mappings_rules_df)
    for index, sparql_query in enumerate(sparql_queries):
        output_file_path = mapping_suite_package_path / VALIDATE_PACKAGE_NAME / SPARQL_PACKAGE_NAME / CONCEPTUAL_MAPPINGS_ASSERTIONS
        output_file_path.mkdir(parents=True, exist_ok=True)
        output_file_path = output_file_path / f"sparql_query_{index}.rq"
        with open(output_file_path, "w") as output_file:
            output_file.write(sparql_query)
