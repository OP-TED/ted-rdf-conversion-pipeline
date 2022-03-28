import pytest
from pytest_bdd import scenario, given, when, then, parsers

from ted_sws.domain.model.manifestation import RDFManifestation, RDFValidationManifestation, METSManifestation
from ted_sws.domain.model.metadata import NormalisedMetadata
from ted_sws.domain.model.notice import NoticeStatus
from tests.features import str2bool


@scenario("test_notice_operations.feature", "add normalised metadata")
def test_add_normalised_metadata():
    pass


@scenario("test_notice_operations.feature", "overwrite normalised metadata")
def test_overwrite_normalised_metadata():
    pass


@scenario("test_notice_operations.feature", "add RDF manifestation")
def test_add_rdf_manifestation():
    pass


@scenario("test_notice_operations.feature", "overwrite RDF manifestation")
def test_overwrite_rdf_manifestation():
    pass


@scenario("test_notice_operations.feature", "add validation report for a transformation")
def test_add_validation_report_for_a_transformation():
    pass


@scenario("test_notice_operations.feature", "cannot add a validation report when there is no transformation")
def test_cannot_add_a_validation_report_when_there_is_no_transformation():
    pass


@scenario("test_notice_operations.feature", "add METS manifestation")
def test_add_mets_manifestation():
    pass


@scenario("test_notice_operations.feature", "overwrite METS manifestation")
def test_overwrite_mets_manifestation():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for transformation before transformation")
def test_set_notice_eligibility_for_transformation_before_transformation():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for transformation after transformation")
def test_set_notice_eligibility_for_transformation_after_transformation():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for packaging before packaging")
def test_set_notice_eligibility_for_packaging_when_validated():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for packaging after packaging")
def test_set_notice_eligibility_for_packaging_when_not_validated():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for publishing after packaging")
def test_set_mets_package_validity_when_package_is_available():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for publishing after publishing")
def test_set_mets_package_validity_when_package_is_missing():
    pass


@scenario("test_notice_operations.feature", "mark notice as published if eligible")
def test_mark_notice_as_published_if_eligible():
    pass


@scenario("test_notice_operations.feature", "set notice public availability after publishing")
def test_set_notice_public_availability_after_publishing():
    pass


# --------------------------------
# Step implementations
# --------------------------------

@given("a notice", target_fixture="a_notice")
def step_impl(publicly_available_notice):
    return publicly_available_notice


@given("normalised metadata", target_fixture="normalised_metadata")
def step_impl(normalised_metadata_dict):
    return NormalisedMetadata(**normalised_metadata_dict)


@when("normalised metadata is added")
def step_impl(raw_notice, normalised_metadata):
    raw_notice.set_normalised_metadata(normalised_metadata=normalised_metadata)


@then("the notice object contains the normalised metadata")
def step_impl(raw_notice):
    assert raw_notice.normalised_metadata is not None


@then("the notice status is NORMALISED_METADATA")
def step_impl(raw_notice):
    assert raw_notice.status is NoticeStatus.NORMALISED_METADATA


@given("the notice already contains normalised metadata")
def step_impl(raw_notice,normalised_metadata_dict):
    raw_notice.set_normalised_metadata(NormalisedMetadata(**normalised_metadata_dict))
    assert raw_notice.normalised_metadata is not None


@when("normalised metadata is overwritten", target_fixture="old_normalised_metadata")
def step_impl(raw_notice, normalised_metadata):
    assert raw_notice.normalised_metadata is not None
    old = raw_notice.normalised_metadata
    normalised_metadata.notice_publication_number = "something else"
    raw_notice.set_normalised_metadata(normalised_metadata=normalised_metadata)
    return old


@then("the notice object contains the new normalised metadata")
def step_impl(raw_notice, normalised_metadata, old_normalised_metadata):
    assert raw_notice.normalised_metadata == normalised_metadata
    assert raw_notice.normalised_metadata != old_normalised_metadata


@then("normalised notice contains no RDF manifestation")
def step_impl(raw_notice):
    assert raw_notice.rdf_manifestation is None


@then("notice contains no RDF validation")
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.rdf_validation is None


@then("notice contains no METS manifestation")
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.mets_manifestation is None


@given("RDF manifestation", target_fixture="rdf_manifestation")
def step_impl():
    return RDFManifestation(object_data="featured object data of the RDF manifestation")


@when("RDF manifestation is added")
def step_impl(transformation_eligible_notice, rdf_manifestation):
    transformation_eligible_notice.set_rdf_manifestation(rdf_manifestation)


@then("the notice object contains the RDF manifestation")
def step_impl(transformation_eligible_notice, rdf_manifestation):
    assert transformation_eligible_notice.rdf_manifestation == rdf_manifestation


@then("the notice status is TRANSFORMED")
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.status is NoticeStatus.TRANSFORMED


@given("the notice already contains an RDF manifestation")
def step_impl(transformation_eligible_notice, rdf_manifestation):
    transformation_eligible_notice.set_rdf_manifestation(
        rdf_manifestation=RDFManifestation(object_data="data some data"))


@when("the RDF manifestation is overwritten", target_fixture="old_rdf_manifestation")
def step_impl(transformation_eligible_notice, rdf_manifestation):
    old_manifestation = transformation_eligible_notice.rdf_manifestation
    transformation_eligible_notice.set_rdf_manifestation(rdf_manifestation)
    return old_manifestation


@then("the notice object contains the new RDF manifestation")
def step_impl(transformation_eligible_notice, old_rdf_manifestation, rdf_manifestation):
    assert transformation_eligible_notice.rdf_manifestation != old_rdf_manifestation
    assert transformation_eligible_notice.rdf_manifestation == rdf_manifestation


@given("RDF validation report", target_fixture="rdf_validation")
def step_impl():
    return RDFValidationManifestation(object_data="this is another validation report")


@given("the notice contains an RDF manifestation")
def step_impl(transformation_eligible_notice):
    transformation_eligible_notice.set_rdf_manifestation(
        rdf_manifestation=RDFManifestation(object_data="data some data"))


@when("RDF validation report is added an exception is raised")
def step_impl(transformation_eligible_notice, rdf_validation):
    with pytest.raises(Exception):
        transformation_eligible_notice.set_rdf_validation(rdf_validation)


@then("the notice object contains the RDF validation report")
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.rdf_validation is not None


@then("the notice status is VALIDATED")
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.status is NoticeStatus.VALIDATED


@given("the notice does not contains an RDF manifestation")
def step_impl(transformation_eligible_notice):
    transformation_eligible_notice._rdf_manifestation = None


@given("METS manifestation", target_fixture="mets_manifestation")
def step_impl():
    return METSManifestation(object_data="THE METS manifestation")


@when("METS manifestation is added")
def step_impl(packaging_eligible_notice, mets_manifestation):
    packaging_eligible_notice.set_mets_manifestation(mets_manifestation=mets_manifestation)


@then("the notice object contains the METS manifestation")
def step_impl(packaging_eligible_notice, mets_manifestation):
    assert packaging_eligible_notice.mets_manifestation == mets_manifestation


@then("the notice status is PACKAGED")
def step_impl(packaging_eligible_notice):
    assert packaging_eligible_notice.status is NoticeStatus.PACKAGED


@given("the notice already contains an METS manifestation", target_fixture="packaging_eligible_notice")
def step_impl(publicly_available_notice):
    publicly_available_notice.update_status_to(NoticeStatus.PACKAGED)
    return publicly_available_notice


@then("the notice object contains the new METS manifestation")
def step_impl(packaging_eligible_notice, mets_manifestation):
    assert packaging_eligible_notice.mets_manifestation == mets_manifestation


@given(parsers.parse("eligibility check result is {eligibility}"),
       target_fixture="eligibility")
def step_impl(eligibility):
    return str2bool(eligibility)


@given("the notice status is lower than TRANSFORMED")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.NORMALISED_METADATA)


@when("eligibility for transformation is set")
def step_impl(a_notice, eligibility):
    a_notice.set_is_eligible_for_transformation(eligibility)


@then(parsers.parse("notice status is {notice_status}"))
def step_impl(a_notice, notice_status):
    assert a_notice.status == NoticeStatus[notice_status]


@given("the notice status is equal or greater than TRANSFORMED")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.VALIDATED)


@when("eligibility for packaging is set")
def step_impl(a_notice, eligibility):
    a_notice.set_is_eligible_for_packaging(eligibility)


@given("notice contains a METS package")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.PACKAGED)


@when("the package validity is set")
def step_impl(a_notice, eligibility):
    a_notice.set_is_eligible_for_publishing(eligibility)


@when("the notice is marked as published")
def step_impl(a_notice):
    a_notice.mark_as_published()


@when("public availability is set")
def step_impl(a_notice, availability):
    a_notice.set_is_publicly_available(availability)


@given("a notice eligible for transformation", )
def step_impl(transformation_eligible_notice):
    assert transformation_eligible_notice.status is NoticeStatus.ELIGIBLE_FOR_TRANSFORMATION


@when("RDF validation report is added")
def step_impl(transformation_eligible_notice, rdf_validation):
    transformation_eligible_notice.set_rdf_validation(rdf_validation)


@given("a packaging eligible notice", target_fixture="packaging_eligible_notice")
def step_impl(publicly_available_notice):
    publicly_available_notice.update_status_to(NoticeStatus.ELIGIBLE_FOR_PACKAGING)
    return publicly_available_notice


@given("the notice is validated")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.VALIDATED)


@given("the notice is published")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.PUBLISHED)


@given("the notice is packaged")
def step_impl(a_notice):
    a_notice.update_status_to(NoticeStatus.PACKAGED)


@then("the notice cannot be marked as published")
def step_impl(a_notice):
    with pytest.raises(Exception):
        a_notice.mark_as_published()


@given(parsers.parse("availability check result is {availability}"), target_fixture="availability")
def step_impl(availability):
    return str2bool(availability)
