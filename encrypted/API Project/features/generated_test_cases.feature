Feature: Generated test cases

  Scenario: Register User
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "signup button" on the "login" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "signup button" on the "login" page
    And I enter "ENTER ACCOUNT INFORMATION" into the "message field" on the "contact us" page
    And I enter "{{generated.email}}" into the "signup email field" on the "login" page
    And I check the "newsletter checkbox" on the "account" page
    And I check the "special offers checkbox" on the "account" page
    And I enter "Tester" into the "last name field" on the "account" page
    And I click the "create account button" on the "account" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Login User with correct email and password
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "login button" on the "login" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "login button" on the "login" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click the "delete account link" on the "home" page
    Then I should see the "account deleted heading" on the "account" page

  Scenario: Login User with incorrect email and password
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "login button" on the "login" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "login button" on the "login" page
    Then the "login error message" on the "login" page should contain the text "Your email or password is incorrect!"

  Scenario: Logout User
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "login button" on the "login" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "login button" on the "login" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click the "logout link" on the "home" page
    And I click the "login button" on the "login" page

  Scenario: Register User with existing email
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "signup button" on the "login" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "signup button" on the "login" page
    Then the "signup error message" on the "login" page should contain the text "Email Address already exist!"

  Scenario: Contact Us Form
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "home button" on the "contact us" page
    And I enter "GET IN TOUCH" into the "message field" on the "contact us" page
    And I enter "{{generated.email}}" into the "signup email field" on the "login" page
    And I upload the file "utils/fixtures/sample_upload.txt" to the "upload field" on the "contact us" page
    And I click the "submit button" on the "contact us" page
    And I click the "signup button" on the "login" page
    Then the "success message" on the "contact us" page should contain the text "Success! Your details have been submitted successfully."
    Given I navigate to the "home" page

  Scenario: Verify Test Cases Page
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "test cases link" on the "home" page
    Then the "page title" on the "test cases" page should contain the text "Test Cases"

  Scenario: Verify All Products and product detail page
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "search button" on the "products" page
    Given I navigate to the "products" page
    When I enter "This is an automated contact us submission." into the "message field" on the "contact us" page
    And I click "View Product" in the "view product link by position" on the "products" page
    Then I should see the "product name" on the "product detail" page
    And the "availability text" on the "product detail" page should contain the text "Availability"

  Scenario: Search Product
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "search button" on the "products" page
    Given I navigate to the "products" page
    When I click the "search button" on the "products" page
    Then the "results title" on the "products" page should contain the text "SEARCHED PRODUCTS"
    When I click the "search button" on the "products" page

  Scenario: Verify Subscription in home page
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I scroll to the "top" of the "home" page
    Then I should see the "subscription heading" on the "home" page
    When I enter "123 Test Street" into the "address field" on the "account" page
    Then the "success message" on the "contact us" page should contain the text "You have been successfully subscribed!"

  Scenario: Verify Subscription in Cart page
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click "Cart" in the "cart row remove button" on the "cart" page
    And I scroll to the "top" of the "home" page
    Then I should see the "subscription heading" on the "home" page
    When I enter "123 Test Street" into the "address field" on the "account" page
    Then the "success message" on the "contact us" page should contain the text "You have been successfully subscribed!"

  Scenario: Add Products in Cart
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "search button" on the "products" page
    And I hover over "Add to cart" in the "product card by position" on the "products" page
    And I click the "continue shopping button" on the "products" page
    And I click "Add to cart" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    And I click "Dress" in the "add to cart link" on the "products" page
    Then the "price text" on the "product detail" page should contain the text "Rs."

  Scenario: Verify Product quantity in Cart
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click "View Product" in the "view product link by position" on the "products" page
    Then I should see the "product name" on the "product detail" page
    Given I navigate to the "products" page
    When I click "Add to cart" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page

  Scenario: Place Order: Register while Checkout
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    And I click the "login button" on the "login" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click "Cart" in the "cart row remove button" on the "cart" page
    And I click the "proceed to checkout button" on the "cart" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review"
    When I click the "place order button" on the "checkout" page
    And I enter "4242424242424242" into the "card number field" on the "payment" page
    And I click the "pay button" on the "payment" page
    Then the "order success message" on the "payment" page should contain the text "Your order has been placed successfully!"
    When I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Place Order: Register before Checkout
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review"
    When I click the "place order button" on the "checkout" page
    And I enter "4242424242424242" into the "card number field" on the "payment" page
    And I click the "pay button" on the "payment" page
    Then the "order success message" on the "payment" page should contain the text "Your order has been placed successfully!"
    When I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Place Order: Login before Checkout
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "login button" on the "login" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review"
    When I click the "place order button" on the "checkout" page
    And I enter "4242424242424242" into the "card number field" on the "payment" page
    And I click the "pay button" on the "payment" page
    Then the "order success message" on the "payment" page should contain the text "Your order has been placed successfully!"
    When I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Remove Products From Cart
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page

  Scenario: View Category Products
    Given I navigate to the "products" page
    When I enter "QA Tester" into the "name on card field" on the "payment" page
    Then the "category text" on the "product detail" page should contain the text "Women"
    And the "category text" on the "product detail" page should contain the text "Women"
    And the "category text" on the "product detail" page should contain the text "WOMEN - TOPS PRODUCTS"
    And the "category text" on the "product detail" page should contain the text "Men"
    And the "category text" on the "product detail" page should contain the text "Category"

  Scenario: View & Cart Brand Products
    Given I navigate to the "products" page
    When I click the "search button" on the "products" page
    Then I should see the "brands sidebar" on the "products" page
    And the "brand text" on the "product detail" page should contain the text "Brand"
    And the "brand text" on the "product detail" page should contain the text "Brand"
    And the "brand text" on the "product detail" page should contain the text "Brand"
    And the "brand text" on the "product detail" page should contain the text "Brand"

  Scenario: Search Products and Verify Cart After Login
    Given I navigate to the "products" page
    When I click the "search button" on the "products" page
    Given I navigate to the "products" page
    When I click the "search button" on the "products" page
    Then the "results title" on the "products" page should contain the text "SEARCHED PRODUCTS"
    When I click the "search button" on the "products" page
    And I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    And I click the "signup button" on the "login" page
    And I click the "proceed to checkout button" on the "cart" page
    Then I should see "{{generated.name}}" in the "logged in as label" on the "home" page

  Scenario: Add review on product
    Given I navigate to the "products" page
    When I click the "search button" on the "products" page
    Given I navigate to the "products" page
    When I click "View Product" in the "view product link by position" on the "products" page
    Then the "review success message" on the "product detail" page should contain the text "Write Your Review"
    When I enter "QA Tester" into the "review name field" on the "product detail" page
    And I click the "submit button" on the "contact us" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review."

  Scenario: Add to cart from Recommended items
    Given I navigate to the "products" page
    When I scroll to the "bottom" of the "home" page
    And I scroll to the "top" of the "home" page
    And I click "Add To Cart" in the "add to cart link" on the "products" page
    And I click the "view cart modal link" on the "products" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page

  Scenario: Verify address details in checkout page
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "signup button" on the "login" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I enter "123 Test Street" into the "address field" on the "account" page
    And I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Download Invoice after purchase order
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click "Dress" in the "add to cart link" on the "products" page
    And I click "Cart" in the "cart row remove button" on the "cart" page
    Then I should see "Blue Top" in the "cart row" on the "cart" page
    When I click the "proceed to checkout button" on the "cart" page
    And I click the "login button" on the "login" page
    And I click the "create account button" on the "account" page
    And I click the "continue button" on the "account" page
    Then I should see "Logged in as username" in the "logged in as label" on the "home" page
    When I click "Cart" in the "cart row remove button" on the "cart" page
    And I click the "proceed to checkout button" on the "cart" page
    Then the "review success message" on the "product detail" page should contain the text "Thank you for your review"
    When I click the "place order button" on the "checkout" page
    And I enter "4242424242424242" into the "card number field" on the "payment" page
    And I click the "pay button" on the "payment" page
    Then the "order success message" on the "payment" page should contain the text "Your order has been placed successfully!"
    When I click the "signup button" on the "login" page
    And I click the "continue button" on the "account" page
    And I click the "delete account link" on the "home" page
    And I click the "continue button" on the "account" page

  Scenario: Verify Scroll Up using 'Arrow' button and Scroll Down functionality
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I scroll to the "bottom" of the "home" page
    Then I should see the "subscription heading" on the "home" page
    When I scroll to the "bottom" of the "home" page
    And I enter "Full-Fledged practice website for Automation Engineers" into the "message field" on the "contact us" page

  Scenario: Verify Scroll Up without 'Arrow' button and Scroll Down functionality
    Given I navigate to the "products" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I scroll to the "bottom" of the "home" page
    Then I should see the "subscription heading" on the "home" page
    When I click the "scroll up button" on the "home" page
    And I enter "Full-Fledged practice website for Automation Engineers" into the "message field" on the "contact us" page
