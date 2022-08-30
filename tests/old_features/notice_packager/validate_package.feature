# Created by dude at 26/01/2022
Feature: Validate a METS package
  The system is checking if the METS package has all the necessary files.

  Scenario: Validate METS package
    Given a TED RDF notice
    And cdm metadata rdf files
    And METS metadata xml file
    When the validation is executed
    Then a success message is received


  Scenario: Fail to validate METS package
    Given a TED RDF notice
    And cdm metadata rdf files
    When the validation is executed
    Then a error message is received