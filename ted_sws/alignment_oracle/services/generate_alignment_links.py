import pathlib
import tempfile

from ted_sws import config
from ted_sws.alignment_oracle.adapters.limes_alignment_engine import LimesAlignmentEngine
from ted_sws.alignment_oracle.model.limes_config import LimesConfigParams, LimesConfigGenerator
from ted_sws.core.model.notice import Notice

DEFAULT_MAX_ACCEPTANCE_THRESHOLD = 1.0
DEFAULT_MAX_REVIEW_THRESHOLD = 0.95
DEFAULT_DELTA_THRESHOLD = 0.05


def generate_alignment_links(limes_config_params: LimesConfigParams, threshold: float,
                             delta: float = DEFAULT_DELTA_THRESHOLD) -> str:
    """
        This function generate alignment links using limes engine.
    :param limes_config_params:
    :param threshold:
    :param delta:
    :return:
    """
    limes_config_params.review.threshold = min(threshold, DEFAULT_MAX_REVIEW_THRESHOLD)
    limes_config_params.acceptance.threshold = min(threshold + delta, DEFAULT_MAX_ACCEPTANCE_THRESHOLD)
    limes_alignment_engine = LimesAlignmentEngine(limes_executable_path=config.LIMES_ALIGNMENT_PATH)
    limes_alignment_engine.execute(limes_config_params=limes_config_params)
    review_result_path = pathlib.Path(limes_config_params.review.result_file_path)
    review_result_content = review_result_path.read_text(encoding="utf-8")
    if limes_config_params.acceptance.threshold == DEFAULT_MAX_ACCEPTANCE_THRESHOLD:
        acceptance_result_path = pathlib.Path(limes_config_params.acceptance.result_file_path)
        acceptance_result_content = acceptance_result_path.read_text(encoding="utf-8")
        review_result_content += acceptance_result_content
    return review_result_content


def generate_alignment_links_for_notice(notice: Notice, sparql_endpoint: str,
                                        limes_config_generator: LimesConfigGenerator,
                                        threshold: float,
                                        delta: float = DEFAULT_DELTA_THRESHOLD) -> str:
    """
         This function generate alignment links for a Notice RDF Manifestation.
    :param notice:
    :param sparql_endpoint:
    :param limes_config_generator:
    :param threshold:
    :param delta:
    :return:
    """
    notice_rdf_manifestation = notice.distilled_rdf_manifestation.object_data
    notice_rdf_file = tempfile.NamedTemporaryFile(suffix=".ttl")
    notice_rdf_file.write(notice_rdf_manifestation.encode(encoding="utf-8"))
    notice_rdf_file_path = notice_rdf_file.name
    with tempfile.TemporaryDirectory() as tmp_result_dir_path:
        limes_config_params = limes_config_generator(source_sparql_endpoint=notice_rdf_file_path,
                                                     target_sparql_endpoint=sparql_endpoint,
                                                     result_dir_path=pathlib.Path(tmp_result_dir_path)
                                                     )
        result_alignment_links = generate_alignment_links(limes_config_params=limes_config_params,
                                                          threshold=threshold,
                                                          delta=delta
                                                          )
    notice_rdf_file.close()
    return result_alignment_links
