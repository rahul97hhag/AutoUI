# Automation UI

Python UI automation framework: Playwright + Behave (BDD) + Page Object Model.
Currently exercises [automationexercise.com](https://automationexercise.com), a public ecommerce demo site built for automation practice.

## Project layout

```
config/            base_url, browser, headless, timeout, viewport
pages/              Page Object Model classes (one per page/component)
features/*.feature  Gherkin scenarios
features/steps/     step definitions, mapped to pages
features/environment.py   Behave hooks: browser/context lifecycle, screenshot-on-failure
utils/              logger, test data generators
reports/screenshots failure screenshots (auto-created)
```

## Setup

```powershell
py -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
./venv/Scripts/python.exe -m playwright install chromium --with-deps
```

## Running tests

```powershell
# full suite, headless
./venv/Scripts/python.exe -m behave

# a single feature
./venv/Scripts/python.exe -m behave features/checkout.feature

# headed, in Firefox, against a different base URL
HEADLESS=false BROWSER=firefox BASE_URL=https://automationexercise.com ./venv/Scripts/python.exe -m behave
```

Config can also be edited directly in [config/config.yaml](config/config.yaml); env vars `BROWSER`, `HEADLESS`, `BASE_URL` override it.

## Adding a new page/flow

1. Add a page object in `pages/`, subclassing `BasePage` (locators as class constants, actions as methods — no assertions).
2. Write a `.feature` file describing the behavior in Gherkin.
3. Add step definitions in `features/steps/` that call page object methods and assert on results.

## Notes

- Each failed scenario saves a screenshot to `reports/screenshots/`.
- Registration/checkout scenarios create a fresh account per run (`utils/test_data.py`) to avoid collisions.
- The live demo site occasionally rate-limits rapid signups; a registration-related failure that doesn't reproduce on retry is a site flake, not a framework bug.
