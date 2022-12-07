"""Notice publisher in S3 feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.notice_publisher.adapters.s3_notice_publisher import S3Publisher
from ted_sws.notice_publisher.services.notice_publisher import publish_notice_rdf_into_s3, publish_notice_into_s3


@scenario('test_notice_publisher_s3.feature', 'Publish notice METS manifestation')
def test_publish_notice_mets_manifestation():
    """Publish notice METS manifestation."""


@scenario('test_notice_publisher_s3.feature', 'Publish notice RDF manifestation')
def test_publish_notice_rdf_manifestation():
    """Publish notice RDF manifestation."""


@given('a notice')
def a_notice(publish_eligible_notice):
    """a notice."""
    assert publish_eligible_notice
    assert isinstance(publish_eligible_notice, Notice)


@given('knowing the S3 endpoint')
def knowing_the_s3_endpoint(s3_publisher):
    """knowing the S3 endpoint."""
    assert s3_publisher
    assert isinstance(s3_publisher, S3Publisher)


@given('the notice is eligible for publishing')
def the_notice_is_eligible_for_publishing(publish_eligible_notice):
    """the notice is eligible for publishing."""
    assert publish_eligible_notice.status == NoticeStatus.ELIGIBLE_FOR_PUBLISHING


@when('the notice METS manifestation publication is executed', target_fixture="published_notice")
def the_notice_mets_manifestation_publication_is_executed(publish_eligible_notice, s3_publisher, s3_bucket_name):
    """the notice METS manifestation publication is executed."""
    publish_result = publish_notice_into_s3(notice=publish_eligible_notice, s3_publisher=s3_publisher,
                                            bucket_name=s3_bucket_name)
    assert publish_result
    publish_eligible_notice.update_status_to(new_status=NoticeStatus.PUBLISHED)
    return publish_eligible_notice


@when('the notice RDF manifestation publication is executed', target_fixture="published_notice")
def the_notice_rdf_manifestation_publication_is_executed(publish_eligible_notice, s3_publisher, s3_bucket_name):
    """the notice RDF manifestation publication is executed."""
    publish_result = publish_notice_rdf_into_s3(notice=publish_eligible_notice, s3_publisher=s3_publisher,
                                                bucket_name=s3_bucket_name)
    assert publish_result
    return publish_eligible_notice


@then('the METS package is available in a S3 bucket')
def the_mets_package_is_available_in_a_s3_bucket(s3_publisher, s3_bucket_name, mets_package_published_name):
    """the METS package is available in a S3 bucket."""
    assert s3_publisher.is_published(bucket_name=s3_bucket_name,object_name=mets_package_published_name)
    s3_publisher.remove_object(bucket_name=s3_bucket_name, object_name=mets_package_published_name)
    assert not s3_publisher.is_published(bucket_name=s3_bucket_name, object_name=mets_package_published_name)

@then('the RDF manifestation is available in a S3 bucket')
def the_rdf_manifestation_is_available_in_a_s3_bucket(s3_publisher, s3_bucket_name, rdf_manifestation_published_name):
    """the RDF manifestation is available in a S3 bucket."""
    assert s3_publisher.is_published(bucket_name=s3_bucket_name, object_name=rdf_manifestation_published_name)
    s3_publisher.remove_object(bucket_name=s3_bucket_name, object_name=rdf_manifestation_published_name)
    assert not s3_publisher.is_published(bucket_name=s3_bucket_name, object_name=rdf_manifestation_published_name)


@then('the notice status is PUBLISHED')
def the_notice_status_is_published(published_notice: Notice, s3_publisher, s3_bucket_name):
    """the notice status is PUBLISHED."""
    assert published_notice.status == NoticeStatus.ELIGIBLE_FOR_PUBLISHING

