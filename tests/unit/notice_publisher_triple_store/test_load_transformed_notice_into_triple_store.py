from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store


def test_load_notice_into_triple_store( allegro_triple_store):
    repository_name = "notice"


    load_notice_into_triple_store(notice_id="asdsad")

    assert repository_name in allegro_triple_store.list_repositories()
