Feature: Recharge Plans API

  Background:
    Given the API base URL is "http://127.0.0.1:5000/api"

  Scenario: Health check reports ok
    When I check the API health
    Then the response status should be 200
    And the response JSON path "$.status" should equal "ok"

  Scenario: Listing all plans returns summaries with benefit names only
    When I request the list of all plans
    Then the response status should be 200
    And the response matches the plan list schema
    And the response JSON path "$[0].name" should equal "30GB + Top OTTs"

  Scenario: Fetching a single plan returns full benefit details
    When I request plan "1"
    Then the response status should be 200
    And the response matches the plan detail schema
    And the response JSON path "$.name" should equal "30GB + Top OTTs"
    And the response JSON path "$.benefits[0].id" should equal 1
    And the response JSON path "$.benefits[0].name" should equal "Prime Video Mobile Edition"

  Scenario: Fetching a plan that does not exist returns 404
    When I request plan "999999"
    Then the response status should be 404
    And the response matches the error schema
    And the response JSON path "$.message" should equal "Plan not found"

  Scenario: Fetching review notes for a benefit that has notes
    When I request review notes for benefit "7"
    Then the response status should be 200
    And the response JSON path "$[0].plan_name" should equal "Aha Premium + 18 OTTs on Airtel Xstream Play"

  Scenario: Fetching review notes for a benefit that does not exist returns 404
    When I request review notes for benefit "999999"
    Then the response status should be 404
    And the response matches the error schema
    And the response JSON path "$.message" should equal "Benefit not found"
