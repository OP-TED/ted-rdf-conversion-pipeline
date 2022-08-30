"""Notice packager feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.manifestation import METSManifestation
from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.notice_packager.services.notice_packager import create_notice_package


@scenario('test_notice_packager.feature', 'Package a TED notice in a METS package')
def test_package_a_ted_notice_in_a_mets_package():
    """Package a TED notice in a METS package."""


@given('a notice')
def a_notice(package_eligible_notice):
    """a notice."""
    assert package_eligible_notice
    assert isinstance(package_eligible_notice, Notice)


@given('the notice status is ELIGIBLE_FOR_PACKAGING')
def the_notice_status_is_eligible_for_packaging(package_eligible_notice):
    """the notice status is ELIGIBLE_FOR_PACKAGING."""
    assert package_eligible_notice.status == NoticeStatus.ELIGIBLE_FOR_PACKAGING


@when('the notice packaging is executed', target_fixture="packaged_notice")
def the_notice_packaging_is_executed(package_eligible_notice):
    """the notice packaging is executed."""
    rdf_content = package_eligible_notice.distilled_rdf_manifestation.object_data.encode("utf-8")
    mets_manifestation_content = create_notice_package(in_data=package_eligible_notice, rdf_content=rdf_content)
    package_eligible_notice.set_mets_manifestation(
        mets_manifestation=METSManifestation(object_data=mets_manifestation_content))
    return package_eligible_notice


@then('the notice have METS manifestation')
def the_notice_have_mets_manifestation(packaged_notice: Notice):
    """the notice have METS manifestation."""
    assert packaged_notice.mets_manifestation
    assert packaged_notice.mets_manifestation.object_data


@then('the notice status is PACKAGED')
def the_notice_status_is_packaged(packaged_notice: Notice):
    """the notice status is PACKAGED."""
    assert packaged_notice.status == NoticeStatus.PACKAGED
