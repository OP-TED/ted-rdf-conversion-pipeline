# Created by dude at 25/01/2022
Feature: Notice metadata normalizer
  A fetched notice metadata should be normalized

  Scenario Outline: Normalizing a notice metadata
    Given a notice
    When the normalize process is executed
    Then a normalized notice <metadata> is <possibly> available
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
      | city_of_buyer             | False    |
      | name_of_buyer             | False    |
      | original_language         | False    |
      | country_of_buyer          | False    |
      | eu_institution            | False    |
      | document_sent_date        | False    |
      | deadline_for_submission   | False    |
      | notice_type               | True     |
      | form_type                 | True     |
      | place_of_performance      | True     |
      | legal_basis_directive     | True     |

