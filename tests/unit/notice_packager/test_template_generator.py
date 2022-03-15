#!/usr/bin/python3

# test_template_generator.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """

import re

import pytest

from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from tests import TEST_DATA_PATH


def __sanitize(s):
    return re.sub(r"[\n\t\s]*", "", s)


def __test_template_generator(template):
    path_to_test_template = TEST_DATA_PATH / "notice_packager" / "templates" / template
    return path_to_test_template.read_text()


def __test(template_generate, data, test_tpl):
    template_render = template_generate(data)
    test_template_render = __test_template_generator(test_tpl)
    assert __sanitize(template_render) == __sanitize(test_template_render)


def test_mets_xml_dmd_rdf_generator(template_sample_metadata):
    test_template = "196390_2016-0.mets.xml.dmd.rdf"
    __test(TemplateGenerator.mets_xml_dmd_rdf_generator, template_sample_metadata, test_template)


def test_tmd_rdf_generator(template_sample_metadata):
    test_template = "techMDID001.tmd.rdf"
    __test(TemplateGenerator.tmd_rdf_generator, template_sample_metadata, test_template)


def test_mets2create_mets_xml_generator(template_sample_metadata):
    template_sample_metadata["notice"]["action"]["type"] = "create"
    test_template = "196390_2016_mets2create.mets.xml"
    __test(TemplateGenerator.mets2action_mets_xml_generator, template_sample_metadata, test_template)


def test_mets2update_mets_xml_generator(template_sample_metadata):
    template_sample_metadata["notice"]["action"]["type"] = "update"
    test_template = "196390_2016_mets2update.mets.xml"
    __test(TemplateGenerator.mets2action_mets_xml_generator, template_sample_metadata, test_template)


def test_mets2action_mets_xml_generator_with_wrong_action(template_sample_metadata):
    template_sample_metadata["notice"]["action"]["type"] = "wrong_action"
    with pytest.raises(ValueError):
        TemplateGenerator.mets2action_mets_xml_generator(template_sample_metadata)
