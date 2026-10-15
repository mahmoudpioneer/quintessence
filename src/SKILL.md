---
name: quintessence
description: Five design toolkits distilled into one workflow for building, redesigning, reviewing and polishing frontend UI — ui-ux-pro-max (design-system generator, styles/palettes/fonts/UX database), impeccable (product context, 24 design commands, anti-slop detector, review agents), Emil Kowalski's skills (animation craft, motion review, native feel, UI library picks), taste-skill (anti-generic aesthetic directions — minimalist, soft/premium, brutalist, redesign), and Forever AI Components (604 ready-made animated HTML components). Use for any task that changes how an interface looks, feels, moves or reads: landing pages, dashboards, app screens, components, design systems, tokens, typography, color, layout, animation, accessibility, UX copy, redesigns, critiques and audits. Also for brand, logo, banner and slide design. Not for backend-only work.
user-invocable: true
argument-hint: "[build|quick|redesign|system|style|components|init|shape|critique|audit|polish|bolder|quieter|distill|harden|onboard|colorize|typeset|layout|delight|overdrive|clarify|adapt|optimize|live|generate|animate|motion-review|mobile|library|prototype|capture|brand|logo|banner|slides|tokens|help] [target]"
license: MIT (bundles MIT and Apache-2.0 modules; see LICENSES/)
---

# Quintessence

One entry point over five design toolkits. This file decides **which module runs, in what order, and who wins when they disagree.** The modules hold the depth — load only the ones the current step needs.

`<q>` below means this skill's base directory (the folder containing this file, normally `~/.claude/skills/quintessence`). Every module lives in `<q>/modules/<name>/` with its own `SKILL.md`; relative paths inside a module (`scripts/…`, `reference/…`, `references/…`) resolve against **that module's folder**.

**Platform notes.** Commands below are written for macOS/Linux (`python3`, forward slashes). On **Windows**, Claude Code runs commands in Git Bash: forward-slash paths still work and `<q>` is `%USERPROFILE%\.claude\skills\quintessence`; use `python` (or `py -3`) whenever `python3` is not found; run the impeccable launcher as `scripts/impeccable` from Git Bash, or `scripts\impeccable.cmd` from cmd/PowerShell. Screenshots need Node 22+ and any Chromium browser (Edge ships with Windows).

## Modules

| Module | Path | Owns |
|---|---|---|
| ui-ux-pro-max | `modules/ui-ux-pro-max/` | Design-system generator + searchable DB: 79 styles, 192 palettes, 74 font pairings, 119 UX rules, charts, 22 stack guides. Script: `scripts/search.py`. Read its generator output through `<q>/scripts/design_brief.py`. |
| uupm extras | `modules/uupm-design-system/`, `uupm-ui-styling/`, `uupm-brand/`, `uupm-banner-design/`, `uupm-slides/`, `uupm-design/` | Token architecture, shadcn/Tailwind setup, brand voice, banners, HTML slides, logo/CIP/icon generation (image generation needs a `GEMINI_API_KEY` or other provider key) |
| impeccable | `modules/impeccable/` | PRODUCT.md / DESIGN.md context, 24 commands, quality floor (`reference/craft-floor.md`), 61-rule deterministic detector via `scripts/impeccable`, and four installed subagents: `impeccable-finish-reviewer`, `impeccable-documenter`, `impeccable-asset-producer`, `impeccable-manual-edit-applier` |
| emil | `modules/emil/<skill>/` | `emil-design-eng` (philosophy), `animate`, `review-animations`, `improve-animations`, `find-animation-opportunities`, `animation-vocabulary`, `apple-design`, `mobile-native`, `pick-ui-library`, `prototype`, `ask-sonner` |
| taste | `modules/taste/<skill>/` | `taste-skill` (anti-slop direction + pre-flight), `minimalist-skill`, `soft-skill`, `brutalist-skill`, `redesign-skill`, `stitch-skill` (DESIGN.md for Google Stitch), `output-skill` (no truncation) |
| forever | `modules/forever/` | 604 local HTML components (~320 ambient/looping animations, plus reveals, effects and widgets) + `scripts/forever_search.py`. The default source for page-level motion. |

## Precedence (when modules disagree)

1. **The user's brief wins** — pinned fonts, palettes, eras, aesthetics. Never steer a clear brief toward a module's taste.
2. **Project truth:** `PRODUCT.md` (who/why) and `DESIGN.md` (the visual system) at the project root are the single source of truth. impeccable owns these files; other modules feed decisions *into* them rather than writing parallel files. Don't run ui-ux-pro-max `--persist` (which writes `design-system/MASTER.md`) unless the user asks; put its output into DESIGN.md instead.
3. **Quality floor:** impeccable `reference/craft-floor.md` is the hard floor for any UI edit. taste's bans and ui-ux-pro-max's priority-1–3 rules (accessibility, touch, performance) stack on top — follow the stricter rule.
4. **Motion:** Forever supplies *what* moves at page level (ambient loops, reveals, effects); emil owns *how* it moves (easing, duration, interruption, reduced-motion, hover gating) and has the final say on UI controls. On Persuade/Experience surfaces, "atmosphere" is a valid purpose for Forever motion inside the **Motion budget** below, so emil's frequency gate applies to controls and repeated interactions, not to the page's ambient layer. impeccable's "one authored moment" means one *signature* moment; the budget's ambient slots don't count against it.
5. **Aesthetic direction:** impeccable's new-work flow picks the visual world. taste presets are *options inside that decision* — use one when the user names the aesthetic ("minimal", "premium/soft", "brutalist") or asks for a less generic look.
6. **Design data:** ui-ux-pro-max's generator stitches pattern, style, palette and fonts from separate rows and can contradict itself. Always run it through `design_brief.py`: KEEP items are reliable, REVIEW items are candidates for the direction step, REJECT items lose to the module that bans them.
7. **Components:** search Forever before hand-rolling a visual effect; search emil `pick-ui-library` before hand-rolling a behavior (toast, command menu, OTP, virtualization, charts). Retrieved components are restyled to the project's tokens — never the reverse.
8. **Verification:** impeccable's bounded verify loop (build → one batched inspect → one fix batch → at most one confirm round). Don't loop forever.

## Routing

Map `/quintessence <arg>` or the user's plain-language request:

| Request | Do |
|---|---|
| no argument / "help" / "what can you do" | Print this routing table as a short menu. Don't auto-run anything. |
| **build** a new page/app/screen | Run the **Build pipeline** below. |
| **quick** / a single component, section or small page / "just make it look good" / a prototype or throwaway | Run the **Quick path** below. When the size is ambiguous, offer both in one line: full build (direction round, review agents) or quick (one pass). |
| **redesign** / "make this look better / less generic" | Run the **Redesign pipeline** below. |
| **system** / palette / fonts / "what style fits X" | `design_brief.py`, then supplementary ui-ux-pro-max `--domain` searches. |
| **style** minimalist / soft / premium / brutalist | Load the matching taste preset; reconcile it with DESIGN.md. |
| **components** / "find a loader/background/hero effect" | forever search. |
| **capture** / screenshots | `node <q>/scripts/capture.mjs <url>` |
| init, shape, document, extract, critique, audit, polish, bolder, quieter, distill, harden, onboard, colorize, typeset, layout, delight, overdrive, clarify, adapt, optimize, live, generate, hooks, doctor, pin | impeccable — load `modules/impeccable/SKILL.md`, then the command's reference file, exactly as impeccable's own routing says. |
| **animate** / add motion / transitions | Forever search for the motion itself (ambient, reveal, effect), then emil `animate` (web) for its ingredients — with `apple-design` for gesture/spring-heavy UI. Use `animation-vocabulary` when the user describes motion vaguely. impeccable `animate` only for its "where should motion go" survey, then hand execution to emil. |
| **motion-review** / review my animations | emil `review-animations` (single change) or `improve-animations` (whole codebase audit + plans); `find-animation-opportunities` for "where should we add motion". |
| **mobile** / feels like a website on my phone | emil `mobile-native`, then impeccable `adapt`. |
| **library** / "which package for X" | emil `pick-ui-library` (and `ask-sonner` for toasts). |
| **prototype** / "show me a few versions" | emil `prototype` (in-page variant switcher). For variants on a live running app, impeccable `live`/`generate`. |
| **brand**, **logo**, **banner**, **slides**, **tokens**, shadcn/Tailwind setup | the matching `uupm-*` module (`uupm-brand`, `uupm-design` for logo/CIP/icons, `uupm-banner-design`, `uupm-slides`, `uupm-design-system`, `uupm-ui-styling`). |
| Google Stitch DESIGN.md | taste `stitch-skill`. |

If two routes fit equally, ask once.

## Motion budget

Pick the slots from the surface's mode (impeccable's Persuade / Operate / Read / Experience):

| Mode | Signature moment | Forever ambient / reveal slots | Micro-feedback |
|---|---|---|---|
| Persuade, Experience | 1, tied to the product's mechanism (often a Forever piece adapted) | **up to 2** (e.g. one ambient loop + one one-shot reveal) | emil rules |
| Operate, Read | 0–1 | 0. Forever only for loaders, empty/feedback states | emil rules |

Every animated piece, Forever-derived or not, must:
- **Keep real content in the DOM.** Motion layers on top; a hidden tab, crawler or failed script still shows final values. Only hide or zero content *after* confirming frames run (inside the first `requestAnimationFrame`) or after an observer has reported the element off-screen.
- **Pause when not seen:** `IntersectionObserver` off-screen and `visibilitychange` hidden. Observe a wrapper, not an element you clip or hide — an element's own `clip-path` hides it from the observer.
- **Settle to a readable final state under `prefers-reduced-motion`** (fades allowed, movement removed).
- **Never keep moving text the visitor must read.** Turn a looping reveal into a one-shot on scroll-in; let tickers pause on hover/focus and mark duplicated tracks `aria-hidden`. A pause rule must out-rank any `animation:` shorthand, which silently resets `animation-play-state`.
- **Use the project's tokens and fonts**, never Forever's system display faces (craft-floor ban).
- **Stay in budget on performance:** `--perf medium` max, `heavy` only for the signature moment.

**Known clash with impeccable's detector:** it flags every infinite horizontal loop as `marquee`. A Forever ticker/marquee is allowed only when everything it shows also appears elsewhere on the page (it is atmosphere, not the only copy). Report the `marquee` finding to the user as a deliberate Motion-budget choice, not a silent pass. If the ticker is the only place information lives, it fails: use a static list instead.

## Build pipeline (new surface)

1. **Context** — Run impeccable setup (`modules/impeccable/scripts/impeccable context`, cwd = user's project). If PRODUCT.md is missing for a new product, run impeccable `init` first (it asks only for real gaps). Use `shape` when the request is vague.
2. **Design intelligence** — `python3 <q>/scripts/design_brief.py "<product type> <industry> <keywords>" -p "<Name>"`. Carry KEEP into the build, REVIEW into the direction step, and drop REJECT. Add `search.py --stack <stack>` guidance for the project's framework.
3. **Direction** — Follow impeccable `reference/new-work.md` to commit to a visual world, using step 2's candidates and, when it fits, a taste preset. Then shortlist motion: run `forever_search.py` with the world's mood/style and the page's use-cases (hero, section-divider, cta, background) and note 3–5 candidates for the Motion budget's slots.
4. **Parts** — For each visual effect, run `forever_search.py`; for each behavior, check emil `pick-ui-library`. Adopt, restyle to tokens, keep their a11y/reduced-motion code.
5. **Build** — Read impeccable `reference/craft-floor.md` immediately before writing UI. Apply taste `output-skill` rules for large files: complete code, no placeholders or `// ...rest` elisions.
6. **Motion** — Fill the Motion budget: adapt the shortlisted Forever pieces into the signature and ambient/reveal slots (restyled, one-shot where content is read, paused off-screen), then run emil `animate` on every piece and every interactive control for curve, duration, interruption and reduced motion. Controls and repeated interactions still pass emil's "should it animate" gate.
7. **Verify** — one batched pass: `node <q>/scripts/capture.mjs <url>` writes `.impeccable/review/desktop.png` and `mobile.png`; run the impeccable detector once; emil `review-animations` on motion code; ui-ux-pro-max `references/pro-rules.md` pre-delivery checklist. Confirm motion actually plays in a foreground tab (`capture.mjs --motion`, or a visible browser) and settles correctly with reduced motion. Fix all findings in one batch, confirm once.
8. **Finish** — spawn the `impeccable-finish-reviewer` agent with the inputs impeccable's new-work section 7 lists, act on its disposition, then spawn `impeccable-documenter` to write DESIGN.md. Agents are installed globally by Quintessence; only if they are unavailable, run `modules/impeccable/reference/degraded/finish-reviewer.md` / `documenter.md` in-thread and say so in one line.

## Quick path (small or throwaway work)

Same quality floor, no ceremony. Use for one component, one section, a small page, or anything the user calls quick, rough or a prototype.

1. Read PRODUCT.md / DESIGN.md if they exist (no init interview, no `concept-seed` roll, no decision page, no surface brief).
2. If there's no visual system yet: `design_brief.py` once, pick one direction yourself in a single sentence (a taste preset is fine), and state it.
3. Forever search for any effect or motion; emil `pick-ui-library` for any behavior.
4. Read `craft-floor.md`, build, apply emil's Never-Ship table to motion.
5. One verify pass: detector once + `capture.mjs` once. Fix mechanical findings. No review agents, no DESIGN.md unless asked.
6. End by offering the full pipeline if the work turns out to matter.

## Redesign pipeline (existing UI)

1. impeccable context; `document` to generate DESIGN.md if none exists.
2. Diagnose in one pass: impeccable `critique` (UX/hierarchy) + `audit` (a11y/perf/responsive/detector) + taste `redesign-skill`'s generic-AI-pattern checklist.
3. Decide refine vs replace (impeccable: *refinement preserves; redesign replaces*). For replace, run Build steps 2–3 to pick the new world.
4. Apply targeted impeccable commands (`typeset`, `layout`, `colorize`, `bolder`/`quieter`, `clarify`, `harden`…) and Forever/emil per Build steps 4–6.
5. Finish with impeccable `polish` and Build steps 7–8.

## Tooling notes

- **Design brief:** `python3 <q>/scripts/design_brief.py "<query>" [-p Name] [--json] [--variance/--motion/--density 1-10]` — ui-ux-pro-max's generator filtered against impeccable's font/palette bans, contrast, and emil's motion rules.
- **ui-ux-pro-max search:** `python3 <q>/modules/ui-ux-pro-max/scripts/search.py "<query>" [--domain style|color|typography|google-fonts|ux|landing|product|chart|icons|gsap|react|web] [--stack nextjs|react|vue|svelte|astro|html-tailwind|shadcn|swiftui|react-native|flutter|...] [-n N]`. Python 3 stdlib only.
- **Capture:** `node <q>/scripts/capture.mjs <url> [--out .impeccable/review] [--widths 1440,390] [--motion]` — full-page desktop + true-width mobile screenshots through headless Chrome (Node 22+, no npm deps). Reduced motion by default so entrances have settled.
- **impeccable launcher:** `<q>/modules/impeccable/scripts/impeccable <verb>`. Runs a verified engine binary cached in `~/.impeccable/bin/`. Quintessence's copy of the launcher turns off impeccable's telemetry ping and update check. `concept-seed` still fetches its direction catalog from impeccable.style (only the roll settings are sent); set `QUINTESSENCE_OFFLINE=1` for a fully offline roll without catalog challengers. If the launcher fails, say so in one line, read PRODUCT.md/DESIGN.md directly, and continue. Inside impeccable's docs, `.claude/skills/impeccable/…` means `<q>/modules/impeccable/…`, and `/impeccable <cmd>` means `/quintessence <cmd>`.
- **forever search:** `python3 <q>/modules/forever/scripts/forever_search.py "<keywords>" [filters]`; `--show <file>` for path + adaptation metadata; `--facets` for filter values.
- **emil / taste** modules are pure guidance — read the module's `SKILL.md` (and its `RECIPES.md` / `STANDARDS.md` / `AUDIT.md` when it points there).
- Upstream versions and licenses: `<q>/SOURCES.md`, `<q>/LICENSES/`.
