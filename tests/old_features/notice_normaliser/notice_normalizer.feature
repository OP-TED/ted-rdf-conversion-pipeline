# Created by dude at 27/01/2022
Feature: Notice normaliser
  The system is able to normalise a XML notice

  Scenario: Normalise a XML notice
    Given a XML notice
    When normalise process is executed
    Then a normalised XML notice is available
    And it is stored


  Scenario: Fail to normalise a XML notice
    Given a XML notice
    When normalise process is executed
    Then a normalised XML notice is not available
    And an error message is generated indicating the problem