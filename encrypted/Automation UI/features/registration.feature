Feature: Account registration and login
  As a new visitor
  I want to create an account, log in and log out
  So that I can place orders under my own identity

  Background:
    Given I navigate to the "home" page
    When I click the "signup login link" on the "home" page
    And I enter "{{random_name}}" into the "signup name field" on the "login" page
    And I enter "{{random_email}}" into the "signup email field" on the "login" page
    And I click the "signup button" on the "login" page
    And I check the "title mr radio" on the "account" page
    And I enter "Test@1234" into the "password field" on the "account" page
    And I select "10" from the "days dropdown" on the "account" page
    And I select "5" from the "months dropdown" on the "account" page
    And I select "1995" from the "years dropdown" on the "account" page
    And I check the "newsletter checkbox" on the "account" page
    And I check the "special offers checkbox" on the "account" page
    And I enter "QA" into the "first name field" on the "account" page
    And I enter "Tester" into the "last name field" on the "account" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I select "United States" from the "country dropdown" on the "account" page
    And I enter "California" into the "state field" on the "account" page
    And I enter "Los Angeles" into the "city field" on the "account" page
    And I enter "90001" into the "zipcode field" on the "account" page
    And I enter "9999999999" into the "mobile number field" on the "account" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page

  Scenario: Register a new account and delete it
    Then I should see "{{generated.name}}" in the "logged in as label" on the "home" page
    When I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page

  Scenario: Login with correct credentials
    When I click the "logout link" on the "home" page
    And I click the "signup login link" on the "home" page
    And I enter "{{generated.email}}" into the "login email field" on the "login" page
    And I enter "Test@1234" into the "login password field" on the "login" page
    And I click the "login button" on the "login" page
    Then I should see "{{generated.name}}" in the "logged in as label" on the "home" page
    When I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page

  Scenario: Login with incorrect credentials shows an error
    When I click the "logout link" on the "home" page
    And I click the "signup login link" on the "home" page
    And I enter "wrong.email@example.com" into the "login email field" on the "login" page
    And I enter "WrongPass123" into the "login password field" on the "login" page
    And I click the "login button" on the "login" page
    Then the "login error message" on the "login" page should contain the text "incorrect"
    # cleanup: log back in to delete the account created in the Background
    When I enter "{{generated.email}}" into the "login email field" on the "login" page
    And I enter "Test@1234" into the "login password field" on the "login" page
    And I click the "login button" on the "login" page
    And I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page

  Scenario: Logout returns to the login page
    When I click the "logout link" on the "home" page
    Then the current url should contain "/login"
    # cleanup: log back in to delete the account created in the Background
    When I click the "signup login link" on the "home" page
    And I enter "{{generated.email}}" into the "login email field" on the "login" page
    And I enter "Test@1234" into the "login password field" on the "login" page
    And I click the "login button" on the "login" page
    And I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page

  Scenario: Register with an already-registered email shows an error
    When I click the "logout link" on the "home" page
    And I click the "signup login link" on the "home" page
    And I enter "Another Name" into the "signup name field" on the "login" page
    And I enter "{{generated.email}}" into the "signup email field" on the "login" page
    And I click the "signup button" on the "login" page
    Then the "signup error message" on the "login" page should contain the text "already exist"
    # cleanup: log back in to delete the account created in the Background
    When I enter "{{generated.email}}" into the "login email field" on the "login" page
    And I enter "Test@1234" into the "login password field" on the "login" page
    And I click the "login button" on the "login" page
    And I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page
