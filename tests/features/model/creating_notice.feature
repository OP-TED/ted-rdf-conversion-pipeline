# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: Notice creation

  A notice is created so that it can be used in the system.

  Scenario: Create a bare minimum notice
    Given a TED identifier ted_identifier
    And original TED notice metadata notice_metadata
    And the source URL source_url
    And the XML content of the notice xml_content
    When a notice is instantiated
    Then a new notice object is available
    And notice_metadata, xml_content, source_url and status RAW are accessible

