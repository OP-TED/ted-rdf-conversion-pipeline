"""Tests for Template Generator's METS DMD RDF generation."""

from urllib.parse import urlparse, ParseResult
from pytest_bdd import given, when, then, scenario
from rdflib import Graph

from ted_sws.notice_packager.adapters.template_generator import TemplateGenerator
from ted_sws.notice_packager.model.metadata import PackagerMetadata


@scenario('test_template_generator.feature', 'Template Generator generates METS DMD RDF that has work_id')
def test_package_a_ted_notice_in_a_mets_package() -> None:
    """Test METS package generation with work_id."""


@given('a PackagerMetadata')
def a_packager_metadata(template_sample_metadata: PackagerMetadata) -> None:
    """Verify PackagerMetadata existence."""
    assert template_sample_metadata
    assert isinstance(template_sample_metadata, PackagerMetadata)


@given('a work_id predicate')
def a_work_id_predicate(work_id_predicate: str, work_id_str: str) -> None:
    """Check work_id predicate validity."""
    assert work_id_predicate
    assert isinstance(work_id_predicate, str)
    assert work_id_str in work_id_predicate
    valid_url: ParseResult = urlparse(work_id_predicate)
    assert valid_url.netloc
    assert valid_url.fragment == work_id_str


@when("METS DMD RDF generator is executed", target_fixture="mets_xml_dmd_rdf")
def mets_dmd_rdf_generator_is_executed(template_sample_metadata: PackagerMetadata) -> str:
    """Generate METS DMD RDF."""
    return TemplateGenerator.mets_xml_dmd_rdf_generator(template_sample_metadata)


@then("METS DMD RDF is a valid RDF")
def mets_dmd_rdf_is_a_valid_rdf(mets_xml_dmd_rdf: str) -> None:
    """Validate RDF format."""
    Graph().parse(data=mets_xml_dmd_rdf, format="xml")


@then("work_id persist in METS DMD RDF")
def work_id_persist_in_mets_dmd_rdf(mets_xml_dmd_rdf: str, work_id_str: str) -> None:
    """Verify work_id presence in RDF."""
    assert work_id_str in mets_xml_dmd_rdf