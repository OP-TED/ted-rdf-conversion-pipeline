import pathlib
import shutil

import pandas as pd

CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME = "Resources"
CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME = "RML_Modules"
FILE_NAME_KEY = "File name"


def mapping_suite_processor_inject_resources(conceptual_mappings_file_path: pathlib.Path,
                                             resources_folder_path: pathlib.Path,
                                             output_resources_folder_path: pathlib.Path
                                             ):
    """
        This function reads the resource names from conceptual_mappings_file_path,
         and then, based on the list of resource names,
          the resources in resources_folder_path will be copied to output_resource_folder_path.
    :param conceptual_mappings_file_path:
    :param resources_folder_path:
    :param output_resources_folder_path:
    :return:
    """
    resources_df = pd.read_excel(conceptual_mappings_file_path,
                                 sheet_name=CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME)
    resource_file_names = list(resources_df[FILE_NAME_KEY].values)
    for resource_file_name in resource_file_names:
        src_resource_file_path = resources_folder_path / resource_file_name
        dest_resource_file_path = output_resources_folder_path / resource_file_name
        shutil.copy(src_resource_file_path, dest_resource_file_path)


def mapping_suite_processor_inject_rml_modules(conceptual_mappings_file_path: pathlib.Path,
                                               rml_modules_folder_path: pathlib.Path,
                                               output_rml_modules_folder_path: pathlib.Path
                                               ):
    """
        This function reads the RML Modules from conceptual_mappings_file_path, and then, based on this list,
          the resources in rml_modules_folder_path will be copied to output_rml_modules_folder_path.
    :param conceptual_mappings_file_path:
    :param rml_modules_folder_path:
    :param output_rml_modules_folder_path:
    :return:
    """
    rml_modules_df = pd.read_excel(conceptual_mappings_file_path,
                                   sheet_name=CONCEPTUAL_MAPPINGS_RML_MODULES_SHEET_NAME)
    rml_module_file_names = list(rml_modules_df[FILE_NAME_KEY].values)
    for rml_module_file_name in rml_module_file_names:
        src_rml_module_file_path = rml_modules_folder_path / rml_module_file_name
        dest_rml_module_file_path = output_rml_modules_folder_path / rml_module_file_name
        shutil.copy(src_rml_module_file_path, dest_rml_module_file_path)


def mapping_suite_processor_inject_shacl_shapes(shacl_shape_file_path: pathlib.Path,
                                                output_shacl_shape_folder_path: pathlib.Path):
    """
        This function copies a shacl_shape file to the desired directory.
    :param shacl_shape_file_path:
    :param output_shacl_shape_folder_path:
    :return:
    """
    dest_shacl_shape_file_path = output_shacl_shape_folder_path / shacl_shape_file_path.name
    shutil.copy(shacl_shape_file_path, dest_shacl_shape_file_path)


def mapping_suite_processor_inject_sparql_queries(sparql_queries_folder_path: pathlib.Path,
                                                  output_sparql_queries_folder_path: pathlib.Path
                                                  ):
    """
       This function copies SPARQL queries from the source folder to the destination folder.
    :param sparql_queries_folder_path:
    :param output_sparql_queries_folder_path:
    :return:
    """
    shutil.copytree(sparql_queries_folder_path, output_sparql_queries_folder_path)
