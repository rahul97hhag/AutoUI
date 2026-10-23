"""Map the raw, manually-written test_cases.txt steps onto the generated Gherkin
step library using classic NLP similarity (Bag-of-Words and TF-IDF + cosine
similarity).

For every raw step ("13. Click 'Create Account button'") this finds the closest
matching step among every distinct Given/When/Then line across features/*.feature
("When I click the "create account button" on the "account" page") and scores
the match. The output is a traceability report (raw sentence -> generated
sentence) plus a "coverage gaps" list: raw steps with no good match, which are
either missing scenarios or missing vocabulary in the generic step library.

The same similarity engine doubles as a step-authoring aid: given a brand new
manual test step, `--suggest "<text>"` returns the closest existing generic
step patterns so a new feature file can reuse known phrasing instead of
inventing new step text.

Usage:
  python tools/test_case_mapper.py [--html path/to/report.html] [--threshold 0.15]
  python tools/test_case_mapper.py --suggest "Click the 'Logout' button"
"""
import argparse
import html
import re
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
TEST_CASES_PATH = ROOT / "test_cases.txt"
FEATURES_DIR = ROOT / "features"
DEFAULT_HTML_PATH = ROOT / "reports" / "test_case_mapping_report.html"
DEFAULT_THRESHOLD = 0.15

STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")
TC_HEADER_RE = re.compile(r"^Test Case (\d+):\s*(.+)$")
RAW_STEP_RE = re.compile(r"^(\d+)\.\s+(.*)$")
WORD_RE = re.compile(r"[a-zA-Z]+")


def tokenize(text):
    return WORD_RE.findall(text.lower())


def parse_test_cases(path):
    """Return a list of {tc, title, step_no, text} for every numbered raw step."""
    steps = []
    current_tc, current_title = None, None
    for line in path.read_text(encoding="utf-8").splitlines():
        header = TC_HEADER_RE.match(line.strip())
        if header:
            current_tc, current_title = int(header.group(1)), header.group(2).strip()
            continue
        step_match = RAW_STEP_RE.match(line.strip())
        if step_match and current_tc is not None:
            steps.append(
                {
                    "tc": current_tc,
                    "title": current_title,
                    "step_no": int(step_match.group(1)),
                    "text": step_match.group(2).strip(),
                }
            )
    return steps


def parse_generated_steps(features_dir):
    """Return one entry per distinct Given/When/Then/And/But line across all .feature files."""
    entries, seen = [], set()
    for feature_file in sorted(features_dir.glob("*.feature")):
        for line_no, line in enumerate(feature_file.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.strip()
            for keyword in STEP_KEYWORDS:
                if stripped.startswith(keyword + " "):
                    text = stripped[len(keyword):].strip()
                    if text not in seen:
                        seen.add(text)
                        entries.append({"feature": feature_file.name, "line_no": line_no, "text": text})
                    break
    return entries


def similarity_matrices(raw_texts, generated_texts):
    corpus = raw_texts + generated_texts
    n_raw = len(raw_texts)

    bow = CountVectorizer(tokenizer=tokenize, token_pattern=None)
    bow_matrix = bow.fit_transform(corpus)
    bow_sim = cosine_similarity(bow_matrix[:n_raw], bow_matrix[n_raw:])

    tfidf = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    tfidf_matrix = tfidf.fit_transform(corpus)
    tfidf_sim = cosine_similarity(tfidf_matrix[:n_raw], tfidf_matrix[n_raw:])

    return bow_sim, tfidf_sim


def build_report(threshold=DEFAULT_THRESHOLD):
    raw_items = parse_test_cases(TEST_CASES_PATH)
    generated_items = parse_generated_steps(FEATURES_DIR)

    raw_texts = [item["text"] for item in raw_items]
    generated_texts = [item["text"] for item in generated_items]
    bow_sim, tfidf_sim = similarity_matrices(raw_texts, generated_texts)

    rows = []
    for i, raw in enumerate(raw_items):
        bow_idx = bow_sim[i].argmax()
        tfidf_idx = tfidf_sim[i].argmax()
        rows.append(
            {
                **raw,
                "bow_match": generated_items[bow_idx],
                "bow_score": float(bow_sim[i][bow_idx]),
                "tfidf_match": generated_items[tfidf_idx],
                "tfidf_score": float(tfidf_sim[i][tfidf_idx]),
            }
        )

    gaps = [row for row in rows if row["tfidf_score"] < threshold]
    return rows, gaps, generated_items


def print_report(rows, gaps, generated_items, threshold):
    print(f"{len(rows)} raw test_cases.txt steps compared against {len(generated_items)} distinct generated steps")
    print(f"Coverage gaps (TF-IDF best score < {threshold}): {len(gaps)}\n")

    current_tc = None
    for row in rows:
        if row["tc"] != current_tc:
            current_tc = row["tc"]
            print(f"\nTest Case {row['tc']}: {row['title']}")
        flag = "  [GAP]" if row["tfidf_score"] < threshold else ""
        print(f"  {row['step_no']:>2}. {row['text']}{flag}")
        print(f"      -> [{row['tfidf_score']:.2f} tfidf / {row['bow_score']:.2f} bow] {row['tfidf_match']['text']}")

    if gaps:
        print("\n\nCoverage gaps (no good match in the generated step library):")
        for row in gaps:
            print(f"  TC{row['tc']} step {row['step_no']}: {row['text']}  (best tfidf={row['tfidf_score']:.2f})")


def write_html_report(rows, gaps, generated_items, threshold, out_path):
    def esc(text):
        return html.escape(text, quote=True)

    def score_class(score):
        if score < threshold:
            return "gap"
        if score < 0.4:
            return "weak"
        return "strong"

    row_html = []
    current_tc = None
    for row in rows:
        if row["tc"] != current_tc:
            current_tc = row["tc"]
            row_html.append(
                f"<tr class='tc-header'><td colspan='4'>Test Case {row['tc']}: {esc(row['title'])}</td></tr>"
            )
        cls = score_class(row["tfidf_score"])
        row_html.append(
            f"<tr class='{cls}'>"
            f"<td class='num'>{row['step_no']}</td>"
            f"<td><code>{esc(row['text'])}</code></td>"
            f"<td><code>{esc(row['tfidf_match']['text'])}</code>"
            f"<div class='src'>{esc(row['tfidf_match']['feature'])}:{row['tfidf_match']['line_no']}</div></td>"
            f"<td class='num'>{row['tfidf_score']:.2f} / {row['bow_score']:.2f}</td>"
            f"</tr>"
        )
    rows_html = "\n".join(row_html)

    gap_rows = "\n".join(
        f"<tr><td class='num'>TC{row['tc']}.{row['step_no']}</td><td><code>{esc(row['text'])}</code></td>"
        f"<td class='num'>{row['tfidf_score']:.2f}</td></tr>"
        for row in gaps
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Test case &rarr; Gherkin step mapping</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
  h1 {{ font-size: 1.4rem; }}
  .stats {{ display: flex; gap: 1.5rem; margin: 1rem 0 2rem; flex-wrap: wrap; }}
  .stat {{ background: rgba(127,127,127,0.1); border-radius: 8px; padding: 0.75rem 1.25rem; }}
  .stat .value {{ font-size: 1.6rem; font-weight: 700; display: block; }}
  .stat .label {{ font-size: 0.8rem; opacity: 0.7; }}
  table {{ border-collapse: collapse; width: 100%; margin-bottom: 2rem; font-size: 0.85rem; }}
  th, td {{ text-align: left; padding: 0.35rem 0.6rem; border-bottom: 1px solid rgba(127,127,127,0.25); vertical-align: top; }}
  th {{ position: sticky; top: 0; background: Canvas; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  tr.tc-header td {{ font-weight: 700; background: rgba(127,127,127,0.18); padding-top: 0.6rem; }}
  tr.gap {{ background: rgba(220,60,60,0.14); }}
  tr.weak {{ background: rgba(230,160,40,0.10); }}
  code {{ font-size: 0.82rem; }}
  .src {{ font-size: 0.72rem; opacity: 0.6; }}
  .legend span {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.8rem; }}
</style>
</head>
<body>
  <h1>Test case &rarr; Gherkin step mapping (BOW / TF-IDF cosine similarity)</h1>
  <div class="stats">
    <div class="stat"><span class="value">{len(rows)}</span><span class="label">raw steps (test_cases.txt)</span></div>
    <div class="stat"><span class="value">{len(generated_items)}</span><span class="label">distinct generated steps</span></div>
    <div class="stat"><span class="value">{len(gaps)}</span><span class="label">coverage gaps (tfidf &lt; {threshold})</span></div>
  </div>
  <p class="legend">
    <span style="background: rgba(220,60,60,0.25);">red</span> = gap, no adequate match &nbsp;
    <span style="background: rgba(230,160,40,0.25);">amber</span> = weak match (&lt; 0.4) &nbsp;
    <span style="background: rgba(127,127,127,0.1);">plain</span> = strong match
  </p>

  <h2>Raw step &rarr; best-matching generated step</h2>
  <table>
    <thead><tr><th>#</th><th>Raw test_cases.txt step</th><th>Closest generated Gherkin step</th><th>tfidf / bow score</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>

  <h2>Coverage gaps</h2>
  <p>Raw steps with no adequately similar generated step &mdash; either the scenario isn't implemented yet,
  or the generic step library is missing vocabulary for this action.</p>
  <table>
    <thead><tr><th>Test case / step</th><th>Raw text</th><th>Best tfidf score</th></tr></thead>
    <tbody>
{gap_rows}
    </tbody>
  </table>
</body>
</html>
""",
        encoding="utf-8",
    )


def suggest(new_text, top_n=5):
    """Given a brand-new manual test step, print the closest existing generated steps."""
    generated_items = parse_generated_steps(FEATURES_DIR)
    generated_texts = [item["text"] for item in generated_items]

    tfidf = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    matrix = tfidf.fit_transform(generated_texts + [new_text])
    sim = cosine_similarity(matrix[-1], matrix[:-1])[0]

    ranked = sorted(zip(sim, generated_items), key=lambda pair: -pair[0])[:top_n]
    print(f'Closest existing generic steps for: "{new_text}"\n')
    for score, item in ranked:
        print(f"  [{score:.2f}] {item['text']}")
        print(f"         ({item['feature']}:{item['line_no']})")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--html", nargs="?", const=str(DEFAULT_HTML_PATH), default=None,
                         help=f"Also write an HTML report (default path: {DEFAULT_HTML_PATH})")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                         help=f"TF-IDF score below which a raw step counts as a coverage gap (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--suggest", metavar="TEXT", default=None,
                         help="Instead of the full report, suggest the closest generic steps for a new raw test step")
    args = parser.parse_args()

    if args.suggest:
        suggest(args.suggest)
        return

    rows, gaps, generated_items = build_report(threshold=args.threshold)
    print_report(rows, gaps, generated_items, args.threshold)

    if args.html:
        out_path = Path(args.html)
        write_html_report(rows, gaps, generated_items, args.threshold, out_path)
        print(f"\nHTML report written to {out_path.resolve()}")


if __name__ == "__main__":
    main()
