Feature: [FWC 10829 | BDC 47874 | TEDSWS-184] General status should reflect the internal statuses

  As a data pipeline maintainer,
  I want the DAG-run status in Airflow to accurately reflect the final statuses notices in a batch,
  So that failures in notice processing are not hidden behind misleading "Success" statuses at the DAG level.

  Background:
    Given the notice processing pipeline is configured
    And the success statuses are defined as "PUBLISHED,PUBLICLY_AVAILABLE,PACKAGED,VALIDATED"

  Scenario: DAG Run ends with success when all notices have default success status
    Given a batch of notices with IDs "123456-2022,789012-2022,345678-2022"
    When the notice processing pipeline processes all notices
    And all notices end with status "PUBLISHED"
    And the stop_processing task checks the notice statuses
    Then the DAG run should complete successfully
    And no AirflowException should be raised
    And the notices_with_status xcom should contain all notices with "PUBLISHED" status

  Scenario: DAG Run ends with success when all notices have various success statuses
    Given a batch of notices with IDs "123456-2022,789012-2022,345678-2022"
    When the notice processing pipeline processes all notices
    And notice "123456-2022" ends with status "PUBLISHED"
    And notice "789012-2022" ends with status "PUBLICLY_AVAILABLE"
    And notice "345678-2022" ends with status "PACKAGED"
    And the stop_processing task checks the notice statuses
    Then the DAG run should complete successfully
    And no AirflowException should be raised

  Scenario: DAG Run ends with failure when some notices have non-success status
    Given a batch of notices with IDs "123456-2022,789012-2022,345678-2022"
    When the notice processing pipeline processes all notices
    And notice "123456-2022" ends with status "PUBLISHED"
    And notice "789012-2022" ends with status "INELIGIBLE_FOR_TRANSFORMATION"
    And notice "345678-2022" ends with status "RAW"
    And the stop_processing task checks the notice statuses
    Then the DAG run should fail
    And an AirflowException should be raised with message "There are notices that are not processed with success. Please check failed tasks."

  Scenario: DAG Run ends with failure when all notices have non-success status
    Given a batch of notices with IDs "123456-2022,789012-2022"
    When the notice processing pipeline processes all notices
    And notice "123456-2022" ends with status "INELIGIBLE_FOR_TRANSFORMATION"
    And notice "789012-2022" ends with status "TRANSFORMED"
    And the stop_processing task checks the notice statuses
    Then the DAG run should fail
    And an AirflowException should be raised with message "There are notices that are not processed with success. Please check failed tasks."

  Scenario: Transformation task fails when notices cannot be processed successfully
    Given a batch of notices with IDs "123456-2022,789012-2022"
    And notice "123456-2022" is eligible for transformation
    And notice "789012-2022" is not eligible for transformation
    When the notice_transformation_pipeline task processes the batch
    Then notice "123456-2022" should be processed successfully
    And notice "789012-2022" should not be processed successfully
    And the task should raise AirflowFailException with message "There are notices failed during this task. Please check logs."

  Scenario: Normalisation task fails when processing encounters errors
    Given a batch of notices with IDs "123456-2022,789012-2022"
    And notice "123456-2022" has valid XML content
    And notice "789012-2022" has corrupted XML content
    When the notice_normalisation_pipeline task processes the batch
    Then notice "123456-2022" should be processed to "NORMALISED_METADATA" status
    And processing of notice "789012-2022" should raise an exception
    And the task should fail with the processing exception

  Scenario: Validation task fails when notices have validation errors
    Given a batch of notices with IDs "123456-2022,789012-2022-invalid"
    And notice "123456-2022" has valid RDF manifestation
    And notice "789012-2022-invalid" has invalid RDF manifestation causing validation failure
    When the notice_validation_pipeline task processes the batch
    Then notice "123456-2022" should be processed successfully
    And processing of notice "789012-2022-invalid" should fail during validation
