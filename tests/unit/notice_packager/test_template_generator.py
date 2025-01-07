#!/usr/bin/python3

# test_template_generator.py
# Date:  09/03/2022
# Author: Kolea PLESCO
# Email: kalean.bl@gmail.com

""" """
import re

import pytest
from rdflib import Graph, Literal, XSD

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


def test_mets_dmd_rdf_has_work_id_after_generation(template_sample_metadata: PackagerMetadata,
                                                   work_id_predicate: str):
    mets_dmd_rdf: str = TemplateGenerator.mets_xml_dmd_rdf_generator(template_sample_metadata)
    mets_graph: Graph = Graph().parse(data=mets_dmd_rdf, format="xml")

    work_id_predicate_exists: bool = mets_graph.query(
        f""" ASK WHERE {{ ?subject <{work_id_predicate}> ?object . }} """).askAnswer

    assert work_id_predicate_exists

def test_mets_dmd_rdf_has_work_id_as_string_after_generation(template_sample_metadata: PackagerMetadata,
                                                   work_id_predicate: str):
    mets_dmd_rdf: str = TemplateGenerator.mets_xml_dmd_rdf_generator(template_sample_metadata)
    mets_graph: Graph = Graph().parse(data=mets_dmd_rdf, format="xml")
    string_datatype = XSD.string

    work_id_predicate_exists: bool = mets_graph.query(
        f""" ASK WHERE {{ ?subject <{work_id_predicate}> ?object . FILTER(datatype(?object) = <{string_datatype}>) }} """).askAnswer

    assert work_id_predicate_exists

def test_mets_dmd_rdf_has_correct_work_id_value_after_generation(template_sample_metadata: PackagerMetadata,
                                                                 work_id_predicate: str):
    mets_dmd_rdf: str = TemplateGenerator.mets_xml_dmd_rdf_generator(template_sample_metadata)
    mets_graph: Graph = Graph().parse(data=mets_dmd_rdf, format="xml")

    assert template_sample_metadata.work.uri
    work_id_value_literal = Literal(template_sample_metadata.work.uri, datatype=XSD.string)

    work_id_is_same: bool = mets_graph.query(
        f""" ASK WHERE {{ ?subject <{work_id_predicate}> {work_id_value_literal.n3()} . }} """).askAnswer

    assert work_id_is_same


