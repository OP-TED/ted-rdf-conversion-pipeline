from ted_sws.notice_metadata_processor.model.metadata import ExtractedMetadata, EncodedValue, LanguageTaggedString, \
    CompositeTitle


def test_extracted_metadata(notice_id):
    metadata = ExtractedMetadata(**{"notice_publication_number": notice_id, "No_key": ["Value"]})
    assert metadata.notice_publication_number == notice_id
    assert "No_key" not in metadata.model_dump().keys()
    assert "country_of_buyer" in metadata.model_dump().keys()


def test_dict_extracted_metadata(notice_id):
    data_dict = {
        "ojs_issue_number": "232452",
        "city_of_buyer": [LanguageTaggedString("french", "fr"), LanguageTaggedString("english", "en")]
    }
    metadata = ExtractedMetadata(**data_dict)
    filtered_metadata = {k: v for k, v in metadata.model_dump().items() if v is not None}
    assert data_dict["city_of_buyer"] == metadata.model_dump()["city_of_buyer"]
    assert data_dict["city_of_buyer"][0].text == metadata.city_of_buyer[0].text
    assert data_dict == filtered_metadata


def test_multilingual_string():
    title = LanguageTaggedString(text="This is a text", language="en")

    assert isinstance(title, tuple)
    assert title.text == "This is a text"
    assert title.language == "en"


def test_composite_title():
    language = "en"
    city = "city name"
    country = "country name"
    title_city = LanguageTaggedString(city, language)
    title_country = LanguageTaggedString(country, language)
    composed_title = CompositeTitle(title_city=title_city, title_country=title_country)

    assert isinstance(composed_title.title_city, tuple)
    assert composed_title.title_city.language == "en"
    assert composed_title.title_city.text == city
    assert composed_title.title is None


def test_code_value():
    code = "3452"
    value = "Services"

    contract_type = EncodedValue(code, value)

    assert isinstance(contract_type, tuple)
    assert contract_type.value == value
