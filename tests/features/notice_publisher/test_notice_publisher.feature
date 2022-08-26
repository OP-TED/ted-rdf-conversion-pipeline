# Created by Stefan at 19.08.2022
Feature: Notice publisher
  The system is able to publish notice METS manifestation to SFTP endpoint.


  Scenario: Publish notice
    Given a notice
    And knowing the SFTP endpoint
    And the notice is eligible for publishing
    When the notice publication is executed
    Then the METS package available in a shared SFTP drive
    And the notice status is PUBLISHED

  Scenario: Publish notice by id
    Given a notice id
    And a notice repository
    And knowing the SFTP endpoint
    And the notice is eligible for publishing
    When the notice publication by id is executed
    Then the METS package available in a shared SFTP drive
    And the notice status is PUBLISHED