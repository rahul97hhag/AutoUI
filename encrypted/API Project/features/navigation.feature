Feature: Site navigation
  As a visitor
  I want to browse static pages and shop by category or brand
  So that I can find test documentation and relevant products

  Scenario: Open the test cases page
    Given I navigate to the "home" page
    When I click the "test cases link" on the "home" page
    Then the current url should contain "/test_cases"
    And the "page title" on the "test cases" page should contain the text "Test Cases"

  Scenario Outline: Browse products by category and subcategory
    Given I navigate to the "home" page
    Then I should see the "category sidebar" on the "home" page
    When I click "<category>" in the "category toggle" on the "home" page
    And I click "<subcategory>" in the "category item" on the "home" page
    Then the "page title" on the "listing" page should contain the text "<category> - <subcategory>"

    Examples:
      | category | subcategory |
      | Women    | Dress       |
      | Men      | Tshirts     |

  Scenario Outline: Browse products by brand
    Given I navigate to the "products" page
    Then I should see the "brands sidebar" on the "products" page
    When I click "<brand>" in the "brand link" on the "products" page
    Then the "page title" on the "listing" page should contain the text "<brand>"

    Examples:
      | brand |
      | Polo  |
      | H&M   |
