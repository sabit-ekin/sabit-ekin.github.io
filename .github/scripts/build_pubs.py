"""Build publications.html (the full publication list) from the CV.

Reads cv/publications.tex (and cv/patents.tex, which it inputs) and writes publications.html with the same
sections and numbers as the CV PDF (J52 ... J1, C51 ... C1, and so on). Impact factors and acceptance rates
(\\metric) are left out; awards and notes (\\award, \\pubnote) are shown. build_cv.py runs this after it builds
the PDF; it can also be run alone:

  python3 .github/scripts/build_pubs.py

Each citable entry gets a Cite button (its BibTeX entry, also collected in assets/publications.bib) and, where one
is known, a link to a free version. The details the CV does not hold (authors' full names, volume and pages from
Crossref; free versions from OpenAlex and arXiv) are looked up by DOI or title and kept in pubs_meta.json next to
this script. A normal build never goes online; after adding papers to the CV, run

  python3 .github/scripts/build_pubs.py --fetch     (looks up entries that have no record yet; --refetch: all)
  python3 .github/scripts/build_pubs.py --check     (lists where Crossref and the CV disagree)

Until then a new entry's citation is built from the CV alone (initials instead of full names). The CV wins where
the two disagree. A record with "manual": true is left alone by --refetch.

cv/ is not part of the site repo, so commit the generated publications.html, assets/publications.bib and
pubs_meta.json.
"""
import datetime, difflib, hashlib, html, json, os, re, sys, time, unicodedata, urllib.error, urllib.parse, urllib.request

SRC = 'cv'
OUT = 'publications.html'

# Sections appear in the CV's order; these are the short labels used in the page's jump links.
SHORT = {'J': 'Journals', 'C': 'Conferences', 'B': 'Books', 'P': 'Patents', 'PR': 'Preprints',
         'N': 'Other papers', 'O': 'Theses &amp; other', 'JR': 'Journals under review',
         'CR': 'Conferences under review', 'JP': 'In preparation'}
REVERSE = {'J', 'C', 'B', 'P', 'N', 'O'}  # these count down in the CV (newest = highest number)

META = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pubs_meta.json')
BIB = 'assets/publications.bib'
# Sections whose entries can be cited (published work), with the BibTeX type they start from.
CITABLE = {'J': 'article', 'C': 'inproceedings', 'B': 'book', 'PR': 'misc', 'N': 'inproceedings', 'O': 'misc'}
MONTHS = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
# Repositories a "Free version" link may point to (from OpenAlex); anything else is only printed for review.
REPOS = {'osti.gov': 'OSTI', 'par.nsf.gov': 'NSF PAR', 'ncbi.nlm.nih.gov': 'PubMed Central',
         'pmc.ncbi.nlm.nih.gov': 'PubMed Central', 'europepmc.org': 'Europe PMC', 'techrxiv.org': 'TechRxiv',
         'zenodo.org': 'Zenodo', 'ntrs.nasa.gov': 'NASA NTRS'}
UA = 'publication-list-builder/1.0'


def strip_comments(tex):
    return re.sub(r'(?<!\\)%.*', '', tex)


def arg(s, i):
    """Balanced {...} or [...] starting at s[i] (after whitespace); returns (content, index after it)."""
    while s[i].isspace():
        i += 1
    open_, close = s[i], {'{': '}', '[': ']'}[s[i]]
    depth, j = 0, i
    while True:
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == open_ or (open_ == '[' and c == '{'):
            depth += 1
        elif c == close or (open_ == '[' and c == '}'):
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1


def peek(s, i):
    while i < len(s) and s[i].isspace():
        i += 1
    return s[i] if i < len(s) else ''


def macro(s, name, fn):
    """Replace every \\name{arg} with fn(arg), innermost text converted first."""
    out, i = [], 0
    pat = re.compile(r'\\' + name + r'(?![a-zA-Z])')
    while True:
        m = pat.search(s, i)
        if not m:
            return ''.join(out) + s[i:]
        a, j = arg(s, m.end())
        out.append(s[i:m.start()] + fn(a))
        i = j


def tex(s):
    """LaTeX fragment -> HTML."""
    s = html.escape(s.strip(), quote=False)
    s = s.replace('\\&amp;', '&amp;')
    s = re.sub(r'\$\^\{(\*{1,3})\}\$', r'<sup>\1</sup>', s)
    s = s.replace('$\\sim$', '~').replace('$\\approx$', '≈')
    s = macro(s, 'textit', lambda a: '<i>' + a + '</i>')
    s = macro(s, 'textbf', lambda a: '<b>' + a + '</b>')
    s = re.sub(r'\\me(?![a-zA-Z])', '<b>S. Ekin</b>', s)
    s = s.replace('\\ ', ' ').replace('~', '\u00a0')
    s = s.replace('---', '—').replace('--', '–').replace('``', '“').replace("''", '”')
    s = re.sub(r'\s+', ' ', s)
    return s


def pills(extra):
    """\\award{...} and \\pubnote{...} from an entry's optional argument; \\metric{...} is dropped."""
    out = []
    i = 0
    for m in re.finditer(r'\\(award|pubnote|metric)(?![a-zA-Z])', extra):
        if m.start() < i:
            continue
        a, i = arg(extra, m.end())
        if m.group(1) != 'metric':
            out.append((m.group(1), tex(a)))
    rest = re.sub(r'\\(award|pubnote|metric)\s*\{(?:[^{}]|\{[^{}]*\})*\}', '', extra).strip()
    if rest:
        out.append(('pubnote', tex(rest)))
    return out


def parse(src):
    pubs = strip_comments(open(os.path.join(src, 'publications.tex'), encoding='utf-8').read())
    patents = strip_comments(open(os.path.join(src, 'patents.tex'), encoding='utf-8').read())
    patents = re.sub(r'\\ifdefined\\cvpatentsseparate.*?\\else(.*?)\\fi', r'\1', patents, flags=re.S)
    pubs = re.sub(r'\\ifdefined\\cvpatentsseparate\\else\\input\{patents\}\\fi', lambda m: patents, pubs)
    pubs = pubs[pubs.index('\\subsection'):]

    sections, cur, year, prefix = [], None, None, None
    tok = re.compile(r'\\(subsection|pubyear|pub|subm)(?![a-zA-Z])|\\begin\{publist\}(?:\[[^\]]*\])?\{(\w+)\}')
    i = 0
    while True:
        m = tok.search(pubs, i)
        if not m:
            break
        if m.group(2):
            prefix, i = m.group(2), m.end()
            if cur is not None and cur['prefix'] is None:
                cur['prefix'] = prefix
            continue
        kind, i = m.group(1), m.end()
        if kind == 'subsection':
            a, i = arg(pubs, i)
            n = re.search(r'\{\\mdseries[^(]*\((.*)\)\}\s*$', a)
            title = a[:n.start()].strip() if n else a.strip()
            cur = {'title': tex(title), 'note': tex(n.group(1)) if n else '', 'prefix': None, 'groups': []}
            sections.append(cur)
            year = None
        elif kind == 'pubyear':
            year, i = arg(pubs, i)
            cur['groups'].append({'year': tex(year), 'items': []})
        else:
            extra = ''
            if peek(pubs, i) == '[':
                extra, i = arg(pubs, i)
            f = []
            for _ in range(5):
                a, i = arg(pubs, i)
                f.append(a.strip())
            if not cur['groups'] or (year is None and cur['groups'][-1]['year']):
                cur['groups'].append({'year': '', 'items': []})
            cur['groups'][-1]['items'].append({'kind': kind, 'prefix': prefix, 'authors': tex(f[0]),
                                               'title': tex(f[1]), 'venue': tex(f[2]), 'details': tex(f[3]),
                                               'doi': f[4], 'pills': pills(extra)})
    # numbers as in the CV: count down for published lists, up for in-progress ones
    counts = {}
    for s in sections:
        for g in s['groups']:
            for it in g['items']:
                counts[it['prefix']] = counts.get(it['prefix'], 0) + 1
    seen = {}
    for s in sections:
        for g in s['groups']:
            for it in g['items']:
                p = it['prefix']
                seen[p] = seen.get(p, 0) + 1
                it['n'] = p + str(counts[p] + 1 - seen[p] if p in REVERSE else seen[p])
    return sections, counts


def check(sections):
    bad = []
    for s in sections:
        for g in s['groups']:
            for it in g['items']:
                text = ' '.join([it['authors'], it['title'], it['venue'], it['details']] + [p[1] for p in it['pills']])
                if re.search(r'[\\${}]', text):
                    bad.append(it['n'] + ': ' + text)
    if bad:
        sys.exit('Could not convert these entries (unknown LaTeX):\n' + '\n'.join(bad))


# ---------------------------------------------------------------------------------------------------------------
# Citations (BibTeX) and free versions

def plain(h):
    """HTML from tex() -> plain text (student marks dropped)."""
    h = re.sub(r'<sup>\*+</sup>', '', h)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', h)).replace(' ', ' ')).strip()


def ascii_(s):
    s = s.translate(str.maketrans({'ı': 'i', 'İ': 'I', 'ø': 'o', 'Ø': 'O', 'ł': 'l', 'Ł': 'L', 'ß': 'ss'}))
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))


def fold(s):
    """Letters and digits only, lower case, accents dropped: for comparing titles and names."""
    return re.sub(r'[^a-z0-9]+', '', ascii_(s).lower())


def meta_key(it):
    return it['doi'].lower() if it['doi'] else 'title:' + fold(plain(it['title']))


def load_meta():
    if not os.path.exists(META):    # without it the page would quietly lose its abstracts, free links and full names
        sys.exit(META + ' is missing: it is part of the site repo (restore it, or start one with {} and run --fetch).')
    return json.load(open(META, encoding='utf-8'))


def save_meta(meta):
    with open(META + '.new', 'w', encoding='utf-8') as f:     # written whole, then swapped in: never left half-written
        json.dump(meta, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write('\n')
    os.replace(META + '.new', META)


def each(sections, prefixes=CITABLE):
    for s in sections:
        for g in s['groups']:
            for it in g['items']:
                if it['prefix'] in prefixes:
                    yield it, g['year']


def cv_names(it):
    """Authors as the CV gives them: [(initials, family), ...]; "et al." becomes ('', 'others')."""
    out = []
    for n in re.split(r',\s*(?:and\s+)?|\s+and\s+', plain(it['authors'])):
        n = n.strip()
        if not n:
            continue
        if n.startswith('et al'):
            out.append(('', 'others'))
            continue
        n = re.sub(r'\.\s*-', '.-', n)        # "D. -T. Do" -> "D.-T. Do"
        n = re.sub(r'\.(?=[A-Z])', '. ', n)    # "P.G. LoPresti" -> "P. G. LoPresti"
        toks, k = n.split(), 0
        while k < len(toks) - 1 and (re.fullmatch(r'(?:[A-Z][a-z]?\.-?)+', toks[k]) or toks[k] == 'Md'):
            k += 1
        out.append((' '.join(toks[:k]), ' '.join(toks[k:])))
    return out


def tidy_name(x):
    """Crossref names in capitals -> ordinary case."""
    x = re.sub(r'\s+', ' ', html.unescape(x or '')).replace('’', "'").replace('\u2010', '-').strip()
    x = re.sub(r'(?<=[a-z])([A-Z])$', r' \1.', x)                 # "KhalidA" -> "Khalid A."
    x = re.sub(r'\b([A-Z])(?= |$)', r'\1.', x)                    # "John F" -> "John F."
    return x.title() if x.isupper() and len(x) > 3 else x


def bib_names(it, csl, notes):
    """BibTeX author field: full names from Crossref when they agree with the CV (count, family names, first
    initials), otherwise the CV's own (initials). Mostafa Ibrahim is always given under that name."""
    cv = cv_names(it)
    cr = [(tidy_name(g), tidy_name(f)) for g, f in (csl or {}).get('authors', [])]
    cr = [tuple(f.rsplit(' ', 1)) if not g and ' ' in f else (g, f) for g, f in cr]   # a name Crossref holds in one piece
    cr = [('Mostafa', 'Ibrahim') if fold(f) == 'abdelhadi' and fold(g).startswith('mostafa') else (g, f) for g, f in cr]
    if cr:
        def same(c, v):   # same family name (or a near miss: Crossref has typos such as "Imrant") and first initial
            (g, f), (i, fam) = c, v
            a, b = fold(f), fold(fam)
            near = a == b or a.endswith(b) or b.endswith(a) or difflib.SequenceMatcher(None, a, b).ratio() >= .8
            return bool(a) and near and (not g or not i or fold(g)[:1] == fold(i)[:1])
        if len(cr) == len(cv) and all(same(c, v) for c, v in zip(cr, cv)):
            fams = [f if fold(f) == fold(v[1]) or fold(f).endswith(fold(v[1])) or fold(v[1]).endswith(fold(f)) else v[1]
                    for (g, f), v in zip(cr, cv)]     # a misspelled family name: the CV's spelling
            return ' and '.join(f'{f}, {g}' if g else f for (g, _), f in zip(cr, fams))
        notes.append('authors: CV "' + plain(it['authors']) + '" | Crossref "'
                     + '; '.join((g + ' ' + f).strip() for g, f in cr) + '"')
    return ' and '.join('others' if f == 'others' else (f'{f}, {i}' if i else f) for i, f in cv)


def bx(s):
    """Plain text -> BibTeX value."""
    s = s.replace('\\', '').replace('\u2010', '-').replace('\u2011', '-').replace('\u00a0', ' ').replace('“', '``').replace('”', "''").replace('—', '---').replace('–', '--')
    return re.sub(r'([&%#_$])', r'\\\1', s)


STOP = set('a an the on of for in to and with from by at is are can if how what toward towards using via'.split())


def bib_key(it, year, used):
    fam = re.sub(r'[^A-Za-z]', '', ascii_(cv_names(it)[0][1])) or 'Anon'
    words = [re.sub(r'[^A-Za-z0-9]', '', w) for w in ascii_(plain(it['title'])).split()]   # "RF-Based" -> RFBased
    words = [w for w in words if w.lower() not in STOP and len(w) > 2]
    w = words[0] if words else 'Paper'
    key = base = fam + year + w[:1].upper() + w[1:]
    k = 1
    while key in used:
        k += 1
        key = base + 'abcdefghij'[k - 1]
    used.add(key)
    return key


DATE = (r'(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s*)?(?:\d{1,2}(?:\s*[–-]\s*\d{1,2})?,?\s*)?'
        r'(?:19|20)\d\d')


def bib_entry(it, gyear, rec, key, notes):
    """One BibTeX entry. The CV gives the title, the year and whatever else it states; Crossref (rec['csl']) adds
    full author names, the official journal or proceedings name, and volume, issue, pages and month where the CV
    has none. Differences between the two go to notes (shown by --check)."""
    p, csl = it['prefix'], (rec or {}).get('csl') or {}
    d, venue, title = plain(it['details']), plain(it['venue']), plain(it['title'])
    year = gyear if re.fullmatch(r'(?:19|20)\d\d', gyear or '') else (re.findall(r'(?:19|20)\d\d', d) or [''])[-1]

    def grab(pat):
        m = re.search(pat, d)
        return m.group(1) if m else ''
    cv = {'volume': grab(r'\bvol\.\s*([\w-]+)'), 'number': grab(r'\bno\.\s*([\w-]+)'), 'pages': grab(r'\bart\.\s*(\w+)')}
    m = re.search(r'\bpp?\.\s*(\w+)(?:\s*[–-]\s*(\w+))?', d)
    if m:
        cv['pages'] = m.group(1) + ('--' + m.group(2) if m.group(2) else '')
    m = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?', d)
    month = m.group(1).lower() if m else ''
    cr = {'volume': str(csl.get('volume') or ''), 'number': str(csl.get('issue') or ''),
          'pages': str(csl.get('page') or csl.get('article') or '').replace('-', '--')}
    early = 'early access' in d
    for k in cv:
        if cv[k] and cr[k] and fold(cv[k]) != fold(cr[k]):
            notes.append(f'{k}: CV "{cv[k]}" | Crossref "{cr[k]}"')
        elif early and k == 'volume' and cr[k]:
            notes.append(f'CV says early access; Crossref now has volume {cr[k]}')
    date = csl.get('date') or []
    if date and year and str(date[0]) != year:
        notes.append(f'year: CV {year} | Crossref {date[0]}')
    elif not month and len(date) > 1:
        month = MONTHS[int(date[1]) - 1]
    crt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', csl.get('title') or ''))).strip()
    if crt and fold(crt) != fold(title):
        notes.append(f'title: CV "{title}" | Crossref "{crt}"')
    container = re.sub(r'\s+', ' ', html.unescape(csl.get('container') or '')).strip()
    left = re.sub(r'\b(?:vol|no|pp?|art)\.\s*[\w-]+(?:\s*[–-]\s*\w+)?|early access|\(accepted\)|' + DATE, '', d)
    left = re.sub(r'(?:\s*[,;]\s*)+', ', ', left).strip(' ,;')
    left = re.sub(r'^\((.*)\)$', r'\1', left)

    typ, f = CITABLE[p], []
    if p == 'J':
        f = [('journal', container or venue)]
    elif p in ('C', 'N'):
        f = [('booktitle', container or venue)]
    elif p == 'B':
        if re.fullmatch(r'[^,]+, (?:19|20)\d\d', d):      # "Publisher, year": a chapter in the book named as venue
            typ, f, left = 'incollection', [('booktitle', venue), ('publisher', d.split(',')[0])], ''
        else:
            f = [('publisher', venue)]
    elif p == 'O' and re.match(r'(Ph\.D\.|M\.Sc\.)', venue):
        typ = 'phdthesis' if venue.startswith('Ph.D.') else 'mastersthesis'
        f = [('school', venue.split(', ', 1)[1])]
    else:                                                  # preprints, posters and other works
        f = [('howpublished', container or venue)]
    f += [(k, cv[k] or cr[k]) for k in ('volume', 'number', 'pages')]
    note = 'Early access' if early else 'Accepted; to appear' if '(accepted)' in d else 'Preprint' if p == 'PR' else ''
    if left and not csl:
        if p == 'C' or (p == 'N' and '(' not in left and len(left.split()) <= 4):
            f.append(('address', left))
        else:
            note = '; '.join(x for x in (left[:1].upper() + left[1:], note) if x)
    f += [('year', year), ('month', month), ('doi', it['doi']), ('note', note)]
    f = [('author', bib_names(it, csl, notes)), ('title', '{' + bx(title) + '}')] + [(k, v if k in ('doi', 'month') else bx(v)) for k, v in f]
    lines = [f'  {k:<12} = ' + (v if k == 'month' else '{' + v + '}') for k, v in f if v]
    return '@' + typ + '{' + key + ',\n' + ',\n'.join(lines) + '\n}'


def build_bib(sections, meta):
    """Gives every citable entry its key (it['bib']) and returns (text of the .bib file, notes per entry, entries
    with a DOI but no Crossref record yet)."""
    used, out, notes, missing = set(), [], {}, []
    for it, gyear in each(sections):
        rec = meta.get(meta_key(it)) or {}
        year = gyear if re.fullmatch(r'(?:19|20)\d\d', gyear or '') else (re.findall(r'(?:19|20)\d\d', plain(it['details'])) or [''])[-1]
        it['bib'], n = bib_key(it, year, used), []
        out.append(bib_entry(it, gyear, rec, it['bib'], n))
        if n:
            notes[it['n']] = n
        if it['doi'] and 'csl' not in rec:
            missing.append(it['n'])
    head = ('% Publications of Sabit Ekin, in the order of the list at https://sabit-ekin.github.io/publications.html\n'
            '% Generated from the CV; one entry per published work.\n\n')
    return head + '\n\n'.join(out) + '\n', notes, missing


def http(url, accept=None):
    req = urllib.request.Request(url, headers={'User-Agent': UA, **({'Accept': accept} if accept else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


def crossref(doi):
    d = json.loads(http('https://doi.org/' + urllib.parse.quote(doi, safe='/()'), 'application/vnd.citationstyles.csl+json'))
    one = lambda v: (v[0] if v else '') if isinstance(v, list) else (v or '')
    return {'type': d.get('type', ''), 'title': re.sub(r'<[^>]+>', '', one(d.get('title'))), 'container': one(d.get('container-title')),
            'volume': d.get('volume', ''), 'issue': d.get('issue', ''), 'page': d.get('page', ''),
            'article': d.get('article-number', ''), 'date': ((d.get('issued') or {}).get('date-parts') or [[]])[0],
            'authors': [[a.get('given', ''), a.get('family', '') or a.get('name', '')] for a in d.get('author', [])],
            'abstract': d.get('abstract', '')}


def openalex(doi):
    return json.loads(http('https://api.openalex.org/works/doi:' + urllib.parse.quote(doi, safe='/()')
                           + '?select=open_access,locations,abstract_inverted_index'))


def arxiv_entries(xml):
    out = []
    for e in re.findall(r'<entry>(.*?)</entry>', xml, re.S):
        g = lambda pat: ' '.join(html.unescape(m.group(1)).split()) if (m := re.search(pat, e, re.S)) else ''
        out.append({'id': re.sub(r'v\d+$', '', g(r'<id>https?://arxiv\.org/abs/(.*?)</id>')), 'title': g(r'<title>(.*?)</title>'),
                    'summary': g(r'<summary>(.*?)</summary>'),
                    'doi': g(r'<arxiv:doi[^>]*>(.*?)</arxiv:doi>').lower(), 'authors': re.findall(r'<name>(.*?)</name>', e)})
    return out


def arxiv_search(title):
    q = 'ti:"' + re.sub(r'[^A-Za-z0-9]+', ' ', ascii_(title)).strip() + '"'
    return arxiv_entries(http('https://export.arxiv.org/api/query?' + urllib.parse.urlencode({'search_query': q, 'max_results': 5})))


TEXSYM = {'sim': '~', 'geq': '≥', 'leq': '≤', 'times': '×', 'approx': '≈', 'pm': '±', 'theta': 'θ', 'phi': 'φ',
          'eta': 'η', 'lambda': 'λ', 'mu': 'μ', 'alpha': 'α', 'beta': 'β'}


def clean_abstract(a):
    """Abstract as plain text: tags, a leading "Abstract" label and $...$ around a symbol dropped; a missing space
    after a sentence or a label ("...ship.Background:Rural...") put back."""
    a = re.sub(r'<(?:jats:)?title>.*?</(?:jats:)?title>', ' ', a or '', flags=re.S | re.I)
    a = re.sub(r'\s+', ' ', html.unescape(re.sub(r'</?[A-Za-z][^<>]*>', ' ', a))).strip()   # real tags only, not "< 5 dB"
    a = re.sub(r'^Abstract\s*[:.—–-]?\s*', '', a)
    a = re.sub(r'^View Video Presentation: \S+\s*', '', a)                 # AIAA records start with this
    a = re.sub(r'\s*Copyright ©.*$', '', a).replace('\u2010', '-').replace('∘', '°')
    a = re.sub(r'\$\\(\w+)\$', lambda m: TEXSYM.get(m.group(1), m.group(0)), a)
    a = re.sub(r'\$([^$\\]{1,30})\$', r'\1', a)
    return re.sub(r'(?<=[a-z)][.?!])(?=[A-Z])|(?<=[a-z]:)(?=[A-Z])', ' ', a)


def arxiv_match(it, entries, by_title=True):
    """(arXiv id of the same paper, near misses). Same paper: its DOI, or exactly the same title, unless arXiv
    records another DOI for it (a journal paper and a conference paper can share a title)."""
    t, near, doi = fold(plain(it['title'])), [], it['doi'].lower()
    for e in entries:
        if (doi and e['doi'] == doi) or (by_title and fold(e['title']) == t and (not e['doi'] or e['doi'] == doi)):
            return e, []
        if difflib.SequenceMatcher(None, fold(e['title']), t).ratio() > .75:
            near.append(e)
    return None, near


def repo_link(url):
    """(label, link) for a copy in a repository we link to, else ('', url). arXiv copies link to the abstract page."""
    m = re.search(r'arxiv\.org/(?:abs|pdf)/(.+?)(?:v\d+)?(?:\.pdf)?$', url) or re.search(r'10\.48550/arxiv\.(.+)$', url, re.I)
    if m:
        return 'arXiv', 'https://arxiv.org/abs/' + m.group(1)
    host = re.sub(r'^www\.', '', urllib.parse.urlparse(url).netloc)
    return REPOS.get(host, ''), url


def responds(url):
    try:
        http(url)
        return True
    except Exception:
        return False


def fetch(sections, meta, everything=False, arxiv=None, only=None):
    """Look up citable entries that have no record yet (with everything: all but the ones marked manual).
    arxiv: a list from arxiv_entries() to match against instead of searching arXiv title by title."""
    today = datetime.date.today().isoformat()
    titles = [fold(plain(it['title'])) for it, _ in each(sections)]
    for it, _ in each(sections):
        key = meta_key(it)
        if (key in meta and (not everything or meta[key].get('manual'))) or (only is not None and it['n'] not in only):
            continue
        rec, title, log, abstracts = {'fetched': today}, plain(it['title']), [], {}
        if it['doi']:
            try:
                rec['csl'] = crossref(it['doi'])
                abstracts['Crossref'] = rec['csl'].pop('abstract', '')
            except Exception as e:
                log.append(f'no Crossref record ({e})')
            try:
                oa = openalex(it['doi'])
                words = sorted((i, w) for w, pos in (oa.get('abstract_inverted_index') or {}).items() for i in pos)
                abstracts['OpenAlex'] = ' '.join(w for _, w in words)
                if (oa.get('open_access') or {}).get('oa_status') in ('gold', 'diamond', 'hybrid'):
                    rec['oa'] = True
                for loc in oa.get('locations') or []:
                    url = loc.get('landing_page_url') or ''
                    if not loc.get('is_oa') or ((loc.get('source') or {}).get('type') != 'repository'):
                        continue
                    label, url = repo_link(url)
                    if label and not any(l['label'] == label for l in rec.get('links', [])):
                        if responds(url):
                            rec.setdefault('links', []).append({'label': label, 'url': url})
                        else:
                            log.append('free copy did not respond: ' + url)
                    elif not label:
                        log.append('free copy elsewhere (not added): ' + url)
            except Exception as e:
                log.append(f'no OpenAlex record ({e})')
            time.sleep(.3)
        try:
            found = arxiv if arxiv is not None else arxiv_search(title)
            if arxiv is None:
                time.sleep(3)
            known = [l['url'].rsplit('/abs/', 1)[1] for l in rec.get('links', []) if l['label'] == 'arXiv']
            # two entries with one title (a journal and a conference paper): the title alone does not say which
            hit, near = arxiv_match(it, found, by_title=titles.count(fold(title)) == 1)
            hit = next((e for e in found if e['id'] in known), hit)      # OpenAlex already named the arXiv copy
            if hit:
                abstracts['arXiv'] = hit['summary']
                if not known:
                    rec.setdefault('links', []).insert(0, {'label': 'arXiv', 'url': 'https://arxiv.org/abs/' + hit['id']})
            for e in ([] if hit else near):
                log.append(f'arXiv near miss (not added): {e["id"]} "{e["title"]}"')
        except Exception as e:
            log.append(f'arXiv search failed ({e})')
        # the abstract: the publisher's (Crossref, then OpenAlex), else the arXiv version's
        for src in ('Crossref', 'OpenAlex', 'arXiv'):
            a = clean_abstract(abstracts.get(src, ''))
            if len(a) > 200:
                rec['abstract'], rec['abstract_from'] = a, src
                break
        if rec.get('oa'):
            rec.pop('links', None)      # the title already links to the free published version
        meta[key] = rec
        save_meta(meta)
        print(f'{it["n"]}: ' + ('Crossref ' if 'csl' in rec else '') + ('open access ' if rec.get('oa') else '')
              + (f'abstract({rec["abstract_from"]}) ' if 'abstract' in rec else '')
              + ' '.join(l['label'] for l in rec.get('links', [])) + ''.join('\n    ' + x for x in log))


def entry(it, rec=None):
    rec = rec or {}
    t = it['title']
    if it['doi']:
        t = f'<a href="https://doi.org/{html.escape(it["doi"])}">{t}</a>'
    if it['kind'] == 'subm':
        v = f'Submitted to <i>{it["venue"]}</i>' + (f', {it["details"]}' if it['details'] else '')
    else:
        v = ', '.join(x for x in (f'<i>{it["venue"]}</i>' if it['venue'] else '', it['details']) if x)
        v = v[:1].upper() + v[1:]
    h = ''.join(f'<span class="pub-{"hl" if k == "award" else "note"}">{p}</span>' for k, p in it['pills'])
    n, x, a = it['n'], [], clean_abstract(rec.get('abstract', ''))
    if a:               # the abstract sits below the row, folded (find-in-page still reaches it)
        x.append(f'<button type="button" class="abs-btn" aria-expanded="false" aria-controls="abs-{n}">Abstract'
                 f'<span class="sr-only"> of {n}</span></button>')
    if it.get('bib'):   # the script at the end of the page shows this entry of assets/publications.bib
        x.append(f'<button type="button" class="cite" aria-expanded="false">Cite<span class="sr-only"> {n}</span></button>')
    if rec.get('oa') and it['doi']:
        x.append('<span class="pub-oa">Open access</span>')
    for l in rec.get('links', []):
        x.append(f'<a class="pub-l" href="{html.escape(l["url"])}">Free version · {html.escape(l["label"])}'
                 f'<span class="sr-only"> of {n}</span></a>')
    if x:
        h += '<span class="pub-x">' + ''.join(x) + '</span>'
    if a:
        h += f'<div class="abs" id="abs-{n}" hidden="until-found"><p>{html.escape(a, quote=False)}</p></div>'
    bib = f' data-bib="{it["bib"]}"' if it.get('bib') else ''
    return (f'<li id="{n}" data-n="{n}"{bib}><span class="pub-t">{t}</span><span class="pub-a">{it["authors"]}</span>'
            f'<span class="pub-v">{v}</span>{h}</li>')


def count(n):
    """Entry count shown after a section or year heading (read as ", 8 entries")."""
    return (f'<span class="n"><span class="sr-only">, </span>{n}'
            f'<span class="sr-only"> {"entry" if n == 1 else "entries"}</span></span>')


def render(sections, counts, meta, bibv):
    nav, body = [], []
    for s in sections:
        sid = s['prefix'].lower()
        n = sum(len(g['items']) for g in s['groups'])
        nav.append(f'<li><a href="#{sid}">{SHORT.get(s["prefix"], s["title"])} <span>{n}</span></a></li>')
        # sections and years collapse: the script gives each heading a button for its .sec-body / year list
        parts = [f'    <section id="{sid}" aria-labelledby="{sid}-h">',
                 f'      <h2 id="{sid}-h">{s["title"]}{count(n)}</h2>',
                 f'      <div class="sec-body" id="{sid}-body">']
        if s['note']:
            parts.append(f'      <p class="note sec-note">{s["note"]}</p>')
        for g in s['groups']:
            items = ['        ' + entry(it, meta.get(meta_key(it))) for it in g['items']]
            if g['year']:
                yid = sid + '-' + re.sub(r'\W+', '', g['year'])
                parts += [f'      <div class="yr" data-year="{html.escape(g["year"])}">',
                          f'      <h3 class="year">{g["year"]}{count(len(g["items"]))}</h3>',
                          f'      <ol class="pubs" id="{yid}">', *items, '      </ol>', '      </div>']
            else:
                parts += ['      <ol class="pubs">', *items, '      </ol>']
        parts += ['      </div>', '    </section>']
        body.append('\n'.join(parts))
    arts = counts.get('J', 0) + counts.get('C', 0)
    month = datetime.date.today().strftime('%B %Y')
    return PAGE.format(nav='\n          '.join(nav), body='\n\n'.join(body), month=month, arts=arts, bibv=bibv,
                       j=counts.get('J', 0), c=counts.get('C', 0), b=counts.get('B', 0), p=counts.get('P', 0))


def aux_counts(src):
    p = os.path.join(src, 'main.aux')
    if not os.path.exists(p):
        return {}
    aux = open(p, errors='replace').read()
    return {k[3:]: int(v) for k, v in re.findall(r'cvtotal@(pub\w+)\\endcsname\{(\d+)\}', aux)}


def main(expected=None, src=SRC, out=OUT, mode=''):
    """expected: the CV's own totals ({'J': 52, ...}); a mismatch means an entry was skipped or merged.
    mode: 'fetch' or 'refetch' looks entries up online first; 'check' lists where Crossref and the CV differ."""
    sections, counts = parse(src)
    check(sections)
    meta = load_meta()
    if mode in ('fetch', 'refetch'):
        fetch(sections, meta, everything=mode == 'refetch')
    bib, notes, missing = build_bib(sections, meta)
    if mode:
        for n, lines in notes.items():
            print(n + ':' + ''.join('\n    ' + x for x in lines))
        print(f'{len(notes)} entries where Crossref and the CV differ (the CV is used).' if notes else 'Crossref and the CV agree.')
    if missing:
        print('WARNING: no Crossref record yet for ' + ', '.join(missing)
              + '; their citations use the CV alone. Run: python3 .github/scripts/build_pubs.py --fetch')
    bibpath = os.path.join(os.path.dirname(out), BIB)
    if not os.path.exists(bibpath) or open(bibpath, encoding='utf-8').read() != bib:
        open(bibpath, 'w', encoding='utf-8').write(bib)
        print(f'{bibpath} written: {bib.count(chr(10) + "@")} entries')
    bibv = hashlib.sha1(bib.encode()).hexdigest()[:8]
    exp = expected if expected is not None else aux_counts(src)
    off = {k: (counts.get(k, 0), v) for k, v in exp.items() if k in SHORT and counts.get(k, 0) != v}
    if off:
        msg = ', '.join(f'{k}: page {a}, CV {b}' for k, (a, b) in off.items())
        if expected is not None:
            sys.exit('Publication counts differ from the CV (' + msg + '); publications.html not written.')
        print('WARNING: counts differ from cv/main.aux (stale aux?): ' + msg)
    page = render(sections, counts, meta, bibv)
    old = open(out, encoding='utf-8').read() if os.path.exists(out) else ''
    if re.sub(r'Last updated [A-Z][a-z]+ \d{4}', '', old) == re.sub(r'Last updated [A-Z][a-z]+ \d{4}', '', page):
        print(f'{out} already matches the CV.')
        return
    open(out, 'w', encoding='utf-8').write(page)
    print(f'{out} written: ' + ', '.join(f'{k} {v}' for k, v in counts.items()))


PAGE = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>document.documentElement.classList.add('js'); try {{ var t = localStorage.getItem('theme'); if (t === 'light' || t === 'dark') document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<title>Publications · Sabit Ekin</title>
<link rel="icon" href="assets/favicon.svg?v=4" type="image/svg+xml">
<link rel="icon" href="assets/favicon-32.png?v=4" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png?v=4">
<meta name="theme-color" content="#500000">
<meta name="description" content="Full list of publications by Sabit Ekin: journal articles, conference papers, books, patents, and preprints in wireless communications and sensing, AI/ML, and generative AI literacy.">
<meta property="og:title" content="Publications · Sabit Ekin">
<meta property="og:description" content="Journal articles, conference papers, books, patents, and preprints by Sabit Ekin.">
<link rel="canonical" href="https://sabit-ekin.github.io/publications.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://sabit-ekin.github.io/publications.html">
<meta property="og:image" content="https://sabit-ekin.github.io/assets/og-card.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Sabit Ekin: Wireless, AI, Education. Associate Professor, Texas A&amp;M University">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<!-- Generated from the CV by .github/scripts/build_pubs.py; do not edit by hand. -->
<style>
  :root {{
    --maroon: #500000;
    --accent: #6d0f0f;
    --bg: #fbfaf8;
    --surface: #ffffff;
    --text: #1e1b18;
    --muted: #625a53;
    --line: #e6e1db;
    --chip: #f4eeea;
    --band: #f3eee7;
    --radius: 14px;
    --serif: "EB Garamond", Georgia, serif;
    --sans: Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }}
  /* Dark: follows the system unless the theme picker forces light or dark */
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --maroon: #e7a3a3;
      --accent: #f0b9b9;
      --bg: #151312;
      --surface: #1e1b19;
      --text: #ece7e2;
      --muted: #a89f97;
      --line: #322d29;
      --chip: #2a2421;
      --band: #1c1917;
    }}
  }}
  :root[data-theme="dark"] {{
    --maroon: #e7a3a3;
    --accent: #f0b9b9;
    --bg: #151312;
    --surface: #1e1b19;
    --text: #ece7e2;
    --muted: #a89f97;
    --line: #322d29;
    --chip: #2a2421;
    --band: #1c1917;
  }}
  :root {{ color-scheme: light dark; }}
  :root[data-theme="light"] {{ color-scheme: light; }}
  :root[data-theme="dark"] {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; scroll-padding-top: 92px; }}
  body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.65 var(--sans); }}
  a {{ color: var(--accent); text-underline-offset: 3px; }}
  a:hover {{ text-decoration-thickness: 2px; }}
  :focus-visible {{ outline: 3px solid var(--maroon); outline-offset: 3px; border-radius: 4px; }}
  .wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 20px; }}
  .skip {{ position: absolute; left: -999px; }}
  .skip:focus {{ left: 16px; top: 12px; background: var(--surface); padding: 8px 12px; z-index: 10; }}

  header.nav {{
    position: sticky; top: 0; z-index: 5;
    background: color-mix(in srgb, var(--bg) 88%, transparent);
    backdrop-filter: blur(8px); border-bottom: 1px solid var(--line);
  }}
  .nav .wrap {{ display: flex; align-items: center; justify-content: space-between; height: 76px; gap: 16px; }}
  .brand {{ display: inline-flex; align-items: center; text-decoration: none; }}
  .brand picture {{ display: block; line-height: 0; }}
  .brand img {{ display: block; width: auto; height: 58px; }}
  /* Site links, as on the other pages (assets/site.css): the current page is marked; a Menu button below 800 px */
  .nav .wrap > nav {{ min-width: 0; margin-left: auto; }}
  .nav ul {{ display: flex; gap: 22px; list-style: none; margin: 0; padding: 8px 0; overflow-x: auto; min-width: 0; scrollbar-width: none; }}
  .nav ul a {{ position: relative; color: var(--muted); text-decoration: none; font-size: .92rem; font-weight: 500; white-space: nowrap; transition: color .2s; }}
  .nav ul a:hover, .nav ul a.active {{ color: var(--maroon); }}
  .nav ul a.active::after {{ content: ""; position: absolute; left: 0; right: 0; bottom: -5px; height: 2px; border-radius: 2px; background: var(--maroon); }}
  @media (max-width: 1040px) {{ .nav ul {{ gap: 14px; }} .nav ul a {{ font-size: .86rem; }} }}
  @media (max-width: 860px) {{ .nav ul {{ gap: 8px; }} .nav ul a {{ font-size: .8rem; }} }}
  .menu-btn {{ display: none; align-items: center; gap: 8px; font: 600 .9rem var(--sans); color: var(--maroon); background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 7px 14px; cursor: pointer; }}
  .menu-btn::before {{ content: ""; width: 14px; height: 10px; background: linear-gradient(currentColor 0 0) 0 0/100% 2px no-repeat, linear-gradient(currentColor 0 0) 0 50%/100% 2px no-repeat, linear-gradient(currentColor 0 0) 0 100%/100% 2px no-repeat; }}
  header.nav.open .menu-btn::before {{ background: linear-gradient(45deg, transparent 44%, currentColor 44% 56%, transparent 56%), linear-gradient(-45deg, transparent 44%, currentColor 44% 56%, transparent 56%); height: 14px; }}
  @media (max-width: 800px) {{
    .nav ul {{ display: none; }}
    .menu-btn {{ display: inline-flex; }}
    header.nav.open ul {{ display: flex; flex-direction: column; gap: 0; position: absolute; top: 70px; left: 16px; right: 16px; padding: 6px; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; box-shadow: 0 12px 30px rgba(0,0,0,.12); max-height: calc(100vh - 80px); overflow-y: auto; }}
    header.nav.open ul a {{ display: block; padding: 12px 14px; font-size: 1rem; border-radius: 10px; }}
    header.nav.open ul a:hover, header.nav.open ul a:focus-visible, header.nav.open ul a.active {{ background: var(--chip); }}
    header.nav.open ul a.active::after {{ display: none; }}
  }}

  /* Light/dark switch (assets/theme.js); its look comes from the theme alone, so it is right before the script runs */
  .theme {{ position: relative; flex: none; }}
  .theme-toggle {{ position: relative; display: block; width: 56px; height: 30px; padding: 0; border-radius: 999px; border: 1px solid var(--line); background: var(--chip); color: var(--muted); cursor: pointer; }}
  .theme-toggle:hover {{ border-color: var(--maroon); }}
  .theme svg {{ display: block; width: 14px; height: 14px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }}
  .tt-ic {{ position: absolute; inset: 0 8px; display: flex; align-items: center; justify-content: space-between; opacity: .7; }}
  .tt-knob {{ position: absolute; top: 2px; left: 2px; width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; background: var(--surface); color: var(--maroon); box-shadow: 0 1px 3px rgba(0,0,0,.25); transition: transform .2s ease; }}
  .tt-knob .i-dark {{ display: none; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) .tt-knob {{ transform: translateX(26px); }} :root:not([data-theme="light"]) .tt-knob .i-light {{ display: none; }} :root:not([data-theme="light"]) .tt-knob .i-dark {{ display: block; }} }}
  :root[data-theme="dark"] .tt-knob {{ transform: translateX(26px); }} :root[data-theme="dark"] .tt-knob .i-light {{ display: none; }} :root[data-theme="dark"] .tt-knob .i-dark {{ display: block; }}
  @media (prefers-reduced-motion: reduce) {{ .tt-knob {{ transition: none; }} }}
  /* wide screens: the switch sits in the window's top-right corner, outside the 1040 px content column */
  @media (min-width: 1200px) {{ .theme {{ position: absolute; right: 24px; top: 50%; transform: translateY(-50%); }} }}

  .intro {{ padding: 76px 0 8px; margin-bottom: 64px; }}
  h1 {{ font-family: var(--serif); font-weight: 500; font-size: clamp(2.4rem, 6vw, 3.2rem); line-height: 1.05; margin: 0 0 12px; color: var(--maroon); }}
  .lede {{ color: var(--muted); margin: 0 0 14px; max-width: 72ch; }}
  .note {{ font-size: .9rem; color: var(--muted); margin: 0; }}
  .links {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 0; }}
  .links a {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--text); text-decoration: none; font-size: .9rem; font-weight: 500; }}
  .links svg {{ width: 16px; height: 16px; flex: none; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
  .links a:hover {{ border-color: var(--maroon); color: var(--maroon); }}

  .tools {{ padding: 14px 0 12px; border-bottom: 1px solid var(--line); margin-top: 28px; }}
  .tools ul {{ display: flex; flex-wrap: wrap; gap: 6px; list-style: none; margin: 0 0 10px; padding: 0; }}
  .tools ul a {{ display: inline-flex; gap: 6px; align-items: baseline; padding: 3px 11px; border-radius: 999px; background: var(--chip); color: var(--text); text-decoration: none; font-size: .82rem; font-weight: 500; }}
  .tools ul a span {{ color: var(--muted); font-size: .76rem; }}
  .tools ul a:hover {{ color: var(--maroon); }}
  .search {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; }}
  .search label {{ font-size: .88rem; font-weight: 500; }}
  .search input {{ flex: 1 1 240px; max-width: 420px; font: 400 .95rem var(--sans); color: var(--text); background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 7px 14px; }}
  .search input:focus-visible {{ outline: 3px solid var(--maroon); outline-offset: 1px; }}
  .search output {{ font-size: .85rem; color: var(--muted); }}

  .fold {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
  .fold button {{ font: 500 .82rem var(--sans); color: var(--text); background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 4px 12px; cursor: pointer; }}
  .fold button:hover {{ border-color: var(--maroon); color: var(--maroon); }}
  .fold button:focus-visible {{ outline: 3px solid var(--maroon); outline-offset: 1px; }}

  section {{ padding: 36px 0 12px; }}
  /* search hides entries (beats display: grid on li); a collapsed section or year is hidden="until-found",
     which find-in-page can still open */
  [hidden]:not([hidden="until-found"]) {{ display: none !important; }}
  .sr-only {{ position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }}
  h2 {{ font-family: var(--serif); font-weight: 500; font-size: 1.9rem; line-height: 1.2; margin: 0 0 4px; color: var(--maroon); }}
  .sec-note {{ margin-bottom: 6px; }}
  h3.year {{ font-family: var(--serif); font-weight: 500; font-size: 1.3rem; color: var(--muted); margin: 22px 0 2px; }}
  .n {{ margin-left: 10px; padding: 2px 9px; border-radius: 999px; background: var(--chip); color: var(--muted); font: 600 .76rem var(--sans); vertical-align: middle; }}
  .tog {{ all: unset; display: inline-block; cursor: pointer; border-radius: 8px; }}  /* long titles wrap; the count follows the last word */
  .tog:hover {{ color: var(--maroon); }}
  .tog:focus-visible {{ outline: 3px solid var(--maroon); outline-offset: 3px; }}
  .tog svg {{ width: .6em; height: .6em; vertical-align: .05em; margin-right: 10px; fill: none; stroke: currentColor; stroke-width: 3; stroke-linecap: round; stroke-linejoin: round; transition: transform .2s ease; }}
  .tog[aria-expanded="false"] svg {{ transform: rotate(-90deg); }}
  section:has(> h2 > .tog[aria-expanded="false"]) {{ padding: 10px 0 0; }}  /* collapsed sections stack tightly */
  .yr:has(> h3 > .tog[aria-expanded="false"]) h3.year {{ margin: 10px 0 0; }}
  @media (prefers-reduced-motion: reduce) {{ .tog svg {{ transition: none; }} }}
  @media print {{
    [hidden="until-found"] {{ display: block !important; content-visibility: visible !important; }}
    .tog svg, .fold {{ display: none; }}
  }}
  ol.pubs {{ list-style: none; margin: 0; padding: 0; }}
  ol.pubs li {{ position: relative; display: grid; grid-template-columns: minmax(0, 1fr); gap: 3px; padding: 13px 0 13px 58px; border-bottom: 1px dashed var(--line); }}
  ol.pubs li:last-child {{ border-bottom: 0; }}
  ol.pubs li.hit {{ background: var(--chip); border-radius: 10px; box-shadow: 0 0 0 8px var(--chip); }}
  ol.pubs li::before {{ content: attr(data-n); position: absolute; left: 0; top: 13px; box-sizing: border-box; width: 46px; height: 26px; border-radius: 999px; display: grid; place-items: center; background: var(--chip); color: var(--maroon); font-weight: 600; font-size: .78rem; }}
  .pub-t {{ font-weight: 600; line-height: 1.35; }}
  .pub-t a {{ color: var(--text); text-decoration-color: var(--maroon); }}
  .pub-a {{ color: var(--muted); font-size: .9rem; }}
  .pub-a b {{ color: var(--text); }}
  .pub-v {{ color: var(--muted); font-size: .88rem; overflow-wrap: anywhere; }}
  .pub-v i {{ color: var(--maroon); font-style: italic; }}
  .pub-hl {{ justify-self: start; margin-top: 3px; font-size: .76rem; font-weight: 600; padding: 2px 10px; border-radius: 999px; background: var(--chip); color: var(--maroon); }}
  .pub-note {{ font-size: .85rem; font-style: italic; color: var(--muted); }}
  /* Abstract and Cite buttons, "Free version" link and "Open access" mark under an entry, and the panels the buttons open */
  .pub-x {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px; margin-top: 5px; }}
  .cite, .abs-btn, .pub-l, .pub-oa {{ font: 500 .78rem/1.5 var(--sans); padding: 2px 11px; border-radius: 999px; border: 1px solid var(--line); background: var(--surface); color: var(--text); text-decoration: none; }}
  .cite, .abs-btn {{ display: none; cursor: pointer; }}
  .js .cite, .js .abs-btn {{ display: inline-block; }}
  .cite:hover, .abs-btn:hover, .pub-l:hover {{ border-color: var(--maroon); color: var(--maroon); }}
  .cite[aria-expanded="true"], .abs-btn[aria-expanded="true"] {{ background: var(--chip); border-color: var(--maroon); color: var(--maroon); }}
  .cite:focus-visible, .abs-btn:focus-visible, .pub-l:focus-visible, .bib button:focus-visible {{ outline: 3px solid var(--maroon); outline-offset: 1px; }}
  .abs p {{ margin: 6px 0 2px; padding: 2px 0 2px 14px; border-left: 3px solid var(--line); font-size: .9rem; max-width: 84ch; }}  /* the box is on the p: a folded .abs takes no room */
  html:not(.js) .abs {{ display: block !important; content-visibility: visible !important; }}  /* no script: abstracts shown */
  .pub-oa {{ border-color: transparent; background: var(--chip); color: var(--muted); }}
  .bib {{ margin-top: 6px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }}
  .bib pre {{ margin: 0; padding: 12px 14px 8px; font: 400 .78rem/1.55 var(--mono); color: var(--text); white-space: pre-wrap; overflow-wrap: anywhere; }}
  .bib-bar {{ display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; padding: 0 14px 12px; font-size: .82rem; color: var(--muted); }}
  .bib button {{ font: 500 .8rem var(--sans); color: var(--text); background: var(--chip); border: 1px solid var(--line); border-radius: 999px; padding: 3px 12px; cursor: pointer; }}
  .bib button:hover {{ border-color: var(--maroon); color: var(--maroon); }}
  @media print {{ .cite, .abs-btn, .bib-bar, .abs[hidden] {{ display: none !important; }} }}
  .none {{ padding: 24px 0; color: var(--muted); }}

  footer {{ border-top: 1px solid var(--line); margin-top: 40px; padding: 28px 0 40px; color: var(--muted); font-size: .85rem; }}
  footer p {{ margin: 4px 0; }}

  @media (max-width: 640px) {{
    .wrap {{ padding: 0 16px; }}
    .brand img {{ height: 48px; }}
    .nav .wrap {{ height: 64px; }}
    html {{ scroll-padding-top: 76px; }}
    .intro {{ padding-top: 36px; }}
    ol.pubs li {{ padding-left: 0; padding-top: 42px; }}
  }}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="nav">
  <div class="wrap">
    <a class="brand" href="./"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/brand/signature-c3-dark-anim.svg"><img src="assets/brand/signature-c3-light-anim.svg" alt="Sabit Ekin, home page" width="157" height="58"></picture></a>
    <nav aria-label="Site">
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav-list">Menu</button>
      <ul id="nav-list">
        <li><a href="./">Home</a></li>
        <li><a href="research.html">Research</a></li>
        <li><a href="publications.html" class="active" aria-current="page">Publications</a></li>
        <li><a href="leadership.html">Leadership/Honors</a></li>
        <li><a href="team.html">Team</a></li>
        <li><a href="teaching.html">Teaching</a></li>
        <li><a href="outreach.html">Outreach</a></li>
        <li><a href="./#contact">Contact</a></li>
      </ul>
    </nav>
    <div class="theme"><button class="theme-toggle" type="button" role="switch" aria-checked="false" aria-label="Dark mode" title="Switch light or dark mode"><span class="tt-ic"><svg class="i-light" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="i-dark" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span><span class="tt-knob"><svg class="i-light" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg><svg class="i-dark" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/></svg></span></button></div>
  </div>
</header>
<script src="assets/theme.js?v=2"></script>

<main id="main">
  <div class="wrap">
    <div class="intro">
      <h1>Publications</h1>
      <p class="lede">{arts} peer-reviewed articles ({j} journal and {c} conference papers), {b} books and book chapters, and {p} patents, patent applications, and invention disclosures. This list matches my CV; newest first, numbered as in the CV.</p>
      <p class="note">Supervised student co-authors: Ph.D.<sup>*</sup>, M.Sc./MSET<sup>**</sup>, B.Sc.<sup>***</sup>. Titles link to the paper (DOI) where one is available. Under each paper, <strong>Abstract</strong> and <strong>Cite</strong> show its abstract and BibTeX entry; a free version is linked where one exists.</p>
      <div class="links">
        <a href="assets/Sabit_Ekin_CV.pdf"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4M10 9H8m8 4H8m8 4H8"/></svg>CV (PDF)</a>
        <a href="https://scholar.google.com/citations?user=cgJM6k0AAAAJ"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21.42 10.92a1 1 0 0 0-.02-1.84L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.83l8.57 3.91a2 2 0 0 0 1.66 0z"/><path d="M22 10v6M6 12.5V16a6 3 0 0 0 12 0v-3.5"/></svg>Google Scholar</a>
        <a href="https://orcid.org/0000-0002-9957-7752"><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10"/><path d="M8.5 7.5v.01M8.5 10.5v6M12 7.5v9h2a4.5 4.5 0 0 0 0-9z"/></svg>ORCID</a>
        <a href="assets/publications.bib" download><svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 4v11m0 0-4-4m4 4 4-4M5 19h14"/></svg>All citations (BibTeX)</a>
      </div>
    </div>

    <div class="tools">
      <nav aria-label="Publication types">
        <ul>
          {nav}
        </ul>
      </nav>
      <div class="search" role="search">
        <label for="q">Search</label>
        <input id="q" type="search" placeholder="Title, author, venue, or year" autocomplete="off">
        <output id="q-count" for="q" aria-live="polite"></output>
      </div>
    </div>

{body}

    <p class="none" id="none" hidden>No publications match this search.</p>
  </div>
</main>

<footer>
  <div class="wrap">
    <p>© 2026 Sabit Ekin · Last updated {month}</p>
    <p><a href="./">Home page</a> · Personal academic page. Views are my own.</p>
  </div>
</footer>
<script>
  // Menu button for the site links on narrow screens (as in assets/site.js)
  (function () {{
    var h = document.querySelector('header.nav'), b = h && h.querySelector('.menu-btn');
    if (!b) return;
    function set(open) {{ h.classList.toggle('open', open); b.setAttribute('aria-expanded', open); b.textContent = open ? 'Close' : 'Menu'; }}
    b.addEventListener('click', function () {{ set(!h.classList.contains('open')); }});
    document.addEventListener('keydown', function (e) {{ if (e.key === 'Escape' && h.classList.contains('open')) {{ set(false); b.focus(); }} }});
  }})();
  // Collapsible sections and years: each heading gets a disclosure button (heading order stays intact).
  // Collapsing sets hidden="until-found" on the body, so find-in-page still opens it (beforematch).
  (function () {{
    var groups = [];
    function fold(h, body) {{
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'tog'; b.setAttribute('aria-expanded', 'true'); b.setAttribute('aria-controls', body.id);
      b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>';
      while (h.firstChild) b.appendChild(h.firstChild);
      h.appendChild(b);
      var g = {{ set: function (open) {{
        b.setAttribute('aria-expanded', open);
        if (open) body.removeAttribute('hidden'); else body.setAttribute('hidden', 'until-found');
      }} }};
      b.addEventListener('click', function () {{ g.set(b.getAttribute('aria-expanded') !== 'true'); }});
      body.addEventListener('beforematch', function () {{ b.setAttribute('aria-expanded', 'true'); }});
      groups.push(g);
      return g;
    }}
    document.querySelectorAll('main section').forEach(function (s) {{
      s.fold = fold(s.querySelector('h2'), s.querySelector('.sec-body'));
      s.querySelectorAll('.yr').forEach(function (y) {{ y.fold = fold(y.querySelector('h3'), y.querySelector('ol')); }});
    }});
    var bar = document.createElement('div');
    bar.className = 'fold';
    [['Expand all', true], ['Collapse all', false]].forEach(function (x) {{
      var b = document.createElement('button');
      b.type = 'button'; b.textContent = x[0];
      b.addEventListener('click', function () {{ groups.forEach(function (g) {{ g.set(x[1]); }}); }});
      bar.appendChild(b);
    }});
    document.querySelector('.tools').appendChild(bar);
    // a section reached from the chips or a link (publications.html#j) opens
    // an entry linked from another page (publications.html#J24) opens its section and year, and is marked
    function reveal() {{
      var s = location.hash && document.getElementById(location.hash.slice(1));
      if (!s) return;
      for (var e = s; e; e = e.parentElement) if (e.fold) e.fold.set(true);
      if (s.tagName === 'LI') {{
        document.querySelectorAll('ol.pubs li.hit').forEach(function (x) {{ x.classList.remove('hit'); }});
        s.classList.add('hit'); s.scrollIntoView({{ block: 'center' }});
      }}
    }}
    document.querySelectorAll('.tools nav a').forEach(function (a) {{
      a.addEventListener('click', function () {{ var s = document.getElementById(a.hash.slice(1)); if (s && s.fold) s.fold.set(true); }});
    }});
    window.addEventListener('hashchange', reveal);
    reveal();
  }})();
  (function () {{
    var q = document.getElementById('q'), out = document.getElementById('q-count'), none = document.getElementById('none');
    var items = Array.prototype.slice.call(document.querySelectorAll('ol.pubs li'));
    var text = items.map(function (li) {{ var y = li.closest('.yr'); var t = Array.prototype.map.call(li.querySelectorAll('.pub-t, .pub-a, .pub-v, .pub-hl, .pub-note, .pub-oa, .pub-l'), function (e) {{ return e.textContent; }}).join(' '); return (li.dataset.n + ' ' + t + ' ' + (y ? y.dataset.year : '')).toLowerCase(); }});
    function run() {{
      var words = q.value.toLowerCase().split(/\\s+/).filter(Boolean), shown = 0;
      items.forEach(function (li, i) {{
        var ok = words.every(function (w) {{ return text[i].indexOf(w) >= 0; }});
        li.hidden = !ok; if (ok) shown++;
      }});
      document.querySelectorAll('main .yr, main section').forEach(function (g) {{ g.hidden = !g.querySelector('li:not([hidden])'); }});
      // a search opens the sections and years that hold matches
      if (words.length) document.querySelectorAll('main .yr:not([hidden]), main section:not([hidden])').forEach(function (g) {{ if (g.fold) g.fold.set(true); }});
      out.textContent = words.length ? shown + (shown === 1 ? ' match' : ' matches') : '';
      none.hidden = shown > 0;
    }}
    q.addEventListener('input', run);
    q.addEventListener('search', run);
  }})();
  // Abstract: opens the folded abstract under the entry (find-in-page opens it by itself: beforematch)
  document.querySelectorAll('ol.pubs button.abs-btn').forEach(function (btn) {{
    var box = document.getElementById(btn.getAttribute('aria-controls'));
    btn.addEventListener('click', function () {{
      var open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', open);
      if (open) box.removeAttribute('hidden'); else box.setAttribute('hidden', 'until-found');
    }});
    box.addEventListener('beforematch', function () {{ btn.setAttribute('aria-expanded', 'true'); }});
  }});
  // Cite: shows the entry's BibTeX (from assets/publications.bib, loaded on first use) with a Copy button
  (function () {{
    var src = 'assets/publications.bib?v={bibv}', bibs = null, loading = null;
    function load() {{
      return loading || (loading = fetch(src).then(function (r) {{ if (!r.ok) throw new Error(r.status); return r.text(); }}).then(function (t) {{ bibs = t; }}));
    }}
    function find(key) {{
      var i = bibs.indexOf('{{' + key + ','), a = bibs.lastIndexOf('@', i), b = bibs.indexOf('\\n}}', i);
      return i < 0 || a < 0 || b < 0 ? '' : bibs.slice(a, b + 2);
    }}
    document.querySelectorAll('ol.pubs button.cite').forEach(function (btn) {{
      var li = btn.closest('li'), panel = null;
      btn.addEventListener('click', function () {{
        var open = btn.getAttribute('aria-expanded') !== 'true';
        if (open && !panel) {{
          panel = document.createElement('div');
          panel.className = 'bib'; panel.id = 'bib-' + li.id;
          panel.setAttribute('role', 'group'); panel.setAttribute('aria-label', 'BibTeX entry for ' + li.id);
          var pre = document.createElement('pre'), bar = document.createElement('div'), copy = document.createElement('button'), say = document.createElement('span');
          bar.className = 'bib-bar'; copy.type = 'button'; copy.textContent = 'Copy'; copy.hidden = true;
          say.setAttribute('role', 'status'); say.textContent = 'Loading…';
          bar.appendChild(copy); bar.appendChild(say); panel.appendChild(pre); panel.appendChild(bar); li.appendChild(panel);
          btn.setAttribute('aria-controls', panel.id);
          copy.addEventListener('click', function () {{
            function done(ok) {{ say.textContent = ok ? 'Copied' : 'Selected: press Ctrl or ⌘ + C to copy'; if (ok) setTimeout(function () {{ say.textContent = ''; }}, 2500); }}
            // older way (also when the clipboard is not allowed): select the entry and copy the selection
            function select() {{
              var r = document.createRange(), sel = window.getSelection(), ok = false;
              r.selectNodeContents(pre); sel.removeAllRanges(); sel.addRange(r);
              try {{ ok = document.execCommand('copy'); }} catch (e) {{}}
              if (ok) sel.removeAllRanges();
              done(ok);
            }}
            if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(pre.textContent).then(function () {{ done(true); }}, select);
            else select();
          }});
          load().then(function () {{
            var t = find(li.dataset.bib);
            if (!t) throw new Error('missing');
            pre.textContent = t; copy.hidden = false; say.textContent = '';
          }}).catch(function () {{
            pre.hidden = true;
            say.innerHTML = 'The citation could not be loaded. All entries are in <a href="assets/publications.bib">publications.bib</a>.';
          }});
        }}
        btn.setAttribute('aria-expanded', open);
        panel.hidden = !open;
      }});
    }});
  }})();
</script>
<script src="assets/banner.js?v=8"></script>
</body>
</html>
'''

if __name__ == '__main__':
    main(mode=next((a[2:] for a in sys.argv[1:] if a in ('--fetch', '--refetch', '--check')), ''))
