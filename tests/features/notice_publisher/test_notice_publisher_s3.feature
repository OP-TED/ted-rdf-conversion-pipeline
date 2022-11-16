# Created by capitan at 15.11.2022
Feature: Notice publisher in S3
  The system is able to publish notice METS and RDF manifestations to S3 bucket.


  Scenario: Publish notice RDF manifestation
    Given a notice
    And knowing the S3 endpoint
    And the notice is eligible for publishing
    When the notice RDF manifestation publication is executed
    Then the RDF manifestation is available in a S3 bucket
    And the notice status is PUBLISHED

  Scenario: Publish notice METS manifestation
    Given a notice
    And knowing the S3 endpoint
    And the notice is eligible for publishing
    When the notice METS manifestation publication is executed
    Then the METS package is available in a S3 bucket
    And the notice status is PUBLISHED