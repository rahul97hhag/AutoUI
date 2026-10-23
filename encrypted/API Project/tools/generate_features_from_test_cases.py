"""Batch-generate a Gherkin feature file directly from a raw test-cases text
file, using the trained TF-IDF step-retrieval model (tools/step_model.pkl).

This is the "nobody hand-writes Gherkin" pipeline: paste scraped test cases
into a text file in the same "Test Case N: Title" / numbered-steps format as
test_cases.txt, run this script, and get a ready .feature file assembled
entirely from the existing generic step library -- one Scenario per test
case, one Gherkin line per numbered step.

It reuses exactly the same retrieval/substitution engine as
generate_scenario.py (one raw step line = one "action" lookup), just applied
to every step of every test case in the file at once instead of one typed
line at a time.

IMPORTANT LIMIT: this can only emit steps that already exist in THIS
application's generic step vocabulary and locators.yaml registry. Point it at
a test_cases.txt scraped from a different site (Amazon, Google, ...) and it
will still run and still produce a .feature file -- but every line will be a
low-confidence guess against automationexercise.com's own step corpus, because
that site's pages/buttons/fields were never registered in locators.yaml. The
retrieval *approach* is site-agnostic; the locator *registry* is not. Reusing
this for a different application means building that application's own
locators.yaml and generic steps first (or swapping in role/text-based
Playwright locators that don't need a registry), then retraining the model
on it -- this script only automates the "test case -> Gherkin" half.

Usage:
  python tools/generate_features_from_test_cases.py test_cases.txt --out features/generated_test_cases.feature
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_scenario import (  # noqa: E402
    classify_keyword,
    data_slot_index,
    extract_quoted_values,
    load_model,
    match_action,
    substitute_data_slot,
)
from test_case_mapper import parse_test_cases  # noqa: E402

LOW_CONFIDENCE = 0.25
SKIP_STEPS = {"launch browser"}  # preconditions with no automatable action, not real gaps


def build_scenario_lines(model, steps):
    lines = []
    previous_keyword = None
    for step in steps:
        if step["text"].strip().lower() in SKIP_STEPS:
            continue

        ranked = match_action(model, step["text"])
        score, best = ranked[0]
        step_text = best["text"]

        values = extract_quoted_values(step["text"])
        if len(values) == 1:
            idx = data_slot_index(step_text)
            if idx is not None:
                step_text = substitute_data_slot(step_text, idx, values[0])

        keyword = classify_keyword(step_text)
        display_keyword = "And" if keyword == previous_keyword else keyword
        previous_keyword = keyword
        lines.append((display_keyword, step_text, score, step))
    return lines


def group_by_test_case(raw_items):
    by_tc, order = {}, []
    for item in raw_items:
        if item["tc"] not in by_tc:
            by_tc[item["tc"]] = {"title": item["title"], "steps": []}
            order.append(item["tc"])
        by_tc[item["tc"]]["steps"].append(item)
    return by_tc, order


def generate_feature(test_cases_path, feature_name="Generated test cases"):
    model = load_model()
    raw_items = parse_test_cases(test_cases_path)
    by_tc, order = group_by_test_case(raw_items)

    scenario_blocks = []
    low_confidence_report = []
    for tc in order:
        entry = by_tc[tc]
        lines = build_scenario_lines(model, entry["steps"])
        if not lines:
            continue
        body = "\n".join(f"    {kw} {text}" for kw, text, score, _ in lines)
        scenario_blocks.append(f"  Scenario: {entry['title']}\n{body}")
        for kw, text, score, step in lines:
            if score < LOW_CONFIDENCE:
                low_confidence_report.append((tc, step["step_no"], step["text"], score, text))

    feature_text = f"Feature: {feature_name}\n\n" + "\n\n".join(scenario_blocks) + "\n"
    return feature_text, low_confidence_report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("test_cases_file", help="Raw test cases text file (same format as test_cases.txt)")
    parser.add_argument("--out", default=None, help="Where to write the generated .feature file")
    parser.add_argument("--name", default="Generated test cases", help="Feature: name to use")
    args = parser.parse_args()

    feature_text, low_confidence = generate_feature(Path(args.test_cases_file), args.name)

    if args.out:
        Path(args.out).write_text(feature_text, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(feature_text)

    if low_confidence:
        print(f"\n{len(low_confidence)} low-confidence lines (score < {LOW_CONFIDENCE}) -- review before trusting these:")
        for tc, step_no, raw_text, score, matched in low_confidence:
            print(f'  TC{tc}.{step_no} [{score:.2f}] "{raw_text}"')
            print(f"    -> {matched}")


if __name__ == "__main__":
    main()
