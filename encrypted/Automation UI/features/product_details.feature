Feature: Product details and reviews
  As a shopper
  I want to view full product details and leave a review
  So that I can make informed purchase decisions and share feedback

  Background:
    Given I navigate to the "products" page
    When I hover over "first" in the "product card by position" on the "products" page
    And I click "first" in the "view product link by position" on the "products" page

  Scenario: View full product detail information
    Then I should see the "product name" on the "product detail" page
    And the "category text" on the "product detail" page should contain the text "Category"
    And the "price text" on the "product detail" page should contain the text "Rs."
    And the "availability text" on the "product detail" page should contain the text "Availability"
    And the "condition text" on the "product detail" page should contain the text "Condition"
    And the "brand text" on the "product detail" page should contain the text "Brand"

  Scenario: Submit a product review
    When I enter "QA Tester" into the "review name field" on the "product detail" page
    And I enter "qa.tester@example.com" into the "review email field" on the "product detail" page
    And I enter "Great product, exactly as described." into the "review text field" on the "product detail" page
    And I click the "review submit button" on the "product detail" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review"
