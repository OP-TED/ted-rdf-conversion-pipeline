# Created by dude at 25/01/2022
Feature: Notice metadata normalizer
  A fetched notice metadata should be normalized

  Scenario: Normalizing a notice metadata
    Given a notice metadata
    And a normalizing process
    When the normalize process is executed
    Then a normalized notice metadata is available

  Scenario: Failing to normalize a notice metadata
    Given a notice metadata
    And a normalizing process
    When the normalize process is executed
    And no normalized notice metadata is available
    Then an error message is generated indicating the problem