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
- `awards: []` and `talks: []` are intentionally empty — the generator renders a
  quiet "nothing yet" note rather than fake entries.
- Only R is listed under software skills. That is accurate; don't pad it.
- Research pages stay at a high level by choice: the PhD is early and its
  chapter structure is still moving. Don't add a chapter plan or infer thesis
  structure beyond what's already written.
