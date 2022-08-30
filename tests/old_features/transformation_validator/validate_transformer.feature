# Created by dude at 26/01/2022
Feature: Validate transformed notice
  The system will notify if the notice transformation process was successful or not

  Scenario: Validation of transformed notice
    Given a TED RDF notice
    And validation tests
    When validation process is executed
    Then a successful message is returned
    And the state is stored


  Scenario: Failing validation of transformed notice
    Given a TED RDF notice
    And validation tests
    When validation process is executed
    Then a error message is returned
    And the state is stored