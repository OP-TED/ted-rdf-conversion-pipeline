import random
import shutil
import tempfile
from pathlib import Path

from ted_sws.mapping_suite_processor.entrypoints.cli import CONCEPTUAL_MAPPINGS_FILE_TEMPLATE
from ted_sws.mapping_suite_processor.services.conceptual_mapping_files_injection import \
    mapping_suite_processor_inject_resources, mapping_suite_processor_inject_shacl_shapes, \
    mapping_suite_processor_inject_sparql_queries, mapping_suite_processor_inject_rml_modules


def test_mapping_suite_processor_inject_resources(fake_mapping_suite_id, file_system_repository_path,
                                                  resources_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        conceptual_mappings_file_path = Path(CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=temp_mapping_suite_path,
            mapping_suite_id=fake_mapping_suite_id
        ))

        output_folder_path = Path(temp_folder) / "_mappings_files"
        output_folder_path.mkdir(exist_ok=True)
        mapping_suite_processor_inject_resources(
            conceptual_mappings_file_path=conceptual_mappings_file_path,
            resources_folder_path=resources_files_path,
            output_resources_folder_path=output_folder_path)

        assert any(output_folder_path.iterdir())


def test_mapping_suite_processor_inject_rml_modules(fake_mapping_suite_id, file_system_repository_path,
                                                    rml_modules_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        conceptual_mappings_file_path = Path(CONCEPTUAL_MAPPINGS_FILE_TEMPLATE.format(
            mappings_path=temp_mapping_suite_path,
            mapping_suite_id=fake_mapping_suite_id
        ))

        output_folder_path = Path(temp_folder) / "_rml_modules"
        output_folder_path.mkdir(exist_ok=True)

        mapping_suite_processor_inject_rml_modules(
            conceptual_mappings_file_path=conceptual_mappings_file_path,
            rml_modules_folder_path=rml_modules_path,
            output_rml_modules_folder_path=output_folder_path)

        assert any(output_folder_path.iterdir())


def test_mapping_suite_processor_inject_shacl_shapes(fake_mapping_suite_id, file_system_repository_path,
                                                     resources_shacl_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        random_file = random.choice([x for x in resources_shacl_files_path.iterdir()])

        output_folder_path = Path(temp_folder) / "_shacl_shapes"
        output_folder_path.mkdir(exist_ok=True)

        mapping_suite_processor_inject_shacl_shapes(
            shacl_shape_file_path=random_file,
            output_shacl_shape_folder_path=output_folder_path)

        assert (output_folder_path / random_file.name).is_file()


def test_mapping_suite_processor_inject_sparql_queries(fake_mapping_suite_id, file_system_repository_path,
                                                       resources_sparql_files_path):
    with tempfile.TemporaryDirectory() as temp_folder:
        temp_mapping_suite_path = Path(temp_folder)
        shutil.copytree(file_system_repository_path, temp_mapping_suite_path, dirs_exist_ok=True)

        output_folder_path = Path(temp_folder) / "_sparql_queries"

        mapping_suite_processor_inject_sparql_queries(
            sparql_queries_folder_path=resources_sparql_files_path,
            output_sparql_queries_folder_path=output_folder_path)

        assert any(output_folder_path.iterdir())
