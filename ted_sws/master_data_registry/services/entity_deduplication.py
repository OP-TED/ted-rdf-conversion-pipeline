from typing import List

from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams
from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links
from ted_sws.core.model.notice import Notice
from ted_sws.data_manager.adapters.triple_store import FusekiAdapter
from ted_sws.master_data_registry.services.rdf_fragment_processor import get_rdf_fragment_by_cet_uri_from_notice, \
    write_rdf_fragments_in_triple_store

MDR_TEMPORARY_FUSEKI_DATASET_NAME = "tmp_mdr_dataset"


def generate_alignment_links_for_rdf_fragments(limes_config_params: LimesConfigParams):
    """

    :param limes_config_params:
    :return:
    """

    alignment_links_raw = generate_alignment_links(limes_config_params=limes_config_params, threshold=0.95)
    print(alignment_links_raw)


def deduplicate_entities_by_cet_uri(notices: List[Notice], cet_uri: str):
    rdf_fragments = []
    for notice in notices:
        rdf_fragments.extend(get_rdf_fragment_by_cet_uri_from_notice(notice=notice, cet_uri=cet_uri))

    write_rdf_fragments_in_triple_store(rdf_fragments=rdf_fragments,
                                        triple_store=FusekiAdapter(),
                                        repository_name=MDR_TEMPORARY_FUSEKI_DATASET_NAME)

    generate_alignment_links_for_rdf_fragments