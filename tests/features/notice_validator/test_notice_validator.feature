# Created by Stefan at 16.08.2022
Feature: Notice Validator
  The system is able to validate the notice xml and rdf manifestation.

  Scenario: SHACL validation
    Given a notice
    And a mapping suite package
    And at least one SHACL test suite is available
    And the notice status is DISTILLED
    When the notice shacl validation is executed
    Then the notice have SHACL validation reports for each RDF manifestation

  Scenario: SPARQL validation
    Given a notice
    And a mapping suite package
    And at least one SPARQL test suite is available
    And the notice status is DISTILLED
    When the notice sparql validation is executed
    Then the notice have SPARQL validation reports for each RDF manifestation

