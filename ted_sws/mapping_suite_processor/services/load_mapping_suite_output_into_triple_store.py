import pathlib

from ted_sws import config
from ted_sws.mapping_suite_processor.adapters.allegro_triple_store import AllegroGraphTripleStore


def repository_exists(triple_store: AllegroGraphTripleStore, repository_name) -> bool:
    """
    Method to check if the repository is in the triple store
    :param triple_store:
    :param repository_name:
    :return:
    """
    return True if repository_name in triple_store.list_repositories() else False


def load_mapping_suite_output_into_triple_store(package_folder_path, allegro_host=config.ALLEGRO_HOST,
                                                allegro_user=config.AGRAPH_SUPER_USER,
                                                allegro_password=config.AGRAPH_SUPER_PASSWORD,
                                                allegro_catalog_name: str = None):
    """
    Method to create a repository in the triple store and load all ttl files from the output folder of a mapping suite
    package. Name of the repository will be auto-generated from the folder name.
    :param package_folder_path:
    :param allegro_host:
    :param allegro_user:
    :param allegro_password:
    :param allegro_catalog_name:
    :return:
    """
    package_folder_path = pathlib.Path(package_folder_path)
    metadata_file = package_folder_path / "metadata.json"
    assert metadata_file.exists()
    package_name = package_folder_path.stem

    ttl_files_paths = [str(path) for path in package_folder_path.glob("output/**/*.ttl")]

    triple_store = AllegroGraphTripleStore(host=allegro_host, password=allegro_password,
                                           user=allegro_user, catalog_name=allegro_catalog_name)

    if repository_exists(triple_store=triple_store, repository_name=package_name):
        triple_store.delete_repository(repository_name=package_name)

    triple_store.create_repository(repository_name=package_name)
    for ttl_file_path in ttl_files_paths:
        triple_store.add_file_to_repository(file_path=ttl_file_path, repository_name=package_name)
