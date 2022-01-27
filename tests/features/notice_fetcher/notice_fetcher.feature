# Created by dude at 25/01/2022
Feature: Notice fetcher
  The system is able to fetch selected TED-XML notices together with their metadata

  Scenario: Fetch a TED notice
    Given a TED REST API download endpoint
    And API call parameters
    When the call to the API is made
    Then a notice is received from the API
    And the notice is stored

  Scenario: Fail to fetch a TED notice
    Given a TED REST API download endpoint
    And API call parameters
    When the call to the API is made
    And no notice is returned
    Then an error message is received indicating the problem


  Scenario: Fetch a TED notice metadata
    Given a TED REST API download endpoint
    And API call parameters
    When the call to the API is made
    Then metadata for the notice is available
    And the notice metadata is stored

  Scenario: Fail to fetch a TED notice metadata
    Given a TED REST API download endpoint
    And API call parameters
    When the call to the API is made
    And no metadata is returned
    Then an error message is received indicating the problem



