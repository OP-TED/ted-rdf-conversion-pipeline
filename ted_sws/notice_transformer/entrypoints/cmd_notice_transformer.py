#!/usr/bin/python3

import sys
import os

module_path = os.path.dirname(os.path.realpath(__file__)) + '/../../../'
sys.path.append(module_path)

import click
from pymongo import MongoClient

from ted_sws import config
from ted_sws.data_manager.adapters.mapping_suite_repository import MappingSuiteRepositoryMongoDB
from ted_sws.data_manager.adapters.notice_repository import NoticeRepository
from ted_sws.notice_transformer.adapters.rml_mapper import RMLMapper
import ted_sws.notice_transformer.services.notice_transformer as notice_transformer


class CmdRunner:
    """
    Keeps the logic to be used by Notice Transformer CMD
    """


@click.command()
@click.option('--notice-id', prompt='NOTICE_ID', help='Notice ID.')
@click.option('--mapping-suite-id', prompt='MAPPING_SUITE_ID', help='Mapping Suite ID.')
def transform_notice(notice_id, mapping_suite_id):
    """
    Transforms the Notice (identified by NOTICE_ID),
    based on Mapping Rules (identified by MAPPING_SUITE_ID)
    """

    print(notice_id, mapping_suite_id)
    mongo_client = MongoClient(config.MONGO_DB_AUTH_URL)
    notice_repository = NoticeRepository(mongodb_client=mongo_client)
    notice = notice_repository.get(reference=notice_id)
    print("NOTICE :: ", notice)
    mapping_suite_repository = MappingSuiteRepositoryMongoDB(mongodb_client=mongo_client)
    mapping_suite = mapping_suite_repository.get(reference=mapping_suite_id)
    print("MAPPING_SUITE :: ", mapping_suite)
    result_notice = notice_transformer.transform_notice(notice=notice, mapping_suite=mapping_suite,
                                                        rml_mapper=RMLMapper(
                                                            rml_mapper_path=config.RML_MAPPER_PATH
                                                        ))
    notice_repository.update(notice=result_notice)


if __name__ == '__main__':
    transform_notice()
