from ted_sws.data_sampler.services.notice_xml_manifestation_indexer import NoticeXMLIndexer


def test_unique_xpaths_from_xml(notice_2016):
    notice_xml_indexer = NoticeXMLIndexer()
    result_notice = notice_xml_indexer.index_notice(notice = notice_2016)
    print(result_notice.xml_metadata.unique_xpaths)