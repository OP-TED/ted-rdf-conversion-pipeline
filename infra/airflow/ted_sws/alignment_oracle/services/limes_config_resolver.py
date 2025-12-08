from ted_sws.alignment_oracle.model.limes_config import LimesConfigGenerator
from ted_sws.alignment_oracle.services.limes_configurator import generate_organisation_cet_limes_config_params

LIMES_CONFIGURATORS_MAPPING = {
    "http://www.w3.org/ns/org#Organization": generate_organisation_cet_limes_config_params,

}


def get_limes_config_generator_by_cet_uri(cet_uri: str) -> LimesConfigGenerator:
    """
        This function return concrete LimesConfigGenerator based on concrete cet_uri.
    :param cet_uri:
    :return:
    """
    if cet_uri in LIMES_CONFIGURATORS_MAPPING.keys():
        return LIMES_CONFIGURATORS_MAPPING[cet_uri]
    else:
        raise Exception("Invalid CET URI!")
