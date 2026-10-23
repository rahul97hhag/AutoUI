Feature: Mobile recharge
  As a customer
  I want to recharge my mobile number and reach the payment page for a plan
  So that I can pay for a prepaid recharge pack

  Scenario Outline: Recharge a mobile number and reach the payment page
    Given I navigate to the "recharge" page
    Then I should see the "h1 recharge online heading" on the "recharge" page
    When I enter "<mobile_number>" into the "mobile number field" on the "recharge" page
    And I click the "next button" on the "recharge" page
    Then the current url should contain "/recharge-packs"
    And I should see the "h1 recharge packs heading" on the "recharge packs" page
    When I click the "view details link" on the "recharge packs" page
    Then I should see the "pay button" on the "recharge" page
    When I click the "pay button" on the "recharge" page
    Then the current url should contain "/payment"
    And I should see the "h1 payment options heading" on the "recharge payment" page

    Examples:
      | mobile_number |
      | 9876543210    |
      | 9123456780    |
