# Created by Stefan at 18.08.2022
Feature: Notice packager
  The system is able to pack TED-RDF notices in METS packages that are described with the metadata fetched from TED.

  Scenario: Package a TED notice in a METS package
    Given a notice
    And the notice status is ELIGIBLE_FOR_PACKAGING
    When the notice packaging is executed
    Then the notice have METS manifestation
    And the notice status is PACKAGED
