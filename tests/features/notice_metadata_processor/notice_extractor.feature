# Created by dude at 24/02/2022
Feature: Notice extractor
  The system is extracting metadata from the xml manifestation

  Scenario Outline: Extracting metadata
    Given an XML manifestation
    When the extracting process is executed
    Then extracted <metadata> is possibly available

    Examples:
      | metadata                  |
      | title                     |
      | notice_publication_number |
      | publication_date          |
      | ojs_issue_number          |
      | ojs_type                  |
      | city_of_buyer             |
      | name_of_buyer             |
      | original_language         |
      | country_of_buyer          |
      | type_of_buyer             |
      | eu_institution            |
      | document_sent_date        |
      | deadline_for_submission   |
      | type_of_contract          |
      | type_of_procedure         |
      | extracted_notice_type     |
      | extracted_form_number     |
      | regulation                |
      | type_of_bid               |
      | award_criteria            |
      | common_procurement        |
      | place_of_performance      |
      | internet_address          |
      | legal_basis_directive     |
      | xml_schema_version        |


