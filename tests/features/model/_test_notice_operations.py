from pytest_bdd import scenario, given, when, then


@scenario("test_notice_operations.feature", "add normalised metadata")
def test_add_normalised_metadata():
    pass


@scenario("test_notice_operations.feature", "overwrite normalised metadata")
def test_overwrite_normalised_metadata():
    pass


@scenario("test_notice_operations.feature", "add normalised metadata")
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


@scenario("test_notice_operations.feature", "set notice eligibility for packaging when validated")
def test_set_notice_eligibility_for_packaging_when_validated():
    pass


@scenario("test_notice_operations.feature", "set notice eligibility for packaging when not validated")
def test_set_notice_eligibility_for_packaging_when_not_validated():
    pass


@scenario("test_notice_operations.feature", "set METS package validity when package is available")
def test_set_mets_package_validity_when_package_is_available():
    pass


@scenario("test_notice_operations.feature", "set METS package validity when package is missing")
def test_set_mets_package_validity_when_package_is_missing():
    pass


@scenario("test_notice_operations.feature", "mark notice as published when package is available")
def test_mark_notice_as_published_when_package_is_available():
    pass


@scenario("test_notice_operations.feature", "mark notice as published when package is missing")
def test_mark_notice_as_published_when_package_is_missing():
    pass


@scenario("test_notice_operations.feature", "set notice public availability after publishing")
def test_set_notice_public_availability_after_publishing():
    pass


# --------------------------------
# Step implementations
# --------------------------------

@given("a notice")
def step_impl():
    raise NotImplementedError(u'STEP: Given a notice')


@given("normalised metadata")
def step_impl():
    raise NotImplementedError(u'STEP: And normalised metadata')


@when("normalised metadata is added")
def step_impl():
    raise NotImplementedError(u'STEP: When normalised metadata is added')


@then("the notice object contains the normalised metadata")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the normalised metadata')


@given("the notice status is NORMALISED_METADATA")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is NORMALISED_METADATA')


@given("the notice already contains normalised metadata")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice already contains normalised metadata')


@when("normalised metadata is overwritten")
def step_impl():
    raise NotImplementedError(u'STEP: When normalised metadata is overwritten')


@then("the notice object contains the new normalised metadata")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the new normalised metadata')


@given("notice contains no RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And notice contains no RDF manifestation')


@given("notice contains no RDF validation")
def step_impl():
    raise NotImplementedError(u'STEP: And notice contains no RDF validation')


@given("notice contains no METS manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And notice contains no METS manifestation')


@given("RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And RDF manifestation')


@when("RDF manifestation is added")
def step_impl():
    raise NotImplementedError(u'STEP: When RDF manifestation is added')


@then("the notice object contains the RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the RDF manifestation')


@given("the notice status is TRANSFORMED")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is TRANSFORMED')


@given("the notice already contains an RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice already contains an RDF manifestation')


@when("the RDF manifestation is overwritten")
def step_impl():
    raise NotImplementedError(u'STEP: When the RDF manifestation is overwritten')


@then("the notice object contains the new RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the new RDF manifestation')


@given("RDF validation report")
def step_impl():
    raise NotImplementedError(u'STEP: And RDF validation report')


@given("the notice contains an RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice contains an RDF manifestation')


@when("RDF validation report is added")
def step_impl():
    raise NotImplementedError(u'STEP: When RDF validation report is added')


@then("the notice object contains the RDF validation report")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the RDF validation report')


@given("the notice status is VALIDATED_TRANSFORMATION")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is VALIDATED_TRANSFORMATION')


@given("the notice does not contains an RDF manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice does not contains an RDF manifestation')


@then("an exception is raised")
def step_impl():
    raise NotImplementedError(u'STEP: Then an exception is raised')


@given("METS manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And METS manifestation')


@when("METS manifestation is added")
def step_impl():
    raise NotImplementedError(u'STEP: When METS manifestation is added')


@then("the notice object contains the METS manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the METS manifestation')


@given("the notice status is PACKAGED")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is PACKAGED')


@given("the notice already contains an METS manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice already contains an METS manifestation')


@then("the notice object contains the new METS manifestation")
def step_impl():
    raise NotImplementedError(u'STEP: Then the notice object contains the new METS manifestation')


@given("eligibility check result is <eligibility>")
def step_impl():
    raise NotImplementedError(u'STEP: And eligibility check result is <eligibility>')


@given("the notice status is lower than TRANSFORMED")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is lower than TRANSFORMED')


@when("eligibility for transformation is set")
def step_impl():
    raise NotImplementedError(u'STEP: When eligibility for transformation is set')


@then("notice status is <notice_status>")
def step_impl():
    raise NotImplementedError(u'STEP: Then notice status is <notice_status>')


@given("eligibility check result")
def step_impl():
    raise NotImplementedError(u'STEP: And eligibility check result')


@given("the notice status is equal or greater than TRANSFORMED")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is equal or greater than TRANSFORMED')


@when("eligibility for packaging is set")
def step_impl():
    raise NotImplementedError(u'STEP: When eligibility for packaging is set')


@given("the notice status is not VALIDATED_TRANSFORMATION")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is not VALIDATED_TRANSFORMATION')


@given("package check result is <validity>")
def step_impl():
    raise NotImplementedError(u'STEP: And package check result is <validity>')


@given("notice contains a METS package")
def step_impl():
    raise NotImplementedError(u'STEP: And notice contains a METS package')


@when("the package validity is set")
def step_impl():
    raise NotImplementedError(u'STEP: When the package validity is set')


@then("the status is <notice_status>")
def step_impl():
    raise NotImplementedError(u'STEP: Then the status is <notice_status>')


@given("notice does not contains a METS package")
def step_impl():
    raise NotImplementedError(u'STEP: And notice does not contains a METS package')


@when("the notice is marked as published")
def step_impl():
    raise NotImplementedError(u'STEP: When the notice is marked as published')


@given("public availability check result is <availability>")
def step_impl():
    raise NotImplementedError(u'STEP: And public availability check result is <availability>')


@given("the notice status is equal or greater than PUBLISHED")
def step_impl():
    raise NotImplementedError(u'STEP: And the notice status is equal or greater than PUBLISHED')


@when("public availability is set")
def step_impl():
    raise NotImplementedError(u'STEP: When public availability is set')
