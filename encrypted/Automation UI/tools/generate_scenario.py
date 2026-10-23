"""Natural-language -> Gherkin scenario generator.

Loads the TF-IDF model trained by tools/train_step_model.py and, given a
free-text description of what a tester wants to do, finds the closest
matching generic step for each described action and assembles a ready
Scenario block using real step phrasing from features/steps/generic_steps.py.

This is retrieval, not generation: it can only emit steps that already exist
in the step library. A low match score means "the library has no step for
this yet" -- treat that as a prompt to add a new generic step or locator
alias, not as something to trust blindly.

Input convention: separate each distinct action with "then", a period, or a
semicolon -- e.g. "Go to the products page, then search for Dress, then add
it to the cart." One free-text chunk per desired Gherkin line.

Usage:
  python tools/generate_scenario.py --text "Register a new user, then login, then logout"
  python tools/generate_scenario.py                                  # interactive chat prompt
  python tools/generate_scenario.py --text "..." --save features/my_new.feature
"""
import argparse
import pickle
import re
import sys
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

MODEL_PATH = Path(__file__).resolve().parent / "step_model.pkl"
LOW_CONFIDENCE = 0.25
AMBIGUOUS_MARGIN = 0.08

SEGMENT_RE = re.compile(r"\s*(?:,?\s*then\s+|[.;]\s+)", re.IGNORECASE)
QUOTED_VALUE_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')
QUOTED_SPAN_RE = re.compile(r'"[^"]*"')

# Which quoted slot (0-indexed, left to right) in a matched step is user-supplied DATA,
# as opposed to the structural element/page/dropdown name chosen by the retrieval match.
# None means the step has no data slot at all -- every quote in it is structural.
# This mirrors the exact step shapes defined in features/steps/generic_steps.py; if that
# file's step wording changes, these patterns need to change with it.
STEP_SHAPES = [
    (re.compile(r'^I navigate to the "[^"]*" page$'), None),
    (re.compile(r'^I click the "[^"]*" on the "[^"]*" page$'), None),
    (re.compile(r'^I click "[^"]*" in the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I hover over "[^"]*" in the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I enter "[^"]*" into the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I select "[^"]*" from the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I check the "[^"]*" on the "[^"]*" page$'), None),
    (re.compile(r'^I upload the file "[^"]*" to the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I scroll to the "[^"]*" of the "[^"]*" page$'), None),
    (re.compile(r'^I accept the confirmation dialog$'), None),
    (re.compile(r'^I should see the "[^"]*" on the "[^"]*" page$'), None),
    (re.compile(r'^I should see "[^"]*" in the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^I should not see the "[^"]*" on the "[^"]*" page$'), None),
    (re.compile(r'^I should not see "[^"]*" in the "[^"]*" on the "[^"]*" page$'), 0),
    (re.compile(r'^the "[^"]*" on the "[^"]*" page should contain the text "[^"]*"$'), 2),
    (re.compile(r'^the current url should contain "[^"]*"$'), 0),
]


def extract_quoted_values(text):
    """Return every 'value' or "value" the user typed, in order of appearance."""
    return [single or double for double, single in QUOTED_VALUE_RE.findall(text)]


def data_slot_index(step_text):
    for pattern, idx in STEP_SHAPES:
        if pattern.match(step_text):
            return idx
    return None  # unrecognized shape -- don't guess, leave the matched step's own data alone


def substitute_data_slot(step_text, idx, value):
    spans = list(QUOTED_SPAN_RE.finditer(step_text))
    if idx >= len(spans):
        return step_text
    span = spans[idx]
    return step_text[: span.start()] + f'"{value}"' + step_text[span.end() :]


def load_model():
    if not MODEL_PATH.exists():
        sys.exit(f"No trained model at {MODEL_PATH} -- run tools/train_step_model.py first.")
    # train_step_model.py pickles a vectorizer whose tokenizer is
    # test_case_mapper.tokenize, so that sibling module must be importable.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def split_into_actions(text):
    parts = SEGMENT_RE.split(text.strip())
    return [p.strip().rstrip(".") for p in parts if p.strip()]


def classify_keyword(step_text):
    """Infer the Gherkin keyword a matched step was written under in generic_steps.py."""
    if step_text.startswith("I navigate"):
        return "Given"
    if step_text.startswith("I should") or step_text.startswith("the "):
        return "Then"
    return "When"


def match_action(model, action_text, top_n=3):
    vectorizer, matrix, items = model["vectorizer"], model["matrix"], model["items"]
    vec = vectorizer.transform([action_text])
    sims = cosine_similarity(vec, matrix)[0]
    ranked_idx = sims.argsort()[::-1][:top_n]
    return [(float(sims[i]), items[i]) for i in ranked_idx]


def generate_scenario(model, description, scenario_name=None):
    # Matching runs on the action text as typed (quotes and all) -- the quoted word in
    # something like "Click the 'Logout' button" is exactly the signal that picks the
    # right element out of the corpus, so stripping it before matching would hurt, not
    # help. Quoted values are only used afterwards, to override the matched step's own
    # literal example data with whatever the user actually asked for.
    actions = split_into_actions(description)
    lines = []
    alternates = []
    previous_keyword = None

    for action in actions:
        ranked = match_action(model, action)
        score, best = ranked[0]
        step_text = best["text"]

        values = extract_quoted_values(action)
        note = None
        if len(values) == 1:
            idx = data_slot_index(step_text)
            if idx is not None:
                step_text = substitute_data_slot(step_text, idx, values[0])
        elif len(values) > 1:
            note = f"{len(values)} quoted values in this action -- used the matched step's own data as-is"

        keyword = classify_keyword(step_text)
        display_keyword = "And" if keyword == previous_keyword else keyword
        previous_keyword = keyword
        lines.append((display_keyword, step_text, score, action, note))
        alternates.append((action, ranked))

    title = scenario_name or description.strip().rstrip(".")
    return title, lines, alternates


def _is_ambiguous(ranked):
    return len(ranked) > 1 and (ranked[0][0] - ranked[1][0]) < AMBIGUOUS_MARGIN


def print_scenario(title, lines, alternates):
    print(f"\nScenario: {title}")
    for (keyword, text, score, source, note), (_, ranked) in zip(lines, alternates):
        if score < LOW_CONFIDENCE:
            flag = "   <-- LOW CONFIDENCE"
        elif _is_ambiguous(ranked):
            flag = "   <-- CLOSE CALL, check alternates below"
        else:
            flag = ""
        print(f"    {keyword} {text}{flag}")
        if note:
            print(f"        ({note})")

    needs_review = [
        (action, ranked) for action, ranked in alternates if ranked[0][0] < LOW_CONFIDENCE or _is_ambiguous(ranked)
    ]
    if needs_review:
        print("\nMatches worth a second look -- low confidence or a near-tie between candidates:")
        for action, ranked in needs_review:
            print(f'  "{action}"')
            for score, item in ranked:
                print(f"    [{score:.2f}] {item['text']}  ({item['feature']}:{item['line_no']})")


def to_feature_text(title, lines):
    body = "\n".join(f"    {keyword} {text}" for keyword, text, _, _, _ in lines)
    return f"Feature: Generated scenario\n\n  Scenario: {title}\n{body}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--text", default=None, help="Natural-language description of what to automate")
    parser.add_argument("--save", default=None, help="Write the generated scenario to this .feature file")
    args = parser.parse_args()

    model = load_model()

    if args.text:
        title, lines, alternates = generate_scenario(model, args.text)
        print_scenario(title, lines, alternates)
        if args.save:
            Path(args.save).write_text(to_feature_text(title, lines), encoding="utf-8")
            print(f"\nSaved to {args.save}")
        return

    print("Describe what you want to test (separate steps with 'then', '.', or ';'). Ctrl+C to quit.")
    while True:
        try:
            description = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not description:
            continue
        title, lines, alternates = generate_scenario(model, description)
        print_scenario(title, lines, alternates)


if __name__ == "__main__":
    main()
