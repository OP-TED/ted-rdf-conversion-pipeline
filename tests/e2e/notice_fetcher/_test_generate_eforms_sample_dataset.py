import pathlib

TED_API_EFORMS_QUERY = """
TD NOT IN (C E G I D P M Q O R 0 1 2 3 4 5 6 7 8 9 B S Y V F A H J K) AND
notice-subtype IN ({eforms_subtype}) AND
FT~"eforms-sdk-{eforms_sdk_version}"
"""

EFORMS_SUBTYPES = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
EFORMS_SDK_VERSIONS = [f"1.{version}" for version in range(3, 11)]


def _test_generate_eforms_sample_dataset(ted_document_search):
    results_path = pathlib.Path(__file__).parent / "eforms_samples"

    for eforms_sdk_version in EFORMS_SDK_VERSIONS:
        for eforms_subtype in EFORMS_SUBTYPES:
            results_dir_path = results_path / f"eforms_sdk_v{eforms_sdk_version}" / f"eform_subtype_{eforms_subtype}"

            print(f"Load for {results_dir_path}")
            query = {"query": TED_API_EFORMS_QUERY.format(eforms_sdk_version=eforms_sdk_version,
                                                          eforms_subtype=eforms_subtype)}
            print(query)
            notices = ted_document_search.get_generator_by_query(query=query)
            for sample_id in range(1, 2):
                notice = next(notices, None)
                if notice is None:
                    break
                results_dir_path.mkdir(parents=True, exist_ok=True)
                result_notice_xml_path = results_dir_path / f"{notice['ND']}.xml"
                result_notice_xml_path.write_text(notice["content"], encoding="utf-8")


def test_fetch_notice_by_id(ted_document_search):
    notice_id = "067623-2022"
    import json
    notice_content = ted_document_search.get_by_id(document_id=notice_id)
    result_notice_path = pathlib.Path(__file__).parent / "epo_notice.xml"
    result_notice_path.write_text(json.dumps(notice_content), encoding="utf-8")

