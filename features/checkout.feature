Feature: Checkout
  As a registered shopper
  I want to buy products I've added to my cart
  So that I receive the items I paid for

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
    And I navigate to the "products" page
    And I enter "Dress" into the "search field" on the "products" page
    And I click the "search button" on the "products" page
    And I hover over "Dress" in the "product card" on the "products" page
    And I click "Dress" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    And I click the "proceed to checkout button" on the "cart" page

  Scenario: Place an order end to end
    When I enter "Please deliver in the morning" into the "comment field" on the "checkout" page
    And I click the "place order button" on the "checkout" page
    And I enter "QA Tester" into the "name on card field" on the "payment" page
    And I enter "4242424242424242" into the "card number field" on the "payment" page
    And I enter "123" into the "cvc field" on the "payment" page
    And I enter "12" into the "expiry month field" on the "payment" page
    And I enter "2030" into the "expiry year field" on the "payment" page
    And I click the "pay button" on the "payment" page
    Then the "order success message" on the "payment" page should contain the text "order has been confirmed"
    When I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page
