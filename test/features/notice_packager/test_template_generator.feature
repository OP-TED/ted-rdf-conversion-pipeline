
Feature: Template Generator
  The system is able to generate METS packages based on jinja templates.

  Scenario: Template Generator generates METS DMD RDF that has work_id
    Given a PackagerMetadata
    And a work_id predicate
    When METS DMD RDF generator is executed
    Then METS DMD RDF is a valid RDF
    And work_id persist in METS DMD RDF