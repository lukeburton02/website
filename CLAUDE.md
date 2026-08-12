# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

A personal academic website built with Quarto, deployed to GitHub Pages at
<https://lukeaburton.co.uk>.

## The one rule that matters

**`data/*.yml` and `data/publications.bib` are the single source of truth for
every fact on this site.** Never hardcode a name, role, date, job title, or
affiliation directly in a `.qmd` file. If a fact needs to appear on a page, it
goes in a data file and reaches the page through a generated partial or a
`{{< var >}}` substitution.

**Never invent publications, talks, dates, venues, or affiliations.** If a
detail is missing, leave it marked `PLACEHOLDER` and ask. A wrong date on a
public academic CV is worse than a visible gap.

**`data/cv.private.yml` is gitignored.** It must never be committed, and
nothing from it may appear in `_site/` or on the `gh-pages` branch.

## Build pipeline

`_render/build.py` runs as a Quarto `pre-render` step and turns `data/*.yml`
into two kinds of generated output:

| Output | Purpose | Used as |
|---|---|---|
| `_variables.yml` | scalars — name, role, affiliation, tagline, location, aside | `{{< var personal.name >}}` |
| `_generated/*.md` | markdown partials for repeating lists | `{{< include _generated/cv-roles.md >}}` |

Both are gitignored — they are derived, and regenerated on every render.

### The ordering trap

Quarto expands `{{< include >}}` directives while building the project context,
which happens **before** `pre-render` scripts execute. A checkout with no
`_generated/` directory therefore fails to render *before* `build.py` gets a
chance to create it.

Consequences, both already handled — don't "tidy" either away:

- After a fresh clone, run `python3 _render/build.py` once before the first render.
- `.github/workflows/publish.yml` runs `build.py` as an explicit step, not just
  via the `pre-render` hook.
- If `quarto preview` dies right after you add a **new** `{{< include >}}`, this
  is why. Run `python3 _render/build.py` and restart it.

### Loose `.md` files at the project root become public pages

Quarto treats **every `.md` file in the project directory as a render input**.
`CLAUDE.md` and `TASKS.md` were therefore built into `_site/` and published to
`gh-pages` — `TASKS.html` was publicly readable on the live site until it was
caught. They are excluded explicitly in `_quarto.yml`:

```yaml
render:
  - "*"
  - "!CLAUDE.md"
  - "!TASKS.md"
```

**Any new maintainer doc added at the repo root must be added to that exclusion
list**, or it ships to the public site. After adding one, confirm with
`ls _site/ | grep -i <name>` and `grep -rl <name> _site/` — the search index
(`search.json`) picks these up too.

### A failed render leaves a partially-built `_site/`

If a render aborts midway, Quarto leaves `_site/` containing only the pages
completed before the failure. The symptom is that *some* navbar links work and
others 404 — it looks like a broken navbar but is not. This was reported once
as "clicking CV and Writing does nothing"; the real cause was a dead preview
server and a stale `.quarto/preview/lock`.

If nav links appear broken, check `_site/` actually contains every page before
touching `_quarto.yml`.

## Commands

```bash
python3 _render/build.py      # regenerate _variables.yml and _generated/
quarto preview                # local server with live reload
quarto render                 # full build into _site/
grep -ri "placeholder" _quarto.yml *.qmd data/*.yml data/*.bib   # pre-push check
```

There are no tests. The meaningful check before pushing is the `grep` above
plus reading the rendered pages. Matches inside YAML/BibTeX *comments* are
fine; matches in `.qmd` prose are not — those render to the public page.

## Deploy loop

Edit → commit → push to `main` → GitHub Actions redeploys in ~25s.

The workflow renders and publishes to the `gh-pages` branch via
`quarto-actions/publish`. Pages serves from `gh-pages` / root. `CNAME` is
listed under `project.resources` in `_quarto.yml` so it survives into the
published output — if it ever goes missing, the custom domain breaks.

## Common tasks

**Add a talk** — append to `data/talks.yml`. Sorted newest-first at build time,
so order in the file doesn't matter. Omit `slides_url` (or set it `null`) and
no link renders.

**Publish slides** — a deck is written for a room that already knows who
everyone is; the published file is not. Work through this before committing
one, every time:

1. **Strip every personal name from the title slide.** Conference decks
   normally open with the full project-team list. The published
   `slides/2026-08-ini-behavioural-drivers.pdf` keeps only "Luke Burton –
   NIHR HPRU PhD" and the talk title; five names on the source slide were
   removed. Match that.
2. **Check the rest of the deck too** — acknowledgements slides, "joint work
   with" lines, supervisor names in a footer, names inside screenshots.
   Citations of published papers are fine: those are already public.
3. **Named groups follow the site-wide rule below** — his own affiliations may
   be named, collaborating groups are described rather than named.
4. **Export the PDF from the redacted copy, and keep the source deck out of
   the repo.** A `.pptx` or `.key` carries author metadata, speaker notes and
   edit history that the PDF does not. Only the PDF is committed, to `slides/`.
5. **Verify the committed file**, don't trust the export:

   ```bash
   pdftotext slides/<file>.pdf - | grep -i -e "<surname>" -e "joint work" -e "with thanks"
   python3 -c "import re,sys; d=open(sys.argv[1],'rb').read(); print([k for k in (b'/Author',b'/Title',b'/Creator') if re.search(k+rb'\s*\((.*?)\)',d)])" slides/<file>.pdf
   ```

   The existing deck has no `/Author` key at all and a filename-derived
   `/Title` — that's the standard to match. A name surviving in metadata is
   invisible on screen and still ships.

**Add a publication** — append a BibTeX entry to `data/publications.bib`.
`research.qmd` sets `nocite: "@*"`, so every entry appears automatically. No
`.qmd` edit needed.

**Update the Now page** — `now.qmd` is ordinary prose and the one page that's
allowed to go stale between rewrites. The pint-count line comes from
`personal.aside` in `cv.yml`, deliberately kept off `cv.qmd`.

**Change the accent colour** — `styles.scss`, top of the `scss:defaults` layer.
Eight variables (`$accent`, `$bg`, `$surface`, `$ink`, `$ink-muted`, the two
font stacks, `$font-size-root`) drive everything, including the background
motifs, which interpolate the palette into inline SVG data URIs. Change the
value there, nowhere else.

**Add a CV section** — add the block to `data/cv.yml`, write a `build_*()`
function in `_render/build.py`, register it in `main()`, and add an
`{{< include >}}` to `cv.qmd`. See `build_service()` for the pattern.

**Add the headshot** — drop the image at the path in `personal.headshot`
(`images/headshot.jpg`). `build_headshot()` emits nothing unless the file
actually exists on disk, so a missing image leaves a clean gap rather than a
broken-image icon.

## Layout notes

- The navbar deliberately has **no title** (`navbar: title: false`). `_quarto.yml`
  can't read from `cv.yml`, so a title there would be the one hardcoded copy of
  the name. About is the route home.
- `website.site-url` is set to the canonical host. Quarto needs it to emit
  `sitemap.xml` and `robots.txt`; without it both are absent or hostless.
- `talks: []` is intentionally empty — the generator renders a quiet "nothing
  yet" note rather than fake entries. Same for `publications.bib`.
- Only R is listed under software skills. That is accurate; don't pad it.
- Research interests are deliberately capped at four, with near-duplicates
  collapsed ("epidemiological modelling" folded into "infectious disease
  modelling"; the three economics entries into "economic evaluation"). Don't
  re-split them. The same four appear on the Research page — keep them in sync.

### Never name individuals; be careful naming groups

**No colleague, collaborator or supervisor is named anywhere on the public
site.** This is a standing instruction, not a stylistic preference — naming
someone publicly is their business as much as his.

Named *research groups* follow a subtler line:

- **His own roles may name their group** — e.g. the CMMID volunteering entry
  names the centre, which he has confirmed is fine.
- **Groups he collaborates with are described, not named** — "the mathematical
  modelling team at Bristol", not the group's formal name. He was explicit that
  this extends to groups within LSHTM. He may revisit this later, but ask
  before changing it.

Institutions (Bristol, Leicester, UKHSA) are fine to name.

### Proportion: convey it once, through structure

The LSHTM PhD is full-time; the UCL health-economics work is one day a week.
The pages should reflect that — but say it **once**, plainly, and let the page
structure carry the rest.

He pushed back in both directions here, so aim for the middle: first when the
two strands were given equal billing, then again when the fix over-corrected
into "almost all of the week goes to… a much smaller strand is…", which he
found laboured. A single mention that the second is part-time is enough.

Don't let the smaller strand grow to match the larger one just because there
is more concrete detail available about it.

### Keep specific facts specific

Plain prose does not mean vague prose. When he gives an exact figure or detail,
keep it exactly — softening "301 pints" to "a few hundred" was wrong and he
asked for the number back. Strip the framing around a detail, never the detail.
- Research pages stay at a high level by choice: the PhD is early and its
  chapter structure is still moving. Don't add a chapter plan or infer thesis
  structure beyond what's already written.
