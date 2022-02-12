# Date:  29/01/2022
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com

Feature: Notice state and content in the lifecycle process

  A notice accounts for its state and status in the process lifecycle
  so that affordances are known and constraints are met.

  Scenario: add normalised metadata
    Given a notice
    And normalised metadata
    When normalised metadata is added
    Then the notice object contains the normalised metadata
    And the notice status is NORMALISED_METADATA

  Scenario: overwrite normalised metadata
    Given a notice
    And normalised metadata
    And the notice already contains normalised metadata
    When normalised metadata is overwritten
    Then the notice object contains the new normalised metadata
    And the notice status is NORMALISED_METADATA
    And notice contains no RDF manifestation
    And notice contains no RDF validation
    And notice contains no METS manifestation

  Scenario: add RDF manifestation
    Given a notice
    And RDF manifestation
    When RDF manifestation is added
    Then the notice object contains the RDF manifestation
    And the notice status is TRANSFORMED

  Scenario: overwrite RDF manifestation
    Given a notice
    And RDF manifestation
    And the notice already contains an RDF manifestation
    When the RDF manifestation is overwritten
    Then the notice object contains the new RDF manifestation
    And the notice status is TRANSFORMED
    And notice contains no RDF validation
    And notice contains no METS manifestation

  Scenario: add validation report for a transformation
    Given a notice
    And RDF validation report
    And the notice contains an RDF manifestation
    When RDF validation report is added
    Then the notice object contains the RDF validation report
    And the notice status is VALIDATED_TRANSFORMATION
    And notice contains no METS manifestation

  Scenario: cannot add a validation report when there is no transformation
    Given a notice
    And RDF validation report
    And the notice does not contains an RDF manifestation
    When RDF validation report is added
    Then an exception is raised

  Scenario: add METS manifestation
    Given a notice
    And METS manifestation
    When METS manifestation is added
    Then the notice object contains the METS manifestation
    And the notice status is PACKAGED

  Scenario: overwrite METS manifestation
    Given a notice
    And RDF manifestation
    And the notice already contains an METS manifestation
    When METS manifestation is added
    Then the notice object contains the new METS manifestation
    And the notice status is PACKAGED

  Scenario Outline: set notice eligibility for transformation before transformation
    Given a notice
    And eligibility check result is <eligibility>
    And the notice status is lower than TRANSFORMED
    When eligibility for transformation is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status                 |
      | true        | ELIGIBLE_FOR_TRANSFORMATION   |
      | false       | INELIGIBLE_FOR_TRANSFORMATION |

  Scenario: set notice eligibility for transformation after transformation
    Given a notice
    And eligibility check result
    And the notice status is equal or greater than TRANSFORMED
    When eligibility for transformation is set
    Then an exception is raised


  Scenario Outline: set notice eligibility for packaging when validated
    Given a notice
    And eligibility check result is <eligibility>
    And the notice status is VALIDATED_TRANSFORMATION
    When eligibility for packaging is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status            |
      | true        | ELIGIBLE_FOR_PACKAGING   |
      | false       | INELIGIBLE_FOR_PACKAGING |

  Scenario: set notice eligibility for packaging when not validated
    Given a notice
    And eligibility check result
    And the notice status is not VALIDATED_TRANSFORMATION
    When eligibility for packaging is set
    Then an exception is raised


  Scenario Outline: set METS package validity when package is available
    Given a notice
    And package check result is <validity>
    And notice contains a METS package
    When the package validity is set
    Then the status is <notice_status>

    Examples:
      | validity | notice_status   |
      | true     | CORRECT_PACKAGE |
      | false    | FAULTY_PACKAGE  |

  Scenario Outline: set METS package validity when package is missing
    Given a notice
    And package check result is <validity>
    And notice does not contains a METS package
    When the package validity is set
    Then an exception is raised

    Examples:
      | validity |
      | true     |
      | false    |

  Scenario: mark notice as published when package is available
    Given a notice
    And notice contains a METS package
    When the notice is marked as published
    Then the status is PUBLISHED

  Scenario: mark notice as published when package is missing
    Given a notice
    And notice does not contains a METS package
    When the notice is marked as published
    Then an exception is raised


  Scenario Outline: set notice public availability after publishing
    Given a notice
    And public availability check result is <availability>
    And the notice status is equal or greater than PUBLISHED
    When public availability is set
    Then notice status is <notice_status>

    Examples:
      | availability | notice_status        |
      | true         | PUBLICLY_AVAILABLE   |
      | false        | PUBLICLY_UNAVAILABLE |

