from ted_sws.notice_publisher_triple_store.services.load_transformed_notice_into_triple_store import \
    load_notice_into_triple_store


def test_load_notice_into_triple_store(transformed_notice, allegro_triple_store):
    ted_id = transformed_notice.ted_id
    print(ted_id)
    # repository_name = "notice"
    #
    #
    # load_notice_into_triple_store(notice_id="asdsad")
    #
    # assert repository_name in allegro_triple_store.list_repositories()
