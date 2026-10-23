Feature: Login API

  As an API consumer
  I want to authenticate against the login endpoint
  So that I receive a token to use for subsequent authorized calls

  Background:
    Given the API base URL is "https://reqres.in/api"

  Scenario: Successful login returns a token
    When I log in with email "eve.holt@reqres.in" and password "cityslicker"
    Then the response status should be 200
    And the response JSON path "$.token" should equal "QpwL5tke4Pnpja7X4"

  Scenario: Login without a password is rejected
    When I log in with email "eve.holt@reqres.in" and no password
    Then the response status should be 400
    And the response JSON path "$.error" should equal "Missing password"

  Scenario: Successful login response matches the expected schema
    When I log in with email "eve.holt@reqres.in" and password "cityslicker"
    Then the response matches the login success schema
