# Created by capitan at 15.11.2022
Feature: Master Data Registry
  The system is able to deduplicate CETs(critical entity types) from a notice RDF manifestation.

  Scenario: Deduplicate organisation CET
    Given a notice
    And the notice status is TRANSFORMED
    And knowing the MDR dataset name
    When the organisation CET deduplication is executed
    Then the notice status is DISTILLED
    And the notice distilled rdf manifestation contains owl:sameAs links
    And the MDR contain organisation canonical entities


  Scenario: Deduplicate procedure CET
    Given a notice
    And the notice status is TRANSFORMED
    And knowing a MongoDB endpoint
    When the procedure CET deduplication is executed
    Then the notice status is DISTILLED
    And the notice distilled rdf manifestation contains owl:sameAs links