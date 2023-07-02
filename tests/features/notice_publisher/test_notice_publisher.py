"""Notice publisher feature tests."""

from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

from ted_sws.core.model.notice import Notice, NoticeStatus
from ted_sws.data_manager.adapters.repository_abc import NoticeRepositoryABC
from ted_sws.notice_publisher.adapters.sftp_notice_publisher import SFTPPublisher
from ted_sws.notice_publisher.services.notice_publisher import publish_notice, publish_notice_by_id


@scenario('test_notice_publisher.feature', 'Publish notice')
def test_publish_notice():
    """Publish notice."""


@scenario('test_notice_publisher.feature', 'Publish notice by id')
def test_publish_notice_by_id():
    """Publish notice by id."""


@given('a notice')
def a_notice(publish_eligible_notice):
    """a notice."""
    assert publish_eligible_notice
    assert isinstance(publish_eligible_notice, Notice)


@given('a notice id', target_fixture="publish_notice_id")
def a_notice_id(publish_eligible_notice):
    """a notice id."""
    assert publish_eligible_notice
    assert isinstance(publish_eligible_notice, Notice)
    assert publish_eligible_notice.ted_id
    assert type(publish_eligible_notice.ted_id) == str
    return publish_eligible_notice.ted_id


@given('a notice repository')
def a_notice_repository(notice_repository):
    """a notice repository."""
    assert notice_repository
    assert isinstance(notice_repository, NoticeRepositoryABC)


@given('knowing the SFTP endpoint')
def knowing_the_sftp_endpoint(sftp_endpoint):
    """knowing the SFTP endpoint."""
    assert sftp_endpoint
    assert type(sftp_endpoint) == str


@given('the notice is eligible for publishing')
def the_notice_is_eligible_for_publishing(publish_eligible_notice):
    """the notice is eligible for publishing."""
    assert publish_eligible_notice.status == NoticeStatus.ELIGIBLE_FOR_PUBLISHING


@when('the notice publication is executed', target_fixture="published_notice")
def the_notice_publication_is_executed(publish_eligible_notice):
    """the notice publication is executed."""
    publish_notice(notice=publish_eligible_notice)
    return publish_eligible_notice


@when('the notice publication by id is executed', target_fixture="published_notice")
def the_notice_publication_by_id_is_executed(publish_notice_id, notice_repository):
    """the notice publication by id is executed."""
    publish_notice_by_id(notice_id=publish_notice_id, notice_repository=notice_repository)
    return notice_repository.get(reference=publish_notice_id)


@then('the METS package available in a shared SFTP drive')
def the_mets_package_available_in_a_shared_sftp_drive(published_notice: Notice, sftp_remote_folder_path):
    """the METS package available in a shared SFTP drive."""
    publisher: SFTPPublisher = SFTPPublisher()
    remote_notice_path = f"{sftp_remote_folder_path}/{published_notice.ted_id}.zip"
    publisher.connect()
    assert publisher.exists(remote_path=remote_notice_path)
    publisher.disconnect()


@then('the notice status is PUBLISHED')
def the_notice_status_is_published(published_notice: Notice):
    """the notice status is PUBLISHED."""
    assert published_notice.status == NoticeStatus.PUBLISHED
