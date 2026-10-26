"""Build the CV and update the numbers on the site that come from it.

The CV sources live in cv/ (their own private repo, sabit-ekin/cv; not part of this site's repo).
This script builds cv/main.tex with latexmk (TinyTeX), copies the PDF to assets/Sabit_Ekin_CV.pdf, and
updates the numbers on index.html that the CV computes (articles, funding, students, patents, talks,
editorial roles, team counts). Text on the site (papers, honors, students, news) is updated by hand.

  python3 .github/scripts/build_cv.py

Google Scholar figures are left to update_scholar.py.
"""
import datetime, os, re, shutil, subprocess, sys, tempfile

SRC = 'cv'
PAGE = 'index.html'
PDF = 'assets/Sabit_Ekin_CV.pdf'
TEX_PATH = os.path.expanduser('~/Library/TinyTeX/bin/universal-darwin')


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


def main():
    if not os.path.exists(os.path.join(SRC, 'main.tex')):
        sys.exit(f'{SRC}/main.tex not found (clone sabit-ekin/cv into {SRC}/)')
    with tempfile.TemporaryDirectory() as out:
        counts = build(SRC, out)
        shutil.copy(os.path.join(out, 'main.pdf'), PDF)
    print(f'CV built: {PDF}')
    t = typed(open(os.path.join(SRC, 'main.tex'), errors='replace').read())

    page = open(PAGE, encoding='utf-8').read()
    new, missing = update_numbers(page, counts, t)
    print('Numbers on index.html updated from the CV.' if new != page else 'Numbers on index.html already match the CV.')
    new = re.sub(r'Last updated [A-Z][a-z]+ \d{4}', 'Last updated ' + datetime.date.today().strftime('%B %Y'), new)
    if new != page:
        open(PAGE, 'w', encoding='utf-8').write(new)
    for k, what in (('talks', 'invited talks'), ('editorial', 'editorial roles')):
        if k not in t:
            print(f'WARNING: could not read the {what} number from main.tex (\\glnum wording changed?); check it by hand.')
    for m in missing:
        print(f'WARNING: could not find this stat on the page (markup changed?): {re.sub("<[^>]+>", " ", m).strip()}')


if __name__ == '__main__':
    main()
