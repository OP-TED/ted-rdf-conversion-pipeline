# Created by Stefan at 18.08.2022
Feature: Notice metadata processor
  The system is able to process TED notice metadata and check eligibility with mapping rules.

  Scenario: Notice eligibility checking negative
    Given a notice
    And the notice is with form number F03
    And the notice status is NORMALISED
    And a mapping suite repository
    And a mapping suite for F03 is not available in mapping suite repository
    When the notice eligibility checking is executed
    Then the notice status is INELIGIBLE_FOR_TRANSFORMATION


  Scenario: Notice eligibility checking positive
    Given a notice
    And the notice is with form number F03
    And the notice status is NORMALISED
    And a mapping suite repository
    And a mapping suite for F03 is available in mapping suite repository
    When the notice eligibility checking is executed
    Then the notice status is ELIGIBLE_FOR_TRANSFORMATION
