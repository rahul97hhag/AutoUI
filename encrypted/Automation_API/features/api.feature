Feature: API Automation

  Scenario: Call an API and print its response
    Given I want to run "https://jsonplaceholder.typicode.com/posts/1" api
    When I run the api
    Then I print the response of the "https://jsonplaceholder.typicode.com/posts/1" api
