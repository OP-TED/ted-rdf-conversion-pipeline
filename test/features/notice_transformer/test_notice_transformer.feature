# Created by Stefan at 16.08.2022
Feature: Notice transformer
  The system is able to transform a notice from XML format in RDF format

  Scenario: Transform a TED notice
    Given a notice
    And a mapping suite package
    And a rml mapper
    And given notice is eligible for transformation
    And given mapping suite is eligible for notice transformation
    When the notice transformation is executed
    Then the notice have RDF manifestation
    And the notice status is TRANSFORMED

  Scenario: Transform a TED notice by id
    Given a notice id
    And a mapping suite package id
    And a rml mapper
    And a notice repository
    And a mapping suite repository
    And given notice is eligible for transformation
    And given mapping suite is eligible for notice transformation
    When the notice transformation by id is executed
    Then the RDF notice manifestation is available in the database
    And the notice have RDF manifestation
    And the notice status is TRANSFORMED