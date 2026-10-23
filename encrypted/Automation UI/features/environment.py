import os

from playwright.sync_api import sync_playwright

from config.config_reader import get_config
from utils.logger import get_logger, get_root_logger
from utils.network_recorder import NetworkRecorder
from utils.allure_helpers import ListLogHandler, attach_screenshot, attach_logs, attach_network_trace

logger = get_logger(__name__)


def before_all(context):
    context.config_data = get_config()
    context.playwright = sync_playwright().start()
    browser_type = getattr(context.playwright, context.config_data["browser"])
    context.browser = browser_type.launch(
        headless=context.config_data["headless"],
        slow_mo=context.config_data.get("slow_mo", 0),
    )
    logger.info(
        f"Launched {context.config_data['browser']} browser "
        f"(headless={context.config_data['headless']})"
    )


def before_scenario(context, scenario):
    context.browser_context = context.browser.new_context(
        base_url=context.config_data["base_url"],
        viewport=context.config_data["viewport"],
    )
    context.browser_context.set_default_timeout(context.config_data["timeout"])
    context.page = context.browser_context.new_page()
    context.network_recorder = NetworkRecorder()
    context.network_recorder.attach(context.page)
    logger.info(f"Starting scenario: {scenario.name}")


def before_step(context, step):
    logger.info(f"STEP START: {step.keyword} {step.name}")
    # Mark where this step's network activity starts (see NetworkRecorder.
    # since() -- the history itself is never cleared mid-scenario, so a
    # later step's assert_response() can still look back at a response an
    # earlier step triggered) and start collecting this step's logs.
    context._network_mark = context.network_recorder.mark()
    context._step_log_handler = ListLogHandler()
    get_root_logger().addHandler(context._step_log_handler)


def after_step(context, step):
    if step.status.name == "failed":
        logger.error(f"STEP FAILED: {step.keyword} {step.name}")
    else:
        logger.info(f"STEP {step.status.name.upper()}: {step.keyword} {step.name}")

    # Each capture is independently guarded so a failure in one (e.g. the
    # page having already navigated away) can't suppress the others -- all
    # three must come through regardless of whether the step passed or
    # failed, since after_step itself always runs either way.
    if context.config_data.get("capture_step_screenshots", True):
        try:
            attach_screenshot(context.page, name="screenshot")
        except Exception:
            logger.exception("Failed to capture step screenshot")

    try:
        get_root_logger().removeHandler(context._step_log_handler)
        attach_logs(context._step_log_handler, name="step_logs")
    except Exception:
        logger.exception("Failed to attach step logs")

    if context.config_data.get("capture_network", True):
        try:
            attach_network_trace(context.network_recorder.since(context._network_mark), name="network_trace")
        except Exception:
            logger.exception("Failed to attach network trace")


def after_scenario(context, scenario):
    if scenario.status == "failed":
        screenshot_dir = "reports/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in scenario.name)
        screenshot_path = f"{screenshot_dir}/{safe_name}.png"
        context.page.screenshot(path=screenshot_path)
        logger.error(f"Scenario failed: {scenario.name}. Screenshot saved to {screenshot_path}")
        if hasattr(context, "embed"):
            with open(screenshot_path, "rb") as f:
                context.embed("image/png", f.read())

    context.page.close()
    context.browser_context.close()
    logger.info(f"Finished scenario: {scenario.name}")


def after_all(context):
    context.browser.close()
    context.playwright.stop()
    logger.info("Browser closed, Playwright stopped")
