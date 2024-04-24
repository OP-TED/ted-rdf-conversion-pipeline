# Created by Stefan at 16.08.2022
Feature: Notice transformer with eForm
  The system is able to transform a notice from XML format in RDF format

  Scenario: Transform a eForm TED notice
    Given a eForm notice
    And a mapping suite package
    And a rml mapper
    And given notice is eligible for transformation
    And given mapping suite is eligible for notice transformation
    When the notice transformation is executed
    Then the notice has RDF manifestation
    And the notice status is TRANSFORMED