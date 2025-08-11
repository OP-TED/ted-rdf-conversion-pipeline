Feature: Notice metadata processor for Eforms
  The system is able to process TED notice metadata and check eligibility with mapping rules.

  Scenario: Notice eligibility checking for eForms
    Given a notice
    And the notice has eforms subtype 16 and sdk version 1.7
    And the notice status is NORMALISED
    And a mapping suite repository
    And a mapping suite for eforms subtype 16 and sdk version 1.7 is available in mapping suite repository
    When the notice eligibility checking is executed
    Then the notice status is ELIGIBLE_FOR_TRANSFORMATION
