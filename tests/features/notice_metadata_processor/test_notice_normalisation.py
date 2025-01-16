from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

import pytest
from pytest_bdd import scenario, given, when, then

from ted_sws.core.model.metadata import LanguageTaggedString
from ted_sws.core.model.notice import Notice
from ted_sws.notice_metadata_processor.adapters.notice_metadata_normaliser import get_html_compatible_string
from ted_sws.notice_metadata_processor.services.metadata_normalizer import normalise_notice


def html_str(content: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?> <body>{content}</body>"""


@scenario('notice_normalisation.feature', 'Normalising notice with spaces in notice ID')
def test_normalising_notice_with_spaces():
    """Test normalisation of notices with spaces in ID."""


@scenario('notice_normalisation.feature', 'Processing HTML incompatible string')
def test_processing_html_incompatible_string():
    """Test processing of HTML incompatible strings."""


@scenario('notice_normalisation.feature', 'Normalising notice with HTML incompatible title')
def test_normalising_notice_with_html_incompatible_title():
    """Test normalisation of notices with HTML incompatible titles."""


# Shared fixtures and steps
@given('an EF notice with spaces in notice ID')
def an_ef_notice_with_spaces_in_notice_id(sample_indexed_ef_html_unsafe_notice: Notice) -> Notice:
    """Provide EF notice fixture."""
    return sample_indexed_ef_html_unsafe_notice


@given('an SF notice with spaces in notice ID')
def an_sf_notice_with_spaces_in_notice_id(sample_indexed_sf_html_unsafe_notice: Notice) -> Notice:
    """Provide SF notice fixture."""
    return sample_indexed_sf_html_unsafe_notice


@when('the EF notice is normalised', target_fixture='normalised_ef_notice')
def the_ef_notice_is_normalised(sample_indexed_ef_html_unsafe_notice: Notice) -> Notice:
    """Normalize EF notice."""
    return normalise_notice(sample_indexed_ef_html_unsafe_notice)


@when('the SF notice is normalised', target_fixture='normalised_sf_notice')
def the_sf_notice_is_normalised(sample_indexed_sf_html_unsafe_notice: Notice) -> Notice:
    """Normalize SF notice."""
    return normalise_notice(sample_indexed_sf_html_unsafe_notice)


@then('the EF notice ID should not contain leading or trailing spaces')
def the_ef_notice_id_should_not_contain_leading_or_trailing_spaces(normalised_ef_notice: Notice):
    """Verify EF notice ID has no extra spaces."""
    assert normalised_ef_notice.normalised_metadata.notice_publication_number.strip() == \
           normalised_ef_notice.normalised_metadata.notice_publication_number


@then('the SF notice ID should not contain leading or trailing spaces')
def the_sf_notice_id_should_not_contain_leading_or_trailing_spaces(normalised_sf_notice: Notice):
    """Verify SF notice ID has no extra spaces."""
    assert normalised_sf_notice.normalised_metadata.notice_publication_number.strip() == \
           normalised_sf_notice.normalised_metadata.notice_publication_number


# HTML incompatible string scenario steps
@given('an HTML incompatible string', target_fixture='incompatible_string')
def an_html_incompatible_string(html_incompatible_str: str) -> str:
    """Provide HTML incompatible string fixture."""
    return html_incompatible_str


@when('the string cannot be parsed as XML')
def the_string_cannot_be_parsed_as_xml(html_incompatible_str: str):
    """Verify string cannot be parsed as XML."""
    with pytest.raises(ParseError):
        ElementTree.fromstring(html_incompatible_str)


@when('the string is converted to HTML compatible format', target_fixture='compatible_string')
def the_string_is_converted_to_html_compatible_format(html_incompatible_str: str) -> LanguageTaggedString:
    """Convert string to HTML compatible format."""
    return get_html_compatible_string(LanguageTaggedString(text=html_incompatible_str))


@then('the resulting string should be well-formed XML')
def the_resulting_string_should_be_well_formed_xml(compatible_string: LanguageTaggedString):
    """Verify string is well-formed XML."""
    ElementTree.fromstring(html_str(compatible_string.text))


# HTML incompatible title scenario steps
@given('an EF notice with HTML incompatible title')
def an_ef_notice_with_html_incompatible_title(sample_indexed_ef_html_unsafe_notice: Notice) -> Notice:
    """Provide EF notice with incompatible title fixture."""
    return sample_indexed_ef_html_unsafe_notice


@given('an SF notice with HTML incompatible title')
def an_sf_notice_with_html_incompatible_title(sample_indexed_sf_html_unsafe_notice: Notice) -> Notice:
    """Provide SF notice with incompatible title fixture."""
    return sample_indexed_sf_html_unsafe_notice


@then('all EF notice titles should be valid XML')
def all_ef_notice_titles_should_be_valid_xml(normalised_ef_notice: Notice):
    """Verify all EF notice titles are valid XML."""
    [ElementTree.fromstring(html_str(title.text)) for title in normalised_ef_notice.normalised_metadata.title]


@then('all SF notice titles should be valid XML')
def all_sf_notice_titles_should_be_valid_xml(normalised_sf_notice: Notice):
    """Verify all SF notice titles are valid XML."""
    [ElementTree.fromstring(html_str(title.text)) for title in normalised_sf_notice.normalised_metadata.title]
