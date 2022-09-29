from pymongo import MongoClient

from dags.pipelines.pipeline_protocols import NoticePipelineOutput
from ted_sws import config
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_sampler.services.notice_xml_indexer import index_notice
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from ted_sws.notice_metadata_processor.services.notice_eligibility import notice_eligibility_checker
from ted_sws.notice_packager.services.notice_packager import package_notice
from ted_sws.notice_publisher.services.notice_publisher import publish_notice
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
from ted_sws.notice_transformer.services.notice_transformer import transform_notice
from ted_sws.notice_validator.services.shacl_test_suite_runner import validate_notice_with_shacl_suite
from ted_sws.notice_validator.services.sparql_test_suite_runner import validate_notice_with_sparql_suite
from ted_sws.notice_validator.services.xpath_coverage_runner import validate_xpath_coverage_notice


def notice_normalisation_pipeline(notice: Notice) -> NoticePipelineOutput:
    """

    """
    indexed_notice = index_notice(notice=notice)
    normalised_notice = normalise_notice(notice=indexed_notice)

    return NoticePipelineOutput(notice=normalised_notice)


def notice_transformation_pipeline(notice: Notice) -> NoticePipelineOutput:
    """

    """
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    result = notice_eligibility_checker(notice=notice, mapping_suite_repository=mapping_suite_repository)
    if not result:
        return NoticePipelineOutput(notice=notice, processed=False)
    notice_id, mapping_suite_id = result
    # TODO: Implement XML preprocessing
    notice.update_status_to(new_status=NoticeStatus.PREPROCESSED_FOR_TRANSFORMATION)
    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
    rml_mapper = RMLMapper(rml_mapper_path=config.RML_MAPPER_PATH)
    transformed_notice = transform_notice(notice=notice, mapping_suite=mapping_suite, rml_mapper=rml_mapper)
    # TODO: Implement RDF distilation
    transformed_notice.set_distilled_rdf_manifestation(
        distilled_rdf_manifestation=transformed_notice.rdf_manifestation.copy())
    return NoticePipelineOutput(notice=transformed_notice)


def notice_validation_pipeline(notice: Notice) -> NoticePipelineOutput:
    """

    """
    mapping_suite_id = notice.distilled_rdf_manifestation.mapping_suite_id
    mongodb_client = MongoClient(config.MONGO_DB_AUTH_URL)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongodb_client)
    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
    validate_xpath_coverage_notice(notice=notice, mapping_suite=mapping_suite, mongodb_client=mongodb_client)
    validate_notice_with_sparql_suite(notice=notice, mapping_suite_package=mapping_suite)
    validate_notice_with_shacl_suite(notice=notice, mapping_suite_package=mapping_suite)
    return NoticePipelineOutput(notice=notice)


def notice_package_pipeline(notice: Notice) -> NoticePipelineOutput:
    """

    """
    # TODO: Implement notice package eligiblity
    notice.set_is_eligible_for_packaging(eligibility=True)
    packaged_notice = package_notice(notice=notice)
    return NoticePipelineOutput(notice=packaged_notice)


def notice_publish_pipeline(notice: Notice) -> NoticePipelineOutput:
    """

    """
    result = publish_notice(notice=notice)
    if result:
        return NoticePipelineOutput(notice=notice)
    else:
        return NoticePipelineOutput(notice=notice, processed=False)
