"""Update the Google Scholar figures on index.html and in the CV (cv/main.tex) from the Scholar profile.

Run weekly on Sabit's Mac by scholar_weekly.sh (launchd), which then rebuilds the CV PDF when the CV changed,
or by hand: python3 .github/scripts/update_scholar.py
Writes nothing if Scholar cannot be read or the numbers look wrong (exits 1). The CV part is skipped if cv/ is
not checked out.
"""
import datetime, os, re, sys, urllib.request

PROFILE = 'https://scholar.google.com/citations?user=cgJM6k0AAAAJ&hl=en'
PAGE = 'index.html'
CV = 'cv/main.tex'
CV_MONTHS = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']  # the CV's style
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

def fetch():
    req = urllib.request.Request(PROFILE, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')

def update_cv(cites, shown, h, i10, today):
    """Set the Google Scholar macros at the top of cv/main.tex (\\gsdate, \\gscites, \\gscitesround, ...)."""
    if not os.path.exists(CV):
        print(f'{CV} not found; CV not updated.')
        return
    tex = open(CV, encoding='utf-8').read()
    old = re.search(r'\\newcommand\{\\gscites\}\{([\d,]+)\}', tex)
    if not old:
        print(f'WARNING: Google Scholar macros not found in {CV}; CV not updated.')
        return
    if cites < int(old.group(1).replace(',', '')) * 0.9:
        print(f'WARNING: numbers look wrong for the CV (Scholar {cites}, CV {old.group(1)}); CV not updated.')
        return
    values = {'gsdate': f'{CV_MONTHS[today.month - 1]}~{today.year}', 'gscites': f'{cites:,}',
              'gscitesround': shown, 'gshindex': str(h), 'gsiten': str(i10)}
    new = tex
    for name, value in values.items():
        new, n = re.subn(r'(\\newcommand\{\\' + name + r'\}\{)[^}]*\}', lambda m: m.group(1) + value + '}', new, count=1)
        if not n:
            print(f'WARNING: \\{name} not found in {CV}; left as is.')
    if new == tex:
        print('CV: no change.')
        return
    open(CV, 'w', encoding='utf-8').write(new)
    print(f'CV updated: {cites:,} citations ({shown}+), h-index {h}, i10-index {i10}, {values["gsdate"]}.')

def main():
    try:
        html = fetch()
    except Exception as e:
        sys.exit(f'Could not reach Google Scholar: {e}')
    # profile table: citations (all, since), h-index (all, since), i10-index (all, since)
    nums = [int(n) for n in re.findall(r'class="gsc_rsb_std">(\d+)<', html)]
    if len(nums) < 6:
        sys.exit('Google Scholar did not return the profile table (likely blocked); nothing changed.')
    cites, h, i10 = nums[0], nums[2], nums[4]

    page = open(PAGE, encoding='utf-8').read()
    # the card also names the source and month: <small><a href="…">Google Scholar</a>, November&nbsp;2026</small>
    stat = re.search(r'<div class="stat"><b>([\d,]+)\+</b><span>citations · h-index (\d+)</span>'
                     r'<small>(<a href="[^"]+">Google Scholar</a>), [A-Z][a-z]+&nbsp;\d{4}</small></div>', page)
    if not stat:
        sys.exit('Citation stat not found in index.html; nothing changed.')
    old_cites = int(stat.group(1).replace(',', ''))
    if cites < old_cites * 0.9 or h < 1:
        sys.exit(f'Numbers look wrong (Scholar {cites}, page {old_cites}+); nothing changed.')

    today = datetime.date.today()
    shown = f'{cites // 10 * 10:,}'          # rounded down to the nearest 10, shown with "+" (site and CV)
    month = today.strftime('%B %Y')
    new = page.replace(stat.group(0), f'<div class="stat"><b>{shown}+</b><span>citations · h-index {h}</span>'
                                      f'<small>{stat.group(3)}, {month.replace(" ", "&nbsp;")}</small></div>')
    if new == page:
        print(f'Site: no change ({shown}+ citations, h-index {h}).')
    else:
        new = re.sub(r'Last updated [A-Z][a-z]+ \d{4}', f'Last updated {month}', new)
        open(PAGE, 'w', encoding='utf-8').write(new)
        print(f'Site updated: {shown}+ citations, h-index {h} (Scholar: {cites}).')
    update_cv(cites, shown, h, i10, today)

if __name__ == '__main__':
    main()
