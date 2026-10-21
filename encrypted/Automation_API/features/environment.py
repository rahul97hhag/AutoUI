import datetime
import html
import os

REPORT_DIR = "reports"
REPORT_FILE = os.path.join(REPORT_DIR, "report.html")


def before_all(context):
    context.report = {
        "started_at": datetime.datetime.now(),
        "features": [],
    }


def before_feature(context, feature):
    context.report_feature = {
        "name": feature.name,
        "scenarios": [],
    }


def before_scenario(context, scenario):
    context.report_scenario = {
        "name": scenario.name,
        "status": "passed",
        "steps": [],
    }


def after_step(context, step):
    context.report_scenario["steps"].append(
        {
            "keyword": step.keyword,
            "name": step.name,
            "status": step.status.name,
            "duration": step.duration,
            "error": str(step.exception) if step.exception else None,
        }
    )
    if step.status.name == "failed":
        context.report_scenario["status"] = "failed"


def after_scenario(context, scenario):
    context.report_feature["scenarios"].append(context.report_scenario)


def after_feature(context, feature):
    context.report["features"].append(context.report_feature)


def after_all(context):
    context.report["finished_at"] = datetime.datetime.now()
    _write_html_report(context.report)


def _write_html_report(report):
    os.makedirs(REPORT_DIR, exist_ok=True)

    total_steps = passed_steps = failed_steps = 0
    total_scenarios = passed_scenarios = failed_scenarios = 0
    feature_blocks = []

    for feature in report["features"]:
        scenario_blocks = []
        for scenario in feature["scenarios"]:
            total_scenarios += 1
            if scenario["status"] == "passed":
                passed_scenarios += 1
            else:
                failed_scenarios += 1

            step_rows = []
            for step in scenario["steps"]:
                total_steps += 1
                if step["status"] == "passed":
                    passed_steps += 1
                elif step["status"] == "failed":
                    failed_steps += 1

                error_html = ""
                if step["error"]:
                    error_html = f'<pre class="error">{html.escape(step["error"])}</pre>'

                step_rows.append(
                    f'''
                    <li class="step {step["status"]}">
                      <span class="badge {step["status"]}">{step["status"].upper()}</span>
                      <span class="step-text">{html.escape(step["keyword"])} {html.escape(step["name"])}</span>
                      <span class="duration">{step["duration"]:.3f}s</span>
                      {error_html}
                    </li>'''
                )

            scenario_blocks.append(
                f'''
                <div class="scenario {scenario["status"]}">
                  <h3>{html.escape(scenario["name"])}
                    <span class="badge {scenario["status"]}">{scenario["status"].upper()}</span>
                  </h3>
                  <ul class="steps">{"".join(step_rows)}</ul>
                </div>'''
            )

        feature_blocks.append(
            f'''
            <div class="feature">
              <h2>Feature: {html.escape(feature["name"])}</h2>
              {"".join(scenario_blocks)}
            </div>'''
        )

    duration = (report["finished_at"] - report["started_at"]).total_seconds()

    html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>API Automation - Execution Report</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; background: #f4f6f8; margin: 0; padding: 24px; color: #1f2933; }}
  h1 {{ margin-top: 0; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #fff; border-radius: 8px; padding: 16px 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 140px; }}
  .card .value {{ font-size: 28px; font-weight: 700; }}
  .card .label {{ color: #6b7280; font-size: 13px; text-transform: uppercase; }}
  .card.passed .value {{ color: #16a34a; }}
  .card.failed .value {{ color: #dc2626; }}
  .feature {{ background: #fff; border-radius: 8px; padding: 16px 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .scenario {{ border-left: 4px solid #d1d5db; padding-left: 12px; margin: 16px 0; }}
  .scenario.passed {{ border-left-color: #16a34a; }}
  .scenario.failed {{ border-left-color: #dc2626; }}
  .steps {{ list-style: none; padding-left: 0; margin: 8px 0 0 0; }}
  .step {{ padding: 6px 0; border-bottom: 1px solid #f0f0f0; display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; }}
  .step-text {{ font-family: Consolas, monospace; }}
  .duration {{ color: #9ca3af; font-size: 12px; margin-left: auto; }}
  .badge {{ font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; color: #fff; }}
  .badge.passed {{ background: #16a34a; }}
  .badge.failed {{ background: #dc2626; }}
  .badge.skipped, .badge.untested {{ background: #9ca3af; }}
  .error {{ width: 100%; background: #fef2f2; color: #991b1b; padding: 8px; border-radius: 4px; font-size: 12px; overflow-x: auto; }}
  .timestamp {{ color: #6b7280; font-size: 13px; margin-bottom: 24px; }}
</style>
</head>
<body>
  <h1>API Automation &mdash; Execution Report</h1>
  <div class="timestamp">
    Run started: {report["started_at"].strftime("%Y-%m-%d %H:%M:%S")} &nbsp;|&nbsp;
    Duration: {duration:.2f}s
  </div>
  <div class="summary">
    <div class="card"><div class="value">{total_scenarios}</div><div class="label">Scenarios</div></div>
    <div class="card passed"><div class="value">{passed_scenarios}</div><div class="label">Scenarios Passed</div></div>
    <div class="card failed"><div class="value">{failed_scenarios}</div><div class="label">Scenarios Failed</div></div>
    <div class="card"><div class="value">{total_steps}</div><div class="label">Steps</div></div>
    <div class="card passed"><div class="value">{passed_steps}</div><div class="label">Steps Passed</div></div>
    <div class="card failed"><div class="value">{failed_steps}</div><div class="label">Steps Failed</div></div>
  </div>
  {"".join(feature_blocks)}
</body>
</html>'''

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"\nHTML report written to: {os.path.abspath(REPORT_FILE)}")
