#!/usr/bin/python3

# test_metadata.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """


from ted_sws.notice_packager.model.metadata import PackagerMetadata


def test_validate_packager_metadata(template_sample_metadata_json):
    PackagerMetadata(**template_sample_metadata_json)
