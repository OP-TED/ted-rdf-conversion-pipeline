import pathlib
from typing import List

from jinja2 import Environment, PackageLoader

from ted_sws import config
from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams, LimesDataSource, LimesDataResult

TEMPLATES = Environment(loader=PackageLoader("ted_sws.alignment_oracle.resources", "templates"))
LIMES_CONFIG_TEMPLATE = "limes_config.jinja2"
DEFAULT_SOURCE_SPARQL_VAR = "?x"
DEFAULT_TARGET_SPARQL_VAR = "?y"
DEFAULT_ACCEPTANCE_THRESHOLD = 0.95
DEFAULT_REVIEW_THRESHOLD = 0.7
DEFAULT_ACCEPTANCE_FILE_NAME = "acceptance.ttl"
DEFAULT_REVIEW_FILE_NAME = "review.ttl"
DEFAULT_PREFIXES = config.SPARQL_PREFIXES
DEFAULT_RESULT_FILE_FORMAT = "NT"
DEFAULT_RELATION = "owl:sameAs"
DEFAULT_SOURCE_ID = "default_source_id"
DEFAULT_TARGET_ID = "default_target_id"
DEFAULT_SOURCE_DATA_TYPE = "SPARQL"


def generate_xml_config_from_limes_config(limes_config_params: LimesConfigParams) -> str:
    """
        This function generate xml config from an instance of LimesConfigParams.
    :param limes_config_params:
    :return:
    """
    return TEMPLATES.get_template(LIMES_CONFIG_TEMPLATE).render(limes_config_params.dict())


def generate_default_limes_config_params(source_sparql_endpoint: str,
                                         target_sparql_endpoint: str,
                                         result_dir_path: pathlib.Path,
                                         alignment_metric: str,
                                         source_sparql_restrictions: List[str],
                                         target_sparql_restrictions: List[str],
                                         source_sparql_properties: List[str],
                                         target_sparql_properties: List[str],
                                         ) -> LimesConfigParams:
    """
        This function generate default LimesConfigParams.
    :param source_sparql_endpoint:
    :param target_sparql_endpoint:
    :param result_dir_path:
    :param alignment_metric:
    :param source_sparql_restrictions:
    :param target_sparql_restrictions:
    :param source_sparql_properties:
    :param target_sparql_properties:
    :return:
    """
    acceptance_file_path = str(result_dir_path / DEFAULT_ACCEPTANCE_FILE_NAME)
    review_file_path = str(result_dir_path / DEFAULT_REVIEW_FILE_NAME)
    return LimesConfigParams(prefixes=DEFAULT_PREFIXES,
                             source=LimesDataSource(id=DEFAULT_SOURCE_ID,
                                                    sparql_endpoint=source_sparql_endpoint,
                                                    sparql_variable=DEFAULT_SOURCE_SPARQL_VAR,
                                                    sparql_restrictions=source_sparql_restrictions,
                                                    sparql_properties=source_sparql_properties,
                                                    data_type=DEFAULT_SOURCE_DATA_TYPE
                                                    ),
                             target=LimesDataSource(id=DEFAULT_TARGET_ID,
                                                    sparql_endpoint=target_sparql_endpoint,
                                                    sparql_variable=DEFAULT_TARGET_SPARQL_VAR,
                                                    sparql_restrictions=target_sparql_restrictions,
                                                    sparql_properties=target_sparql_properties,
                                                    data_type=DEFAULT_SOURCE_DATA_TYPE
                                                    ),
                             alignment_metric=alignment_metric,
                             acceptance=LimesDataResult(threshold=DEFAULT_ACCEPTANCE_THRESHOLD,
                                                        result_file_path=acceptance_file_path,
                                                        relation=DEFAULT_RELATION
                                                        ),
                             review=LimesDataResult(threshold=DEFAULT_REVIEW_THRESHOLD,
                                                    result_file_path=review_file_path,
                                                    relation=DEFAULT_RELATION
                                                    ),
                             result_file_format=DEFAULT_RESULT_FILE_FORMAT
                             )


def generate_organisation_cet_limes_config_params(source_sparql_endpoint: str,
                                                  target_sparql_endpoint: str,
                                                  result_dir_path: pathlib.Path) -> LimesConfigParams:
    """
        This function generate LimesConfigParams for an Organisation CET.
    :param source_sparql_endpoint:
    :param target_sparql_endpoint:
    :param result_dir_path:
    :return:
    """
    return generate_default_limes_config_params(source_sparql_endpoint=source_sparql_endpoint,
                                                target_sparql_endpoint=target_sparql_endpoint,
                                                result_dir_path=result_dir_path,
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
