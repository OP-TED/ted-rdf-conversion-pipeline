# Created by dude at 26/01/2022
Feature: METS metadata generation
  The system is able to generate the necessary files that will form the METS metadata starting from a notice metadata

  Scenario: Generate METS metadata
    Given a notice metadata
    And METS metadata templates
    When the METS metadata generation is executed
    Then cdm metadata files and METS metadata are available


  Scenario: Fail to generate METS metadata
    Given a notice metadata
    And METS metadata templates
    When the METS metadata generation is executed
    And cdm metadata files or METS metadata are missing
    Then an error message is received indicating the problem