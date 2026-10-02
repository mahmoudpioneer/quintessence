#!/usr/bin/env python3
"""Run ui-ux-pro-max's design-system generator and filter it through the rest of Quintessence.

The generator assembles pattern, style, palette and typography from separate database rows,
so its output can contradict itself and the other modules (e.g. "no smooth transitions" next to
a checklist asking for 150-300ms transitions, or Inter, which impeccable's detector flags).
This script keeps what survives, marks what needs a decision, and rejects what another module bans.

Usage:
  python3 design_brief.py "<product type> <industry> <keywords>" [-p "Name"] [--json]
  (any other ui-ux-pro-max flags such as --variance/--motion/--density are passed through)
"""
import colorsys
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEARCH = ROOT / "modules" / "ui-ux-pro-max" / "scripts" / "search.py"

# impeccable: detector's overused-font rule + new-work.md's "you stopped looking" list (display faces)
DETECTOR_OVERUSED = {"inter", "roboto", "fraunces", "geist", "plus jakarta sans", "space grotesk"}
DISPLAY_DEFAULTS = {"fraunces", "playfair display", "cormorant", "cormorant garamond", "lora", "crimson", "crimson text",
                    "newsreader", "syne", "space grotesk", "space mono", "ibm plex sans", "ibm plex serif", "ibm plex mono",
                    "inter", "dm sans", "dm serif display", "dm serif text", "outfit", "plus jakarta sans", "instrument sans"}


def hex_rgb(h):
    h = h.strip().lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def lum(h):
    c = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in hex_rgb(h)]
    return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + .05) / (min(la, lb) + .05)


def hls(h):
    hh, l, s = colorsys.rgb_to_hls(*hex_rgb(h))
    return hh * 360, l, s


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    want_json = "--json" in sys.argv
    if not args or args[0].startswith("-"):
        sys.exit(__doc__)
    if "--design-system" not in args:
        args.append("--design-system")
    out = subprocess.run([sys.executable, str(SEARCH), *args, "--json"], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(out.stderr or out.stdout)
    ds = json.loads(out.stdout)["design_system"]

    keep, review, reject = [], [], []
    style, colors, typo = ds.get("style", {}), ds.get("colors", {}), ds.get("typography", {})

    # Structure: the most reliable part of the generator.
    p = ds.get("pattern", {})
    keep.append(f"Section order: {p.get('sections')}")
    keep.append(f"CTA placement: {p.get('cta_placement')}")
    if p.get("conversion"):
        keep.append(f"Conversion/a11y notes: {p.get('conversion')}")
    if style.get("accessibility"):
        keep.append(f"Accessibility requirements: {style.get('accessibility')}")

    # Typography vs impeccable.
    for role in ("heading", "body"):
        face = (typo.get(role) or "").strip()
        if not face:
            continue
        f = face.lower()
        if f in DETECTOR_OVERUSED:
            reject.append(f"{role.title()} font {face}: impeccable's detector flags it as overused (`overused-font`). Pick a face with character.")
        elif role == "heading" and f in DISPLAY_DEFAULTS:
            reject.append(f"Heading font {face}: on impeccable's list of training-data display defaults. Needs a reason no other face could satisfy.")
        else:
            review.append(f"{role.title()} font {face}: allowed. Use only if it fits the chosen visual world.")

    # Palette: contrast, AI-palette tells, cream ground.
    pairs = [("foreground", "background"), ("on_primary", "primary"), ("on_accent", "accent"),
             ("card_foreground", "card"), ("muted_foreground", "muted")]
    for fg, bg in pairs:
        if colors.get(fg) and colors.get(bg):
            r = contrast(colors[fg], colors[bg])
            (keep if r >= 4.5 else reject).append(f"Contrast {fg} on {bg}: {r:.2f}:1" + ("" if r >= 4.5 else " (below 4.5:1)"))
    for role in ("primary", "secondary", "accent"):
        if colors.get(role):
            h, l, s = hls(colors[role])
            if 255 <= h <= 300 and s > .35:
                reject.append(f"{role} {colors[role]} is purple/violet: impeccable's detector flags this as the most recognizable AI palette (`ai-color-palette`).")
    if colors.get("background"):
        h, l, s = hls(colors["background"])
        if l > .9 and 25 <= h <= 60 and s > .2:
            reject.append(f"Background {colors['background']} is warm cream: impeccable flags it (`cream-palette`) as the reflexive \"tasteful AI\" ground.")
    review.append("Palette roles " + ", ".join(f"{k} {colors[k]}" for k in ("primary", "secondary", "accent", "background") if colors.get(k))
                  + f" — notes: {colors.get('notes', '')}. Candidates only; impeccable's new-work picks the color strategy.")

    # Style + effects vs Emil.
    effects = (ds.get("key_effects") or style.get("effects") or "")
    if any(w in effects.lower() for w in ("no smooth transition", "instant", "no transition")):
        reject.append(f"Effect \"{effects}\": contradicts the generator's own checklist (150-300ms) and Emil's rules. "
                      "Resolution: state changes use 150-250ms with a strong ease-out; \"instant\" is allowed only for decorative, non-interactive changes.")
    review.append(f"Style {style.get('name')} ({style.get('keywords')}): one candidate world. Weigh it in impeccable's direction step, never adopt it unexamined.")

    ids = ds.get("source_identities", {})
    if len({v for k, v in ids.items() if k in ("style", "typography", "color")}) > 1:
        review.append("Style, palette and typography came from different database rows (" +
                      ", ".join(f"{k}: {v}" for k, v in ids.items()) + "). Treat them as independent suggestions, not one coherent system.")

    result = {"project": ds.get("project_name"), "category": ds.get("category"),
              "keep": keep, "review": review, "reject": reject,
              "google_fonts_url": typo.get("google_fonts_url")}
    if want_json:
        print(json.dumps(result, indent=1))
        return
    print(f"# Design brief: {result['project'] or 'project'} ({result['category']})\n")
    for title, items in (("KEEP (reliable)", keep), ("REVIEW (candidates for the direction step)", review), ("REJECT (conflicts with another module)", reject)):
        print(f"## {title}")
        for i in items:
            print(f"- {i}")
        print()


if __name__ == "__main__":
    main()
