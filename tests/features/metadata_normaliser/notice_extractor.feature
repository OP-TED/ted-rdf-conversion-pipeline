# Created by dude at 24/02/2022
Feature: Notice extractor
    The system is extracting metadata from the xml manifestation

  Scenario: Extracting metadata
    Given a notice
    When the extracting process is executed
    Then a extracted metadata is available


