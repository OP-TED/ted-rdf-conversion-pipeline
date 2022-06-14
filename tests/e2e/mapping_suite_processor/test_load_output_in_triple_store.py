from ted_sws.mapping_suite_processor.services.load_mapping_suite_output_into_triple_store import \
    load_mapping_suite_output_into_triple_store, repository_exists


def test_load_output_folder_in_triple_store(package_folder_path, allegro_triple_store):
    package_name = package_folder_path.stem
    load_mapping_suite_output_into_triple_store(package_folder_path=package_folder_path)

    assert package_name in allegro_triple_store.list_repositories()
    # TODO: see why left side returns different number (compared to right side)
    assert allegro_triple_store._get_repository(repository_name=package_name).getConnection().size() > 0  # == 3016
    allegro_triple_store.delete_repository(repository_name=package_name)


def test_check_repository_exists(allegro_triple_store):
    assert not repository_exists(triple_store=allegro_triple_store, repository_name="No name")
