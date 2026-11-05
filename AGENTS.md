# Sabit Ekin — personal home page (sabit-ekin.github.io)

Instructions for AI agents (Codex, Claude Code) editing this repository.

## What this is
- A static site published by GitHub Pages at https://sabit-ekin.github.io: a short home page (`index.html`: hero,
  At a glance, Highlights, Explore cards, Contact) and one page per area: `research.html`,
  `publications.html` (generated, see below), `leadership.html` (leadership, honors, media news), `team.html`,
  `teaching.html`, `outreach.html`. The top bar (Home first, Contact last) links to these pages and marks the current one.
- No build step for the pages. Shared styles in `assets/site.css`, shared scripts in `assets/site.js` (top bar,
  scroll-in effects, research banner); bump their `?v=` in every page when you change them. Each page keeps the
  small inline `<head>` script (theme before paint). The header, top bar, and footer are repeated in every page:
  change them in all of them (and in `build_pubs.py` for publications.html, which has its own CSS).
- Section pages use `<body class="subpage">`: the section title is the page's h1 and the headings below it are one
  level up (h2, h3) from what they were on the old single page; `site.css` gives them the same look. Section titles (`h2.sub`) are 1.9rem, the size of the section headings (Journals, ...) on publications.html.
- Page banners: every section page and publications.html load `assets/banner.js`, which draws a faint animated
  line drawing on a `--band` strip behind the title and intro, one per page (research: beams from a cell tower and a Wi-Fi access point, a QAM constellation, and a neural network side by side, taking turns on narrow screens;
  publications: pages being typeset, each finished page getting a gold star; leadership: trees that grow and blossom in gold; team: a mesh
  network growing outward from the mentor's node; teaching: an open book right of the intro, its pages turning, with a wave, a neuron, a chat bubble and an antenna rising from it; outreach: the light-wave kit, a phone's music carried by LED light to a solar cell and a speaker). It picks
  the drawing from the file name, keeps a soft clear patch around every line of the title, intro and buttons (so the
  text stays readable), reads colors from the tokens (light/dark), pauses off screen, and shows one still
  frame under prefers-reduced-motion. Bump its `?v=` in every page (and in `build_pubs.py`) when you change it.
- Explore cards on the home page each have a line icon (inline SVG in a `.ic` chip).
- Old links to sections of the single page (e.g. `/#team`, `/#honors`) forward to the new pages (inline script
  in the `<head>` of index.html).
- `.nojekyll` disables Jekyll processing.
- Course sites live in their own repositories and appear at `sabit-ekin.github.io/<course>`
  (e.g. `entc689/`). They are linked from the Teaching page (`teaching.html`); do not create course folders here.

## Source of truth
- Facts (titles, numbers, awards, courses) come from Sabit Ekin's CV, whose LaTeX sources are in `cv/`
  (see "CV" below). Read them rather than guessing. Never invent awards, numbers, dates, or links.
- The old Google Site is retired: sabitekin.com and www.sabitekin.com now permanently redirect
  (301, paths dropped) to https://sabit-ekin.github.io via Squarespace Domains forwarding
  (domain registered through Aug 2027). Do not link to sabitekin.com. Its content may be
  reused here, but it is outdated: use it only for content the CV lacks
  (project descriptions, outreach details); whenever the two disagree, the CV wins.
- Citation numbers must carry an "as of" month (the citations card ends with "Google Scholar, <month year>").
- The Google Scholar figures update weekly (Mondays 9 a.m.), on the site and in the CV in the same run,
  by a launchd job on Sabit's Mac: `~/Library/LaunchAgents/com.sabitekin.scholar-update.plist` runs
  `~/Library/Application Support/scholar-update/scholar_weekly.sh`, which uses its own clones there
  (`repo/`, and the CV in `repo/cv/`; macOS blocks background jobs from Dropbox). It runs
  `.github/scripts/update_scholar.py` (the site's citations card and the `\gs…` macros at the top of
  `cv/main.tex`), rebuilds the CV PDF with `build_cv.py` when the CV changed, and pushes both repos.
  If the CV fails to build, the site still updates and the CV is retried the next week.
  Log: `~/Library/Logs/scholar-update.log`. Scholar blocks GitHub Actions, so it can't run there.
  The script also bumps the card's month and the footer. Pull both (site and `cv/`) before editing.
- Update the "Last updated" line in the footer whenever content changes.
- Every page has a canonical link, Open Graph/Twitter tags and the shared preview image `assets/og-card.jpg`
  (1200×630; rendered from `tools/scenes/og-card.html`, local only). The home page also has schema.org Person data
  (JSON-LD in `<head>`): keep its title, affiliation and profile links in step with the hero. ORCID:
  0000-0002-9957-7752. `sitemap.xml` lists the seven pages (update `lastmod` when content changes); `robots.txt`
  points to it. `404.html` uses root-relative links (/assets/…) because GitHub Pages serves it at any missing path.

## Style
- Keep the existing design tokens in `:root` (maroon accent, EB Garamond headings, Inter body)
  and the dark-mode block. Add new colors as tokens, not hard-coded values.
- Home page sections alternate between `--bg` and a full-width `--band` (every odd `section` in `main > .wrap`),
  so a new or moved section keeps the alternation without extra markup. Section pages do the same below the banner strip: each `h2.sub` part is its own `<section class="part">`, and every
  second section (the 2nd, 4th, …) sits on the band. publications.html keeps a plain background (its sections fold and filter).
- Light/dark switch (header, top right; window corner from 1200 px): the page follows the system until the
  visitor picks the other mode (its tooltip marks the system's mode "(system)"; picking it goes back to following
  the system). `assets/theme.js` sets `data-theme` on `<html>` (saved in localStorage; an inline script in
  `<head>` applies it before paint). Every dark-mode rule needs two
  forms: `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) ... }` and
  `:root[data-theme="dark"] ...`. Logo `<picture>` sources are switched by the script; SVG figures in `<img>`
  follow the page's `color-scheme`. publications.html gets the same switch from `build_pubs.py`.
- Do not use Texas A&M logos or official branding; this is a personal page. Exception: your own materials that carry the logo
  (the DIY kit slides PDF and the kit-box photo on the Outreach page) may stay as they are.
- Keep text concise; this is a landing page, not the CV.

## Accessibility (required, WCAG 2.1 AA)
- Every image needs meaningful `alt` text; keep heading order (h1 → h2 → h3).
- Links must have descriptive text; keep visible focus styles.
- Check the page at phone width (375 px): no horizontal scrolling.

## Local-only files
- `tools/` (figure scripts, prompts, renders) is kept on this computer and is not published;
  it is listed in `.gitignore`. Never commit it or any API key.

## Common edits
- Add a course: copy an `<article class="course">` block in `teaching.html`; link to `<course>/`. Each course has its
  own line icon (inline SVG in the `.ic` chip next to the course code, same style as the Explore cards); give a new course its own.
- Publications: the home page shows no papers (its Explore card links the full list); old `/#publications` links
  forward to `publications.html`.
- Full publication list: `publications.html` is generated from `cv/publications.tex` (+ `patents.tex`) by
  `python3 .github/scripts/build_pubs.py` (also run by `build_cv.py`); numbering matches the CV (J52 … J1).
  Never edit it by hand: change the CV and rerun. Impact factors and acceptance rates (`\metric`) are left out.
  It stops on LaTeX it cannot convert; add the macro to `tex()` in the script.
  Sections and years collapse (a button in each heading; Expand all / Collapse all; search and the section chips
  open what they point to). Collapsed parts use `hidden="until-found"`, so the browser's find still reaches them.
- Add news: add an `<li>` at the top of the Highlights `.timeline` in `index.html`; keep at most ~8 items.
- CV: the LaTeX sources are in `cv/` (main document `cv/main.tex`; layout in `cvstyle.sty`; papers in
  `publications.tex`; grants in `funding.tex`; how-to in `cv/README.txt`). `cv/` is its own private repo
  (`sabit-ekin/cv`), ignored by this site's repo: commit and push CV edits there, never here. It is no longer
  linked to Overleaf. `cv_tees.tex`, `main_nai.tex`, `main-old.tex` are nomination/old variants.
  When the CV changes, update the site in the same session (`/cv` skill, `.claude/skills/cv/`, local):
  `python3 .github/scripts/build_cv.py` builds the PDF into `assets/Sabit_Ekin_CV.pdf` (linked from the hero's
  "CV (PDF)" button) and updates the CV-computed numbers on the page (articles, funding, students, patents,
  talks, editorial roles on index.html; team counts on team.html); carry new papers, honors, students, grants, and titles over by hand,
  only where the site already shows that kind of item. The CV header links to this site; keep it that way.
- Research page order: areas, the `#sky` banner, sponsors, selected current and completed projects, then the full
  list of funded projects (`details.allprojects`, open by default).
  Project cards sit two per row. The funding line (`<em>`) sits in a `.fund` row after the funders' logos
  (`.flogos` > `span.fl` > `img alt=""`, the same files as the sponsor tiles in `assets/sponsors/`); funders without a
  logo there (OSU internal grants, industry) get none. Each card ends with a "Related papers:" line (`.cites`) linking papers by CV number
  (`publications.html#J24`: every entry has its number as id, and the page opens its section and year and marks it).
  Only cite papers whose titles clearly match the project; when none do yet, the line reads "Related papers: to be added soon".
  A project with its own site gets a "Project website →" pill (`a.site`) on the title line, right-aligned (`.ptitle`); the title stays plain text.
- Sponsors: tiles in `.sponsors` (`research.html`), from the CV funding list. Logos in
  `assets/sponsors/` come from official sites or Wikimedia Commons; keep each under ~25 KB
  (large seals as small WebP). QNRF is shown with the QRDI Council logo (QNRF merged into it).
- Header and footer logos are animated: `assets/brand/signature-{c3,c1}-{light,dark}-anim.svg` (header and footer; wave draws in, arcs pulse,
  sparkles twinkle, book closes/opens; off under prefers-reduced-motion), built from the still SVGs by
  `python3 tools/make_logo_anim.py`. Rerun it whenever the signature logos are rebuilt.
- Texas Wireless logo: `assets/texas-wireless-logo.svg` (Zilla Slab "TE★AS", gold star as the X, outlined text),
  built by `python3 tools/make_tw_logo.py`; light/dark SVG and PNG exports in `tools/logo/final/texas-wireless/`.
  Keep it clearly distinct from Texas A&M marks (no ATM-style block T or bevels).
- Photo: `assets/headshot.jpg` (600×600, square crop). To replace it, overwrite that file
  with a square JPEG of similar size; keep the alt text.

- Research banner: `#sky` canvas at the top of `research.html` ("AI at the center": research areas orbit an AI core).
  Script in `assets/site.js`; colors are the `--sky-*` tokens (always a night sky, both themes); it pauses
  off screen and shows one still frame under prefers-reduced-motion. Other concepts: `tools/animations/` (local only).
- Scroll-in effects on the home page (`assets/site.js`; off under prefers-reduced-motion): the Career path cards
  come in one by one, and the "By the numbers" figures count up from zero. The counters read each final value from
  the HTML at run time, so the CV and Scholar scripts keep editing `<div class="stat"><b>…</b>` as before;
  a figure that is not a single number (the award's year range) stays still.
- Project figures: uniform SVG illustrations in `assets/projects/<name>.svg`, generated by
  `tools/project_figures.py` (shared palette + dark-mode styles, 400×300 viewBox). To add or
  change one, edit that script and run `python3 tools/project_figures.py assets/projects`.
  Keep the same style: illustrated scenes with soft gradients and shadows, tapered beams with
  wavefront ticks, pill-shaped labels; maroon hardware, gold signals/light, teal Earth/water,
  sage land. Check every figure in light and dark mode after changes.
  Each SVG has a <title>; use the same text as the <img> alt.
- 3D-render project figures (all projects): Higgsfield soft 3D isometric renders saved as
  `tools/renders/<name>.webp` (1200×900, ~40 KB), wrapped by `tools/render_figures.py` into
  `assets/projects/<name>.svg` with the same label pills drawn on top (no AI-drawn text). Run
  `python3 tools/render_figures.py assets/projects`; `project_figures.py` skips any figure that has
  a render. Labels are positioned by hand per image; check them after any change.
- New figures and icons: prefer `tools/gen_openai_image.py` (OpenAI image API; key in ~/.config/openai/key,
  never committed) with an existing render as the style reference.
- Locally rendered 3D scenes: `tools/scenes/index.html` builds scenes with three.js in the same
  clay style (used for `uav-wearables`, `v2x`, and the four research-area icons). Run
  `python3 tools/scenes/server.py 8817`, open `http://127.0.0.1:8817/?s=<scene>&save=1`; the PNG lands in
  `tools/scenes/out/`. Convert with `cwebp` to `tools/renders/<name>.webp` (project figures, 1200×900)
  or `assets/research/icon-<name>.webp` (research-card icons: `?s=icon-<name>`, transparent background,
  trimmed to the object and saved at 256×256; shown at 88 px). Keep icons to a single object, not scenes.
- Outreach: labeled 3D renders in `assets/outreach/` (GPT Image 2.5 via `tools/gen_openai_image.py`, prompts in
  `tools/image_prompts/`, renders in `tools/renders/outreach-*.webp`, built with
  `python3 tools/render_figures.py assets/outreach outreach-diy outreach-pete outreach-research outreach-museum`).
  Older notes: illustrations in `assets/outreach/` (same script; it writes them to
  `assets/projects/`, then move `outreach-*.svg` to `assets/outreach/`). Real photos in
  `assets/outreach/photos/`, 800×600 JPEG, < 100 KB each. Avoid close-up photos of young children. Exception: the two "young visitors" photos in the Outreach gallery
  were added with consent (Nov 2026). Wide photos in the gallery use `<figure class="wide">` (8:3, two columns).
- Students (`team.html`): each current student gets a wireless "spirit animal" avatar (`.av`: an emoji, a hue
  `--h`, and a `title` explaining the wireless link); alumni are text only. Do not
  copy photos from LinkedIn or other sites; only use photos a student has provided.
- Names: Mostafa Ibrahim (Ph.D. alum and postdoc) also appears as Mostafa Abdelhadi; always use
  "Mostafa Ibrahim" / "M. Ibrahim" in the CV and on the site.

## Preview
    python3 -m http.server 8000   # then open http://localhost:8000
