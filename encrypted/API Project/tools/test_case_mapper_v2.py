"""Same traceability report as test_case_mapper.py, but adds a transformer-based
semantic-embedding similarity (sentence-transformers / torch) alongside the
BOW and TF-IDF scores, so the three methods can be compared side by side.

BOW and TF-IDF only ever see word overlap: two sentences score high only if
they share literal words. A transformer sentence embedding encodes meaning, so
paraphrases and synonyms ("Enter correct email address and password" vs.
"I enter ... into the signup email field") can score well even with little
word overlap -- and, just as informatively, sometimes score two genuinely
different actions as similar because they're structurally alike. The "differs"
column below is exactly the set of rows where that distinction shows up.

Model: sentence-transformers/all-MiniLM-L6-v2 (small, fast, CPU-friendly;
downloaded once from the Hugging Face Hub and cached locally).

Usage:
  python tools/test_case_mapper_v2.py [--html path/to/report.html] [--threshold 0.30]
  python tools/test_case_mapper_v2.py --suggest "Click the 'Logout' button"
"""
import argparse
import html
import sys
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_case_mapper import (  # noqa: E402
    FEATURES_DIR,
    TEST_CASES_PATH,
    parse_generated_steps,
    parse_test_cases,
    similarity_matrices,
)

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HTML_PATH = ROOT / "reports" / "test_case_mapping_report_v2.html"
DEFAULT_THRESHOLD = 0.30
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        print(f"Loading transformer model '{MODEL_NAME}' (first run downloads ~90MB)...", file=sys.stderr)
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def transformer_similarity(raw_texts, generated_texts):
    model = get_model()
    raw_emb = model.encode(raw_texts, normalize_embeddings=True, show_progress_bar=False)
    gen_emb = model.encode(generated_texts, normalize_embeddings=True, show_progress_bar=False)
    return cosine_similarity(raw_emb, gen_emb)


def build_report(threshold=DEFAULT_THRESHOLD):
    raw_items = parse_test_cases(TEST_CASES_PATH)
    generated_items = parse_generated_steps(FEATURES_DIR)

    raw_texts = [item["text"] for item in raw_items]
    generated_texts = [item["text"] for item in generated_items]

    bow_sim, tfidf_sim = similarity_matrices(raw_texts, generated_texts)
    transformer_sim = transformer_similarity(raw_texts, generated_texts)

    rows = []
    for i, raw in enumerate(raw_items):
        bow_idx = bow_sim[i].argmax()
        tfidf_idx = tfidf_sim[i].argmax()
        transformer_idx = transformer_sim[i].argmax()
        rows.append(
            {
                **raw,
                "bow_match": generated_items[bow_idx],
                "bow_score": float(bow_sim[i][bow_idx]),
                "tfidf_match": generated_items[tfidf_idx],
                "tfidf_score": float(tfidf_sim[i][tfidf_idx]),
                "transformer_match": generated_items[transformer_idx],
                "transformer_score": float(transformer_sim[i][transformer_idx]),
                "differs": tfidf_idx != transformer_idx,
            }
        )

    gaps = [row for row in rows if row["transformer_score"] < threshold]
    differing = [row for row in rows if row["differs"]]
    return rows, gaps, differing, generated_items


def print_report(rows, gaps, differing, generated_items, threshold):
    print(f"{len(rows)} raw test_cases.txt steps compared against {len(generated_items)} distinct generated steps")
    print(f"Model: {MODEL_NAME}")
    print(f"Coverage gaps (transformer best score < {threshold}): {len(gaps)}")
    print(f"Rows where TF-IDF and the transformer pick a DIFFERENT best match: {len(differing)}\n")

    current_tc = None
    for row in rows:
        if row["tc"] != current_tc:
            current_tc = row["tc"]
            print(f"\nTest Case {row['tc']}: {row['title']}")
        flag = "  [GAP]" if row["transformer_score"] < threshold else ""
        flag += "  [DIFFERS]" if row["differs"] else ""
        print(f"  {row['step_no']:>2}. {row['text']}{flag}")
        print(f"      tfidf       [{row['tfidf_score']:.2f}] {row['tfidf_match']['text']}")
        print(f"      transformer [{row['transformer_score']:.2f}] {row['transformer_match']['text']}")

    if differing:
        print("\n\nWhere TF-IDF and the transformer disagree on the best match:")
        for row in differing:
            print(f"\n  TC{row['tc']} step {row['step_no']}: {row['text']}")
            print(f"    tfidf       [{row['tfidf_score']:.2f}] {row['tfidf_match']['text']}")
            print(f"    transformer [{row['transformer_score']:.2f}] {row['transformer_match']['text']}")

    if gaps:
        print("\n\nCoverage gaps (no good match even with semantic embeddings):")
        for row in gaps:
            print(f"  TC{row['tc']} step {row['step_no']}: {row['text']}  (best transformer={row['transformer_score']:.2f})")


def write_html_report(rows, gaps, differing, generated_items, threshold, out_path):
    def esc(text):
        return html.escape(text, quote=True)

    def score_class(score, threshold):
        if score < threshold:
            return "gap"
        if score < threshold + 0.25:
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
        cls = score_class(row["transformer_score"], threshold)
        if row["differs"]:
            cls += " differs"
        row_html.append(
            f"<tr class='{cls}'>"
            f"<td class='num'>{row['step_no']}</td>"
            f"<td><code>{esc(row['text'])}</code></td>"
            f"<td><code>{esc(row['tfidf_match']['text'])}</code><div class='src'>tfidf {row['tfidf_score']:.2f} &middot; "
            f"{esc(row['tfidf_match']['feature'])}:{row['tfidf_match']['line_no']}</div></td>"
            f"<td><code>{esc(row['transformer_match']['text'])}</code><div class='src'>transformer {row['transformer_score']:.2f} &middot; "
            f"{esc(row['transformer_match']['feature'])}:{row['transformer_match']['line_no']}</div></td>"
            f"</tr>"
        )
    rows_html = "\n".join(row_html)

    differ_rows = "\n".join(
        f"<tr><td class='num'>TC{row['tc']}.{row['step_no']}</td><td><code>{esc(row['text'])}</code></td>"
        f"<td><code>{esc(row['tfidf_match']['text'])}</code><div class='src'>{row['tfidf_score']:.2f}</div></td>"
        f"<td><code>{esc(row['transformer_match']['text'])}</code><div class='src'>{row['transformer_score']:.2f}</div></td></tr>"
        for row in differing
    )

    gap_rows = "\n".join(
        f"<tr><td class='num'>TC{row['tc']}.{row['step_no']}</td><td><code>{esc(row['text'])}</code></td>"
        f"<td class='num'>{row['transformer_score']:.2f}</td></tr>"
        for row in gaps
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Test case &rarr; Gherkin step mapping (v2, transformer)</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, Segoe UI, Roboto, sans-serif; max-width: 1200px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }}
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
  tr.differs {{ outline: 2px solid rgba(70,130,220,0.6); outline-offset: -1px; }}
  code {{ font-size: 0.82rem; }}
  .src {{ font-size: 0.72rem; opacity: 0.6; }}
  .legend span {{ display: inline-block; padding: 0.1rem 0.5rem; border-radius: 4px; margin-right: 0.5rem; font-size: 0.8rem; }}
</style>
</head>
<body>
  <h1>Test case &rarr; Gherkin step mapping: TF-IDF vs. transformer (all-MiniLM-L6-v2)</h1>
  <div class="stats">
    <div class="stat"><span class="value">{len(rows)}</span><span class="label">raw steps (test_cases.txt)</span></div>
    <div class="stat"><span class="value">{len(generated_items)}</span><span class="label">distinct generated steps</span></div>
    <div class="stat"><span class="value">{len(differing)}</span><span class="label">tfidf vs transformer disagree</span></div>
    <div class="stat"><span class="value">{len(gaps)}</span><span class="label">coverage gaps (transformer &lt; {threshold})</span></div>
  </div>
  <p class="legend">
    <span style="background: rgba(220,60,60,0.25);">red</span> = gap &nbsp;
    <span style="background: rgba(230,160,40,0.25);">amber</span> = weak match &nbsp;
    <span style="outline: 2px solid rgba(70,130,220,0.6);">blue outline</span> = tfidf and transformer disagree on the best match
  </p>

  <h2>Raw step &rarr; best match per method</h2>
  <table>
    <thead><tr><th>#</th><th>Raw test_cases.txt step</th><th>TF-IDF best match</th><th>Transformer best match</th></tr></thead>
    <tbody>
{rows_html}
    </tbody>
  </table>

  <h2>Where the two methods disagree</h2>
  <p>TF-IDF only sees shared words; the transformer encodes meaning. These are the rows where that difference actually changed the answer &mdash;
  worth a manual look to see which one is actually right.</p>
  <table>
    <thead><tr><th>Test case / step</th><th>Raw text</th><th>TF-IDF picked</th><th>Transformer picked</th></tr></thead>
    <tbody>
{differ_rows}
    </tbody>
  </table>

  <h2>Coverage gaps</h2>
  <p>Raw steps with no adequately similar generated step even under semantic embeddings.</p>
  <table>
    <thead><tr><th>Test case / step</th><th>Raw text</th><th>Best transformer score</th></tr></thead>
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
    """Given a brand-new manual test step, print the closest existing generated steps
    by transformer similarity (with the TF-IDF ranking alongside for comparison)."""
    from sklearn.feature_extraction.text import TfidfVectorizer

    from test_case_mapper import tokenize

    generated_items = parse_generated_steps(FEATURES_DIR)
    generated_texts = [item["text"] for item in generated_items]

    model = get_model()
    gen_emb = model.encode(generated_texts, normalize_embeddings=True, show_progress_bar=False)
    new_emb = model.encode([new_text], normalize_embeddings=True, show_progress_bar=False)
    transformer_sim = cosine_similarity(new_emb, gen_emb)[0]

    tfidf = TfidfVectorizer(tokenizer=tokenize, token_pattern=None)
    matrix = tfidf.fit_transform(generated_texts + [new_text])
    tfidf_sim = cosine_similarity(matrix[-1], matrix[:-1])[0]

    print(f'Closest existing generic steps for: "{new_text}"\n')
    print("By transformer similarity:")
    for idx in transformer_sim.argsort()[::-1][:top_n]:
        print(f"  [{transformer_sim[idx]:.2f}] {generated_items[idx]['text']}")
        print(f"         ({generated_items[idx]['feature']}:{generated_items[idx]['line_no']})")

    print("\nBy TF-IDF similarity:")
    for idx in tfidf_sim.argsort()[::-1][:top_n]:
        print(f"  [{tfidf_sim[idx]:.2f}] {generated_items[idx]['text']}")
        print(f"         ({generated_items[idx]['feature']}:{generated_items[idx]['line_no']})")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--html", nargs="?", const=str(DEFAULT_HTML_PATH), default=None,
                         help=f"Also write an HTML report (default path: {DEFAULT_HTML_PATH})")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                         help=f"Transformer score below which a raw step counts as a coverage gap (default {DEFAULT_THRESHOLD})")
    parser.add_argument("--suggest", metavar="TEXT", default=None,
                         help="Instead of the full report, suggest the closest generic steps for a new raw test step")
    args = parser.parse_args()

    if args.suggest:
        suggest(args.suggest)
        return

    rows, gaps, differing, generated_items = build_report(threshold=args.threshold)
    print_report(rows, gaps, differing, generated_items, args.threshold)

    if args.html:
        out_path = Path(args.html)
        write_html_report(rows, gaps, differing, generated_items, args.threshold, out_path)
        print(f"\nHTML report written to {out_path.resolve()}")


if __name__ == "__main__":
    main()
