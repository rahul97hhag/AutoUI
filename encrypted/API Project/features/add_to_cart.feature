Feature: Add products to cart
  As a shopper
  I want to add products to my cart and remove them
  So that I can purchase the items I actually want

  Background:
    Given I navigate to the "products" page

  Scenario Outline: Add a product to the cart from the products page
    When I hover over "<product>" in the "product card" on the "products" page
    And I click "<product>" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    Then I should see "<product>" in the "cart row" on the "cart" page

    Examples:
      | product    |
      | Blue Top   |
      | Men Tshirt |

  Scenario: Add multiple products to the cart in one session
    When I hover over "Blue Top" in the "product card" on the "products" page
    And I click "Blue Top" in the "add to cart link" on the "products" page
    And I click the "continue shopping button" on the "products" page
    And I hover over "Men Tshirt" in the "product card" on the "products" page
    And I click "Men Tshirt" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    And I should see "Men Tshirt" in the "cart row" on the "cart" page

  Scenario: Continue shopping after adding a product
    When I hover over "Men Tshirt" in the "product card" on the "products" page
    And I click "Men Tshirt" in the "add to cart link" on the "products" page
    And I click the "continue shopping button" on the "products" page
    Then the current url should contain "/products"

  Scenario: Remove a product from the cart
    When I hover over "Blue Top" in the "product card" on the "products" page
    And I click "Blue Top" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    And I click "Blue Top" in the "cart row remove button" on the "cart" page
    Then I should not see "Blue Top" in the "cart row" on the "cart" page
