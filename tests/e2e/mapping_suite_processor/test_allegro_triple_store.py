

def test_allegro_allegro_triple_store(ttl_file, path_ttl_file, allegro_triple_store):
    allegro_triple_store.create_repository(repository_name="testing")
    assert isinstance(allegro_triple_store.list_repositories(), list)
    assert "testing" in allegro_triple_store.list_repositories()
    allegro_triple_store.add_data_to_repository(file_content=ttl_file, repository_name="testing")
    allegro_triple_store.add_file_to_repository(file_path=path_ttl_file, repository_name="testing")
    assert allegro_triple_store._get_repository(repository_name="testing").getConnection().size() == 484
    allegro_triple_store.delete_repository(repository_name="testing")
    assert "testing" not in allegro_triple_store.list_repositories()
