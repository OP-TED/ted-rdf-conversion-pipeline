import pathlib

from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams
from ted_sws.alignment_oracle.services.limes_configurator import generate_xml_config_from_limes_config, \
    generate_default_limes_config_params


def test_alignment_oracle_model():
    limes_config_params = generate_default_limes_config_params(sparql_endpoint="sparql_endpoint",
                                                               result_dir_path=pathlib.Path("."),
                                                               alignment_metric="ADD(Jaccard(x.epo:hasName, y.epo:hasName), Jaccard(x.street, y.street))",
                                                               source_sparql_restrictions=["?x a epo:Organisation"],
                                                               source_sparql_properties=["epo:hasName",
                                                                                         "epo:hasRegisteredAddress/locn:thoroughfare RENAME street"
                                                                                         ],
                                                               target_sparql_restrictions=["?y a epo:Organisation"],
                                                               target_sparql_properties=["epo:hasName",
                                                                                         "epo:hasRegisteredAddress/locn:thoroughfare RENAME street"
                                                                                         ]
                                                               )

    assert limes_config_params
    assert type(limes_config_params) == LimesConfigParams
    limes_xml_config = generate_xml_config_from_limes_config(limes_config_params=limes_config_params)
    assert limes_xml_config
    assert type(limes_xml_config) == str
