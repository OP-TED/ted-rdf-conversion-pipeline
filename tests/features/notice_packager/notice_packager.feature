# Created by dude at 26/01/2022
Feature: Notice packager
  The system is able to pack TED-RDF notices in METS packages that are described with the metadata fetched from TED.

  Scenario: Notice packed in a METS package
    Given a TED RDF notice
    And METS metadata files
    When the package process is executed
    Then a METS package is available
    And it is stored

  Scenario: Fail to pack a notice in a METS package
    Given a TED RDF notice
    And METS metadata files
    When the package process is executed
    And METS package is not available
    Then an error message is received indicating the problem