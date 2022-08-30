# Created by dude at 26/01/2022
Feature: Notice eligibility for validation tests
  The system is able to check if a TED XML notice has validation tests


  Scenario: Find validation test set for a TED XML notice
    Given a notice
    When checking process is executed
    Then a validation test set is found
    And notice status ELIGIBLE_FOR_TRANSFORMATION


  Scenario: not finding validation tests set for a TED XML notice
    Given a notice
    When checking process is executed
    Then validation tests set is not found
    And notice status INELIGIBLE_FOR_TRANSFORMATION