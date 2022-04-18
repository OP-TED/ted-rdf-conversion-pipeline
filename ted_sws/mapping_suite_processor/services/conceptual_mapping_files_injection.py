import pathlib
import shutil
import pandas as pd

CONCEPTUAL_MAPPINGS_RESOURCES_SHEET_NAME = "Resources"
FILE_NAME_KEY = "File name"


def mapping_suite_processor_inject_resources(conceptual_mappings_file_path: pathlib.Path,
                                             resources_folder_path: pathlib.Path,
                                             output_resources_folder_path: pathlib.Path
                                             ):
    """
        This function reads the resource names from conceptual_mappings_file_path,
         and then based on the list of resource names,
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


def mapping_suite_processor_inject_shacl_shapes(shacl_shape_file_path: pathlib.Path,
                                                output_resources_folder_path: pathlib.Path):
    """
        This function copies a shacl_shape file to the desired directory.
    :param conceptual_mappings_file_path:
    :param shacl_shape_file_path:
    :param output_resources_folder_path:
    :return:
    """
    dest_shacl_shape_file_path = output_resources_folder_path / shacl_shape_file_path.name
    shutil.copy(shacl_shape_file_path, dest_shacl_shape_file_path)
