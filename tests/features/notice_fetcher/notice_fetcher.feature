# Created by dude at 25/01/2022
Feature: Notice fetcher
  The system is able to fetch selected TED-XML notices together with their metadata

  Scenario: Fetch a TED notice
    Given a TED REST API download endpoint
    And correct download API parameters
    When call to the API is made
    Then a notice and notice metadata is received from the API
    And the notice and notice metadata are stored

  Scenario: Fail to fetch a TED notice
    Given a TED REST API download endpoint
    And incorrect download API parameters
    When the call to the API is made
    And no notice or metadata is returned
    Then an error message is received indicating the problem





