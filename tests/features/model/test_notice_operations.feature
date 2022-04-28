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
    Given a notice eligible for transformation
    And normalised metadata
    And the notice already contains normalised metadata
    When normalised metadata is overwritten
    Then the notice object contains the new normalised metadata
    And the notice status is NORMALISED_METADATA
    And normalised notice contains no RDF manifestation
    And notice not contains RDF validation
    And notice contains no METS manifestation

  Scenario: add RDF manifestation
    Given a notice eligible for transformation
    And RDF manifestation
    When RDF manifestation is added
    Then the notice object contains the RDF manifestation
    And the notice status is TRANSFORMED

  Scenario: overwrite RDF manifestation
    Given a notice eligible for transformation
    And RDF manifestation
    And the notice already contains an RDF manifestation
    When the RDF manifestation is overwritten
    Then the notice object contains the new RDF manifestation
    And the notice status is TRANSFORMED
    And notice contains no RDF validation
    And notice contains no METS manifestation

  Scenario: add validation report for a transformation
    Given a notice eligible for transformation
    And RDF validation report
    And the notice contains an RDF manifestation
    When RDF validation report is added
    Then the notice object contains the RDF validation report
    And the notice status is VALIDATED
    And notice contains no METS manifestation

  Scenario: cannot add a validation report when there is no transformation
    Given a notice
    And RDF validation report
    And the notice does not contains an RDF manifestation
    When RDF validation report is added an exception is raised


  Scenario: add METS manifestation
    Given a packaging eligible notice
    And METS manifestation
    When METS manifestation is added
    Then the notice object contains the METS manifestation
    And the notice status is PACKAGED

  Scenario: overwrite METS manifestation
    Given a packaging eligible notice
    And METS manifestation
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

  Scenario Outline: set notice eligibility for transformation after transformation
    Given a notice
    And eligibility check result is <eligibility>
    And the notice status is equal or greater than TRANSFORMED
    When eligibility for transformation is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status                 |
      | false       | INELIGIBLE_FOR_TRANSFORMATION |

  Scenario Outline: set notice eligibility for packaging before packaging
    Given a notice
    And eligibility check result is <eligibility>
    And the notice is validated
    When eligibility for packaging is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status            |
      | true        | ELIGIBLE_FOR_PACKAGING   |
      | false       | INELIGIBLE_FOR_PACKAGING |

  Scenario Outline: set notice eligibility for packaging after packaging
    Given a notice
    And eligibility check result is <eligibility>
    And the notice is published
    When eligibility for packaging is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status            |
      | false       | INELIGIBLE_FOR_PACKAGING |

  Scenario Outline: set notice eligibility for publishing after packaging
    Given a notice
    And eligibility check result is <eligibility>
    And notice contains a METS package
    When the package validity is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status             |
      | true        | ELIGIBLE_FOR_PUBLISHING   |
      | false       | INELIGIBLE_FOR_PUBLISHING |

  Scenario Outline: set notice eligibility for publishing after publishing
    Given a notice
    And eligibility check result is <eligibility>
    And the notice is published
    When the package validity is set
    Then notice status is <notice_status>

    Examples:
      | eligibility | notice_status             |
      | false       | INELIGIBLE_FOR_PUBLISHING |


  Scenario Outline: mark notice as published if eligible
    Given a notice
    And eligibility check result is <eligibility>
    And the notice is packaged
    When the package validity is set
    And the notice is marked as published
    Then notice status is <notice_status>
    Examples:
      | eligibility | notice_status |
      | true        | PUBLISHED     |


  Scenario Outline: mark notice as published when ineligible
    Given a notice
    And eligibility check result is <eligibility>
    And the notice is packaged
    When the package validity is set
    Then the notice cannot be marked as published

    Examples:
      | eligibility |
      | false       |


  Scenario Outline: set notice public availability after publishing
    Given a notice
    And availability check result is <availability>
    And the notice is published
    When public availability is set
    Then notice status is <notice_status>

    Examples:
      | availability | notice_status        |
      | true         | PUBLICLY_AVAILABLE   |
      | false        | PUBLICLY_UNAVAILABLE |

