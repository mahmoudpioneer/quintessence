---
name: Swipefile
description: A fly-posted street hoarding where the ads still running stay on the wall.
colors:
  site-green: "#1f3d2b"
  site-green-deep: "#173022"
  chalk: "#eef3ec"
  lichen: "#bcd3c2"
  newsprint: "#eceee8"
  newsprint-shade: "#dfe2da"
  fresh-paste: "#f7f8f4"
  press-black: "#141414"
  press-grey: "#3d3f3a"
  fluoro-orange: "#ff5b1a"
  riso-blue: "#2a49d6"
  fluoro-pink: "#ff3f8e"
  gaffer-yellow: "#ffd400"
  gaffer-ink: "#1a1600"
typography:
  display:
    fontFamily: "Big Shoulders Display, Arial Narrow, sans-serif"
    fontSize: "clamp(3.25rem, 6.6vw, 6rem)"
    fontWeight: 900
    lineHeight: 0.9
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Big Shoulders Display, Arial Narrow, sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 4.5rem)"
    fontWeight: 900
    lineHeight: 0.92
  title:
    fontFamily: "Big Shoulders Display, Arial Narrow, sans-serif"
    fontSize: "clamp(1.25rem, 1.9vw, 1.9rem)"
    fontWeight: 800
    lineHeight: 0.95
  body:
    fontFamily: "Libre Franklin, Franklin Gothic Medium, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Martian Mono, ui-monospace, monospace"
    fontSize: "0.6875rem"
    fontWeight: 600
    letterSpacing: "0.06em"
rounded:
  sm: "2px"
spacing:
  poster: "16px"
  gutter: "clamp(16px, 4vw, 56px)"
  section: "clamp(56px, 9vw, 128px)"
components:
  button-primary:
    backgroundColor: "{colors.press-black}"
    textColor: "{colors.newsprint}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  button-tape:
    backgroundColor: "{colors.gaffer-yellow}"
    textColor: "{colors.gaffer-ink}"
    rounded: "{rounded.sm}"
    padding: "14px 20px"
  input-link:
    backgroundColor: "#ffffff"
    textColor: "{colors.press-black}"
    rounded: "{rounded.sm}"
    padding: "12px 14px"
  poster:
    backgroundColor: "{colors.newsprint}"
    textColor: "{colors.press-black}"
    padding: "{spacing.poster}"
  state-tag:
    textColor: "{colors.press-black}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "3px 6px"
  counter-cell:
    backgroundColor: "{colors.press-black}"
    textColor: "{colors.newsprint}"
    rounded: "{rounded.sm}"
---

# Design System: Swipefile

## Overview

**Creative North Star: "The Fly-Posted Hoarding"**

The page is a painted construction hoarding in a city street. Ads are two-ink posters wheatpasted onto it; the ones still being paid for stay up and weather, one-day tests get pasted over. Every surface is either the hoarding (site green plywood) or paper stuck to it, and the paper carries the product's one idea: run-length is the signal.

The register is loud, physical and direct, the way street posting is, never glossy SaaS. Posters sit a few degrees off true, overlap at their edges, and carry stamps and counters like real bills. Anti-references: the dark dashboard-screenshot hero, feature-card rows, purple gradients, cream-and-serif "tasteful" grounds.

**Key Characteristics:**
- Site-green hoarding ground with plywood grain; paper everywhere content lives.
- Two-ink posters: press black plus one fluoro or riso ink each.
- Condensed wood-type gothic for every headline; Franklin for reading; mono only for counts, stamps and states.
- Run-length shown as fixed-cell split-flap day counters.
- Gaffer-yellow tape marks the visitor's choice.

## Colors

### Primary
- **Site Green** (`#1f3d2b`): the hoarding itself; owns most of every viewport. **Site Green Deep** (`#173022`) only for scrollbar track and shadowed plywood.

### Secondary
- **Fluoro Orange** (`#ff5b1a`): the long-runner ink and the hero highlight. The loudest thing on any screen; one orange field per viewport.
- **Riso Blue** (`#2a49d6`) and **Fluoro Pink** (`#ff3f8e`): second and third poster inks, one ink per poster.

### Tertiary
- **Gaffer Yellow** (`#ffd400`) with **Gaffer Ink** (`#1a1600`): the visitor's mark — tape on a chosen variant, focus rings, text selection, the header CTA.

### Neutral
- **Newsprint** (`#eceee8`): every poster and bill. Cool, never cream. **Newsprint Shade** (`#dfe2da`) for spent stock; **Fresh Paste** (`#f7f8f4`) for a sheet just pasted over another.
- **Press Black** (`#141414`) and **Press Grey** (`#3d3f3a`): ink on paper.
- **Chalk** (`#eef3ec`) and **Lichen** (`#bcd3c2`): text set directly on the hoarding.

### Named Rules
**The Two-Ink Rule.** A poster uses press black plus at most one colour ink. A second colour ink on one poster makes it a flyer, not a fly-poster.

**The Tape Is Yours Rule.** Gaffer yellow appears only where the visitor acted or can act (choice, focus, selection, primary header action). Never as decoration.

## Typography

### Hierarchy
- **Display** (Big Shoulders Display 900, `clamp(3.25rem, 6.6vw, 6rem)`, line-height 0.9, uppercase): the hero bill and the closing bill. Never above 6rem.
- **Headline** (Big Shoulders Display 900, `clamp(2.5rem, 5vw, 4.5rem)`, 0.92, uppercase): section headings set directly on the hoarding.
- **Title** (Big Shoulders Display 800, `clamp(1.25rem, 1.9vw, 1.9rem)`, 0.95, uppercase): poster hooks, state names, handbill steps.
- **Body** (Libre Franklin 400, 1.0625rem / 1.55): all reading copy, max 60ch. Ledes at 1.125rem.
- **Label** (Martian Mono 600, 0.6875rem, 0.06em, uppercase, tabular numerals): platform tags, state tags, stamps, counters. Never below 11px.

### Named Rules
**The Measured Mono Rule.** Mono is for things that are counted or stamped (days, dates, platforms, states). It never sets a sentence.

## Layout

Full-bleed hoarding with a fluid gutter (`clamp(16px, 4vw, 56px)`) and generous section breaks (`clamp(56px, 9vw, 128px)`). The hero splits 45/55: headline bill left, wall of posters right. Section heads pair the headline with its lede across two columns on desktop, stacking under 760px.

The wall is a 6-column grid of posters with explicit placement; posters overlap by up to 14px, staying inside the neighbour's 16px padding so no data is covered. Newer posters stack over older ones. On phones the wall becomes two columns, the long-runner spans both, and the narrowest poster drops.

## Elevation & Depth

Depth is paper on a wall, not floating UI: each sheet has a hairline contact shadow plus a soft drop (`0 1px 1px rgba(0,0,0,.25), 0 10px 24px -8px rgba(0,0,0,.45)`). Sheets are rotated between -1.2° and 1.4°. Newsprint carries a fractal-noise grain and faint wheatpaste creases; a weathered long-runner loses some saturation.

### Named Rules
**The Contact Shadow Rule.** Every shadow has an offset and a blur. No zero-blur block shadows; this is a hoarding, not neobrutalism.

## Shapes

Paper is square-cornered; controls take a 2px radius (`{rounded.sm}`). Borders are 2px press black on inputs and handbill rules, 1.5px on state tags. Tape is an irregular strip rotated against the sheet it holds.

## Components

### Buttons
- **Primary** (`button-primary`): press black on newsprint, 700 Franklin, 14px 20px, trailing arrow drawn as SVG. Press scales to 0.97 over 120ms with the strong ease-out; hover lifts to `#2b2b2b` (fine pointers only).
- **Tape** (`button-tape`): gaffer yellow, used once — the header's "Get the extension".

### Inputs / Fields
- **Link field** (`input-link`): white field, 2px press-black border, visible label above, error border `#c2261b` and an error line that names the fix. Loading state disables the button and says "Pasting…".

### Navigation
Stencilled SWIPEFILE sign at left (chalk plate, site-green letters), text links in Franklin 600, the tape button at right. Links collapse to the sign and tape button under 760px.

### Poster (signature)
Newsprint sheet, brand + platform label row, hook in Title type (optionally on an ink panel), split-flap day counter and state tag in the foot. States: testing, scaling, long-runner, pulled (pasted over by a fresh sheet).

### Day counter (signature)
Fixed-cell press-black tiles with a split line, tabular mono digits, three cells. The real count is always in the DOM; the flip plays once, the first time the page is seen.

### Wall report ticker
A newsprint strip pasted across the hoarding, two rows scrolling run-length counts in Title type with ink-highlighted values. It repeats wall data only, pauses off-screen, when hidden, and on hover/focus, and becomes a hand-scrollable static strip under reduced motion.

## Do's and Don'ts

### Do:
- **Do** keep every viewport mostly site green, with content on paper.
- **Do** show run-length as a counter or stamp wherever an ad appears.
- **Do** label example data as invented, close to where it appears.
- **Do** keep motion to one signature moment (paste-up) plus at most two ambient/reveal pieces (ticker, closing-bill print), all paused when unseen and settled under reduced motion.

### Don't:
- **Don't** use a cream or warm off-white ground; newsprint here is cool.
- **Don't** put a label above a heading (no eyebrows or kickers); ranges and stamps go below or beside.
- **Don't** let poster overlaps cover counters, stamps or hooks.
- **Don't** set text under 11px, or set sentences in mono.
- **Don't** invent customers, metrics, logos or pricing; Swipefile has none yet.
