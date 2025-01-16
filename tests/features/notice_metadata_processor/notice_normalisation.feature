Feature: Notice Normalisation
  As a User
  I want to normalize notice data
  So that it meets the required format

  Scenario: Normalising notice with spaces in notice ID
    Given an EF notice with spaces in notice ID
    And an SF notice with spaces in notice ID
    When the EF notice is normalised
    Then the EF notice ID should not contain leading or trailing spaces
    When the SF notice is normalised
    Then the SF notice ID should not contain leading or trailing spaces

  Scenario: Processing HTML incompatible string
    Given an HTML incompatible string
    When the string cannot be parsed as XML
    And the string is converted to HTML compatible format
    Then the resulting string should be well-formed XML

  Scenario: Normalising notice with HTML incompatible title
    Given an EF notice with HTML incompatible title
    And an SF notice with HTML incompatible title
    When the EF notice is normalised
    Then all EF notice titles should be valid XML
    When the SF notice is normalised
    Then all SF notice titles should be valid XML