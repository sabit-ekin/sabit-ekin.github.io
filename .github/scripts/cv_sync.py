"""Bring the website in line with the Overleaf CV.

The Overleaf project syncs to Dropbox (Apps/Overleaf/Sabit_Ekin_CV). This script:
  1. builds main.tex with latexmk (TinyTeX) and, if the CV sources changed, copies the PDF to
     assets/Sabit_Ekin_CV.pdf;
  2. updates the numbers on index.html that the CV computes (articles, funding, students,
     patents, talks, editorial roles, team counts);
  3. prints which CV sections changed since the last sync and which parts of the site they feed,
     so the rest (publications, honors, news, students, courses) can be updated by hand or by
     Claude (/sync-cv).
Then run with --mark-synced to record the current CV as synced.

  python3 .github/scripts/cv_sync.py                 # build, update numbers, report changes
  python3 .github/scripts/cv_sync.py --publish       # same, then commit and push the PDF and numbers
  python3 .github/scripts/cv_sync.py --mark-synced   # after the rest of the site is updated

The last-synced copy of the CV sources is kept in tools/cv-sync/synced/ (local only, not published).
Google Scholar figures are left to update_scholar.py.
"""
import argparse, datetime, difflib, hashlib, os, re, shutil, subprocess, sys, tempfile

SRC = os.path.expanduser('~/Library/CloudStorage/Dropbox/Apps/Overleaf/Sabit_Ekin_CV')
FILES = ['main.tex', 'publications.tex', 'funding.tex', 'patents.tex', 'metrics.tex', 'cvstyle.sty']
SNAP = 'tools/cv-sync/synced'
PDF_STATE = 'tools/cv-sync/pdf-source.sha'   # sources the published PDF was built from
PAGE = 'index.html'
PDF = 'assets/Sabit_Ekin_CV.pdf'
TEX_PATH = os.path.expanduser('~/Library/TinyTeX/bin/universal-darwin')

# where each part of the CV appears on the site ("" = not on the site)
SITE = {
    '(header)': 'hero titles (.roles) and links',
    'At a Glance': 'At a glance lede and numbers; Leadership cards',
    'Research Interests': '#research lede and research cards',
    'Education': '',
    'Appointments': 'hero titles (.roles); Leadership cards',
    'Honors and Awards': '#honors list; Recent highlights',
    'Teaching': '#courses (course cards)',
    'Invited Talks and Panels': 'At a glance number (talks)',
    'Professional Service': 'At a glance number (editorial roles)',
    'Student Advising': '#team (students, alumni, counts)',
    'Technology Transfer and Entrepreneurship': 'Patents & startups card',
    'Outreach': '#outreach',
    'Media Coverage': 'In the news card; Recent highlights',
    'publications.tex': '#publications (selected list, counts); Recent highlights',
    'funding.tex': '.sponsors tiles; At a glance funding; Recent highlights',
    'patents.tex': 'Patents & startups card; At a glance patents',
    'metrics.tex': '',
    'cvstyle.sty': '',
}


def digest(folder):
    h = hashlib.sha256()
    for f in FILES:
        p = os.path.join(folder, f)
        if os.path.exists(p):
            h.update(f.encode() + open(p, 'rb').read())
    return h.hexdigest()


def build(src, out):
    for f in os.listdir(src):
        if f.endswith(('.tex', '.sty', '.cls', '.bib', '.png', '.jpg', '.pdf')):
            shutil.copy(os.path.join(src, f), out)
    env = dict(os.environ, PATH=TEX_PATH + os.pathsep + os.environ.get('PATH', ''))
    r = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
                       cwd=out, env=env, capture_output=True, text=True)
    if r.returncode or not os.path.exists(os.path.join(out, 'main.pdf')):
        log = open(os.path.join(out, 'main.log'), errors='replace').read()
        errs = [l for l in log.splitlines() if l.startswith('!') or 'not found' in l]
        sys.exit('CV did not compile; nothing changed.\n' + '\n'.join(errs[:5]))
    aux = open(os.path.join(out, 'main.aux'), errors='replace').read()
    return {k: int(v) for k, v in re.findall(r'cvtotal@(\w+)\\endcsname\{(\d+)\}', aux)}


def typed(tex):
    """Numbers typed by hand in the CV's "By the numbers" grid."""
    out = {}
    m = re.search(r'\\glnum\{(\d+)\}\{invited talks[^}]*\}\{\(incl\.~(\d+) panels\)\}', tex)
    if m: out['talks'], out['panels'] = int(m.group(1)), int(m.group(2))
    m = re.search(r'\\glnum\{(\d+)\}\{editorial roles\}\{\((\d+) current', tex)
    if m: out['editorial'], out['editorial_current'] = int(m.group(1)), int(m.group(2))
    m = re.search(r'\\msgradunlisted\}\{(\d+)\}', tex)
    if m: out['msunlisted'] = int(m.group(1))
    return out


def update_numbers(page, c, t):
    msgrads = c['msgrads'] + t.get('msunlisted', 0)
    arts = c['pubJ'] + c['pubC']
    edits = [
        (r'<div class="stat"><b>\d+</b><span>published articles, including \d+ journals</span></div>',
         f'<div class="stat"><b>{arts}</b><span>published articles, including {c["pubJ"]} journals</span></div>'),
        (r'<div class="stat"><b>\$[\d.]+M</b><span>research funding across \d+ grants, \d+ as PI</span></div>',
         f'<div class="stat"><b>${c["granttotal"] / 1e6:.1f}M</b><span>research funding across {c["grants"]} grants, {c["grantspi"]} as PI</span></div>'),
        (r'<div class="stat"><b>\d+</b><span>Ph\.D\. students mentored \(\d+ graduates\)</span></div>',
         f'<div class="stat"><b>{c["phdgrads"] + c["phdcurrent"]}</b><span>Ph.D. students mentored ({c["phdgrads"]} graduates)</span></div>'),
        (r'<div class="stat"><b>\d+</b><span>patent applications \(\d+ issued U\.S\. patents\)</span></div>',
         f'<div class="stat"><b>{c["pubissued"] + c["pubapps"]}</b><span>patent applications ({c["pubissued"]} issued U.S. patents)</span></div>'),
        (r'<p class="lede">\d+ peer-reviewed articles, including \d+ journal papers\.',
         f'<p class="lede">{arts} peer-reviewed articles, including {c["pubJ"]} journal papers.'),
        (r'Current: \d+ Ph\.D\. · \d+ M\.Sc\./MSET &nbsp;\|&nbsp; Alumni: \d+ Ph\.D\. · \d+ M\.Sc\./MSET',
         f'Current: {c["phdcurrent"]} Ph.D. · {c["mscurrent"]} M.Sc./MSET &nbsp;|&nbsp; Alumni: {c["phdgrads"]} Ph.D. · {msgrads} M.Sc./MSET'),
    ]
    if 'talks' in t:
        edits.append((r'<div class="stat"><b>\d+</b><span>invited talks and panels \(including \d+ panels\)</span></div>',
                      f'<div class="stat"><b>{t["talks"]}</b><span>invited talks and panels (including {t["panels"]} panels)</span></div>'))
    if 'editorial' in t:
        edits.append((r'<div class="stat"><b>\d+</b><span>editorial roles \(\d+ current IEEE associate editor\)</span></div>',
                      f'<div class="stat"><b>{t["editorial"]}</b><span>editorial roles ({t["editorial_current"]} current IEEE associate editor)</span></div>'))
    missing = []
    for pat, new in edits:
        page, n = re.subn(pat, lambda m: new, page, count=1)
        if not n:
            missing.append(new)
    return page, missing


def sections(lines):
    """Section title for each line of main.tex ('(header)' before the first \\section)."""
    cur, out = '(header)', []
    for l in lines:
        m = re.match(r'\\(?:section|tablesection)\{([^{}]*(?:\{[^}]*\}[^{}]*)*)\}', l.strip())
        if m:
            cur = re.sub(r'\s*\{.*', '', m.group(1)).strip()
        out.append(cur)
    return out


def report(src):
    if not os.path.isdir(SNAP):
        print('\nNo synced copy yet (first run): review the site against the whole CV, then run --mark-synced.')
        return
    changed = False
    for f in FILES:
        a = open(os.path.join(SNAP, f), errors='replace').read().splitlines() if os.path.exists(os.path.join(SNAP, f)) else []
        b = open(os.path.join(src, f), errors='replace').read().splitlines() if os.path.exists(os.path.join(src, f)) else []
        if a == b:
            continue
        changed = True
        if f != 'main.tex':
            where = SITE.get(f) or 'not on the site'
            print(f'\n=== {f}  ->  {where}')
            print('\n'.join(difflib.unified_diff(a, b, 'synced', 'now', n=1, lineterm='')))
            continue
        sa, sb = sections(a), sections(b)
        groups = {}
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == 'equal':
                continue
            sec = sb[j1] if j1 < len(sb) and j2 > j1 else (sa[i1] if i1 < len(sa) else sb[-1])
            groups.setdefault(sec, []).extend([f'- {l}' for l in a[i1:i2]] + [f'+ {l}' for l in b[j1:j2]])
        for sec, body in groups.items():
            where = SITE.get(sec, 'check the site') or 'not on the site'
            print(f'\n=== main.tex: {sec}  ->  {where}')
            print('\n'.join(body))
    if not changed:
        print('\nNo CV changes since the last sync.')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=SRC, help='Overleaf project folder (default: Dropbox sync folder)')
    ap.add_argument('--mark-synced', action='store_true', help='record the current CV sources as synced')
    ap.add_argument('--force-pdf', action='store_true', help='copy the PDF even if the sources did not change')
    ap.add_argument('--publish', action='store_true', help='commit and push the PDF and numbers (only if neither had uncommitted edits)')
    a = ap.parse_args()
    if not os.path.exists(os.path.join(a.src, 'main.tex')):
        sys.exit(f'main.tex not found in {a.src}')

    if a.mark_synced:
        os.makedirs(SNAP, exist_ok=True)
        for f in FILES:
            if os.path.exists(os.path.join(a.src, f)):
                shutil.copy(os.path.join(a.src, f), SNAP)
        print(f'Marked as synced ({digest(SNAP)[:12]}).')
        return

    if a.publish:
        if git('status', '--porcelain', PAGE, PDF):
            sys.exit(f'{PAGE} or {PDF} has uncommitted edits; publish those first. Nothing changed.')
        git('pull', '--rebase', '--autostash', '--quiet', 'origin', 'main')

    src_hash = digest(a.src)
    with tempfile.TemporaryDirectory() as out:
        counts = build(a.src, out)
        t = typed(open(os.path.join(a.src, 'main.tex'), errors='replace').read())
        old = open(PDF_STATE).read().strip() if os.path.exists(PDF_STATE) else ''
        new_src = old != src_hash
        if new_src or a.force_pdf:
            shutil.copy(os.path.join(out, 'main.pdf'), PDF)
            os.makedirs(os.path.dirname(PDF_STATE), exist_ok=True)
            open(PDF_STATE, 'w').write(src_hash + '\n')
            print(f'CV PDF updated: {PDF}')
        else:
            print('CV sources unchanged since the PDF was last built; PDF left as is.')

    page = open(PAGE, encoding='utf-8').read()
    new, missing = update_numbers(page, counts, t)
    print('Numbers on index.html updated from the CV.' if new != page else 'Numbers on index.html already match the CV.')
    if new != page or new_src or a.force_pdf:
        new = re.sub(r'Last updated [A-Z][a-z]+ \d{4}', 'Last updated ' + datetime.date.today().strftime('%B %Y'), new)
    if new != page:
        open(PAGE, 'w', encoding='utf-8').write(new)
    for k, what in (('talks', 'invited talks'), ('editorial', 'editorial roles')):
        if k not in t:
            print(f'WARNING: could not read the {what} number from main.tex (\\glnum wording changed?); check it by hand.')
    for m in missing:
        print(f'WARNING: could not find this stat on the page (markup changed?): {re.sub("<[^>]+>", " ", m).strip()}')
    if a.publish and git('status', '--porcelain', PAGE, PDF):
        git('add', PAGE, PDF)
        git('-c', 'user.name=Sabit Ekin', '-c', 'user.email=sabitekin@tamu.edu', 'commit', '--quiet',
            '-m', 'CV: update the PDF and numbers from Overleaf')
        git('push', '--quiet', 'origin', 'main')
        print('Published (pushed to main).')
    report(a.src)


def git(*args):
    r = subprocess.run(['git', *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'git {args[0]} failed: {r.stderr.strip()}')
    return r.stdout.strip()


if __name__ == '__main__':
    main()
