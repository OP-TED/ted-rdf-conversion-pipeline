import pathlib
import tempfile

from ted_sws.alignment_oracle.services.generate_alignment_links import generate_alignment_links
from ted_sws.alignment_oracle.services.limes_configurator import generate_default_limes_config_params


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
        result_links = generate_alignment_links(limes_config_params=limes_config_params, threshold=0.95)
        assert result_links