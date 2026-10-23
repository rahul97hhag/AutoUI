"""Bag-of-words analysis of Gherkin step phrasing.

Scans every features/*.feature file, strips out quoted parameters (test data),
and builds a word-frequency table over the remaining step vocabulary. Steps are
then ranked by how many of their words are "rare" (used by only one distinct
step phrasing in the whole suite) -- those are the phrasings most responsible
for vocabulary sprawl and the best candidates to fold into a small set of
generic, parameterized steps.

Usage: python tools/step_vocabulary_report.py [--html path/to/report.html]
"""
import argparse
import html
from collections import Counter
from pathlib import Path
import re

FEATURES_DIR = Path(__file__).resolve().parent.parent / "features"
DEFAULT_HTML_PATH = Path(__file__).resolve().parent.parent / "reports" / "step_vocabulary_report.html"
STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")
QUOTED_RE = re.compile(r'"[^"]*"')
WORD_RE = re.compile(r"[a-zA-Z]+")


def extract_steps(features_dir):
    """Return (feature_file_name, step_text) for every Given/When/Then/And/But line."""
    steps = []
    for feature_file in sorted(features_dir.glob("*.feature")):
        for line in feature_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            for keyword in STEP_KEYWORDS:
                if stripped.startswith(keyword + " "):
                    text = stripped[len(keyword):].strip()
                    steps.append((feature_file.name, text))
                    break
    return steps


def strip_parameters(step_text):
    """Remove quoted literals (test data / dynamic values) so only step vocabulary remains."""
    return QUOTED_RE.sub("", step_text)


def tokenize(text):
    return [w.lower() for w in WORD_RE.findall(text)]


def analyze(features_dir):
    feature_files = sorted(features_dir.glob("*.feature"))
    steps = extract_steps(features_dir)
    distinct_steps = sorted(set(text for _, text in steps))

    doc_freq = Counter()
    step_words = {}
    for text in distinct_steps:
        words = set(tokenize(strip_parameters(text)))
        step_words[text] = words
        doc_freq.update(words)

    ranked = []
    for text in distinct_steps:
        words = step_words[text]
        if not words:
            continue
        rare_words = sorted(w for w in words if doc_freq[w] == 1)
        score = len(rare_words) / len(words)
        ranked.append((score, len(rare_words), text, rare_words))
    ranked.sort(key=lambda row: (-row[0], -row[1], row[2]))

    return {
        "feature_count": len(feature_files),
        "step_occurrences": len(steps),
        "distinct_step_count": len(distinct_steps),
        "word_count": len(doc_freq),
        "doc_freq": doc_freq,
        "ranked": ranked,
    }


def print_report(data):
    print(f"Scanned {data['step_occurrences']} step occurrences across {data['feature_count']} feature files")
    print(f"{data['distinct_step_count']} distinct step phrasings, {data['word_count']} distinct vocabulary words")
    print()

    print("Rarest vocabulary words (doc-frequency = number of distinct steps using the word):")
    rarest = sorted(data["doc_freq"].items(), key=lambda kv: (kv[1], kv[0]))
    for word, count in rarest[:40]:
        print(f"  {count:3d}  {word}")
    print()

    print("Distinct steps ranked by fraction of one-off (rare) words, most uncommon first:")
    for score, rare_count, text, rare_words in data["ranked"]:
        marker = ", ".join(rare_words) if rare_words else "-"
        print(f"  [{score:4.2f}] {text}")
        print(f"          rare words: {marker}")


def write_html_report(data, out_path):
    def esc(text):
        return html.escape(text, quote=True)

    word_rows = "\n".join(
        f"<tr><td class='num'>{count}</td><td>{esc(word)}</td></tr>"
        for word, count in sorted(data["doc_freq"].items(), key=lambda kv: (kv[1], kv[0]))
    )

    step_rows = []
    for score, rare_count, text, rare_words in data["ranked"]:
        marker = ", ".join(esc(w) for w in rare_words) if rare_words else "&mdash;"
        row_class = "rare" if score > 0 else ""
        step_rows.append(
            f"<tr class='{row_class}'><td class='num'>{score:.2f}</td>"
            f"<td><code>{esc(text)}</code></td><td>{marker}</td></tr>"
        )
    step_rows_html = "\n".join(step_rows)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Step vocabulary report</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
  h1 {{ font-size: 1.4rem; }}
  .stats {{ display: flex; gap: 1.5rem; margin: 1rem 0 2rem; flex-wrap: wrap; }}
  .stat {{ background: rgba(127,127,127,0.1); border-radius: 8px; padding: 0.75rem 1.25rem; }}
  .stat .value {{ font-size: 1.6rem; font-weight: 700; display: block; }}
  .stat .label {{ font-size: 0.8rem; opacity: 0.7; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; font-size: 0.9rem; }}
  th, td {{ text-align: left; padding: 0.35rem 0.6rem; border-bottom: 1px solid rgba(127,127,127,0.25); vertical-align: top; }}
  th {{ position: sticky; top: 0; background: Canvas; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  tr.rare {{ background: rgba(230,160,40,0.12); }}
  code {{ font-size: 0.85rem; }}
  .wordtable {{ max-height: 420px; overflow-y: auto; display: block; }}
</style>
</head>
<body>
  <h1>Step vocabulary report</h1>
  <div class="stats">
    <div class="stat"><span class="value">{data['feature_count']}</span><span class="label">feature files</span></div>
    <div class="stat"><span class="value">{data['step_occurrences']}</span><span class="label">step occurrences</span></div>
    <div class="stat"><span class="value">{data['distinct_step_count']}</span><span class="label">distinct step lines</span></div>
    <div class="stat"><span class="value">{data['word_count']}</span><span class="label">distinct vocabulary words</span></div>
  </div>

  <h2>Word frequency</h2>
  <p>Doc-frequency = number of distinct step lines that use the word (quoted parameters excluded).</p>
  <div class="wordtable">
  <table>
    <thead><tr><th>Count</th><th>Word</th></tr></thead>
    <tbody>
{word_rows}
    </tbody>
  </table>
  </div>

  <h2>Steps ranked by rare-word fraction</h2>
  <p>Highlighted rows contain at least one word used by no other step &mdash; the best candidates to fold into a shared, parameterized step.</p>
  <table>
    <thead><tr><th>Score</th><th>Step</th><th>Rare words</th></tr></thead>
    <tbody>
{step_rows_html}
    </tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--html",
        nargs="?",
        const=str(DEFAULT_HTML_PATH),
        default=None,
        help=f"Also write an HTML report (default path: {DEFAULT_HTML_PATH})",
    )
    args = parser.parse_args()

    data = analyze(FEATURES_DIR)
    print_report(data)

    if args.html:
        out_path = Path(args.html)
        write_html_report(data, out_path)
        print(f"\nHTML report written to {out_path.resolve()}")


if __name__ == "__main__":
    main()
