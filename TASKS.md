# Backlog

Running list of things to do to the site. Not urgent, not ordered by priority —
delete items as they're done.

## Content

- [ ] **Publications** — `data/publications.bib` is empty. Add entries as
      preprints and papers appear; they surface on Research automatically.
- [ ] **Talks** — `data/talks.yml` is `talks: []`. Nothing public yet. Add
      conference talks, posters and seminars as they happen.
- [ ] **Headshot** — set `personal.headshot` in `data/cv.yml` points at
      `images/headshot.jpg`, which doesn't exist yet. Drop a photo in and the
      circular hero image on About appears by itself.
- [ ] **Research → Projects** — deliberately high-level for now. Revisit once
      the thesis structure settles; keep it to strands rather than chapters
      until then.
- [ ] **Google Scholar** — commented out in `cv.yml` links. Uncomment and fill
      in once there's a profile worth linking to.

## Routine

- [ ] **Now page** — rewrite roughly monthly, or whenever it stops being true.
- [ ] **CV** — review after each supervisory milestone: upgrade, transfer,
      new collaborations, anything that changes a title or date.
- [ ] **Writing** — currently a single link out to Substack. If pieces
      accumulate, convert to a Quarto listing (instructions are in the comment
      at the bottom of `writing.qmd`).

## Maintenance

- [ ] **GitHub Pages IPs** — the four A records in Cloudflare are hardcoded
      GitHub addresses. Stable for years, but if the site ever goes dark with
      DNS looking correct, re-check them against GitHub's docs before assuming
      something else broke.
- [ ] **HTTPS certificate** — auto-renews, expiry was 2026-11-03 at time of
      setup. If browsers start warning, check Settings → Pages first.
- [ ] **Node 20 deprecation warning** in Actions — harmless for now; the
      `checkout` and `setup-python` actions will need a version bump eventually.
