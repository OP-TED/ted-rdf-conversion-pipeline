"""
    This module implements functionality to load a given notice into a triple store.
"""
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.mapping_suite_processor.adapters.allegro_triple_store import VersatileTripleStoreABC

DEFAULT_NOTICE_REPOSITORY_NAME = "notices"


def load_notice_into_triple_store(notice_id: str, notice_repository: NoticeRepositoryABC,
                                  triple_store: VersatileTripleStoreABC,
                                  repository_name: str = DEFAULT_NOTICE_REPOSITORY_NAME):
    """

    """
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError('Notice, with "%s" notice_id, was not found' % notice_id)

    rdf_manifestation_string = notice.rdf_manifestation.object_data
    triple_store.add_data_to_repository(file_content=rdf_manifestation_string, repository_name=repository_name)
