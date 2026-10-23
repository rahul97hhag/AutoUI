Feature: Scrolling behaviour
  As a visitor
  I want to scroll through the home page
  So that I can browse content and quickly return to the top

  Background:
    Given I navigate to the "home" page
    When I scroll to the "bottom" of the "home" page
    Then I should see the "subscription heading" on the "home" page

  Scenario: Scroll up using the arrow button
    When I click the "scroll up button" on the "home" page
    Then I should see the "hero heading" on the "home" page

  Scenario: Scroll up without the arrow button
    When I scroll to the "top" of the "home" page
    Then I should see the "hero heading" on the "home" page
