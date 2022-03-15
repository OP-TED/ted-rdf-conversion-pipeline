#!/usr/bin/python3

# test_metadata.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """


from ted_sws.notice_packager.model.metadata import PackagerMetadata, NoticeMetadata, WorkMetadata, ExpressionMetadata, \
    ManifestationMetadata


def test_validate_notice(template_sample_notice):
    NoticeMetadata(**template_sample_notice)


def test_validate_work_metadata(template_sample_work):
    WorkMetadata(**template_sample_work)


def test_validate_expression_metadata(template_sample_expression):
    ExpressionMetadata(**template_sample_expression)


def test_validate_manifestation_metadata(template_sample_manifestation):
    ManifestationMetadata(**template_sample_manifestation)


def test_validate_packager_metadata(template_sample_metadata):
    PackagerMetadata(**template_sample_metadata)
