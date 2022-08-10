"""
    This module implements functionality to load a given notice into a triple store.
"""
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.data_manager.adapters.triple_store import TripleStoreEndpointABC, RDF_MIME_TYPES

DEFAULT_NOTICE_REPOSITORY_NAME = "notices"


def load_notice_into_triple_store(notice_id: str, notice_repository: NoticeRepositoryABC,
                                  triple_store_repository: TripleStoreEndpointABC,
                                  repository_name: str = DEFAULT_NOTICE_REPOSITORY_NAME):
    """

    """
    notice = notice_repository.get(reference=notice_id)
    if notice is None:
        raise ValueError('Notice, with "%s" notice_id, was not found' % notice_id)
    mime_type = RDF_MIME_TYPES
    rdf_manifestation_string = notice.rdf_manifestation.object_data
    triple_store_repository.add_data_to_repository(file_content=rdf_manifestation_string, repository_name=repository_name, mime_type=mime_type)
