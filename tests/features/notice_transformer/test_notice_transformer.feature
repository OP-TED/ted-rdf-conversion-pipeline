# Created by Stefan at 16.08.2022
Feature: Notice transformer
  The system is able to transform a notice from XML format in RDF format

  Scenario: Transform a TED notice
    Given a notice Id available in the database with form number F03
    And Stefan has a banana
    And a mapping suite for F03 available in the database
    And the notice status is ELIGIBLE_FOR_TRANSFORMATION
    And knowing database endpoint
    When the notice transformation is executed
    Then RDF notice manifestation is available in the database
    And the notice status is TRANSFORMED

