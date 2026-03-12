Feature: [FWC 10829 | BDC 47874 | TEDSWS-192] Notice publishing failure due to fluctuating SFTP sessions

  Scenario: Publishing fail on multiple connections using individual publishing but succeeds with batch publishing
    Given a list of 3 notices to be published
    When publishing each notice individually in a sftp publisher with threshold of 2 notices
    Then 1 notice fail to publish due to connection limits
    When publishing the same notices in batch in a sftp publisher with threshold of 2 notices
    Then all notices are successfully published