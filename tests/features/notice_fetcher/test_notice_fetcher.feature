# Created by Stefan at 16.08.2022
Feature: Notice fetcher
  The system is able to fetch selected TED-XML notices together with their metadata

  Scenario: Fetch a notice by id, from Ted
    Given a notice_id
    And knowing the TED API endpoint
    And knowing database endpoint
    When notice fetching by id is executed
    Then fetched notice is available in database
    And fetched notice have raw status
    And fetched notice have xml_manifestation
    And fetched notice have original_metadata

  Scenario: Fetch notices by query, from Ted
    Given a query
    And knowing the TED API endpoint
    And knowing database endpoint
    When notices fetching by query is executed
    Then a list of fetched notice_ids is returned
    And foreach returned notice_id exist in database a notice with RAW status
    And foreach returned notice_id exist in database a notice with xml_manifestation
    And foreach returned notice_id exist in database a notice with original_metadata

  Scenario: Fetch notices by date range, from Ted
    Given a start_date
    And a end_date
    And knowing the TED API endpoint
    And knowing database endpoint
    When notices fetching by date range is executed
    Then a list of fetched notice_ids is returned
    And foreach returned notice_id exist in database a notice with RAW status
    And foreach returned notice_id exist in database a notice with xml_manifestation
    And foreach returned notice_id exist in database a notice with original_metadata

  Scenario: Fetch notices by date wild card, from Ted
    Given a wildcard_date
    And knowing the TED API endpoint
    And knowing database endpoint
    When notices fetching by date wild card is executed
    Then a list of fetched notice_ids is returned
    And foreach returned notice_id exist in database a notice with RAW status
    And foreach returned notice_id exist in database a notice with xml_manifestation
    And foreach returned notice_id exist in database a notice with original_metadata




