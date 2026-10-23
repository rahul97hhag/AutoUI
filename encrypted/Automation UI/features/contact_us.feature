Feature: Contact Us
  As a visitor
  I want to submit the contact us form
  So that the support team can get in touch with me

  Scenario: Submit the contact us form successfully
    Given I navigate to the "contact us" page
    When I enter "QA Tester" into the "name field" on the "contact us" page
    And I enter "qa.tester@example.com" into the "email field" on the "contact us" page
    And I enter "Test automation query" into the "subject field" on the "contact us" page
    And I enter "This is an automated contact us submission." into the "message field" on the "contact us" page
    And I upload the file "utils/fixtures/sample_upload.txt" to the "upload field" on the "contact us" page
    And I accept the confirmation dialog
    And I click the "submit button" on the "contact us" page
    Then the "success message" on the "contact us" page should contain the text "submitted successfully"
    When I click the "home button" on the "contact us" page
    Then I should see the "hero heading" on the "home" page
