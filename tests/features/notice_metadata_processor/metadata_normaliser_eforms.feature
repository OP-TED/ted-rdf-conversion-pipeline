Feature: Notice metadata normaliser for eForms
  A fetched eForm notice metadata should be normalised

  Scenario Outline: Normalising notice metadata for an eForm
    Given a eForm notice
    When the normalise process is executed
    Then a normalised notice <metadata> is <possibly> available
    And the notice status is NORMALISED_METADATA
    And normalised metadata is available

    Examples:
      | metadata                  | possibly |
      | title                     | True     |
      | long_title                | True     |
      | notice_publication_number | True     |
      | publication_date          | True     |
      | ojs_issue_number          | True     |
      | ojs_type                  | True     |
      | eforms_subtype            | True     |
      | xsd_version               | False    |
      | original_language         | False    |
      | eform_sdk_version         | True     |
      | notice_source             | True     |
      | document_sent_date        | True     |
      | deadline_for_submission   | False    |
      | notice_type               | True     |
      | form_type                 | True     |
      | place_of_performance      | True     |
      | legal_basis_directive     | True     |

