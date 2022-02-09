# Created by dude at 26/01/2022
Feature: Notice eligibility for validation tests
  The system is able to check if a TED XML notice has validation tests


  Scenario: Find validation test set for a TED XML notice
    Given notice metadata
    When checking process is executed
    Then a validation test set is found


  Scenario: not finding validation tests set for a TED XML notice
    Given notice metadata
    When checking process is executed
    And validation tests set is not found
    Then an error message is generated indicating the problem