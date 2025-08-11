from typing import List

from pymongo import MongoClient

from src.dags.pipelines.pipeline_protocols import NoticePipelineOutput
from src.ted_sws.master_data_registry.services.entity_deduplication import deduplicate_procedure_entities
from src.ted_sws.notice_publisher.adapters.sftp_publisher_abc import SFTPPublisherABC

CET_URIS = ["http://www.w3.org/ns/org#Organization"]
PROCEDURE_CET_URI = "http://data.europa.eu/a4g/ontology#Procedure"


def notices_batch_distillation_pipeline(notice_ids: List[str],
                                        mongodb_client: MongoClient
                                        ) -> List[NoticePipelineOutput]:
    """

    :param notice_ids:
    :param mongodb_client:
    :return:
    """
    from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
    from src.ted_sws.master_data_registry.services.entity_deduplication import deduplicate_entities_by_cet_uri

    notices = []
    notice_repository = NoticeRepository(mongodb_client=mongodb_client)
    for notice_id in notice_ids:
        notice = notice_repository.get(reference=notice_id)
        notice.set_distilled_rdf_manifestation(
            distilled_rdf_manifestation=notice.rdf_manifestation.model_copy())
        notices.append(notice)
    for cet_uri in CET_URIS:
        deduplicate_entities_by_cet_uri(notices=notices, cet_uri=cet_uri)
    deduplicate_procedure_entities(notices=notices, procedure_cet_uri=PROCEDURE_CET_URI, mongodb_client=mongodb_client)
    for notice in notices:
        notice_repository.update(notice=notice)
    return [NoticePipelineOutput(notice=notice) for notice in notices]


def publish_notices_in_batch(notice_ids: List[str],
                             mongodb_client: MongoClient,
                             sftp_publisher: SFTPPublisherABC = None,
                             ) -> List[NoticePipelineOutput]:
    """
        This function publishes the METS manifestation for a list of Notices.
    """
    from src.ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
    from src.ted_sws.data_manager.adapters.notice_repository import NoticeRepository
    import base64
    import pathlib
    import tempfile
    from src.ted_sws import config
    from src.ted_sws.core.model.notice import NoticeStatus
    from src.ted_sws.notice_publisher.services.notice_publisher import publish_notice_rdf_into_s3, \
        publish_notice_into_s3
    from src.ted_sws.event_manager.services.log import log_notice_error

    publisher = sftp_publisher or SFTPPublisher()
    remote_folder_path = config.SFTP_PUBLISH_PATH
    notice_pipeline_results: List[NoticePipelineOutput] = []

    notice_repository = NoticeRepository(mongodb_client=mongodb_client)

    try:
        publisher.connect()
    except Exception as e:
        log_notice_error(message=f"Can't perform notice batch publishing: {str(e)}")
        publisher.disconnect()
        raise e

    for notice_id in notice_ids:
        notice = notice_repository.get(reference=notice_id)
        try:
            notice.update_status_to(new_status=NoticeStatus.PACKAGED)
            if config.S3_PUBLISH_ENABLED:
                published_rdf_into_s3_result = publish_notice_rdf_into_s3(notice=notice)
                publish_notice_into_s3_result = publish_notice_into_s3(notice=notice)
                if not (published_rdf_into_s3_result and publish_notice_into_s3_result):
                    log_notice_error(
                        message="Can't load notice distilled rdf manifestation and METS package into S3 bucket!",
                        notice_id=notice_id,
                    )

            notice.set_is_eligible_for_publishing(eligibility=True)

            mets_manifestation = notice.mets_manifestation
            if not mets_manifestation or not mets_manifestation.object_data:
                raise ValueError("Notice does not have a METS manifestation to be published.")

            package_name = mets_manifestation.package_name
            if not package_name:
                raise ValueError("METS manifestation does not have a package name for publishing.")

            package_content = base64.b64decode(bytes(mets_manifestation.object_data, encoding='utf-8'), validate=True)
            remote_notice_path = f"{remote_folder_path}/{package_name}"
            with tempfile.NamedTemporaryFile() as source_file:
                source_file.write(package_content)
                publisher.publish(source_path=str(pathlib.Path(source_file.name)), remote_path=remote_notice_path)

            notice.update_status_to(NoticeStatus.PUBLISHED)
            notice_repository.update(notice=notice)
            notice_pipeline_results.append(NoticePipelineOutput(notice=notice, processed=True))

        except Exception as e:
            log_notice_error(
                message=f"Can't publish notice {notice_id}: {str(e)}",
                notice_id=notice_id,
            )
            notice_repository.update(notice=notice)
            notice_pipeline_results.append(NoticePipelineOutput(notice=notice, processed=False))

    publisher.disconnect()
    return notice_pipeline_results
