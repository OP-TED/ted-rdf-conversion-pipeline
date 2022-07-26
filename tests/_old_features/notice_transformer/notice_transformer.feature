# Created by dude at 26/01/2022
Feature: Notice transformer
  The system is able to transform a notice from XML format in RDF format

  Scenario: Transform a TED notice
    Given a TED XML notice
    And RML mapping rule
    When transform process is executed
    Then a TED RDF notice is available
    And it is stored


  Scenario: Fail to transform a TED notice
    Given a TED XML notice
    And RML mapping rule
    When transform process failed
    Then an error message is received indicating the problem