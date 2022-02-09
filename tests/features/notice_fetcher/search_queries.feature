# Created by dude at 25/01/2022
Feature: Fetch notices with search query
  The system is able to search for notices so that it knows what is a available


  Scenario Outline: Get all notices for the past period
    Given a TED REST API search endpoint
    And  search query over <start> to <end> period
    When the call to the API is executed
    Then search result set is returned
    And the expected number of result items is between <min> and <max>

    Examples:
      | start      | end        | min  | max  |
      | 2021-01-06 | 2021-01-07 | 1000 | 3000 |
      | 2021-02-06 | 2021-02-09 | 3000 | 9000 |

