"""
locator_agent.py

Scans Angular/HTML template files and emits a Playwright locator registry
compatible with features/steps/generic_steps.py.

Output format mirrors the reference locator file:
    <page>:
      <alias>: "<playwright selector>"

Placeholders used in generated selectors:
    {value} - substituted with the text passed by a step
    {index} - substituted with an ordinal-resolved index
"""

import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple

import yaml
from lxml import html


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_text(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _strip_angular(template: str) -> str:
    """Strip Angular template syntax so lxml can parse."""
    t = re.sub(r'\*ng(If|For|Switch|SwitchCase|SwitchDefault)="[^"]*"', "", template)
    t = re.sub(r"\{\{[^}]*\}\}", "PLACEHOLDER", t)
    t = re.sub(r'\([a-zA-Z]+\)="[^"]*"', "", t)
    t = re.sub(r'\[[^\]]+\]="[^"]*"', "", t)
    return t


def _alias(desc: str) -> str:
    """Convert a human description (or a camelCase attribute name) into a
    space-separated locator alias, matching this project's hand-written
    locators.yaml convention (e.g. 'mobileNumber' -> 'mobile number')."""
    desc = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", desc)  # split camelCase
    desc = desc.lower()
    desc = re.sub(r"[^a-z0-9{} ]+", " ", desc)
    return " ".join(desc.split())


def _page_name_from_path(filepath: str) -> str:
    """Derive a page name from a template's filename, e.g.
    'recharge-packs.component.html' -> 'recharge packs'."""
    name = os.path.basename(filepath)
    name = re.sub(r"\.component\.html$", "", name, flags=re.IGNORECASE)
    return name.replace("-", " ").replace("_", " ").strip()


def page_map_from_paths(filepaths: List[str]) -> Dict[str, str]:
    """Build a {filepath: page_name} map from a flat list of HTML file
    paths, deriving each page name from its filename."""
    return {path: _page_name_from_path(path) for path in filepaths}


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------

class LocatorRegistryAgent:
    """
    Builds a Playwright locator registry from HTML template files.

    The agent maps each template to a logical page name (via the file's
    `page_map` arg), then emits aliases grouped by that page.
    """

    def __init__(self, page_map: Dict[str, str]):
        # page_map: {"recharge-packs.component.html": "recharge packs", ...}
        self.page_map = page_map
        self.registry: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._global_seen: set = set()

    # ---------- Public API ----------
    def build(self) -> Dict[str, Dict[str, str]]:
        for filepath, page in self.page_map.items():
            if not os.path.exists(filepath):
                print(f"[warn] missing file: {filepath}")
                continue
            self._process(filepath, page)
        return dict(self.registry)

    def export_yaml(self, out_path: str = "locators.yaml") -> None:
        data = self.build()
        with open(out_path, "w", encoding="utf-8") as f:
            # Preserve declaration order → use sort_keys=False
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True, width=1000)
        n = sum(len(v) for v in data.values())
        print(f"[ok] wrote {n} locators across {len(data)} pages -> {out_path}")

    # ---------- Core ----------
    def _process(self, filepath: str, page: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            template = f.read()

        # Extract `id="..."` attributes BEFORE stripping (Angular-safe)
        ids_in_file = re.findall(r'\bid="([^"]+)"', template)
        classes_in_file = self._collect_classes(template)

        dom = html.fromstring(_strip_angular(template))

        # 1) Inputs  ------------------------------------------------
        for el in dom.xpath("//input | //textarea | //select"):
            self._handle_input(page, el)

        # 2) Buttons ------------------------------------------------
        for el in dom.xpath("//button"):
            text = _clean_text(el.text_content())
            if not text:
                continue
            if "PLACEHOLDER" in text:
                # Text includes an Angular interpolation (e.g. "Pay
                # {{ priceLabel(...) }}"), stripped to "PLACEHOLDER" by
                # _strip_angular. A text-based selector would never match
                # real rendered content, so fall back to a class-based one
                # and alias off just the static words.
                static_words = text.replace("PLACEHOLDER", "").strip()
                classes = (el.get("class") or "").split()
                if not static_words or not classes:
                    continue
                self._register(page, f"{static_words.lower()} button", f"button.{classes[0]}")
                continue
            self._register(
                page,
                f"{text.lower()} button",
                f"button:has-text('{text}')",
            )

        # 3) Links --------------------------------------------------
        for el in dom.xpath("//a"):
            text = _clean_text(el.text_content())
            if text:
                self._register(
                    page,
                    f"{text.lower()} link",
                    f"a:has-text('{text}')",
                )

        # 4) Headings ----------------------------------------------
        for tag in ("h1", "h2", "h3"):
            for el in dom.xpath(f"//{tag}"):
                text = _clean_text(el.text_content())
                if text:
                    self._register(
                        page,
                        f"{tag} {text.lower()} heading",
                        f"{tag}:has-text('{text}') >> nth=0",
                    )

        # 5) Elements with ids (unique in-file) --------------------
        if len(ids_in_file) == len(set(ids_in_file)):
            for el in dom.xpath("//*[@id]"):
                _id = el.get("id")
                self._register(page, f"{_id} element", f"#{_id}")

        # 6) Unique classes  ---------------------------------------
        for el in dom.xpath("//*[@class]"):
            for cls in (el.get("class") or "").split():
                if cls in classes_in_file and cls not in self._global_seen:
                    # Only register if class appears exactly once in the file
                    self._global_seen.add(cls)
                    self._register(
                        page,
                        f"{cls} container",
                        f".{cls}",
                    )

        # 7) Repeated containers → "{value}" / "{index}" aliases ----
        self._register_repeated_containers(page, dom)

        # 8) Structural landmarks ----------------------------------
        for tag, label in [
            ("header", "site header"),
            ("nav", "main nav"),
            ("aside", "sidebar"),
            ("main", "main content"),
        ]:
            els = dom.xpath(f"//{tag}")
            if not els:
                continue
            if len(els) == 1:
                self._register(page, f"{label} container", f"{tag}")
            else:
                for i in range(len(els)):
                    self._register(page, f"{label} {i}", f"{tag} >> nth={i}")

    # ---------- Inputs ----------
    def _handle_input(self, page: str, el) -> None:
        tag = el.tag
        ph = el.get("placeholder")
        nm = el.get("name")
        _id = el.get("id")
        typ = el.get("type")

        if tag == "input" and ph:
            self._register(page, f"{_alias(ph)} field", f"input[placeholder='{ph}']")
        if tag == "input" and nm:
            self._register(page, f"{_alias(nm)} field", f"input[name='{nm}']")
        if tag == "textarea" and nm:
            self._register(page, f"{_alias(nm)} field", f"textarea[name='{nm}']")
        if tag == "select" and _id:
            self._register(page, f"{_alias(_id)} dropdown", f"#{_id}")
        if tag == "input" and _id:
            self._register(page, f"{_alias(_id)} field", f"#{_id}")
        if typ == "search":
            # treat as a search box alias
            self._register(page, "search field", "input[type='search']")

    # ---------- Repeated containers ----------
    def _register_repeated_containers(self, page: str, dom) -> None:
        """
        Detect repeated wrappers like <article class='pack-card'> and emit:
           pack card: "<sel>:has-text('{value}')"
           pack card by position: "<sel> >> nth={index}"
        """
        candidates = [
            ("article", "pack_card"),         # recharge-packs
            ("details", "payment_method"),    # payment options
            ("tr", "row"),                    # table rows
            ("li", "list_item"),              # list items
        ]
        for tag, base in candidates:
            els = dom.xpath(f"//{tag}")
            if len(els) < 2:
                continue
            cls = None
            for el in els:
                if el.get("class"):
                    cls = el.get("class").split()[0]
                    break
            sel = f"{tag}.{cls}" if cls else tag
            alias = f"{cls or base.replace('_', ' ')}"
            self._register(page, f"{alias} by text", f"{sel}:has-text('{{value}}')")
            self._register(page, f"{alias} by position", f"{sel} >> nth={{index}}")

    # ---------- Utilities ----------
    @staticmethod
    def _collect_classes(template: str) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for m in re.finditer(r'class="([^"]+)"', template):
            for cls in m.group(1).split():
                counts[cls] += 1
        return counts

    def _register(self, page: str, alias: str, selector: str) -> None:
        alias = _alias(alias)
        # Keep first occurrence; later duplicates get numeric suffix
        if alias in self.registry[page]:
            i = 2
            while f"{alias} {i}" in self.registry[page]:
                i += 1
            alias = f"{alias} {i}"
        self.registry[page][alias] = selector


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Full paths to the Angular templates to scan, as a JSON array. Page
    # names are derived automatically from each filename (see
    # _page_name_from_path) -- no need to repeat them here.
    HTML_FILES = [
        "C:\\Bhavani\\Applications\\UI PROJECT\\src\\app\\pages\\payment\\payment.component.html",
        "C:\\Bhavani\\Applications\\UI PROJECT\\src\\app\\pages\\recharge\\recharge.component.html",
        "C:\\Bhavani\\Applications\\UI PROJECT\\src\\app\\pages\\recharge-packs\\recharge-packs.component.html",
    ]

    page_map = page_map_from_paths(HTML_FILES)
    agent = LocatorRegistryAgent(page_map)
    agent.export_yaml("config/locators_2.yaml")