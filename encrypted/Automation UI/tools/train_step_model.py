"""Train and pickle a TF-IDF retrieval model over the generic step library.

This is the "training" half of a tiny retrieval system: it fits a TF-IDF
vectorizer over every distinct Given/When/Then line in features/*.feature --
the full vocabulary of things the automation can actually do -- and pickles
the vectorizer, the fitted step vectors, and their metadata to disk.
tools/generate_scenario.py then just loads this pickle instead of re-parsing
and re-fitting every time: train once, serve many, the same split any
retrieval model uses in production.

Re-run this whenever the feature files change (new steps, new scenarios) so
the model's vocabulary stays in sync with what the automation can actually do.

Usage: python tools/train_step_model.py
"""
import pickle
import re
import sys
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_case_mapper import FEATURES_DIR, parse_generated_steps, tokenize  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parent / "step_model.pkl"
PLACEHOLDER_RE = re.compile(r"<[^>]+>")


def train():
    # Scenario Outline lines like `I click "<product>" in ...` are only valid inside
    # their own Examples table -- not something we can hand back as runnable Gherkin,
    # so they're excluded from what the generator is allowed to retrieve.
    generated_items = [
        item for item in parse_generated_steps(FEATURES_DIR) if not PLACEHOLDER_RE.search(item["text"])
    ]
    texts = [item["text"] for item in generated_items]

    vectorizer = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    matrix = vectorizer.fit_transform(texts)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "items": generated_items}, f)

    print(f"Trained on {len(generated_items)} distinct steps from {FEATURES_DIR}")
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()
