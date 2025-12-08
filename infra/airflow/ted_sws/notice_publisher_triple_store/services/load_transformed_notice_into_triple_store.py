"""
    This module implements functionality to load a given notice into a triple store.
"""
from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.data_manager.adapters.triple_store import TripleStoreABC, RDF_MIME_TYPES

DEFAULT_NOTICE_REPOSITORY_NAME = "notices"
DEFAULT_NOTICE_RDF_MANIFESTATION_MIME_TYPE = RDF_MIME_TYPES["turtle"]


def load_rdf_manifestation_into_triple_store(rdf_manifestation: RDFManifestation,
                                             triple_store_repository: TripleStoreABC,
                                             repository_name: str = DEFAULT_NOTICE_REPOSITORY_NAME,
                                             mime_type: str = DEFAULT_NOTICE_RDF_MANIFESTATION_MIME_TYPE
                                             ):
    """
     Method to create a repository in the Fuseki triple store and load rdf manifestation of an transformed complete notice.
     Name of the repository is given by default.
    :param rdf_manifestation:
    :param triple_store_repository:
    :param repository_name:
    :param mime_type:
    :return:
    """
    if not rdf_manifestation or not rdf_manifestation.object_data:
        raise Exception("RDF Manifestation is invalid!")

    rdf_manifestation_string = rdf_manifestation.object_data
    if repository_name not in triple_store_repository.list_repositories():
        triple_store_repository.create_repository(repository_name=repository_name)
    triple_store_repository.add_data_to_repository(file_content=rdf_manifestation_string.encode(encoding='utf-8'),
                                                   repository_name=repository_name, mime_type=mime_type)
