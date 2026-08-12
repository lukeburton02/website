#!/usr/bin/env python3
"""Turn data/*.yml into the bits of the site that display personal details.

Run automatically by Quarto as a `pre-render` step (see _quarto.yml), which
keeps the output fresh as you edit.

Run it by hand once after a fresh clone, before the first render:

    python3 _render/build.py

That first run is not optional. Quarto expands {{< include >}} directives while
building the project context, which happens before pre-render scripts execute —
so on a checkout with no _generated/ directory, rendering fails before this
script ever gets a chance to create it. The CI workflow does the same thing as
an explicit step for the same reason.

Writes two things, both gitignored because both are derived:

  _variables.yml      scalars for inline use in prose, e.g. {{< var personal.name >}}
  _generated/*.md     markdown partials for the repeating lists, pulled into
                      pages with {{< include _generated/cv-education.md >}}

The point of the arrangement: no .qmd file contains a name, date, job title or
affiliation. data/cv.yml is the only place any of that lives.
"""

from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - environment guard
    sys.exit(
        "build.py needs PyYAML. Install it with:"
        "  python3 -m pip install -r requirements.txt"
    )

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
GENERATED = ROOT / "_generated"

EN_DASH = "–"


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def deep_merge(base: dict, overlay: dict) -> dict:
    """Overlay wins. Nested dicts merge; lists and scalars are replaced."""
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_cv() -> dict:
    """data/cv.yml, with data/cv.private.yml layered on top if it exists."""
    cv = read_yaml(DATA / "cv.yml")
    private = read_yaml(DATA / "cv.private.yml")
    return deep_merge(cv, private) if private else cv


# --------------------------------------------------------------------------
# formatting helpers
# --------------------------------------------------------------------------

def as_text(value) -> str:
    """YAML may hand us dates or numbers; markdown wants strings."""
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value).strip()


def date_range(start, end) -> str:
    """'2024 – Present', '2023 – 2024', or a lone date."""
    start, end = as_text(start), as_text(end)
    if start and end:
        return f"{start} {EN_DASH} {end}"
    if start:
        return f"{start} {EN_DASH} Present"
    return end


def pretty_date(value) -> str:
    """ISO dates become '14 June 2025'; anything else passes through."""
    text = as_text(value)
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        return parsed.strftime("%B %Y" if fmt == "%Y-%m" else "%-d %B %Y")
    return text


def sort_key(value) -> str:
    """Sort talks newest-first without choking on non-ISO dates."""
    return as_text(value)


def entry_block(
    dates: str,
    heading: str,
    subheading: str,
    notes: str,
    department: str = "",
) -> str:
    """One two-column CV row. Styling lives in styles.scss.

    `department` renders on its own line above the heading, for entries where
    the unit within the institution matters (a university department, a
    research group). `notes` may contain several paragraphs — see
    note_lines() — each of which becomes its own line under the heading.
    """
    lines = ["::: {.cv-entry}", f"::: {{.cv-dates}}\n{dates or '&nbsp;'}\n:::", "::: {.cv-body}"]
    if department:
        lines.append(f"::: {{.cv-dept}}\n{department}\n:::")
        lines.append("")
    head = f"**{heading}**" if heading else ""
    if subheading:
        head = f"{head} <span class='cv-org'>{subheading}</span>" if head else subheading
    if head:
        lines.append(head)
    if notes:
        lines.append("")
        lines.append(f"::: {{.cv-notes}}\n{notes}\n:::")
    lines.append(":::")
    lines.append(":::")
    return "\n".join(lines)


def note_lines(*parts) -> str:
    """Join note fragments so each renders as its own line.

    Blank-line separation makes Pandoc emit a paragraph per fragment, which is
    how a grade ends up above a thesis title rather than running into it.
    Empty fragments drop out.
    """
    return "\n\n".join(text for text in (as_text(p) for p in parts) if text)


def placeholder(what: str) -> str:
    """Quiet note for an empty section.

    Deliberately says nothing about where the data lives: this renders on the
    public page, and internal file paths are not a visitor's business.
    """
    return (
        f"::: {{.callout-note appearance='minimal'}}\n"
        f"No {what} yet.\n"
        f":::"
    )


# Kept free of file paths: these partials are pasted into pages verbatim, so
# whatever is here ends up in the public HTML source. The build layout is
# documented in CLAUDE.md, which is where a maintainer will look anyway.
HEADER = "<!-- Generated file. Do not edit by hand. -->\n"


def write(name: str, body: str) -> None:
    GENERATED.mkdir(exist_ok=True)
    (GENERATED / name).write_text(HEADER + body.rstrip() + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# section builders
# --------------------------------------------------------------------------

def build_education(cv: dict) -> None:
    entries = cv.get("education") or []
    blocks = [
        entry_block(
            date_range(e.get("start"), e.get("end")),
            as_text(e.get("title")),
            as_text(e.get("institution")),
            note_lines(e.get("supervision"), e.get("grade"), e.get("notes")),
            department=as_text(e.get("department")),
        )
        for e in entries
    ]
    write("cv-education.md", "\n\n".join(blocks) if blocks else placeholder("education"))


def build_roles(cv: dict) -> None:
    entries = cv.get("roles") or []
    blocks = [
        entry_block(
            date_range(e.get("start"), e.get("end")),
            as_text(e.get("title")),
            as_text(e.get("organisation")),
            as_text(e.get("notes")),
            department=as_text(e.get("department")),
        )
        for e in entries
    ]
    write("cv-roles.md", "\n\n".join(blocks) if blocks else placeholder("roles"))


def build_service(cv: dict) -> None:
    """The `service:` block in cv.yml. Headed "Volunteering" on the page —
    the YAML key and this function keep the older name."""
    entries = cv.get("service") or []
    blocks = [
        entry_block(
            date_range(e.get("start"), e.get("end")),
            as_text(e.get("title")),
            as_text(e.get("organisation")),
            as_text(e.get("notes")),
            department=as_text(e.get("department")),
        )
        for e in entries
    ]
    write("cv-service.md", "\n\n".join(blocks) if blocks else placeholder("volunteering"))


def build_awards(cv: dict) -> None:
    entries = cv.get("awards") or []
    blocks = [
        entry_block(
            as_text(e.get("year")),
            as_text(e.get("title")),
            as_text(e.get("awarder")),
            as_text(e.get("notes")),
        )
        for e in entries
    ]
    write("cv-awards.md", "\n\n".join(blocks) if blocks else placeholder("awards"))


def build_skills(cv: dict) -> None:
    groups = cv.get("skills") or []
    blocks = []
    for group in groups:
        # Separated with a middot, not a comma: some interests contain commas
        # of their own ("Social contact, mobility and attitude data") and a
        # comma-joined list makes them read as separate entries.
        items = " · ".join(as_text(i) for i in (group.get("items") or []) if as_text(i))
        blocks.append(entry_block(as_text(group.get("category")), "", "", items))
    write("cv-skills.md", "\n\n".join(blocks) if blocks else placeholder("skills"))


def build_current_positions(cv: dict) -> None:
    """Everything held right now — education first, then roles. About page.

    The heading on index.qmd reads "Current positions", so the PhD has to be
    in the list: leaving it out would make the two part-time entries below it
    look like the whole of the week. It still lives under `education` in
    cv.yml rather than being duplicated into `roles`, because it is a degree
    in progress and the CV lists it as one — this function is the only place
    the two are read together.

    An education entry contributes its `supervision` line rather than its
    `notes`, since `notes` holds the thesis title, which the paragraphs above
    this list on the About page have already covered.

    Kept as generated output rather than prose in index.qmd so that no job
    title or institution is ever hardcoded in a .qmd file.
    """
    entries = [
        (e.get("title"), e.get("institution"), e.get("supervision"))
        for e in (cv.get("education") or [])
        if not as_text(e.get("end"))
    ] + [
        (r.get("title"), r.get("organisation"), r.get("notes"))
        for r in (cv.get("roles") or [])
        if not as_text(r.get("end"))
    ]

    lines = []
    for heading, org, note in entries:
        heading, org, note = as_text(heading), as_text(org), as_text(note)
        line = f"- **{heading}**" if heading else "-"
        if org:
            line += f", {org}"
        if note:
            line += f" — {note}"
        lines.append(line)
    write(
        "current-positions.md",
        "\n".join(lines) if lines else "<!-- no current positions -->",
    )


def build_collaborations(cv: dict) -> None:
    """Institutions collaborated with but not employed by — the heading in
    research.qmd states that distinction explicitly."""
    entries = cv.get("collaborations") or []
    lines = []
    for entry in entries:
        org = as_text(entry.get("organisation"))
        note = as_text(entry.get("notes"))
        lines.append(f"- {org}" + (f" — {note}" if note else ""))
    write(
        "collaborations.md",
        "\n".join(lines) if lines else "<!-- no collaborations -->",
    )


def build_headshot(cv: dict) -> None:
    """Circular headshot for the About page hero.

    Emits nothing unless `personal.headshot` is set AND the file is actually
    on disk, so an unset or mistyped path leaves a clean gap rather than a
    broken image icon.
    """
    personal = cv.get("personal") or {}
    path = as_text(personal.get("headshot"))
    name = as_text(personal.get("name"))

    if path and (ROOT / path).exists():
        # Empty caption with fig-alt: the name becomes the alt attribute for
        # screen readers without Quarto rendering it as a visible figcaption.
        body = f'::: {{.headshot}}\n![]({path}){{fig-alt="{name}"}}\n:::'
    else:
        # No path echoed here — this comment ships in the public HTML. The
        # console line is for whoever ran the build.
        if path:
            print(f"build.py: no headshot at {path} — skipping the About-page image")
        body = "<!-- no headshot -->"
    write("headshot.md", body)


def build_contact(cv: dict) -> None:
    """Link row used on the About page."""
    links = (cv.get("personal") or {}).get("links") or []
    rendered = [
        f"[{as_text(l.get('label'))}]({as_text(l.get('url'))})"
        for l in links
        if as_text(l.get("label")) and as_text(l.get("url"))
    ]
    body = (
        "::: {.profile-links}\n" + " · ".join(rendered) + "\n:::"
        if rendered
        else "<!-- no links -->"
    )
    write("contact-links.md", body)


def build_talks() -> None:
    talks = (read_yaml(DATA / "talks.yml") or {}).get("talks") or []
    talks = sorted(talks, key=lambda t: sort_key(t.get("date")), reverse=True)

    blocks = []
    for talk in talks:
        title = as_text(talk.get("title"))
        lines = [as_text(talk.get("venue"))]
        # The pin is decorative — aria-hidden so a screen reader reads the place,
        # not "round pushpin".
        location = as_text(talk.get("location"))
        if location:
            lines.append(f'<span class="talk-pin" aria-hidden="true">📍</span>{location}')
        # Buttons for whatever links exist, so a talk with no slides or event
        # page simply has fewer of them.
        buttons = [
            f"[{label}]({url}){{.talk-btn}}"
            for label, url in (
                ("Slides", as_text(talk.get("slides_url"))),
                ("Event", as_text(talk.get("event_url"))),
            )
            if url
        ]
        # One line each, then the buttons together on a row of their own.
        notes = "<br>".join(lines)
        if buttons:
            notes = f'{notes}\n\n::: {{.talk-links}}\n{" ".join(buttons)}\n:::'
        blocks.append(entry_block(pretty_date(talk.get("date")), title, "", notes))

    # The wrapper narrows the date column: talk dates are short, and the extra
    # room keeps a long talk title on one line. See .talk-list in styles.scss.
    body = (
        "::: {.talk-list}\n" + "\n\n".join(blocks) + "\n:::"
        if blocks
        else placeholder("talks")
    )
    write("talks.md", body)


def build_publications() -> None:
    """The quiet note that stands in for an empty bibliography.

    Quarto renders data/publications.bib itself, so this decides only whether
    the note is needed. An entry counts as real when its `@` opens a line
    outside a comment: the file ships with worked examples commented out with
    a leading `%`, and those must not suppress the note. Adding a first paper
    empties this partial, so the note goes away with no .qmd edit.
    """
    path = DATA / "publications.bib"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []

    has_entries = False
    for line in (l.strip() for l in lines):
        if not line.startswith("@"):
            continue
        # @string, @comment and @preamble are BibTeX bookkeeping, not papers.
        if line.lower().startswith(("@string", "@comment", "@preamble")):
            continue
        has_entries = True
        break

    write(
        "publications-note.md",
        "<!-- publications listed below -->" if has_entries else placeholder("publications"),
    )


def build_variables(cv: dict) -> None:
    """Scalars for {{< var ... >}} in page prose."""
    personal = cv.get("personal") or {}
    variables = {
        "personal": {
            key: as_text(personal.get(key))
            for key in (
                "name",
                "role",
                "affiliation",
                "tagline",
                "email",
                "location",
                "aside",
            )
        }
    }
    with (ROOT / "_variables.yml").open("w", encoding="utf-8") as fh:
        fh.write("# Generated by _render/build.py from data/cv.yml. Do not edit.\n")
        yaml.safe_dump(variables, fh, allow_unicode=True, sort_keys=False)


def main() -> None:
    cv = load_cv()
    if not cv:
        sys.exit(f"No CV data found — expected {DATA / 'cv.yml'}")

    build_variables(cv)
    build_education(cv)
    build_roles(cv)
    build_service(cv)
    build_awards(cv)
    build_skills(cv)
    build_current_positions(cv)
    build_collaborations(cv)
    build_headshot(cv)
    build_contact(cv)
    build_talks()
    build_publications()

    print(f"build.py: wrote _variables.yml and {len(list(GENERATED.glob('*.md')))} partials")


if __name__ == "__main__":
    main()
