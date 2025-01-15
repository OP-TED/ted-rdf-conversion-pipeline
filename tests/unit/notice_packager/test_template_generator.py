#!/usr/bin/python3

# test_template_generator.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """
import re
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import pytest

from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import PackagerMetadata
from tests import TEST_DATA_PATH


def __sanitize(s):
    return re.sub(r"[\n\t\s]+", "", s)


def __test_template_generator(template):
    path_to_test_template = TEST_DATA_PATH / "notice_packager" / "templates" / template
    return path_to_test_template.read_text()


def __test(template_generate, data, test_tpl):
    template_render = template_generate(data)
    test_template_render = __test_template_generator(test_tpl)
    assert __sanitize(template_render) == __sanitize(test_template_render)


def test_mets_xml_dmd_rdf_generator(template_sample_metadata):
    test_template = "2021_S_004_003545_0.mets.xml.dmd.rdf"
    __test(TemplateGenerator.mets_xml_dmd_rdf_generator, template_sample_metadata, test_template)


def test_tmd_rdf_generator(template_sample_metadata):
    test_template = "2021_S_004_003545_0.tmd.rdf"
    __test(TemplateGenerator.tmd_rdf_generator, template_sample_metadata, test_template)


def test_mets2create_mets_xml_generator(template_sample_metadata):
    template_sample_metadata.mets.type = "create"
    template_sample_metadata.mets.document_id = f"{template_sample_metadata.work.identifier}_{template_sample_metadata.mets.type}"
    test_template = "2021_S_004_003545_create.mets.xml"
    __test(TemplateGenerator.mets2action_mets_xml_generator, template_sample_metadata, test_template)


def test_mets2update_mets_xml_generator(template_sample_metadata):
    template_sample_metadata.mets.type = "update"
    template_sample_metadata.mets.document_id = f"{template_sample_metadata.work.identifier}_{template_sample_metadata.mets.type}"
    test_template = "2021_S_004_003545_update.mets.xml"
    __test(TemplateGenerator.mets2action_mets_xml_generator, template_sample_metadata, test_template)


def test_mets2action_mets_xml_generator_with_wrong_action(template_sample_metadata):
    template_sample_metadata.mets.type = "wrong_action"
    with pytest.raises(ValueError):
        TemplateGenerator.mets2action_mets_xml_generator(template_sample_metadata)


# def test_mets_dmd_rdf_has_html_safe_sequences_after_generation(sample_metadata_with_wrong_title: PackagerMetadata,
#                                                                sample_mets_xml_dmd_rdf_with_wrong_title_str: str):
#     # Ensure parser raises error on not well-formed xml (HTML sequences or elements)
#     with pytest.raises(ParseError):
#         ElementTree.fromstring(sample_mets_xml_dmd_rdf_with_wrong_title_str)
#
#     mets_dmd_rdf: str = TemplateGenerator.mets_xml_dmd_rdf_generator(sample_metadata_with_wrong_title)
#
#     # Parse to check if xml is well-formed (HTML-safe sequences or elements)
#     ElementTree.fromstring(mets_dmd_rdf)
