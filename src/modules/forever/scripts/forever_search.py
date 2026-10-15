#!/usr/bin/env python3
"""Search the bundled Forever AI Components registry (600+ self-contained HTML components).

Examples:
  python3 forever_search.py "loader" --perf cheap --label mobile-ready
  python3 forever_search.py "hero background calm" --use-case hero --scheme dark -n 5
  python3 forever_search.py --role button --technique css-only
  python3 forever_search.py --show kinetic-type/01-weight-morph-wave.html   # path + agent meta
  python3 forever_search.py --facets                                        # list filter values
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Windows consoles default to a legacy code page; force UTF-8 so bullets and dashes print.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent / "infinite"
INDEX = ROOT / "components.index.json"
REMOTE = "https://raw.githubusercontent.com/isas1/forever-ai-components/main/infinite/"

PERF_RANK = {"cheap": 0, "medium": 1, "heavy": 2}


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def text_of(c):
    parts = [c.get("title", ""), c.get("description", ""), c.get("theme", ""), c.get("role", "")]
    for key in ("style", "useCases", "mood", "tags", "technique", "labels"):
        parts += as_list(c.get(key))
    parts.append(c.get("motion", ""))
    return " ".join(str(p) for p in parts).lower()


def score(c, terms):
    if not terms:
        return 1.0
    hay = text_of(c)
    title = c.get("title", "").lower()
    s = 0.0
    for t in terms:
        if t in hay:
            s += 1.0
            if t in title:
                s += 1.0
            if t in as_list(c.get("useCases")) or t == c.get("role"):
                s += 1.5
    return s


def matches(c, args):
    def has(key, want):
        return not want or all(w in as_list(c.get(key)) for w in want)

    if args.role and c.get("role") not in args.role:
        return False
    if args.perf and PERF_RANK.get(c.get("perfTier"), 9) > PERF_RANK[args.perf]:
        return False
    if args.scheme and c.get("palette", {}).get("scheme") not in args.scheme:
        return False
    if args.intensity and c.get("intensity") not in args.intensity:
        return False
    if args.no_deps and as_list(c.get("deps")) != ["none"]:
        return False
    return (has("technique", args.technique) and has("style", args.style) and has("useCases", args.use_case)
            and has("mood", args.mood) and has("labels", args.label) and has("interaction", args.interaction))


def agent_meta(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<script type="application/json" id="forever-agent-meta">(.*?)</script>', html, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return m.group(1).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("query", nargs="*", help="free-text keywords")
    p.add_argument("--role", action="append", help="background, hero, button, card, loader, nav, input, ...")
    p.add_argument("--technique", action="append", help="css-only, svg, canvas, raf, smil")
    p.add_argument("--style", action="append")
    p.add_argument("--use-case", action="append", dest="use_case")
    p.add_argument("--mood", action="append")
    p.add_argument("--label", action="append", help="accessible, mobile-ready, easy-to-modify, agent-ready, ...")
    p.add_argument("--interaction", action="append")
    p.add_argument("--scheme", action="append", help="dark, light, duotone, vibrant, monochrome")
    p.add_argument("--intensity", action="append", help="calm, moderate, energetic")
    p.add_argument("--perf", choices=list(PERF_RANK), help="maximum performance tier")
    p.add_argument("--no-deps", action="store_true", help="exclude components that load Google Fonts")
    p.add_argument("-n", type=int, default=8, help="max results (default 8)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--show", metavar="FILE", help="print local path + adaptation metadata for one component")
    p.add_argument("--facets", action="store_true", help="print available filter values and counts")
    args = p.parse_args()

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    if args.facets:
        print(json.dumps(data["counts"]["facets"], indent=1))
        return
    if args.show:
        path = ROOT / args.show
        if not path.exists():
            sys.exit(f"not found: {path}")
        print(f"local:  {path}\nremote: {REMOTE}{args.show}\n")
        print(json.dumps(agent_meta(path), indent=1))
        return

    terms = [t.lower() for t in " ".join(args.query).split()]
    hits = []
    for c in data["components"]:
        if not matches(c, args):
            continue
        s = score(c, terms)
        if terms and s == 0:
            continue
        # Prefer cheap, accessible, curated components on ties.
        s += 0.3 * (2 - PERF_RANK.get(c.get("perfTier"), 2)) + 0.2 * ("accessible" in as_list(c.get("labels")))
        s += 0.2 * (c.get("tier") == "curated")
        hits.append((s, c))
    hits.sort(key=lambda h: -h[0])
    hits = hits[: args.n]

    if args.json:
        print(json.dumps([dict(c, localPath=str(ROOT / c["file"])) for _, c in hits], indent=1))
        return
    if not hits:
        print("No matches. Loosen filters or try --facets to see valid values.")
        return
    for _, c in hits:
        print(f"• {c['title']}  [{c['file']}]")
        print(f"  {c.get('role')} · {c.get('perfTier')} · {'/'.join(as_list(c.get('technique')))} · "
              f"{c.get('palette', {}).get('scheme')} · labels: {', '.join(as_list(c.get('labels')))}")
        print(f"  {c.get('description', '')}")
    print(f"\nInspect one: python3 {Path(__file__).name} --show <file>   (files live in {ROOT})")


if __name__ == "__main__":
    main()
