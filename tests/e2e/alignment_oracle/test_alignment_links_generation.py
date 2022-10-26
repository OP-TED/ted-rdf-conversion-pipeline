import pathlib
import tempfile

from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links, \
    generate_alignment_links_for_notice
from ted_sws.alignment_oracle.services.limes_configurator import generate_default_limes_config_params, \
    generate_organisation_cet_limes_config_params


def test_alignment_links_generation(limes_sparql_endpoint):
    with tempfile.TemporaryDirectory() as tmp_dir_path:
        limes_config_params = generate_default_limes_config_params(source_sparql_endpoint=limes_sparql_endpoint,
                                                                   target_sparql_endpoint=limes_sparql_endpoint,
                                                                   result_dir_path=pathlib.Path(tmp_dir_path),
                                                                   alignment_metric="ADD(Jaccard(x.epo:hasLegalName, y.epo:hasLegalName), Jaccard(x.street, y.street))",
                                                                   source_sparql_restrictions=["?x a org:Organization"],
                                                                   source_sparql_properties=["epo:hasLegalName",
                                                                                             "legal:registeredAddress/locn:thoroughfare RENAME street"
                                                                                             ],
                                                                   target_sparql_restrictions=["?y a org:Organization"],
                                                                   target_sparql_properties=["epo:hasLegalName",
                                                                                             "legal:registeredAddress/locn:thoroughfare RENAME street"
                                                                                             ]
                                                                   )
        result_links = generate_alignment_links(limes_config_params=limes_config_params, threshold=0.95,
                                                use_caching=False)
        assert result_links


def test_generate_alignment_links_for_notice(limes_sparql_endpoint, notice_with_distilled_rdf_manifestation):
    limes_config_generator = generate_organisation_cet_limes_config_params
    result_links = generate_alignment_links_for_notice(notice=notice_with_distilled_rdf_manifestation,
                                                       sparql_endpoint=limes_sparql_endpoint,
                                                       limes_config_generator=limes_config_generator,
                                                       threshold=0.95, use_caching=False
                                                       )

    assert result_links

    result_links = generate_alignment_links_for_notice(notice=notice_with_distilled_rdf_manifestation,
                                                       sparql_endpoint=limes_sparql_endpoint,
                                                       limes_config_generator=limes_config_generator,
                                                       threshold=0.95, use_caching=True
                                                       )

    assert result_links
