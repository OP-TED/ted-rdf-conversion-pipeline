# Created by dude at 26/01/2022
Feature: Notice eligibility for RML mapping rule
  The system is able to check if a TED XML notice has a RML mapping rule

  Scenario: Find a mapping rule set for a TED XML notice
    Given notice metadata
    When checking process is executed
    Then a RML mapping rule set is found


  Scenario: not finding a mapping rule set for a TED XML notice
    Given notice metadata
    When checking process is executed
    And RML mapping rule set is not found
    Then an error message is generated indicating the problem

