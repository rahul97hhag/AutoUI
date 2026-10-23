"""Parse a behave `-f plain` run log into a structured list of failures:
which scenario, which step, and why. Used to turn a wall of console output
into an actual reviewable report instead of scrolling a terminal.

Usage:
  python tools/parse_failures.py path/to/behave_run_log.txt [--html path/to/report.html]
"""
import argparse
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HTML_PATH = ROOT / "reports" / "generated_test_cases_failures.html"

SCENARIO_RE = re.compile(r"^\s*Scenario(?: Outline)?: (.+?)\s*$")
STEP_RE = re.compile(r"^\s{4}(Given|When|Then|And|But) (.+?)\s*\.\.\.\s*(passed|failed|skipped|undefined)")
SUMMARY_RE = re.compile(r"^\d+ (?:features?|scenarios?|steps?) ")
LOG_LINE_RE = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")


def parse_log(path):
    """Return a list of {scenario, step_keyword, step_text, status, error} per step."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    results = []
    current_scenario = None
    i = 0
    while i < len(lines):
        line = lines[i]
        scenario_match = SCENARIO_RE.match(line)
        if scenario_match:
            current_scenario = scenario_match.group(1)
            i += 1
            continue

        step_match = STEP_RE.match(line)
        if step_match:
            keyword, text, status = step_match.groups()
            error_block = []
            if status == "failed":
                # behave prints either a one-line "Assertion Failed: ..." or a full Python
                # traceback right after the failed step, ending where behave's own
                # timestamped logger output resumes (sometimes with a blank line first,
                # sometimes not -- so stop on either, not just a blank line).
                j = i + 1
                while j < len(lines) and lines[j].strip() and not LOG_LINE_RE.match(lines[j]):
                    error_block.append(lines[j])
                    j += 1
                i = j
            else:
                i += 1
            results.append(
                {
                    "scenario": current_scenario,
                    "keyword": keyword,
                    "text": text,
                    "status": status,
                    "error": _extract_exception_line(error_block),
                }
            )
            continue
        i += 1
    return results


def _extract_exception_line(error_block):
    """Python tracebacks end with an un-indented '<Type>: <message>' line -- that's the
    actual reason, as opposed to the indented stack-frame listing above it. Behave's
    one-line "Assertion Failed: ..." shorthand is already in that same unindented form."""
    skip_markers = {"Traceback (most recent call last):", "Call log:"}
    for raw in reversed(error_block):
        if not raw.strip():
            continue
        if raw.startswith((" ", "\t")) or raw.strip() in skip_markers:
            continue
        return raw.strip()
    return " / ".join(line.strip() for line in error_block if line.strip())


def summarize(results):
    scenarios = {}
    for row in results:
        scenarios.setdefault(row["scenario"], []).append(row)

    failures = []
    for scenario, steps in scenarios.items():
        for step in steps:
            if step["status"] == "failed":
                failures.append({**step})
                break  # behave stops a scenario at its first failure

    passed_scenarios = sum(1 for steps in scenarios.values() if all(s["status"] == "passed" for s in steps))
    return scenarios, failures, passed_scenarios


def print_report(scenarios, failures, passed_scenarios):
    print(f"{len(scenarios)} scenarios: {passed_scenarios} passed, {len(failures)} failed\n")
    for fail in failures:
        print(f"Scenario: {fail['scenario']}")
        print(f"  Failed at: {fail['keyword']} {fail['text']}")
        print(f"  Reason:    {fail['error']}")
        print()


def write_html_report(scenarios, failures, passed_scenarios, out_path):
    def esc(text):
        return html.escape(text, quote=True)

    rows = []
    for fail in failures:
        rows.append(
            f"<tr><td>{esc(fail['scenario'])}</td>"
            f"<td><code>{esc(fail['keyword'])} {esc(fail['text'])}</code></td>"
            f"<td><code>{esc(fail['error'])}</code></td></tr>"
        )
    rows_html = "\n".join(rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Failed steps report</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
  h1 {{ font-size: 1.4rem; }}
  .stats {{ display: flex; gap: 1.5rem; margin: 1rem 0 2rem; flex-wrap: wrap; }}
  .stat {{ background: rgba(127,127,127,0.1); border-radius: 8px; padding: 0.75rem 1.25rem; }}
  .stat .value {{ font-size: 1.6rem; font-weight: 700; display: block; }}
  .stat .label {{ font-size: 0.8rem; opacity: 0.7; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
  th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid rgba(127,127,127,0.25); vertical-align: top; }}
  th {{ position: sticky; top: 0; background: Canvas; }}
  code {{ font-size: 0.82rem; }}
  tr:nth-child(even) {{ background: rgba(127,127,127,0.06); }}
</style>
</head>
<body>
  <h1>Generated feature file &mdash; failed steps</h1>
  <div class="stats">
    <div class="stat"><span class="value">{len(scenarios)}</span><span class="label">scenarios run</span></div>
    <div class="stat"><span class="value">{passed_scenarios}</span><span class="label">passed</span></div>
    <div class="stat"><span class="value">{len(failures)}</span><span class="label">failed</span></div>
  </div>
  <table>
    <thead><tr><th>Scenario</th><th>Failed on step</th><th>Reason</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_file", help="Path to a behave run's -f plain console output")
    parser.add_argument("--html", nargs="?", const=str(DEFAULT_HTML_PATH), default=None,
                         help=f"Also write an HTML report (default: {DEFAULT_HTML_PATH})")
    args = parser.parse_args()

    results = parse_log(Path(args.log_file))
    scenarios, failures, passed_scenarios = summarize(results)
    print_report(scenarios, failures, passed_scenarios)

    if args.html:
        out_path = Path(args.html)
        write_html_report(scenarios, failures, passed_scenarios, out_path)
        print(f"HTML report written to {out_path.resolve()}")


if __name__ == "__main__":
    main()
