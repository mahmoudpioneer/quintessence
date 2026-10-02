---
name: forever-components
description: Retrieve ready-made, dependency-free HTML components (backgrounds, heroes, loaders, buttons, cards, nav, text effects, dataviz, cursors) from the bundled Forever AI Components registry before hand-rolling new UI.
---

# Forever AI Components (module of Quintessence)

604 self-contained `.html` components (inline CSS + JS, Canvas/SVG/CSS, no build step), bundled locally in `infinite/`. Source: github.com/isas1/forever-ai-components (MIT).

## When to use

Before generating a visual element from scratch — an animated background, hero visual, loader, button effect, card, nav pattern, kinetic text, micro chart, cursor effect, empty/404 state — search here first. Only build new UI if nothing fits.

## Search

```bash
python3 <module-dir>/scripts/forever_search.py "<keywords>" [filters] [-n 8]
```

Filters (repeatable): `--role` `--use-case` `--style` `--mood` `--technique` `--label` `--interaction` `--scheme` `--intensity`, plus `--perf cheap|medium|heavy` (maximum tier) and `--no-deps`. Run `--facets` to see every valid value with counts.

```bash
python3 scripts/forever_search.py loader --perf cheap --label mobile-ready
python3 scripts/forever_search.py "calm hero" --use-case hero --scheme dark --label accessible
python3 scripts/forever_search.py --role button --technique css-only
python3 scripts/forever_search.py --show navigation/10-command-palette.html
```

`--show` prints the local file path and the component's embedded `forever-agent-meta` block (`useWhen`, `avoidWhen`, `editableAreas`, `preserveElements`, `knownLimitations`). Read that block before adapting.

## Selection defaults

1. Default to `--perf medium` max; `cheap` for anything repeated many times on a page; `heavy` only for the page's single signature moment.
2. Prefer `accessible` and `mobile-ready` labels; prefer `easy-to-modify` when you will restyle it.
3. Pick the smallest set that solves the task. For a page, compose a coordinated set (e.g. editorial: swiss type + micro-dataviz + minimal nav; motion hero: kinetic type + particles + loader).
4. The project's design direction wins. A component must fit the palette, type and mood chosen upstream (ui-ux-pro-max design system / taste direction), not the other way around.

## Adaptation rules

- Replace hard-coded hex values with the project's tokens; replace px spacing with its scale; swap Google Fonts for the project's fonts.
- **Keep** `prefers-reduced-motion` handling, `document.hidden` pause logic, namespaced CSS/JS prefixes, and semantic structure.
- Port to the project's framework (React/Vue/Svelte component, Tailwind classes) when the project isn't plain HTML; keep the canvas/animation logic intact and clean up listeners on unmount.
- Add no new dependencies.
- **Adapting a looping component:** keep its pause logic and add an `IntersectionObserver` so it also stops off-screen. If the loop reassembles text people read (poster builds, kinetic headlines), make it a one-shot that runs when it scrolls into view. Tickers/marquees pause on hover and focus, and the duplicated track is `aria-hidden`.
- **Start from the finished state:** the static HTML shows the final composition; JS adds a "ready to animate" class only when the element is visible, not in a hidden tab, and reduced motion is off.
- Count each adapted piece against Quintessence's Motion budget.
- After adapting, motion still goes through the emil animation rules and the result through impeccable's audit.
