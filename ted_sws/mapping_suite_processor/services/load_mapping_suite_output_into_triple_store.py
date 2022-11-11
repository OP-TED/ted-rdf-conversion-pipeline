import pathlib

from ted_sws import config
from ted_sws.data_manager.adapters.triple_store import AllegroGraphTripleStore, FusekiAdapter, TripleStoreABC


def repository_exists(triple_store: TripleStoreABC, repository_name) -> bool:
    """
    Method to check if the repository is in the triple store
    :param triple_store:
    :param repository_name:
    :return:
    """
    return repository_name in triple_store.list_repositories()


def load_mapping_suite_output_into_fuseki_triple_store(package_folder_path,
                                                       triple_store_host: str = None,
                                                       triple_store_user: str = None,
                                                       triple_store_password: str = None,
                                                       ):
    """
    Method to create a repository in the Fuseki triple store and load all ttl files from the output folder of a mapping suite
    package. Name of the repository will be auto-generated from the folder name.
    :param package_folder_path:
    :param triple_store_host:
    :param triple_store_user:
    :param triple_store_password:
    :return:
    """

    triple_store = FusekiAdapter(host=triple_store_host or config.FUSEKI_ADMIN_HOST,
                                 password=triple_store_password or config.FUSEKI_ADMIN_PASSWORD,
                                 user=triple_store_user or config.FUSEKI_ADMIN_USER)
    load_mapping_suite_output_into_triple_store(package_folder_path, triple_store)


def load_mapping_suite_output_into_triple_store(package_folder_path,
                                                triple_store: TripleStoreABC
                                                ):
    """
    Method to create a repository in the triple store and load all ttl files from the output folder of a mapping suite
    package. Name of the repository will be auto-generated from the folder name.
    :param package_folder_path:
    :param triple_store:
    :return:
    """
    package_folder_path = pathlib.Path(package_folder_path)
    metadata_file = package_folder_path / "metadata.json"
    assert metadata_file.exists()
    package_name = package_folder_path.stem

    ttl_files_paths = [path for path in package_folder_path.glob("output/**/*.ttl")]

    if repository_exists(triple_store=triple_store, repository_name=package_name):
        triple_store.delete_repository(repository_name=package_name)

    triple_store.create_repository(repository_name=package_name)
    for ttl_file_path in ttl_files_paths:
        triple_store.add_file_to_repository(file_path=ttl_file_path, repository_name=package_name)
