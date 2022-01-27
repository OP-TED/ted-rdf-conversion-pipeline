# Created by dude at 25/01/2022
Feature: Multiple fetching types
  Notice fetcher component is able to fetch notices by different criteria

  Scenario: Fetch a TED notice by identifier
    Given a TED REST API download endpoint
    And a identifier parameter
    When the call to the API is made
    Then a notice with that identifier and the notice metadata are available
    And are stored


  Scenario: Fetch a TED notice by search query
    Given a TED REST API download endpoint
    And search result set
    When the call to the API is made
    Then notice(s) that match the search query result and their metadata are available
    And are stored


