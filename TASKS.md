# Backlog

Running list of things to do to the site. Not urgent, not ordered by priority —
delete items as they're done.

## Content

- [ ] **Publications** — `data/publications.bib` is empty. Add entries as
      preprints and papers appear; they surface on Research automatically.
- [ ] **Talks** — `data/talks.yml` is `talks: []`. Nothing public yet. Add
      conference talks, posters and seminars as they happen.
- [ ] **Research → Projects** — deliberately high-level for now. Revisit once
      the thesis structure settles; keep it to strands rather than chapters
      until then.
- [ ] **Google Scholar** — commented out in `cv.yml` links. Uncomment and fill
      in once there's a profile worth linking to.
- [x] ~~Headshot~~ — done. `images/headshot.jpg`, sourced from the LSHTM
      profile and converted to JPEG (393K → 69K).

## Routine

- [ ] **Now page** — rewrite roughly monthly, or whenever it stops being true.
- [ ] **CV** — review after each supervisory milestone: upgrade, transfer,
      new collaborations, anything that changes a title or date.
- [ ] **Writing** — currently a single link out to Substack. If pieces
      accumulate, convert to a Quarto listing (instructions are in the comment
      at the bottom of `writing.qmd`).

## Open issues

- [ ] **`www.lukeaburton.co.uk` does not resolve.** The apex works and is the
      canonical URL, so this is cosmetic — but a visitor typing `www.` gets a
      dead name. The `www` CNAME → `lukeburton02.github.io` was added in
      Cloudflare and showed in the record list; check it saved and is set to
      "DNS only". GitHub's certificate already covers `www`.

## Maintenance

- [ ] **GitHub Pages IPs** — the four A records in Cloudflare are hardcoded
      GitHub addresses. Stable for years, but if the site ever goes dark with
      DNS looking correct, re-check them against GitHub's docs before assuming
      something else broke.
- [ ] **HTTPS certificate** — auto-renews, expiry was 2026-11-03 at time of
      setup. If browsers start warning, check Settings → Pages first.
- [ ] **Node 20 deprecation warning** in Actions — harmless for now; the
      `checkout` and `setup-python` actions will need a version bump eventually.

## Traps worth remembering

Both are documented in `CLAUDE.md`; repeated here because they cost time.

- **New `.md` file at the repo root?** Add it to the `render:` exclusion list in
  `_quarto.yml` or Quarto publishes it to the live site. `TASKS.html` was
  publicly readable for about an hour before this was caught.
- **Nav links appear broken?** Check `_site/` contains every page first. A
  render that aborts midway leaves a partial `_site/`, so the last pages in the
  render order 404 while earlier ones work.
- **DNS negative caching.** `.co.uk` has a 3-hour negative TTL. If the domain
  ever looks unreachable, verify with `ping` (which uses the same resolution
  path as the browser) rather than `dig` (which bypasses the OS cache and will
  report success while the browser still fails).
