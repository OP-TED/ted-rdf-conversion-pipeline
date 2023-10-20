#!/usr/bin/python3

# test_notice_packager.py
# Date:  08/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

from ted_sws.core.model.manifestation import RDFManifestation
from ted_sws.core.model.notice import NoticeStatus
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice
from ted_sws.notice_packager.model.metadata import METS_TYPE_CREATE
from ted_sws.notice_packager.services.notice_packager import package_notice


def test_notice_packager_with_notice(notice_2018, rdf_content):
    notice_2018._status = NoticeStatus.INDEXED
    normalise_notice(notice=notice_2018)
    rdf_manifestation = RDFManifestation(object_data=rdf_content)
    notice_2018._status = NoticeStatus.ELIGIBLE_FOR_PACKAGING
    notice_2018._rdf_manifestation = rdf_manifestation
    notice_2018._distilled_rdf_manifestation = rdf_manifestation
    packaged_notice = package_notice(notice_2018, action=METS_TYPE_CREATE)

    assert packaged_notice.mets_manifestation
    assert packaged_notice.mets_manifestation.type == METS_TYPE_CREATE
    assert packaged_notice.mets_manifestation.package_name == "2018_S_22_045279_create.zip"
