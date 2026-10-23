Feature: Product search
  As a shopper
  I want to search for products
  So that I can find items I'm interested in buying

  Scenario Outline: Searching for a product returns matching results
    Given I navigate to the "products" page
    When I enter "<product>" into the "search field" on the "products" page
    And I click the "search button" on the "products" page
    Then the "results title" on the "products" page should contain the text "Searched Products"
    And I should see "<product>" in the "product card" on the "products" page

    Examples:
      | product |
      | Dress   |
      | Top     |
      | Jeans   |
      | Tshirt  |
