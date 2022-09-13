from ted_sws.data_manager.services import \
    load_notice_into_triple_store, DEFAULT_NOTICE_REPOSITORY_NAME

def test_validate_mets_package_publication(notice_id_from_celler, notice_uri, cellar_sparql_endpoint):

    check_availability_of_notice_in_celler(notice_id=notice_id_from_celler, notice_uri=notice_uri, cellar_sparql_endpoint=cellar_sparql_endpoint)
    print(a)
