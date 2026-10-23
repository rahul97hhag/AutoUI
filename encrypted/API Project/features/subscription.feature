Feature: Newsletter subscription
  As a visitor
  I want to subscribe to the newsletter from the footer
  So that I can receive updates from the site

  Scenario Outline: Subscribe to the newsletter from the footer
    Given I navigate to the "<page>" page
    When I scroll to the "bottom" of the "<page>" page
    Then I should see the "subscription heading" on the "<page>" page
    When I enter "qa.subscriber@example.com" into the "subscribe email field" on the "<page>" page
    And I click the "subscribe button" on the "<page>" page
    Then the "subscribe success message" on the "<page>" page should contain the text "subscribed"

    Examples:
      | page |
      | home |
      | cart |
