Feature: API observability pipeline
  As a QA engineer
  I want every step's network traffic, screenshots and logs captured automatically
  So that a failure is diagnosable straight from the Allure report, without re-running

  Scenario: Verify the public products API responds successfully
    Given I navigate to the "home" page
    When I call the GET API "/api/productsList" from the page
    Then the API response should have status 200
    And the API response field "$.responseCode" should equal 200
